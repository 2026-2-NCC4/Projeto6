"""Casos independentes para interpretação de recortes e encerramento."""
import pandas as pd
from src.cti.leitura import resumo, encerramento


def medias():
    return pd.DataFrame({"DRE - Receita":[100e6,120e6],
                         "DRE - Resultado Líquido":[10e6,-5e6],
                         "FLU - Geração de Caixa":[0,2e6]}, index=[11,12])


def test_leitura_nao_confunde_variacao_com_valor():
    textos=" ".join(resumo(medias(),12))
    assert "Resultado líquido: valor médio negativo" in textos
    assert "+20,00 milhões" in textos and "-15,00 milhões" in textos


def test_comparacao_exige_ano_anterior_no_recorte():
    textos=" ".join(resumo(medias().loc[[12]],12))
    assert "Variação" not in textos


def test_ausencia_nao_vira_zero():
    m=medias(); m.loc[12,"FLU - Geração de Caixa"]=float("nan")
    assert "Geração de caixa: valor indisponível." in resumo(m,12)
    assert pd.isna(encerramento(m).loc[1,"Geração de caixa"])


def test_encerramento_mantem_contas_separadas():
    t=encerramento(medias())
    assert t.Ano.tolist()==[11,12]
    assert t["Receita"].tolist()==[100e6,120e6]
    assert t["Geração de caixa"].tolist()==[0,2e6]
