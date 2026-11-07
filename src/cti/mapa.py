"""Mapa de navegação e simulação parcial; recebe apenas médias anuais autorizadas."""
from functools import lru_cache
from pathlib import Path
import math

CONTAS = {"receita": "DRE - Receita", "custos": "DRE - Custos",
          "resultado": "DRE - Resultado Líquido", "caixa": "FLU - Geração de Caixa"}


def preparar_mapa(medias, ano, populacao, cenarios, modo, desconto=0., custo=0.):
    """Allowlist de cinco métricas, sem contas extras, IDs ou linhas de cenário."""
    def valor(v):
        return float(v) if v is not None and math.isfinite(float(v)) else None
    series = {chave: [valor(v) for v in medias[coluna]] for chave, coluna in CONTAS.items()}
    series["margem"] = [None if r is None or c is None else r+c
                        for r,c in zip(series["receita"], series["custos"])]
    indice = list(medias.index).index(ano)
    valores = {k: v[indice] for k,v in series.items()}
    return {"ano": int(ano), "anos": [int(a) for a in medias.index],
            "populacao": populacao, "cenarios": int(cenarios), "modo": modo,
            "valores": valores, "series": series,
            "hipoteses": {"desconto": float(desconto), "custo": float(custo)}}


def validar_aplicacao(evento, ano, populacao):
    """Rejeita evento de outro recorte ou parâmetros fora do mesmo contrato Python."""
    if not isinstance(evento, dict) or set(evento) != {"ano", "populacao", "desconto", "custo"}:
        raise ValueError("Hipóteses do mapa inválidas.")
    if type(evento["ano"]) is not int or evento["ano"] != ano or evento["populacao"] != populacao:
        raise ValueError("O recorte mudou; prepare a simulação novamente.")
    for campo, minimo, maximo in [("desconto", 0, 100), ("custo", -100, 200)]:
        x = evento[campo]
        if isinstance(x, bool) or not isinstance(x, (float, int)) or not math.isfinite(x) or not minimo <= x <= maximo:
            raise ValueError("Hipótese fora do intervalo permitido.")
    return float(evento["desconto"]), float(evento["custo"])


@lru_cache(maxsize=1)
def _componente(html, css, js):
    from streamlit.components.v2 import component
    return component("finsight_mapa", html=html, css=css, js=js)


def mostrar_mapa(dados):
    import streamlit as st
    def aplicar():
        evento = st.session_state["mapa_financeiro"].get("aplicar")
        pop = "sem_copias" if st.session_state.get("unicas", False) else "todos"
        try:
            d,c = validar_aplicacao(evento, st.session_state.get("ano"), pop)
        except ValueError as exc:
            st.toast(str(exc))
            return
        st.session_state["desconto"] = d
        st.session_state["custo_delta"] = c
        st.toast("Hipóteses aplicadas à Sensibilidade e ao relatório.")
    pasta = Path(__file__).resolve().parents[2]/"app/componentes"
    assets = [(pasta/("mapa."+ext)).read_text(encoding="utf-8") for ext in ["html", "css", "js"]]
    _componente(*assets)(data=dados, key="mapa_financeiro", on_aplicar_change=aplicar,
                  width="stretch", height="content")
