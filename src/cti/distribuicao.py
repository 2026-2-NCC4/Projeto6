"""Distribuição entre cenários: percentis por ano e proporção de cenários abaixo de um limite.

As saídas são agregados por ano; nenhum cenário individual é exposto. Como os cenários são futuros
alternativos simulados, a proporção é a parcela dos cenários da simulação, não uma probabilidade real.
"""
import pandas as pd

# conta da base -> (rótulo, sinal de apresentação). A distribuição aos acionistas é uma saída de caixa,
# registrada com sinal negativo; aqui ela aparece como valor pago (positivo).
CONTAS = {
    "DRE - Receita": ("Receita", 1),
    "DRE - EBITDA": ("EBITDA", 1),
    "DRE - Resultado Líquido": ("Resultado líquido", 1),
    "FLU - Geração de Caixa": ("Geração de caixa", 1),
    "FLU - Saldo Final": ("Saldo final de caixa", 1),
    "FLU - Distribuição para Acionista": ("Distribuição aos acionistas", -1),
}
QUANTIS = {"P5": 0.05, "P25": 0.25, "P50": 0.50, "P75": 0.75, "P95": 0.95}


def _valores(base, conta):
    if conta not in CONTAS:
        raise ValueError(f"Conta sem distribuição definida: {conta}")
    if conta not in base.columns:
        raise ValueError(f"Conta ausente na base: {conta}")
    return base[["ano_n"]].assign(valor=base[conta] * CONTAS[conta][1]).dropna()


def percentis_anuais(base, conta):
    """Por ano: P5, P25, P50, P75, P95, média e número de cenários com valor."""
    v = _valores(base, conta)
    if v.empty:
        return pd.DataFrame(columns=[*QUANTIS, "media", "n"], index=pd.Index([], name="ano_n"))
    por_ano = v.groupby("ano_n").valor
    tabela = por_ano.quantile(list(QUANTIS.values())).unstack()
    tabela.columns = list(QUANTIS)
    tabela["media"] = por_ano.mean()
    tabela["n"] = por_ano.size()
    return tabela


def proporcao_abaixo(base, conta, limite):
    """Por ano: fração dos cenários com valor estritamente abaixo do limite (mesma escala da conta)."""
    v = _valores(base, conta)
    if v.empty:
        return pd.Series(dtype=float, name="proporcao")
    return v.assign(abaixo=v.valor < float(limite)).groupby("ano_n").abaixo.mean().rename("proporcao")
