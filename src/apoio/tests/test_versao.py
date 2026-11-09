"""Um deploy só deve anunciar o commit consultado no próprio checkout."""
from pathlib import Path
import subprocess
from src.cti.versao import commit_em_execucao


def test_commit_corresponde_ao_checkout():
    raiz = Path(__file__).resolve().parents[3]
    esperado = subprocess.run(["git", "rev-parse", "HEAD"], cwd=raiz,
                              capture_output=True, text=True, check=True).stdout.strip()
    assert commit_em_execucao(raiz) == esperado


def test_exportacao_sem_git_nao_inventa_versao(tmp_path):
    assert commit_em_execucao(tmp_path) is None
