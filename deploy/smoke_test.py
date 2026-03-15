from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parent.parent
BASE_URL = os.getenv("BARIBUDOS_SMOKE_BASE", "http://127.0.0.1:8787").rstrip("/")
API_URL = f"{BASE_URL}/api"


def log(message: str) -> None:
    print(f"[SMOKE] {message}")


def fail(message: str) -> None:
    raise RuntimeError(message)


def http_json(method: str, url: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"HTTP {exc.code} on {url}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"URL error on {url}: {exc}") from exc


def wait_for_backend(timeout: int = 60) -> None:
    started = time.time()
    while time.time() - started < timeout:
        try:
            data = http_json("GET", f"{API_URL}/health")
            if data.get("ok") is True:
                log("Backend respondeu em /api/health")
                return
        except Exception:
            time.sleep(1)
    fail("Backend não respondeu dentro do tempo esperado.")


def ensure_runtime_commands() -> None:
    required = ["python"]
    optional = ["ffmpeg", "ffprobe", "espeak", "espeak-ng", "node", "npm"]

    for cmd in required:
        if shutil.which(cmd) is None:
            fail(f"Comando obrigatório em falta: {cmd}")

    for cmd in optional:
        log(f"{cmd}: {'OK' if shutil.which(cmd) else 'FALTA'}")


def create_test_image(path: Path) -> None:
    from PIL import Image, ImageDraw

    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (1600, 1600), (245, 238, 214))
    draw = ImageDraw.Draw(image)
    draw.rectangle((120, 120, 1480, 1480), outline=(47, 94, 46), width=16)
    draw.text((220, 300), "Baribudos Smoke Test", fill=(47, 94, 46))
    draw.text((220, 420), "Imagem técnica temporária", fill=(80, 80, 80))
    image.save(path, format="PNG")


