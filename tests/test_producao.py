"""Casos negativos do contrato de produção e referência da meta."""
import copy
from pathlib import Path
import pytest
from src.cti import agregados as ag
from src.cti.sensibilidade import meta_percentual, simular

@pytest.mark.parametrize("caso",["origem","data","n_negativo","n_fracionario","n_excesso","percentil_nulo","cenario","conta_extra"])
def test_contrato_rejeita_corrupcao(caso):
    q=copy.deepcopy(ag.ler())
    d=q["populacoes"]["todos"]["distribuicao"]["DRE - Receita"]
    if caso=="origem": del q["origem"]
    elif caso=="data": q["gerado_em_utc"]="ontem"
    elif caso=="n_negativo": d["n"][0]=-1
    elif caso=="n_fracionario": d["n"][0]=1.5
    elif caso=="n_excesso": d["n"][0]=999999
    elif caso=="percentil_nulo": d["P50"][0]=None
    elif caso=="cenario": q["cenario"]=[1]*12
    elif caso=="conta_extra": q["populacoes"]["todos"]["medias"]["cenario"]=[1]*12
    with pytest.raises(ValueError): ag.validar_agregados(q)

def test_meta_base_e_simulacao():
    assert meta_percentual(100,-60)==pytest.approx(40)
    assert meta_percentual(100,-60,.3)==pytest.approx(30)
    assert simular(100,-60,.1,.2,10,meta_percentual(100,-60,.3))["desvio_meta"]==pytest.approx(-12)

def test_producao_nao_cai_em_ficticio(monkeypatch,tmp_path):
    from streamlit.testing.v1 import AppTest
    monkeypatch.delenv("CTI_DEMO",raising=False)
    monkeypatch.delenv("CTI_BASE_LOCAL",raising=False)
    monkeypatch.setenv("CTI_AGREGADOS",str(tmp_path/"ausente.json"))
    app=AppTest.from_file(str(Path("app/app.py").resolve()),default_timeout=90).run()
    assert not app.exception
    assert app.error and not app.metric
