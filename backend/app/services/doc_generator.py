from app.services.scanner import ScanResult


def generate_placeholder_docs(scan: ScanResult) -> dict[str, str]:
    stack = _format_stack(scan)
    files = "\n".join(f"- `{path}`" for path in scan.files) or "- No files scanned yet"

    return {
        "README.md": f"# {scan.project_name}\n\nDetected stack: {stack}\n",
        "AGENT.md": f"# Agent Notes\n\nProject: {scan.project_name}\n\nFiles:\n{files}\n",
        "SETUP.md": f"# Setup\n\nInstall and run instructions will be generated here.\n",
        "ARCHITECTURE.md": f"# Architecture\n\nArchitecture notes will be generated here.\n",
    }


def _format_stack(scan: ScanResult) -> str:
    stack = scan.tech_stack
    labels = [
        *stack.languages,
        *stack.frameworks,
        *stack.database,
        *stack.infrastructure,
        *stack.package_managers,
    ]
    return ", ".join(dict.fromkeys(labels)) or "Unknown"
