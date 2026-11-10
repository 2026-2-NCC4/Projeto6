"""Regras independentes para as novas hipóteses e a reconciliação de caixa."""
import copy
import pytest
from src.cti import agregados as ag
from src.cti.analises_gerenciais import (CONTAS_ADICIONAIS, contas_ponte_publica,
    eva_hipotetico, ler_medias_ponte, ponte_caixa, validar_medias_ponte)


def test_ponte_reconcilia_movimentos_assinados():
    contas = {"FLU - Saldo Inicial": 100, "FLU - Receita": 80, "FLU - Tributos": -10,
              "FLU - Custos": -20, "FLU - Investimentos": -15, "FLU - Entradas": 5,
              "FLU - Despesas Financeiras": -4, "FLU - Imposto de Renda e Contribuição Social": -6,
              "FLU - Distribuição para Acionista": -10, "FLU - Geração de Caixa": 20,
              "FLU - Saldo Final": 120}
    resultado = ponte_caixa(contas)
    assert resultado.iloc[-1]["Fim"] == 120
    assert resultado.loc[resultado["Etapa"] == "Custos", "Valor"].iloc[0] == -20
    contas["FLU - Saldo Final"] = 121
    with pytest.raises(ValueError): ponte_caixa(contas)
    del contas["FLU - Receita"]
    with pytest.raises(ValueError): ponte_caixa(contas)


def test_medias_publicadas_reconciliam_e_sao_restritas():
    agregados = ag.ler()
    ponte = ler_medias_ponte("app/dados/ponte_cti.json", agregados)
    for pop in ("todos", "sem_copias"):
        assert set(ponte["populacoes"][pop]) == set(CONTAS_ADICIONAIS)
        for ano in range(1, 13):
            assert len(ponte_caixa(contas_ponte_publica(ponte, agregados, pop, ano))) == 10
    corrompida = copy.deepcopy(ponte)
    corrompida["populacoes"]["todos"]["FLU - Receita"][11] += 1000
    with pytest.raises(ValueError): validar_medias_ponte(corrompida, agregados)
    corrompida = copy.deepcopy(ponte)
    corrompida["populacoes"]["todos"]["cenario"] = [1]*12
    with pytest.raises(ValueError): validar_medias_ponte(corrompida, agregados)
    corrompida = copy.deepcopy(ponte)
    corrompida["sha256_base"] = "outro"
    with pytest.raises(ValueError): validar_medias_ponte(corrompida, agregados)


def test_eva_operacional_hipotetico_e_limites():
    valores = eva_hipotetico(100, .25, 200, .10)
    assert valores == {"nopat": 75, "custo_capital": 20, "eva": 55}
    assert eva_hipotetico(100, .25, 200, .20)["eva"] == 35
    for parametros in [(None, .25, 200, .1), (100, .25, -1, .1), (100, 2, 200, .1),
                       (100, .25, 200, float("nan"))]:
        with pytest.raises(ValueError): eva_hipotetico(*parametros)
