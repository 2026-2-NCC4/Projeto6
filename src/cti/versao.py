"""Identificação verificável do checkout em execução, sem depender de SHA fixado no código."""
from pathlib import Path
import re
import subprocess


def commit_em_execucao(raiz: Path) -> str | None:
    """Consulta somente o repositório local; arquivo exportado sem Git retorna indisponível."""
    if not (raiz / ".git").exists():
        return None
    try:
        resultado = subprocess.run(
            ["git", "-C", str(raiz), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True, timeout=3,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    sha = resultado.stdout.strip()
    return sha if re.fullmatch(r"[0-9a-f]{40}", sha) else None
