from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel

from app.services.stack_detector import StackSummary, detect_stack

BACKEND_DIR = Path(__file__).resolve().parents[2]
WORKSPACE_ROOT = BACKEND_DIR.parent
SAMPLE_PROJECT_ROOT = (
    WORKSPACE_ROOT / "sample-projects"
    if (WORKSPACE_ROOT / "sample-projects").exists()
    else BACKEND_DIR / "sample-projects"
)
SAMPLE_PROJECT = SAMPLE_PROJECT_ROOT / "django-api-demo"

IGNORED_DIRS = {
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
    "dist",
    "build",
    "vendor",
    "media",
    "staticfiles",
    ".next",
    ".turbo",
    "coverage",
}

IGNORED_SUFFIXES = {
    ".sqlite3",
    ".db",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".pdf",
    ".zip",
}

TEXT_SUFFIXES = {
    ".cfg",
    ".conf",
    ".css",
    ".env",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".jsx",
    ".md",
    ".mjs",
    ".php",
    ".py",
    ".rb",
    ".rs",
    ".sh",
    ".sql",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".vue",
    ".xml",
    ".yaml",
    ".yml",
}

IMPORTANT_FILE_NAMES = {
    "README.md",
    "package.json",
    "requirements.txt",
    "pyproject.toml",
    "composer.json",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "manage.py",
    "settings.py",
    "urls.py",
    "models.py",
    "views.py",
    "serializers.py",
}

IMPORTANT_PATH_PARTS = {"routes", "src", "app"}
MAX_FILE_SIZE_BYTES = 80 * 1024
MAX_TOTAL_CONTENT_BYTES = 300 * 1024
MAX_TREE_ENTRIES = 250


class SelectedFile(BaseModel):
    path: str
    content: str
    size: int


class ScanResult(BaseModel):
    project_name: str
    file_tree: list[str]
    selected_files: list[SelectedFile]
    skipped_files: int
    total_size: int
    tech_stack: StackSummary
    files: list[str]


class _Candidate(BaseModel):
    path: Path
    relative_path: str
    size: int
    priority: int


def scan_project(project_dir: str | Path) -> ScanResult:
    project_root = Path(project_dir).resolve()
    if not project_root.exists() or not project_root.is_dir():
        raise ValueError(f"Project directory does not exist: {project_root}")

    file_tree: list[str] = []
    candidates: list[_Candidate] = []
    skipped_files = 0

    for path in _walk_project(project_root):
        relative_path = path.relative_to(project_root).as_posix()

        if len(file_tree) < MAX_TREE_ENTRIES:
            file_tree.append(relative_path)

        if _should_ignore_file(path):
            skipped_files += 1
            continue

        try:
            size = path.stat().st_size
        except OSError:
            skipped_files += 1
            continue

        if size > MAX_FILE_SIZE_BYTES:
            skipped_files += 1
            continue

        if not _looks_like_text_file(path):
            skipped_files += 1
            continue

        candidates.append(
            _Candidate(
                path=path,
                relative_path=relative_path,
                size=size,
                priority=_priority_for(relative_path),
            )
        )

    selected_files: list[SelectedFile] = []
    total_size = 0

    for candidate in sorted(candidates, key=lambda item: (item.priority, len(item.relative_path), item.relative_path)):
        if total_size >= MAX_TOTAL_CONTENT_BYTES:
            skipped_files += 1
            continue

        remaining_bytes = MAX_TOTAL_CONTENT_BYTES - total_size
        try:
            content = candidate.path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            skipped_files += 1
            continue

        encoded = content.encode("utf-8")
        if len(encoded) > remaining_bytes:
            content = encoded[:remaining_bytes].decode("utf-8", errors="ignore")

        content_size = len(content.encode("utf-8"))
        selected_files.append(
            SelectedFile(
                path=candidate.relative_path,
                content=content,
                size=content_size,
            )
        )
        total_size += content_size

    selected_paths = [file.path for file in selected_files]
    return ScanResult(
        project_name=project_root.name,
        file_tree=file_tree,
        selected_files=selected_files,
        skipped_files=skipped_files,
        total_size=total_size,
        tech_stack=detect_stack(selected_files),
        files=selected_paths,
    )


def scan_sample_project() -> ScanResult:
    return scan_project(SAMPLE_PROJECT)


def _walk_project(project_root: Path) -> list[Path]:
    files: list[Path] = []
    for directory_name, dirnames, filenames in os.walk(project_root):
        dirnames[:] = sorted(dirname for dirname in dirnames if dirname not in IGNORED_DIRS)
        directory = Path(directory_name)
        for filename in sorted(filenames):
            files.append(directory / filename)
    return files


def _should_ignore_file(path: Path) -> bool:
    return path.suffix.lower() in IGNORED_SUFFIXES


def _looks_like_text_file(path: Path) -> bool:
    if path.name in IMPORTANT_FILE_NAMES or path.suffix.lower() in TEXT_SUFFIXES:
        return not _contains_binary_bytes(path)
    return False


def _contains_binary_bytes(path: Path) -> bool:
    try:
        chunk = path.read_bytes()[:2048]
    except OSError:
        return True
    return b"\0" in chunk


def _priority_for(relative_path: str) -> int:
    path = Path(relative_path)
    score = 100

    if path.name in IMPORTANT_FILE_NAMES:
        score -= 50
    if any(part in IMPORTANT_PATH_PARTS for part in path.parts):
        score -= 25
    if path.suffix.lower() in {".md", ".json", ".toml", ".yml", ".yaml"}:
        score -= 10

    return score