def start_backend() -> subprocess.Popen:
    env = os.environ.copy()
    env["BARIBUDOS_HOST"] = "127.0.0.1"
    env["BARIBUDOS_PORT"] = "8787"
    env["BARIBUDOS_RELOAD"] = "0"

    log("A arrancar backend...")
    process = subprocess.Popen(
        [sys.executable, str(ROOT / "deploy" / "start-backend.py")],
        cwd=str(ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return process


def stop_backend(process: subprocess.Popen | None) -> None:
    if not process:
        return
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()


def read_process_output(process: subprocess.Popen | None) -> str:
    if not process or process.stdout is None:
        return ""
    try:
        return process.stdout.read()
    except Exception:
        return ""


def get_or_create_editor_user() -> Dict[str, Any]:
    users_res = http_json("GET", f"{API_URL}/users")
    users = users_res.get("users", [])

    for user in users:
        if str(user.get("name", "")).strip().lower() == "smoke-admin":
            return user

    created = http_json("POST", f"{API_URL}/users", {
        "name": "smoke-admin",
        "role": "admin",
        "pin": "1234",
        "is_active": True
    })
    return created.get("user", {})


def ensure_test_ip(user: Dict[str, Any]) -> Dict[str, Any]:
    res = http_json("GET", f"{API_URL}/ip-creator?user_id={user.get('id','')}&user_name={user.get('name','')}&user_role={user.get('role','')}")
    ips = res.get("ips", [])

    for item in ips:
        if item.get("slug") == "smoke-ip":
            return item

    created = http_json("POST", f"{API_URL}/ip-creator", {
        "name": "Smoke IP",
        "slug": "smoke-ip",
        "owner_id": user.get("id", ""),
        "owner_name": user.get("name", ""),
        "exclusive": False,
        "visible_to_owner_only": True,
        "editable_by_roles": ["admin", "owner"],
        "publishable_by_roles": ["admin", "owner"],
        "cloneable": True,
        "default_language": "pt-PT",
        "output_languages": ["pt-PT", "en"],
        "metadata": {
            "author_default": "Smoke Admin",
            "producer": "Baribudos Studio",
            "tagline": "Teste técnico",
            "mission": "Validar pipeline",
            "target_age": "4-10",
            "series_name": "Smoke IP",
            "genre": "Teste",
            "description": "IP temporária para smoke test"
        }
    })
    return created.get("ip", {})


def create_test_project(user: Dict[str, Any], ip: Dict[str, Any]) -> Dict[str, Any]:
    created = http_json("POST", f"{API_URL}/projects", {
        "title": f"Smoke Test {int(time.time())}",
        "saga_slug": ip.get("slug", "smoke-ip"),
        "saga_name": ip.get("name", "Smoke IP"),
        "language": "pt-PT",
        "output_languages": ["pt-PT", "en"],
        "created_by": user.get("id", ""),
        "created_by_name": user.get("name", ""),
        "visible_to_owner_only": True
    })
    project = created.get("project", {})
    if not project.get("id"):
        fail("Projeto não foi criado corretamente.")
    return project


def patch_project_story(project_id: str, user: Dict[str, Any]) -> None:
    http_json("PATCH", f"{API_URL}/projects/{project_id}?user_name={user.get('name','')}&user_role={user.get('role','')}", {
        "story": {
            "title": "Smoke Story",
            "language": "pt-PT",
            "raw_text": (
                "Tilo encontrou uma luz estranha entre as árvores. "
                "Parou, observou e chamou a família antes de avançar. "
                "No fim, percebeu que pensar com calma protege melhor."
            )
        }
    })


def upload_test_illustration(project_id: str, ip_slug: str) -> Dict[str, Any]:
    image_path = ROOT / "storage" / "smoke_test_assets" / "smoke_illustration.png"
    create_test_image(image_path)

    boundary = "----WebKitFormBoundaryBaribudosSmoke"
    parts = []

    def add_field(name: str, value: str) -> None:
        parts.append(f"--{boundary}\r\n".encode())
        parts.append(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
        parts.append(f"{value}\r\n".encode())

    add_field("saga_id", ip_slug)
    add_field("project_id", project_id)

    file_bytes = image_path.read_bytes()
    parts.append(f"--{boundary}\r\n".encode())
    parts.append(b'Content-Disposition: form-data; name="file"; filename="smoke_illustration.png"\r\n')
    parts.append(b"Content-Type: image/png\r\n\r\n")
    parts.append(file_bytes)
    parts.append(b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())

    body = b"".join(parts)
    req = urllib.request.Request(
        f"{API_URL}/illustrations/upload",
        data=body,
        method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )
    with urllib.request.urlopen(req, timeout=120) as response:
        raw = response.read().decode("utf-8")
        result = json.loads(raw)
        return result.get("result", {})


def run_factory(project_id: str, user: Dict[str, Any]) -> Dict[str, Any]:
    return http_json("POST", f"{API_URL}/factory/run/{project_id}", {
        "userName": user.get("name", ""),
        "languages": ["pt-PT"],
        "createStory": True,
        "createTranslations": False,
        "createCover": True,
        "createEpub": True,
        "createAudiobook": True,
        "createSeries": True,
        "createGuide": True,
        "publish": False,
        "age_range": "4-10"
    })


def fill_commercial(project_id: str, user: Dict[str, Any]) -> None:
    http_json("PATCH", f"{API_URL}/project-commercial/{project_id}?user_name={user.get('name','')}&user_role={user.get('role','')}", {
        "commercial": {
            "internal_code": f"SMOKE-{project_id[:8]}",
            "isbn": "9780000000001",
            "asin": "B0SMOKETEST",
            "price": "4.99",
            "currency": "EUR",
            "collection_seal": "Smoke Collection",
            "marketplaces": ["PT"],
            "commercial_status": "ready",
            "channels": ["amazon_kdp"],
            "keywords": ["teste", "smoke", "baribudos"],
            "subtitle": "Teste técnico final",
            "blurb": "Projeto técnico para validar o pipeline do Studio."
        }
    })


def assert_file(path: str, label: str) -> None:
    if not path or not Path(path).exists():
        fail(f"Ficheiro em falta: {label} -> {path}")
    log(f"{label}: OK")


def validate_outputs(project_id: str, user: Dict[str, Any]) -> Dict[str, Any]:
    projects_res = http_json("GET", f"{API_URL}/projects?user_id={user.get('id','')}&user_name={user.get('name','')}&user_role={user.get('role','')}")
    projects = projects_res.get("projects", [])
    project = next((p for p in projects if p.get("id") == project_id), None)
    if not project:
        fail("Projeto não encontrado após factory.")

    outputs = project.get("outputs", {}) or {}
    covers = outputs.get("covers", {}) or {}
    epub = (outputs.get("epub", {}) or {}).get("pt-PT", {}) or {}
    audio = (outputs.get("audiobook", {}) or {}).get("pt-PT", {}) or {}
    video = (outputs.get("video", {}) or {}).get("pt-PT", {}) or {}

    assert_file(project.get("cover_image", ""), "project.cover_image")
    assert_file(covers.get("file_path", ""), "covers.file_path")
    assert_file(covers.get("badge_file_path", ""), "covers.badge_file_path")
    assert_file(epub.get("file_path", ""), "epub.pt-PT.file_path")
    assert_file(audio.get("file_path", ""), "audiobook.pt-PT.file_path")
    assert_file(video.get("file_path", ""), "video.pt-PT.file_path")

    return project


def validate_readiness(project_id: str, user: Dict[str, Any]) -> None:
    readiness = http_json("GET", f"{API_URL}/publish-readiness/{project_id}")
    readiness_data = readiness.get("readiness", {}) or {}
    log(f"Readiness status: {readiness_data.get('status')} ({readiness_data.get('score_percent')}%)")

    if readiness_data.get("status") not in {"yellow", "green"}:
        fail(f"Readiness demasiado baixa: {readiness_data}")

    http_json("POST", f"{API_URL}/publish-readiness/{project_id}/mark-ready?user_name={user.get('name','')}&user_role={user.get('role','')}")
    readiness_after = http_json("GET", f"{API_URL}/publish-readiness/{project_id}")
    if not readiness_after.get("ready_for_publish"):
        fail("Projeto não ficou marcado como pronto para publicar.")


def freeze_and_publish(project_id: str, user: Dict[str, Any], project: Dict[str, Any]) -> None:
    package = http_json("POST", f"{API_URL}/publication-package/{project_id}/freeze?user_name={user.get('name','')}&user_role={user.get('role','')}")
    if not package.get("publication_package"):
        fail("Falha ao congelar pacote final.")

    publication = http_json("POST", f"{API_URL}/publishing/publish?user_name={user.get('name','')}&user_role={user.get('role','')}", {
        "project_id": project_id,
        "language": project.get("language", "pt-PT"),
        "channel": "ebook",
        "requested_by": user.get("name", ""),
        "notes": "Smoke test publish"
    })

    if not publication.get("publication"):
        fail("Publish final falhou.")

    log("Publish final: OK")


def main() -> int:
    ensure_runtime_commands()

    backend_process = None
    try:
        backend_process = start_backend()
        wait_for_backend()

        diagnostics = http_json("GET", f"{API_URL}/diagnostics")
        if not diagnostics.get("ok", True):
            fail("Diagnostics falhou.")

        user = get_or_create_editor_user()
        if not user.get("id"):
            fail("User smoke-admin inválido.")

        ip = ensure_test_ip(user)
        if not ip.get("slug"):
            fail("IP smoke-ip inválida.")

        project = create_test_project(user, ip)
        project_id = project["id"]

        patch_project_story(project_id, user)
        illustration = upload_test_illustration(project_id, ip.get("slug", "smoke-ip"))
        if not illustration.get("file_path"):
            fail("Upload da ilustração falhou.")

        run_factory(project_id, user)
        project = validate_outputs(project_id, user)

        fill_commercial(project_id, user)
        validate_readiness(project_id, user)
        freeze_and_publish(project_id, user, project)

        log("SMOKE TEST COMPLETO: OK")
        return 0

    except Exception as exc:
        log(f"SMOKE TEST FALHOU: {exc}")
        if backend_process:
            output = read_process_output(backend_process)
            if output:
                print("\n=== BACKEND OUTPUT ===")
                print(output[-12000:])
        return 1

    finally:
        stop_backend(backend_process)


if __name__ == "__main__":
    raise SystemExit(main())
