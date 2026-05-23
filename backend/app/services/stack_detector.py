from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Protocol

from pydantic import BaseModel


class StackSummary(BaseModel):
    languages: list[str]
    frameworks: list[str]
    database: list[str]
    infrastructure: list[str]
    package_managers: list[str]
    confidence_notes: list[str]


class FileContext(Protocol):
    path: str
    content: str


FileInput = FileContext | Mapping[str, str]


def detect_stack(selected_files: Sequence[FileInput]) -> StackSummary:
    languages: list[str] = []
    frameworks: list[str] = []
    database: list[str] = []
    infrastructure: list[str] = []
    package_managers: list[str] = []
    notes: list[str] = []

    files = [_normalize_file(file) for file in selected_files]
    paths = [path for path, _content in files]
    lower_paths = [path.lower() for path in paths]
    combined_content = "\n".join(content.lower() for _path, content in files)

    def add(bucket: list[str], value: str) -> None:
        if value not in bucket:
            bucket.append(value)

    def note(value: str) -> None:
        if value not in notes:
            notes.append(value)

    if any(path.endswith(".py") for path in lower_paths) or _has_path(lower_paths, "requirements.txt", "pyproject.toml"):
        add(languages, "Python")
        note("Detected Python from Python files or dependency configuration.")

    if _has_path(lower_paths, "manage.py") or (
        _has_path(lower_paths, "settings.py") and "django" in combined_content
    ):
        add(languages, "Python")
        add(frameworks, "Django")
        note("Detected Django from manage.py and settings.py.")
    elif "django" in combined_content:
        add(languages, "Python")
        add(frameworks, "Django")
        note("Detected Django from dependency or import references.")

    if "from fastapi" in combined_content or "import fastapi" in combined_content or "fastapi" in combined_content:
        add(languages, "Python")
        add(frameworks, "FastAPI")
        note("Detected FastAPI from dependency or import references.")

    if "from flask" in combined_content or "import flask" in combined_content or "flask" in combined_content:
        add(languages, "Python")
        add(frameworks, "Flask")
        note("Detected Flask from dependency or import references.")

    if _has_path(lower_paths, "package.json"):
        add(languages, "Node.js")
        add(package_managers, "npm")
        note("Detected Node.js from package.json.")

    if _has_path(lower_paths, "package-lock.json"):
        add(package_managers, "npm")
    if _has_path(lower_paths, "yarn.lock"):
        add(package_managers, "yarn")
    if _has_path(lower_paths, "pnpm-lock.yaml"):
        add(package_managers, "pnpm")

    if _has_path(lower_paths, "requirements.txt"):
        add(package_managers, "pip")
    if _has_path(lower_paths, "pyproject.toml"):
        add(package_managers, "pip")
        note("Detected Python packaging from pyproject.toml.")
    if _has_path(lower_paths, "composer.json"):
        add(languages, "PHP")
        add(package_managers, "composer")
        note("Detected PHP dependencies from composer.json.")

    if any(path.endswith((".ts", ".tsx")) for path in lower_paths) or "typescript" in combined_content:
        add(languages, "TypeScript")
        note("Detected TypeScript from .ts/.tsx files or TypeScript dependency.")

    if any(path.endswith(".php") for path in lower_paths):
        add(languages, "PHP")
        note("Detected PHP from .php files.")

    if "react" in combined_content or any(path.endswith((".jsx", ".tsx")) for path in lower_paths):
        add(frameworks, "React")
        note("Detected React from dependency, imports, or JSX/TSX files.")

    if _has_path(lower_paths, "vite.config.js", "vite.config.ts") or '"vite"' in combined_content:
        add(frameworks, "Vite")
        note("Detected Vite from vite config or dependency.")

    if _has_path(lower_paths, "next.config.js", "next.config.ts", "next.config.mjs") or '"next"' in combined_content:
        add(frameworks, "Next.js")
        note("Detected Next.js from config or dependency.")

    if any(path.endswith(".vue") for path in lower_paths) or '"vue"' in combined_content:
        add(frameworks, "Vue")
        note("Detected Vue from .vue files or dependency.")

    if "laravel/framework" in combined_content or _has_path(lower_paths, "artisan") or any(
        path.startswith("routes/") and path.endswith(".php") for path in lower_paths
    ):
        add(languages, "PHP")
        add(frameworks, "Laravel")
        note("Detected Laravel from composer.json, artisan, or PHP routes.")

    if _has_path(lower_paths, "dockerfile", "docker-compose.yml", "docker-compose.yaml"):
        add(infrastructure, "Docker")
        note("Detected Docker from Dockerfile or Docker Compose configuration.")

    if "postgres" in combined_content or "psycopg" in combined_content or '"pg"' in combined_content:
        add(database, "PostgreSQL")
        note("Detected PostgreSQL from dependency or configuration references.")

    if "mysql" in combined_content or "pymysql" in combined_content or "mysqlclient" in combined_content:
        add(database, "MySQL")
        note("Detected MySQL from dependency or configuration references.")

    if "sqlite" in combined_content or "sqlite3" in combined_content:
        add(database, "SQLite")
        note("Detected SQLite from configuration references.")

    if _has_path(lower_paths, "tailwind.config.js", "tailwind.config.ts", "tailwind.config.cjs") or (
        "tailwindcss" in combined_content or "@tailwind" in combined_content
    ):
        add(frameworks, "Tailwind")
        note("Detected Tailwind from config, dependency, or CSS directives.")

    return StackSummary(
        languages=languages,
        frameworks=frameworks,
        database=database,
        infrastructure=infrastructure,
        package_managers=package_managers,
        confidence_notes=notes,
    )


def _normalize_file(file: FileInput) -> tuple[str, str]:
    if isinstance(file, Mapping):
        return file.get("path", ""), file.get("content", "")
    return file.path, file.content


def _has_path(paths: Sequence[str], *names: str) -> bool:
    wanted = {name.lower() for name in names}
    return any(path in wanted or path.endswith(f"/{path_name}") for path in paths for path_name in wanted)
