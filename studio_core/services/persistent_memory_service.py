from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import quote

from studio_core.core.config import resolve_storage_path


BLOCKED_SECRET_KEYWORDS = [
    "password",
    "senha",
    "token",
    "api_key",
    "apikey",
    "secret",
    "client_secret",
    "private_key",
    "github_pat",
    "openai",
    "stripe_secret",
    "paypal_secret",
    "cookie",
    "authorization",
    "bearer",
]

CORE_FILES = [
    "MEMORIA_MESTRE.md",
    "DECISOES.md",
    "ARQUITETURA.md",
    "BACKLOG.md",
    "HISTORICO.md",
    "PROMPTS.md",
    "ERROS.md",
    "ULTIMA_SESSAO.md",
]

CONTEXT_PRIORITY = [
    "MEMORIA_MESTRE.md",
    "DECISOES.md",
    "ARQUITETURA.md",
    "BACKLOG.md",
    "ULTIMA_SESSAO.md",
]

DEFAULT_PROJECTS = {
    "BARIBUDOS_STUDIO": {
        "title": "BARIBUDOS STUDIO",
        "objective": "Dashboard e cérebro operacional para criar, organizar, produzir, publicar e controlar conteúdos, livros, vídeos, personagens, vozes, campanhas e o website Baribudos.",
        "focus": "Manter contexto persistente entre sessões e controlar o website sem perder decisões, backlog, histórico ou regras criativas.",
    },
    "BARIBUDOS_STUDIO_WEBSITE": {
        "title": "BARIBUDOS STUDIO WEBSITE",
        "objective": "Website público e loja do ecossistema Baribudos Studio, controlado pelo dashboard do Studio através de endpoints administrativos e publicação sincronizada.",
        "focus": "Receber publicações, bundles, visuais, catálogo e estados vindos do Studio, mantendo rastreabilidade e consistência.",
    },
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _now_title() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def _env_path(*names: str) -> Path | None:
    for name in names:
        value = os.getenv(name, "").strip()
        if value:
            return Path(value).expanduser().resolve()
    return None


def _obsidian_vault_name() -> str:
    return os.getenv("BARIBUDOS_OBSIDIAN_VAULT_NAME", "AndreOS").strip() or "AndreOS"


def _memory_root() -> Path:
    """Resolve the live Studio memory root.

    Correct production use on the home PC:
      BARIBUDOS_MEMORY_ROOT=C:\\AndreOS

    or:
      BARIBUDOS_OBSIDIAN_VAULT_ROOT=C:\\Users\\Andre\\Documents\\AndreOS

    This keeps operational memory outside the public repository and aligned with
    the local Obsidian vault. Legacy storage/memory/AndreOS remains available
    only when explicitly requested through BARIBUDOS_USE_LEGACY_STORAGE_MEMORY=1.
    """

    configured = _env_path("BARIBUDOS_MEMORY_ROOT", "BARIBUDOS_OBSIDIAN_VAULT_ROOT")
    if configured:
        return configured
    if os.getenv("BARIBUDOS_USE_LEGACY_STORAGE_MEMORY", "").strip() == "1":
        return resolve_storage_path("memory", "AndreOS").resolve()
    return (Path.home() / "AndreOS").resolve()


def _safe_project_name(project_name: str) -> str:
    value = str(project_name or "").strip().upper().replace(" ", "_").replace("-", "_")
    value = re.sub(r"[^A-Z0-9_]", "", value)
    value = re.sub(r"_+", "_", value).strip("_")
    if not value:
        raise ValueError("project_name_missing")
    return value


def _project_dir(project_name: str) -> Path:
    return _memory_root() / "02_PROJETOS" / _safe_project_name(project_name)


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def contains_blocked_secret(content: str) -> bool:
    text = str(content or "").lower()
    return any(keyword in text for keyword in BLOCKED_SECRET_KEYWORDS)


def sanitize_memory_content(content: str) -> str:
    value = str(content or "").strip()
    if contains_blocked_secret(value):
        raise ValueError("Conteudo bloqueado: possivel segredo detectado. Remova tokens, passwords ou chaves privadas antes de guardar na memoria.")
    return value


def _default_file_content(project_name: str, file_name: str) -> str:
    project_key = _safe_project_name(project_name)
    profile = DEFAULT_PROJECTS.get(project_key, {})
    title = profile.get("title", project_key)
    objective = profile.get("objective", "Descrever objetivo principal do projeto.")
    focus = profile.get("focus", "Definir proximo foco operacional.")

    if file_name == "MEMORIA_MESTRE.md":
        return f"# {title} - MEMORIA MESTRE\n\n## Objetivo\n{objective}\n\n## Fonte de verdade\nEsta nota guarda o contexto persistente operacional local do projeto no PC/Obsidian.\n\n## Relacao com outros sistemas\n- Baribudos Studio controla a producao e o dashboard.\n- Baribudos Studio Website recebe publicacoes e estado publico.\n- AndreOS Memory no GitHub deve guardar apenas contexto tecnico de programacao/repos, nao memoria operacional viva.\n\n## Regras obrigatorias\n- Consultar memoria antes de responder ou executar.\n- Guardar decisoes importantes em DECISOES.md.\n- Guardar execucoes em HISTORICO.md.\n- Atualizar ULTIMA_SESSAO.md no fim de sessoes relevantes.\n- Nunca guardar credenciais, tokens, chaves API, cookies ou segredos.\n\n## Proximo foco\n{focus}\n"
    if file_name == "DECISOES.md":
        return f"# Decisoes - {title}\n\n## {_now_title()}\nMemoria persistente operacional local criada para o projeto.\n"
    if file_name == "ARQUITETURA.md":
        return f"# Arquitetura - {title}\n\n## Estado inicial\nArquitetura a consolidar com base no repo e no fluxo Studio -> Website.\n\n## Componentes esperados\n- Memoria persistente local em Markdown no vault Obsidian AndreOS.\n- Endpoints de consulta e escrita controlada.\n- Logs de acoes.\n- Contexto compacto para IA.\n"
    if file_name == "BACKLOG.md":
        return f"# Backlog - {title}\n\n## Prioridade Alta\n- Manter memoria persistente operacional ativa no PC/Obsidian.\n- Registrar decisoes, historico e ultima sessao.\n- Separar memoria operacional local de memoria tecnica GitHub/andreos-memory.\n\n## Prioridade Media\n- Criar pesquisa semantica/vector database no futuro.\n"
    if file_name == "HISTORICO.md":
        return f"# Historico - {title}\n\n## {_now_title()}\nMemoria persistente operacional local criada.\n"
    if file_name == "ULTIMA_SESSAO.md":
        return f"# Ultima Sessao - {title}\n\n## Data\n{_now_iso()}\n\n## Estado\nMemoria persistente operacional local criada.\n\n## Proximo passo\nUsar os endpoints de memoria para ler, escrever e montar contexto para IA.\n"
    if file_name == "PROMPTS.md":
        return f"# Prompts - {title}\n\n## Prompt base\nUsa a memoria persistente operacional local deste projeto antes de responder.\n"
    if file_name == "ERROS.md":
        return f"# Erros - {title}\n\n## Estado inicial\nAinda sem erros registados.\n"
    return f"# {file_name}\n"


def initialize_memory_core() -> Dict[str, Any]:
    root = _memory_root()
    folders = [
        root / "00_INBOX",
        root / "01_MEMORIA_NUCLEAR",
        root / "02_PROJETOS",
        root / "05_LOGS_IA",
        root / "99_ARQUIVO",
    ]
    for folder in folders:
        folder.mkdir(parents=True, exist_ok=True)

    _write_text(root / "00_INBOX" / "README.md", "# Inbox\n\nEntrada rapida de notas ainda nao processadas.\n")
    _write_text(root / "01_MEMORIA_NUCLEAR" / "README.md", "# Memoria Nuclear\n\nRegras globais, perfil e contexto central do Studio.\n")

    created_projects: List[str] = []
    for project_name in DEFAULT_PROJECTS:
        create_project_memory(project_name)
        created_projects.append(project_name)

    log_path = root / "05_LOGS_IA" / "ACOES_EXECUTADAS.md"
    if not log_path.exists():
        _write_text(log_path, "# Acoes Executadas\n")

    return {
        "ok": True,
        "memory_root": str(root),
        "vault_name": _obsidian_vault_name(),
        "projects": created_projects,
        "created_at": _now_iso(),
        "legacy_storage_memory": os.getenv("BARIBUDOS_USE_LEGACY_STORAGE_MEMORY", "").strip() == "1",
    }


def create_project_memory(project_name: str) -> Dict[str, Any]:
    safe_name = _safe_project_name(project_name)
    project_path = _project_dir(safe_name)
    project_path.mkdir(parents=True, exist_ok=True)

    files: List[str] = []
    for file_name in CORE_FILES:
        file_path = project_path / file_name
        if not file_path.exists():
            _write_text(file_path, _default_file_content(safe_name, file_name))
        files.append(str(file_path))

    return {"ok": True, "project": safe_name, "path": str(project_path), "files": files}


def list_projects() -> Dict[str, Any]:
    initialize_memory_core()
    projects_root = _memory_root() / "02_PROJETOS"
    projects = sorted([path.name for path in projects_root.iterdir() if path.is_dir()]) if projects_root.exists() else []
    return {"ok": True, "memory_root": str(_memory_root()), "projects": projects}


def read_project_memory(project_name: str) -> Dict[str, Any]:
    safe_name = _safe_project_name(project_name)
    create_project_memory(safe_name)
    project_path = _project_dir(safe_name)
    files = {file_name: _read_text(project_path / file_name) for file_name in CORE_FILES}
    return {"ok": True, "project": safe_name, "memory_root": str(_memory_root()), "files": files}


def _append_to_project_file(project_name: str, file_name: str, block: str) -> Dict[str, Any]:
    safe_name = _safe_project_name(project_name)
    create_project_memory(safe_name)
    clean_block = sanitize_memory_content(block)
    path = _project_dir(safe_name) / file_name
    current = _read_text(path).rstrip()
    next_content = f"{current}\n\n{clean_block}\n" if current else f"{clean_block}\n"
    _write_text(path, next_content)
    append_global_action(safe_name, f"append:{file_name}", "updated", "success")
    return {"ok": True, "project": safe_name, "file": file_name, "path": str(path)}


def append_decision(project_name: str, title: str, content: str) -> Dict[str, Any]:
    block = f"## {_now_title()} - {sanitize_memory_content(title)}\n{sanitize_memory_content(content)}"
    return _append_to_project_file(project_name, "DECISOES.md", block)


def append_history(project_name: str, action: str, result: str) -> Dict[str, Any]:
    block = f"## {_now_title()}\n\n### Acao\n{sanitize_memory_content(action)}\n\n### Resultado\n{sanitize_memory_content(result)}"
    return _append_to_project_file(project_name, "HISTORICO.md", block)


def append_backlog_task(project_name: str, task: str, priority: str = "Alta") -> Dict[str, Any]:
    block = f"## {_now_title()} - Prioridade {sanitize_memory_content(priority)}\n- {sanitize_memory_content(task)}"
    return _append_to_project_file(project_name, "BACKLOG.md", block)


def update_last_session(project_name: str, summary: str, next_steps: str) -> Dict[str, Any]:
    safe_name = _safe_project_name(project_name)
    create_project_memory(safe_name)
    content = f"# Ultima Sessao - {safe_name}\n\n## Data\n{_now_iso()}\n\n## Resumo\n{sanitize_memory_content(summary)}\n\n## Proximos passos\n{sanitize_memory_content(next_steps)}\n"
    path = _project_dir(safe_name) / "ULTIMA_SESSAO.md"
    _write_text(path, content)
    append_global_action(safe_name, "update_last_session", "updated", "success")
    return {"ok": True, "project": safe_name, "file": "ULTIMA_SESSAO.md", "path": str(path)}


def append_global_action(project_name: str, action: str, result: str, status: str = "success") -> Dict[str, Any]:
    root = _memory_root()
    log_path = root / "05_LOGS_IA" / "ACOES_EXECUTADAS.md"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if not log_path.exists():
        _write_text(log_path, "# Acoes Executadas\n")

    block = f"\n## {_now_title()}\n\n### Projeto\n{_safe_project_name(project_name)}\n\n### Acao\n{sanitize_memory_content(action)}\n\n### Resultado\n{sanitize_memory_content(result)}\n\n### Estado\n{sanitize_memory_content(status)}\n"
    current = _read_text(log_path).rstrip()
    _write_text(log_path, f"{current}\n{block}\n")
    return {"ok": True, "path": str(log_path)}


def build_ai_context(project_name: str, user_request: str, max_chars_per_file: int = 6000) -> Dict[str, Any]:
    safe_name = _safe_project_name(project_name)
    clean_request = sanitize_memory_content(user_request)
    create_project_memory(safe_name)
    project_path = _project_dir(safe_name)

    sections: List[str] = [
        "# CONTEXTO DO PROJETO",
        "",
        "## Projeto",
        safe_name,
        "",
        "## Pedido atual do utilizador",
        clean_request,
    ]

    for file_name in CONTEXT_PRIORITY:
        raw = _read_text(project_path / file_name).strip()
        if len(raw) > max_chars_per_file:
            raw = raw[-max_chars_per_file:]
        sections.extend(["", f"## {file_name}", raw or "Sem conteudo."])

    sections.extend([
        "",
        "## Regras de execucao",
        "- Nao executar acoes destrutivas sem aprovacao.",
        "- Nao guardar segredos.",
        "- Atualizar historico no fim.",
        "- Atualizar ultima sessao no fim.",
    ])

    context = "\n".join(sections).strip() + "\n"
    return {"ok": True, "project": safe_name, "memory_root": str(_memory_root()), "context": context, "chars": len(context)}


def build_obsidian_uri(project_name: str, file_name: str = "MEMORIA_MESTRE.md") -> Dict[str, Any]:
    safe_name = _safe_project_name(project_name)
    safe_file = Path(str(file_name or "MEMORIA_MESTRE.md")).name
    file_path = f"02_PROJETOS/{safe_name}/{safe_file}"
    vault_name = _obsidian_vault_name()
    uri = f"obsidian://open?vault={quote(vault_name)}&file={quote(file_path)}"
    return {
        "ok": True,
        "project": safe_name,
        "file": safe_file,
        "vault": vault_name,
        "memory_root": str(_memory_root()),
        "uri": uri,
    }
