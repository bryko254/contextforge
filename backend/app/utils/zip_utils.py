from pathlib import Path
from zipfile import ZipFile


def safe_extract_zip(zip_path: Path, destination: Path) -> None:
    destination = destination.resolve()
    with ZipFile(zip_path) as archive:
        for member in archive.infolist():
            target = (destination / member.filename).resolve()
            if destination not in target.parents and target != destination:
                raise ValueError("ZIP archive contains unsafe paths")
        archive.extractall(destination)
