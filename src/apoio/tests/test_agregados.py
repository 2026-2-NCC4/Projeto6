"""Arquivo de agregados publicáveis: fidelidade à base, nenhum dado individual e uso no painel."""
from pathlib import Path
import json
import pandas as pd
import pytest
from src import prepara
from src.cti import agregados as ag
from src.cti.dados import sintetica, HASH_REFERENCIA
from src.cti.recortes import filtrar, medias_anuais
from src.cti.distribuicao import CONTAS as CONTAS_DIST, percentis_anuais, proporcao_abaixo

PROIBIDAS = {"cenario", "grupo_repeticao", "cenario_repetido", "copia_excedente", "P0", "P100", "min", "max"}


@pytest.fixture(scope="module")
def base():
    """Base fictícia com uma trajetória copiada, para a população sem cópias diferir de todos."""
    b = sintetica(40)
    b = pd.concat([b, b.loc[b.cenario.eq(1)].assign(cenario=999)], ignore_index=True)
    b = b.drop(columns=["grupo_repeticao", "cenario_repetido", "copia_excedente"])
    return b.merge(prepara.marcar_repeticoes(b, list(prepara.DEFINICOES)), on="cenario")


@pytest.fixture(scope="module")
def arquivo(base, tmp_path_factory):
    destino = tmp_path_factory.mktemp("agregados") / "agregados.json"
    return ag.salvar(ag.gerar(base, {"descricao": "base fictícia de teste"}), destino)


def conferir_com_base(agregados, base):
    """Médias e percentis do arquivo iguais aos calculados da base pelas regras do painel."""
    for nome, unicas in ag.POPULACOES.items():
        recorte = filtrar(base, (1, 12), unicas)
        assert agregados["populacoes"][nome]["cenarios"] == recorte.cenario.nunique()
        pd.testing.assert_frame_equal(ag.medias(agregados, nome), medias_anuais(recorte)[ag.CONTAS_MEDIAS],
                                      check_exact=True, check_dtype=False, check_index_type=False)
        for conta in CONTAS_DIST:
            esperado = percentis_anuais(recorte, conta, ag.GRADE)
            pd.testing.assert_frame_equal(ag.percentis(agregados, conta, nome)[esperado.columns], esperado,
                                          check_exact=True, check_dtype=False, check_index_type=False)


def conferir_sem_individuais(objeto):
    """Nenhum campo de cenário, mínimo ou máximo; toda lista numérica é uma série de 12 anos."""
    if isinstance(objeto, dict):
        assert not PROIBIDAS & set(objeto), PROIBIDAS & set(objeto)
        for valor in objeto.values():
            conferir_sem_individuais(valor)
    elif isinstance(objeto, list):
        if any(isinstance(x, (int, float)) and not isinstance(x, bool) for x in objeto):
            assert len(objeto) == len(ag.ANOS)
        for valor in objeto:
            conferir_sem_individuais(valor)


def test_medias_e_percentis_batem_com_a_base(base, arquivo):
    agregados = ag.ler(arquivo)
    conferir_com_base(agregados, base)
    populacoes = agregados["populacoes"]
    assert (populacoes["todos"]["cenarios"], populacoes["sem_copias"]["cenarios"]) == (41, 40)
    assert pd.isna(ag.medias(agregados, "todos").loc[12, "BAL - Estoques Diversos"])  # ausência segue ausência
    assert list(ag.medias(agregados, "todos", (3, 5)).index) == [3, 4, 5]
    assert list(ag.percentis(agregados, "DRE - Receita", "sem_copias", (3, 5)).index) == [3, 4, 5]


def test_arquivo_sem_dados_individuais(arquivo):
    conferir_sem_individuais(json.loads(Path(arquivo).read_text(encoding="utf-8")))


