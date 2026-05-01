from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from studio_core.services.persistent_memory_service import (
    append_backlog_task,
    append_decision,
    append_history,
    build_ai_context,
    build_obsidian_uri,
    create_project_memory,
    initialize_memory_core,
    list_projects,
    read_project_memory,
    update_last_session,
)

router = APIRouter(prefix="/persistent-memory", tags=["persistent-memory"])


class CreateProjectPayload(BaseModel):
    project_name: str = Field(..., min_length=1)


class DecisionPayload(BaseModel):
    project_name: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)


class HistoryPayload(BaseModel):
    project_name: str = Field(..., min_length=1)
    action: str = Field(..., min_length=1)
    result: str = Field(..., min_length=1)


class BacklogPayload(BaseModel):
    project_name: str = Field(..., min_length=1)
    task: str = Field(..., min_length=1)
    priority: str = "Alta"


class LastSessionPayload(BaseModel):
    project_name: str = Field(..., min_length=1)
    summary: str = Field(..., min_length=1)
    next_steps: str = Field(..., min_length=1)


class ContextPayload(BaseModel):
    project_name: str = Field(..., min_length=1)
    user_request: str = Field(..., min_length=1)


@router.post("/initialize")
def initialize_memory() -> dict:
    try:
        return initialize_memory_core()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/projects")
def get_projects() -> dict:
    try:
        return list_projects()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/projects")
def create_project(payload: CreateProjectPayload) -> dict:
    try:
        return create_project_memory(payload.project_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/projects/{project_name}")
def get_project_memory(project_name: str) -> dict:
    try:
        return read_project_memory(project_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/decisions")
def save_decision(payload: DecisionPayload) -> dict:
    try:
        return append_decision(payload.project_name, payload.title, payload.content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/history")
def save_history(payload: HistoryPayload) -> dict:
    try:
        return append_history(payload.project_name, payload.action, payload.result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/backlog")
def save_backlog_task(payload: BacklogPayload) -> dict:
    try:
        return append_backlog_task(payload.project_name, payload.task, payload.priority)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/last-session")
def save_last_session(payload: LastSessionPayload) -> dict:
    try:
        return update_last_session(payload.project_name, payload.summary, payload.next_steps)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/context")
def get_ai_context(payload: ContextPayload) -> dict:
    try:
        return build_ai_context(payload.project_name, payload.user_request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/obsidian-uri/{project_name}/{file_name}")
def get_obsidian_uri(project_name: str, file_name: str) -> dict:
    try:
        return build_obsidian_uri(project_name, file_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
