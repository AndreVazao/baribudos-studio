from __future__ import annotations

import html
import re
import shutil
import zipfile
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from studio_core.core.config import resolve_storage_path
from studio_core.services.ip_runtime_service import load_ip_runtime


def _safe_name(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in str(value or "")).strip("_") or "ebook"


def _slug(value: str) -> str:
    text = str(value or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "item"


def _escape(value: str) -> str:
    return html.escape(str(value or ""), quote=True)


def _paragraphize(text: str) -> List[str]:
    raw = str(text or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    if not raw:
        return []
    blocks = [block.strip() for block in raw.split("\n") if block.strip()]
    if blocks:
        return blocks
    return [raw]


def _ensure_pages(story: Dict[str, Any]) -> List[Dict[str, Any]]:
    pages = story.get("pages", [])
    if isinstance(pages, list) and pages:
        normalized = []
        for index, page in enumerate(pages, start=1):
            if not isinstance(page, dict):
                continue
            normalized.append({
                "id": str(page.get("id") or uuid4()),
                "pageNumber": int(page.get("pageNumber") or index),
                "title": str(page.get("title") or f"Página {index}").strip(),
                "text": str(page.get("text") or "").strip(),
            })
        if normalized:
            return normalized

    raw_text = str(story.get("raw_text", "")).strip()
    paragraphs = _paragraphize(raw_text)
    if not paragraphs:
        paragraphs = ["Conteúdo indisponível."]

    pages = []
    chunk_size = 3
    current = []
    page_number = 1

    for paragraph in paragraphs:
        current.append(paragraph)
        if len(current) >= chunk_size:
            pages.append({
                "id": str(uuid4()),
                "pageNumber": page_number,
                "title": f"Página {page_number}",
                "text": "\n\n".join(current).strip(),
            })
            current = []
            page_number += 1

    if current:
        pages.append({
            "id": str(uuid4()),
            "pageNumber": page_number,
            "title": f"Página {page_number}",
            "text": "\n\n".join(current).strip(),
        })

    return pages


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _cover_ext(path: str | None) -> str:
    ext = Path(str(path or "")).suffix.lower()
    if ext in {".jpg", ".jpeg"}:
        return ".jpg"
    if ext == ".webp":
        return ".webp"
    return ".png"


def _cover_media_type(ext: str) -> str:
    if ext == ".jpg":
        return "image/jpeg"
    if ext == ".webp":
        return "image/webp"
    return "image/png"


def _build_styles_css() -> str:
    return """body {
  font-family: sans-serif;
  margin: 5%;
  line-height: 1.5;
}
h1, h2 {
  text-align: center;
}
p {
  margin: 0 0 1em 0;
}
.cover {
  text-align: center;
  margin-top: 1em;
}
.cover img {
  max-width: 100%;
  height: auto;
}
.meta {
  margin-top: 2em;
  font-size: 0.95em;
}
.page-break {
  page-break-before: always;
}
"""
def _build_mimetype() -> bytes:
    return b"application/epub+zip"


def _build_container_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""


def _build_nav_xhtml(book_title: str, page_files: List[str]) -> str:
    items = "\n".join(
        f'        <li><a href="{_escape(page_file)}">Página {index}</a></li>'
        for index, page_file in enumerate(page_files, start=1)
    )
    return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="pt">
<head>
  <title>Índice</title>
  <meta charset="utf-8" />
  <link rel="stylesheet" type="text/css" href="styles.css"/>
</head>
<body>
  <nav epub:type="toc" id="toc">
    <h1>{_escape(book_title)}</h1>
    <ol>
{items}
    </ol>
  </nav>
</body>
</html>
"""


def _build_cover_xhtml(
    title: str,
    subtitle: str,
    author: str,
    producer: str,
    tagline: str,
    description: str,
    cover_file_name: str | None,
) -> str:
    cover_img = (
        f'<div class="cover"><img src="images/{_escape(cover_file_name)}" alt="{_escape(title)}"/></div>'
        if cover_file_name
        else ""
    )

    subtitle_html = f"<h2>{_escape(subtitle)}</h2>" if subtitle else ""
    tagline_html = f"<p><strong>{_escape(tagline)}</strong></p>" if tagline else ""
    description_html = f"<p>{_escape(description)}</p>" if description else ""

    return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="pt">
<head>
  <title>{_escape(title)}</title>
  <meta charset="utf-8" />
  <link rel="stylesheet" type="text/css" href="styles.css"/>
</head>
<body>
  <h1>{_escape(title)}</h1>
  {subtitle_html}
  {cover_img}
  <div class="meta">
    <p><strong>Autor:</strong> {_escape(author)}</p>
    <p><strong>Produzido por:</strong> {_escape(producer)}</p>
    {tagline_html}
    {description_html}
  </div>
</body>
</html>
"""


def _build_page_xhtml(book_title: str, page_title: str, text: str) -> str:
    paragraphs = "\n".join(f"  <p>{_escape(par)}</p>" for par in _paragraphize(text))
    return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="pt">
<head>
  <title>{_escape(page_title)}</title>
  <meta charset="utf-8" />
  <link rel="stylesheet" type="text/css" href="styles.css"/>
</head>
<body>
  <h2>{_escape(book_title)}</h2>
  <h3>{_escape(page_title)}</h3>
{paragraphs}
</body>
</html>
"""


def _build_content_opf(
    *,
    identifier: str,
    title: str,
    language: str,
    author: str,
    description: str,
    cover_file_name: str | None,
    cover_media_type: str | None,
    page_files: List[str],
) -> str:
    manifest_items = [
        '    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
        '    <item id="styles" href="styles.css" media-type="text/css"/>',
        '    <item id="coverpage" href="cover.xhtml" media-type="application/xhtml+xml"/>',
    ]

    if cover_file_name and cover_media_type:
        manifest_items.append(
            f'    <item id="coverimage" href="images/{_escape(cover_file_name)}" media-type="{_escape(cover_media_type)}" properties="cover-image"/>'
        )

    spine_items = ['    <itemref idref="coverpage"/>']

    for index, page_file in enumerate(page_files, start=1):
        item_id = f"page{index}"
        manifest_items.append(
            f'    <item id="{item_id}" href="{_escape(page_file)}" media-type="application/xhtml+xml"/>'
        )
        spine_items.append(f'    <itemref idref="{item_id}"/>')

    manifest_xml = "\n".join(manifest_items)
    spine_xml = "\n".join(spine_items)

    return f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="bookid" version="3.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="bookid">{_escape(identifier)}</dc:identifier>
    <dc:title>{_escape(title)}</dc:title>
    <dc:language>{_escape(language)}</dc:language>
    <dc:creator>{_escape(author)}</dc:creator>
    <dc:description>{_escape(description)}</dc:description>
    <meta property="dcterms:modified">2026-01-01T00:00:00Z</meta>
  </metadata>
  <manifest>
{manifest_xml}
  </manifest>
  <spine>
{spine_xml}
  </spine>
</package>
"""


def _zip_epub(source_dir: Path, output_file: Path) -> None:
    with zipfile.ZipFile(output_file, "w") as zf:
        mimetype_path = source_dir / "mimetype"
        zf.write(mimetype_path, "mimetype", compress_type=zipfile.ZIP_STORED)

        for path in sorted(source_dir.rglob("*")):
            if path == mimetype_path or path.is_dir():
                continue
            arcname = path.relative_to(source_dir).as_posix()
            zf.write(path, arcname, compress_type=zipfile.ZIP_DEFLATED)


def build_epub(
    story: Dict[str, Any],
    *,
    project_id: str,
    project_title: str,
    language: str,
    author: str,
    cover_path: str | None = None,
    saga_id: str = "baribudos",
) -> Dict[str, Any]:
    runtime = load_ip_runtime(saga_id)
    metadata = runtime.get("metadata", {}) or {}

    final_author = str(author or metadata.get("author_default") or "Autor").strip()
    series_name = str(metadata.get("series_name") or runtime.get("name") or "").strip()
    producer = str(metadata.get("producer") or "").strip()
    tagline = str(metadata.get("tagline") or "").strip()
    genre = str(metadata.get("genre") or "").strip()
    description = str(metadata.get("description") or "").strip()
    subtitle = str((story.get("subtitle") or "")).strip()

    output_dir = resolve_storage_path("exports", project_id, "ebooks")
    output_dir.mkdir(parents=True, exist_ok=True)

    file_name = f"{_safe_name(project_title)}_{_safe_name(language)}.epub"
    file_path = output_dir / file_name

    work_dir = output_dir / f".tmp_{_safe_name(project_title)}_{_safe_name(language)}"
    if work_dir.exists():
        shutil.rmtree(work_dir)

    meta_inf = work_dir / "META-INF"
    oebps = work_dir / "OEBPS"
    images_dir = oebps / "images"

    images_dir.mkdir(parents=True, exist_ok=True)
    meta_inf.mkdir(parents=True, exist_ok=True)

    (work_dir / "mimetype").write_bytes(_build_mimetype())
    _write_text(meta_inf / "container.xml", _build_container_xml())
    _write_text(oebps / "styles.css", _build_styles_css())

    cover_file_name = None
    cover_media_type = None

    if cover_path and Path(cover_path).exists():
        ext = _cover_ext(cover_path)
        cover_file_name = f"cover{ext}"
        cover_media_type = _cover_media_type(ext)
        shutil.copy2(cover_path, images_dir / cover_file_name)

    _write_text(
        oebps / "cover.xhtml",
        _build_cover_xhtml(
            title=project_title,
            subtitle=subtitle,
            author=final_author,
            producer=producer,
            tagline=tagline,
            description=description,
            cover_file_name=cover_file_name,
        ),
    )

    pages = _ensure_pages(story)
    page_files: List[str] = []

    for index, page in enumerate(pages, start=1):
        page_file = f"text/page_{index:03d}.xhtml"
        page_files.append(page_file)
        _write_text(
            oebps / page_file,
            _build_page_xhtml(
                book_title=project_title,
                page_title=str(page.get("title") or f"Página {index}"),
                text=str(page.get("text") or ""),
            ),
        )

    _write_text(oebps / "nav.xhtml", _build_nav_xhtml(project_title, page_files))

    identifier = f"urn:uuid:{uuid4()}"
    opf_description = " | ".join(part for part in [series_name, genre, description] if part).strip() or project_title

    _write_text(
        oebps / "content.opf",
        _build_content_opf(
            identifier=identifier,
            title=project_title,
            language=language,
            author=final_author,
            description=opf_description,
            cover_file_name=cover_file_name,
            cover_media_type=cover_media_type,
            page_files=page_files,
        ),
    )

    _zip_epub(work_dir, file_path)
    shutil.rmtree(work_dir, ignore_errors=True)

    return {
        "id": str(uuid4()),
        "type": "ebook",
        "format": "epub",
        "language": language,
        "title": project_title,
        "author": final_author,
        "series_name": series_name,
        "producer": producer,
        "file_name": file_name,
        "file_path": str(file_path),
        "cover_path": cover_path,
        "engine": "python-ebook-builder-real"
                                                                     }
