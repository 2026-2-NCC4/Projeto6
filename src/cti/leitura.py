"""Leitura gerencial de médias anuais, sem reconstruir cenários individuais."""
import math
import pandas as pd

CONTAS = {"Receita": "DRE - Receita", "Resultado líquido": "DRE - Resultado Líquido",
          "Geração de caixa": "FLU - Geração de Caixa"}


def resumo(medias, ano):
    """Compara apenas anos consecutivos disponíveis no mesmo recorte/população."""
    linha = medias.loc[ano]
    textos = []
    for nome, conta in CONTAS.items():
        valor = linha[conta]
        if pd.isna(valor) or not math.isfinite(float(valor)):
            textos.append(f"{nome}: valor indisponível.")
            continue
        estado = "positivo" if valor > 0 else "negativo" if valor < 0 else "zero"
        textos.append(f"{nome}: valor médio {estado} no Ano {ano}.")
        if ano - 1 in medias.index:
            antes = medias.loc[ano - 1, conta]
            if pd.notna(antes) and math.isfinite(float(antes)):
                delta = float(valor - antes) / 1e6
                textos.append(f"Variação de {nome.lower()} em relação ao Ano {ano-1}: "
                              + f"{delta:+,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                              + " milhões de reais.")
    return textos


def encerramento(medias):
    """Contas observadas, em médias, para os anos 11 e 12; não é uma ponte contábil."""
    linhas = []
    for ano in (11, 12):
        if ano in medias.index:
            linhas.append({"Ano": ano, **{nome: medias.loc[ano, conta] for nome, conta in CONTAS.items()}})
    return pd.DataFrame(linhas)
