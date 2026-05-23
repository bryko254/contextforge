from __future__ import annotations

import json
import re
import tempfile
from pathlib import Path
from zipfile import BadZipFile

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel, Field, ValidationError

from app.prompts.documentation_prompt import build_documentation_prompt
from app.services.gemma_client import GemmaClientError, generate_with_gemma
from app.services.scanner import SAMPLE_PROJECT, ScanResult, scan_project
from app.utils.zip_utils import safe_extract_zip

router = APIRouter(prefix="/api", tags=["generate"])

MAX_UPLOAD_BYTES = 20 * 1024 * 1024


class GeneratedSummary(BaseModel):
    project_name_guess: str
    detected_stack: list[str]
    main_features: list[str]
    risks_or_unknowns: list[str]


class GeneratedDocs(BaseModel):
    readme: str
    agent_md: str
    setup: str
    architecture: str
    summary: GeneratedSummary


class GenerateResponse(BaseModel):
    project_name: str
    source: str
    docs: GeneratedDocs
    file_summary: ScanResult = Field(alias="scan")

    model_config = {"populate_by_name": True}


@router.post("/generate", response_model=GenerateResponse)
async def generate_from_zip(file: UploadFile = File(...)) -> GenerateResponse:
    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Upload must be a ZIP file.")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        zip_path = temp_path / "upload.zip"
        extract_root = temp_path / "extracted"
        extract_root.mkdir()

        await _save_upload_with_limit(file, zip_path)

        try:
            safe_extract_zip(zip_path, extract_root)
        except (BadZipFile, ValueError) as exc:
            raise HTTPException(status_code=400, detail=str(exc) or "Invalid ZIP archive.") from exc

        project_root = _find_project_root(extract_root)
        return await _run_generation_pipeline(project_root, source="zip")


@router.get("/sample", response_model=GenerateResponse)
async def generate_from_sample() -> GenerateResponse:
    return await _run_generation_pipeline(SAMPLE_PROJECT, source="sample")


@router.post("/generate/sample", response_model=GenerateResponse)
async def generate_from_sample_compat() -> GenerateResponse:
    return await generate_from_sample()


async def _run_generation_pipeline(project_root: Path, source: str) -> GenerateResponse:
    try:
        scan = scan_project(project_root)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    project_summary = {
        "project_name": scan.project_name,
        "file_tree": scan.file_tree,
        "selected_file_count": len(scan.selected_files),
        "skipped_files": scan.skipped_files,
        "total_size": scan.total_size,
    }
    prompt = build_documentation_prompt(
        project_summary=project_summary,
        stack_summary=scan.tech_stack,
        selected_files=scan.selected_files,
    )

    try:
        raw_response = await generate_with_gemma(prompt)
        docs = _parse_generated_docs(raw_response)
    except GemmaClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return GenerateResponse(
        project_name=scan.project_name,
        source=source,
        docs=docs,
        scan=scan,
    )


async def _save_upload_with_limit(file: UploadFile, destination: Path) -> None:
    total_size = 0
    with destination.open("wb") as output:
        while chunk := await file.read(1024 * 1024):
            total_size += len(chunk)
            if total_size > MAX_UPLOAD_BYTES:
                raise HTTPException(status_code=413, detail="Uploaded ZIP is too large.")
            output.write(chunk)


def _find_project_root(extract_root: Path) -> Path:
    children = [path for path in extract_root.iterdir() if path.is_dir()]
    files = [path for path in extract_root.iterdir() if path.is_file()]
    if len(children) == 1 and not files:
        return children[0]
    return extract_root


def _parse_generated_docs(raw_response: str) -> GeneratedDocs:
    cleaned = _strip_json_fence(raw_response)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError("Gemma response was not valid JSON.") from exc

    try:
        return GeneratedDocs.model_validate(data)
    except ValidationError as exc:
        raise ValueError("Gemma response JSON did not match the expected documentation schema.") from exc


def _strip_json_fence(text: str) -> str:
    stripped = text.strip()
    match = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", stripped, flags=re.DOTALL)
    return match.group(1).strip() if match else stripped
