"""Uma única política de população e agregação para painel e documentos."""
import pandas as pd
from .dados import CONTAS

def filtrar(base, anos=(1, 12), unicas=False):
    inicio, fim = anos
    if not 1 <= inicio <= fim <= 12:
        raise ValueError("Intervalo de anos inválido.")
    mask = base.ano_n.between(inicio, fim)
    if unicas:
        mask &= ~base.copia_excedente
    return base.loc[mask].copy()

def medias_anuais(base):
    if base.empty:
        return pd.DataFrame(columns=CONTAS, index=pd.Index([], name="ano_n"))
    # Se faltar qualquer valor da conta no ano, não mudar silenciosamente o denominador.
    return base.groupby("ano_n")[CONTAS].agg(lambda x: x.mean() if x.notna().all() else float("nan"))