def test_proporcao_interpolada_perto_da_exata(base, arquivo):
    agregados = ag.ler(arquivo)
    recorte = filtrar(base, (1, 12), False)
    n = recorte.cenario.nunique()
    conta = "DRE - Resultado Líquido"
    valores = recorte.loc[recorte.ano_n.eq(5), conta].sort_values().to_numpy()
    for i in (3, 10, 20, 30, 36):
        limite = (valores[i] + valores[i + 1]) / 2
        exata = proporcao_abaixo(recorte, conta, limite).loc[5]
        aproximada = ag.proporcao_abaixo(agregados, conta, "todos", limite).loc[5]
        assert aproximada.faixa == "aproximada"
        assert abs(aproximada.proporcao - exata) <= 1 / (n - 1) + 0.01 + 1e-12
    assert ag.proporcao_abaixo(agregados, conta, "todos", valores[0] - 1).loc[5].faixa == "ate_1"
    assert ag.proporcao_abaixo(agregados, conta, "todos", valores[-1] + 1).loc[5].faixa == "acima_99"
    with pytest.raises(ValueError):
        ag.proporcao_abaixo(agregados, conta, "todos", float("nan"))


def test_arquivo_invalido_e_recusado(arquivo, tmp_path):
    original = json.loads(Path(arquivo).read_text(encoding="utf-8"))
    casos = []
    curto = json.loads(json.dumps(original))
    curto["populacoes"]["todos"]["medias"]["DRE - Receita"].pop()
    casos.append(curto)
    fora_de_ordem = json.loads(json.dumps(original))
    fora_de_ordem["populacoes"]["sem_copias"]["distribuicao"]["DRE - Receita"]["P50"][0] = -1e18
    casos.append(fora_de_ordem)
    casos.append({**original, "schema": "outra-versao"})
    for i, caso in enumerate(casos):
        ruim = tmp_path / f"ruim_{i}.json"
        ruim.write_text(json.dumps(caso), encoding="utf-8")
        with pytest.raises(ValueError):
            ag.ler(ruim)


def test_regressao_publicada_vem_das_evidencias():
    publicada = ag.regressao_publicada()
    assert publicada["todos"]["populacao"] == "todos os cenários"
    assert publicada["sem_copias"]["populacao"] == "trajetórias únicas"
    assert publicada["todos"]["teste"]["RMSE_milhoes"] == pytest.approx(33.6225, abs=1e-4)
    assert publicada["todos"]["baseline_teste"]["RMSE_milhoes"] == pytest.approx(83.5931, abs=1e-4)


def test_interface_agregada(monkeypatch, arquivo):
    from streamlit.testing.v1 import AppTest
    monkeypatch.delenv("CTI_BASE_LOCAL", raising=False)
    monkeypatch.setenv("CTI_AGREGADOS", str(arquivo))
    app = AppTest.from_file(str(Path("app/app.py").resolve()), default_timeout=90).run()
    assert not app.exception
    # Arquivo de teste não declara a base da E1: o painel não pode chamá-lo de CTI.
    assert "AGREGADOS SEM CONFERÊNCIA" in " ".join(w.value for w in app.warning)
    assert len(app.metric) >= 8
    assert not [b for b in app.button if b.key == "rodar_modelo"]  # sem linhas, o modelo não é recalculado
    assert any("evidencias_e2.json" in c.value for c in app.caption)
    app.selectbox(key="conta_dist").set_value("Resultado líquido").run()
    app.number_input(key="limite_dist").set_value(1e9).run()
    assert not app.exception
    assert "99% ou mais" in [m.value for m in app.metric]
    app.checkbox(key="unicas").set_value(True).run()
    app.slider(key="anos").set_value((12, 12)).run()
    assert not app.exception
    assert "Ano 12" in " ".join(w.value for w in app.warning)


def test_arquivo_publicado_corresponde_a_base_local():
    if not ag.ARQUIVO.exists():
        pytest.skip("Arquivo de agregados ainda não gerado.")
    agregados = ag.ler(ag.ARQUIVO)
    conferir_sem_individuais(json.loads(ag.ARQUIVO.read_text(encoding="utf-8")))
    assert agregados["origem"]["entrada_sha256"] == HASH_REFERENCIA
    assert agregados["origem"]["corresponde_referencia_E1"] is True
    if not ag.BASE_PADRAO.exists():
        pytest.skip("Base CTI privada não disponível neste ambiente.")
    conferir_com_base(agregados, pd.read_parquet(ag.BASE_PADRAO))
