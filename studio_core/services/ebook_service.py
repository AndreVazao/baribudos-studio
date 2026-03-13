from __future__ import annotations

import html
import mimetypes
import zipfile
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from studio_core.core.config import resolve_storage_path


def _safe_name(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in str(value or "")).strip("_") or "ebook"


def _xml_escape(value: str) -> str:
    return html.escape(str(value or ""), quote=True)


def _build_page_xhtml(page: Dict[str, Any], language: str) -> str:
    title = _xml_escape(page.get("title", f"Página {page.get('pageNumber', 1)}"))
    text = _xml_escape(page.get("text", "")).replace("\n", "<br/>")

    return f"""<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="{language}">
  <head>
    <title>{title}</title>
    <link rel="stylesheet" type="text/css" href="../styles/style.css"/>
  </head>
  <body>
    <section class="page">
      <h1>{title}</h1>
      <p>{text}</p>
    </section>
  </body>
</html>
"""


def _build_nav(story: Dict[str, Any], language: str) -> str:
    items = []
    for page in story.get("pages", []) or []:
        number = int(page.get("pageNumber", 1))
        title = _xml_escape(page.get("title", f"Página {number}"))
        items.append(f'<li><a href="pages/page_{number}.xhtml">{title}</a></li>')

    items_html = "\n".join(items)

    return f"""<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="{language}">
  <head>
    <title>Índice</title>
  </head>
  <body>
    <nav epub:type="toc" id="toc">
      <h1>Índice</h1>
      <ol>
        {items_html}
      </ol>
    </nav>
  </body>
</html>
"""


def _build_css() -> str:
    return """
body {
  font-family: Arial, sans-serif;
  background: #F5EED6;
  color: #2F5E2E;
  margin: 0;
  padding: 40px;
}

.page {
  max-width: 900px;
  margin: 0 auto;
}

h1 {
  font-size: 2em;
  margin-bottom: 24px;
  color: #2F5E2E;
}

p {
  font-size: 1.25em;
  line-height: 1.7;
  color: #2f2f2f;
}
""".strip()


def _build_container_xml() -> str:
    return """<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/package.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""


def _build_opf(story: Dict[str, Any], title: str, language: str, author: str, cover_name: str | None) -> str:
    pages = story.get("pages", []) or []

    manifest_items: List[str] = [
        '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
        '<item id="css" href="styles/style.css" media-type="text/css"/>',
    ]

    spine_items: List[str] = []

    if cover_name:
        media_type = mimetypes.guess_type(cover_name)[0] or "image/png"
        manifest_items.append(f'<item id="cover-image" href="{cover_name}" media-type="{media_type}" properties="cover-image"/>')
        manifest_items.append('<item id="cover-page" href="cover.xhtml" media-type="application/xhtml+xml"/>')
        spine_items.append('<itemref idref="cover-page"/>')

    for page in pages:
        number = int(page.get("pageNumber", 1))
        manifest_items.append(
            f'<item id="page_{number}" href="pages/page_{number}.xhtml" media-type="application/xhtml+xml"/>'
        )
        spine_items.append(f'<itemref idref="page_{number}"/>')

    manifest = "\n    ".join(manifest_items)
    spine = "\n    ".join(spine_items)

    meta_cover = '<meta name="cover" content="cover-image"/>' if cover_name else ""

    return f"""<?xml version="1.0" encoding="utf-8"?>
<package version="3.0" unique-identifier="bookid" xmlns="http://www.idpf.org/2007/opf">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="bookid">{uuid4()}</dc:identifier>
    <dc:title>{_xml_escape(title)}</dc:title>
    <dc:language>{_xml_escape(language)}</dc:language>
    <dc:creator>{_xml_escape(author)}</dc:creator>
    <dc:publisher>Baribudos Studio</dc:publisher>
    {meta_cover}
  </metadata>
  <manifest>
    {manifest}
  </manifest>
  <spine>
    {spine}
  </spine>
</package>
"""


def _build_cover_xhtml(cover_name: str, language: str) -> str:
    return f"""<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="{language}">
  <head>
    <title>Capa</title>
  </head>
  <body style="margin:0;padding:0;text-align:center;">
    <img src="{cover_name}" alt="cover" style="max-width:100%;height:auto;"/>
  </body>
</html>
"""


def build_epub(
    story: Dict[str, Any],
    *,
    project_id: str,
    project_title: str,
    language: str,
    author: str = "André Vazão",
    cover_path: str | None = None,
) -> Dict[str, Any]:
    export_dir = resolve_storage_path("exports", project_id, "ebooks", language)
    export_dir.mkdir(parents=True, exist_ok=True)

    working_dir = export_dir / "epub_build"
    oebps_dir = working_dir / "OEBPS"
    pages_dir = oebps_dir / "pages"
    styles_dir = oebps_dir / "styles"
    meta_inf_dir = working_dir / "META-INF"

    pages_dir.mkdir(parents=True, exist_ok=True)
    styles_dir.mkdir(parents=True, exist_ok=True)
    meta_inf_dir.mkdir(parents=True, exist_ok=True)

    (working_dir / "mimetype").write_text("application/epub+zip", encoding="utf-8")
    (meta_inf_dir / "container.xml").write_text(_build_container_xml(), encoding="utf-8")
    (styles_dir / "style.css").write_text(_build_css(), encoding="utf-8")
    (oebps_dir / "nav.xhtml").write_text(_build_nav(story, language), encoding="utf-8")

    cover_name: str | None = None
    if cover_path:
        src = Path(cover_path)
        if src.exists():
            cover_name = src.name
            target = oebps_dir / cover_name
            target.write_bytes(src.read_bytes())
            (oebps_dir / "cover.xhtml").write_text(_build_cover_xhtml(cover_name, language), encoding="utf-8")

    for page in story.get("pages", []) or []:
        number = int(page.get("pageNumber", 1))
        (pages_dir / f"page_{number}.xhtml").write_text(
            _build_page_xhtml(page, language),
            encoding="utf-8",
        )

    (oebps_dir / "package.opf").write_text(
        _build_opf(story, project_title, language, author, cover_name),
        encoding="utf-8",
    )

    epub_name = f"{_safe_name(project_title)}_{language}.epub"
    epub_path = export_dir / epub_name

    with zipfile.ZipFile(epub_path, "w") as zf:
        zf.write(working_dir / "mimetype", "mimetype", compress_type=zipfile.ZIP_STORED)

        for path in sorted(working_dir.rglob("*")):
            if path.is_dir():
                continue
            if path.name == "mimetype":
                continue
            zf.write(path, path.relative_to(working_dir).as_posix(), compress_type=zipfile.ZIP_DEFLATED)

    return {
        "id": str(uuid4()),
        "language": language,
        "file_name": epub_name,
        "file_path": str(epub_path),
        "engine": "python-epub-real"
    }
    
