"""Formatação de números no padrão brasileiro, usada pelo painel e pelos testes."""
import math
from datetime import datetime, timedelta, timezone

INDISPONIVEL = "Indisponível"
BRASILIA = timezone(timedelta(hours=-3))  # sem horário de verão desde 2019


def _valido(v):
    try:
        return v is not None and math.isfinite(float(v))
    except (TypeError, ValueError):
        return False


def numero(v, casas=2):
    """1234567.891 -> '1.234.567,89'. Valor ausente ou não finito -> 'Indisponível'."""
    if not _valido(v):
        return INDISPONIVEL
    texto = f"{float(v):,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def reais_mi(v, casas=2):
    """Valor em reais exibido em milhões: 9722980000 -> 'R$ 9.722,98 mi'."""
    return INDISPONIVEL if not _valido(v) else f"R$ {numero(float(v) / 1e6, casas)} mi"


def percentual(v, casas=2):
    """Fração exibida em percentual: 0.4362 -> '43,62%'."""
    return INDISPONIVEL if not _valido(v) else f"{numero(float(v) * 100, casas)}%"


def valor_kpi(valor, unidade, estado=""):
    """Formata um KPI pela unidade; sem valor, mostra o estado (pendente ou indisponível)."""
    if not _valido(valor):
        return estado[:1].upper() + estado[1:] if estado else INDISPONIVEL  # preserva siglas como PC
    if unidade == "R$":
        return reais_mi(valor)
    if unidade == "%":
        return percentual(valor)
    if unidade == "R$ por cliente":
        return f"R$ {numero(valor, 0)}"
    return numero(valor)  # índice e vezes


def parcela(p, faixa="exata"):
    """Parcela de cenários: 0.372 -> '37,2%'. No modo agregado, fora de P1 a P99 vira um limite."""
    if faixa == "ate_1":
        return "1% ou menos"
    if faixa == "acima_99":
        return "99% ou mais"
    return INDISPONIVEL if not _valido(p) else f"{numero(float(p) * 100, 1)}%"


def data_hora(iso):
    """'2026-11-06T15:30:00+00:00' -> '06/11/2026 12:30' (horário de Brasília)."""
    try:
        d = datetime.fromisoformat(iso)
    except (TypeError, ValueError):
        return INDISPONIVEL
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.astimezone(BRASILIA).strftime("%d/%m/%Y %H:%M")
