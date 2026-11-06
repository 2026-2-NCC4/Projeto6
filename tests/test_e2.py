"""Testes de contrato, fórmulas e interação com dados fictícios independentes."""
from pathlib import Path
import copy
import numpy as np
import pandas as pd
import pytest
from src.cti.dados import sintetica, validar
from src.cti.recortes import filtrar, medias_anuais
from src.cti.indicadores import calcular
from src.cti.sensibilidade import simular
from src.cti.regressao import executar, separar, grupos
from src.cti.distribuicao import percentis_anuais, proporcao_abaixo
from src.cti.formatacao import numero, reais_mi, percentual, valor_kpi
from src import prepara

@pytest.fixture(scope="module")
def base(): return sintetica(30)

def test_cobertura_por_cenario(base):
    quebrada=base.drop(base.index[0])
    with pytest.raises(ValueError,match="12 anos"): validar(quebrada)

def test_duplicata(base):
    with pytest.raises(ValueError,match="duplicada"): validar(pd.concat([base,base.iloc[:1]]))

def test_ausencia_essencial(base):
    b=base.copy(); b.loc[0,"DRE - Receita"]=np.nan
    with pytest.raises(ValueError,match="essencial"): validar(b)

def test_filtro_e_agregacao(base):
    b=filtrar(base,(3,5))
    assert set(b.ano_n)=={3,4,5}
    assert len(b)==90
    medias=medias_anuais(b)
    assert medias.loc[3,"DRE - Receita"]==pytest.approx(b.loc[b.ano_n.eq(3),"DRE - Receita"].sum()/30)
    assert medias_anuais(base.iloc[:0]).empty

def test_ausencia_parcial_nao_encolhe_denominador(base):
    b=base.copy(); b.loc[0,"BAL - Estoques Diversos"]=np.nan
    assert pd.isna(medias_anuais(b).loc[1,"BAL - Estoques Diversos"])

def test_repeticao_e_divisao(base):
    b=pd.concat([base,base.loc[base.cenario.eq(1)].assign(cenario=999)],ignore_index=True)
    b=b.drop(columns=["grupo_repeticao","cenario_repetido","copia_excedente"])
    b=b.merge(prepara.marcar_repeticoes(b,list(prepara.DEFINICOES)),on="cenario")
    validar(b)
    assert len(filtrar(b,unicas=True))==len(base)
    g=grupos(b)
    assert set(g[b.cenario.eq(1)])==set(g[b.cenario.eq(999)])
    ids,gs=separar(b)
    sets=[set(gs.iloc[v]) for v in ids.values()]
    assert not (sets[0]&sets[1] or sets[0]&sets[2] or sets[1]&sets[2])

def test_financas_independentes():
    contas={"DRE - Receita":100.,"DRE - Custos":-60.,"DRE - EBITDA":30.,
            "DRE - Resultado Líquido":15.,"BAL - Ativo Circulante":80.,
            "BAL - Disponível":20.,"BAL - Estoques Diversos":10.,
            "BAL - Realizável a Longo Prazo":20.,"BAL - Total do Ativo":200.,
            "BAL - Passivo Circulante":-40.,"BAL - Exigível a Longo Prazo":-60.,
            "BAL - Patrimônio Líquido":-100.}
    k=calcular(contas)
    assert len(k)==18
    esperado=[100,60,40,.4,30,.3,.15,2,1.75,.5,1, .5,1,.4,5,4000,45000,11.25]
    assert [x.valor for x in k]==pytest.approx(esperado)
    contas["BAL - Passivo Circulante"]=40
    assert all(x.valor is None for x in calcular(contas)[7:14])
    contas["DRE - Receita"]=0
    assert calcular(contas)[3].valor is None

def test_encerramento_ausencia(base):
    ks=calcular(medias_anuais(base).loc[12])
    assert ks[8].valor is None and ks[10].valor is None and ks[14].valor is None

def test_sensibilidade():
    original=simular(100,-60)
    assert original["margem"]==40 and original["variacao_margem"]==0
    r=simular(100,-60,.1,.2,10,20)
    assert r["receita"]==90 and r["custo"]==-72 and r["margem"]==18
    assert r["ticket_simulado"]==9 and r["desvio_meta"]==-2
    assert simular(100,-60,1)["margem_percentual"] is None

@pytest.mark.parametrize("args",[(100,-60,0,0,0),(100,60,0,0,10),(100,-60,1.1,0,10),(100,-60,0,-1.1,10),(float("nan"),-60,0,0,10)])
def test_simulacao_invalida(args):
    with pytest.raises(ValueError): simular(*args)

def test_modelo(base):
    res=executar(base)
    assert res["intersecao_grupos"]==0
    assert sum(x["linhas"] for x in res["particoes"].values())==30*11
    assert res["teste"]["RMSE_milhoes"]>=0
    assert res["teste"]["RMSE_milhoes"]<res["baseline_teste"]["RMSE_milhoes"]
    assert len(res["medias_teste_ano"])==11

def test_formatacao_padrao_brasileiro():
    assert numero(1234567.891)=="1.234.567,89"
    assert numero(-1234.5)=="-1.234,50"
    assert numero(1200,0)=="1.200"
    assert numero(None)=="Indisponível" and numero(float("nan"))=="Indisponível"
    assert reais_mi(9_722_980_000)=="R$ 9.722,98 mi"
    assert percentual(.4362)=="43,62%"
    assert valor_kpi(4000,"R$ por cliente")=="R$ 4.000"
    assert valor_kpi(1.583,"índice")=="1,58"
    assert valor_kpi(None,"%","pendente: PC com sinal positivo")=="Pendente: PC com sinal positivo"

def test_distribuicao_valores_conhecidos():
    b=pd.DataFrame({"ano_n":[1,1,1,1,2,2,2,2],
                    "DRE - Receita":[1.,2.,3.,4.,10.,20.,30.,np.nan],
                    "FLU - Distribuição para Acionista":[-1.,-2.,-3.,-4.,-5.,-6.,-7.,-8.]})
    p=percentis_anuais(b,"DRE - Receita")
    assert p.loc[1,"P50"]==pytest.approx(2.5) and p.loc[1,"media"]==pytest.approx(2.5)
    assert p.loc[1,"P5"]==pytest.approx(1.15) and p.loc[1,"P95"]==pytest.approx(3.85)
    assert p.loc[2,"n"]==3 and p.loc[2,"media"]==pytest.approx(20)  # ausência não vira zero
    d=percentis_anuais(b,"FLU - Distribuição para Acionista")
    assert d.loc[1,"P50"]==pytest.approx(2.5)  # saída de caixa exibida como valor pago
    prop=proporcao_abaixo(b,"DRE - Receita",3)
    assert prop.loc[1]==pytest.approx(.5) and prop.loc[2]==pytest.approx(0)
    with pytest.raises(ValueError): percentis_anuais(b,"DRE - Custos")

def test_distribuicao_ordenada(base):
    p=percentis_anuais(base,"DRE - Resultado Líquido")
    assert len(p)==12 and (p.n==30).all()
    assert (p.P5<=p.P25).all() and (p.P25<=p.P50).all() and (p.P50<=p.P75).all() and (p.P75<=p.P95).all()

def test_interface(monkeypatch):
    from streamlit.testing.v1 import AppTest
    monkeypatch.delenv("CTI_BASE_LOCAL",raising=False)
    app=AppTest.from_file(str(Path("app/app.py").resolve()),default_timeout=90).run()
    assert not app.exception
    assert len(app.metric)>=8
    app.slider(key="desconto").set_value(10.).run()
    assert not app.exception
    app.selectbox(key="conta_dist").set_value("Resultado líquido").run()
    app.number_input(key="limite_dist").set_value(100.).run()
    assert not app.exception
    app.checkbox(key="unicas").set_value(True).run()
    assert not app.exception
    app.slider(key="anos").set_value((12,12)).run()
    assert not app.exception
    assert "Ano 12" in " ".join(w.value for w in app.warning)
    app.button(key="rodar_modelo").click().run()
    assert not app.exception

def test_comparacao_real_e_detecta_erro():
    from src.cti.executar_e2 import comparar_planilha
    arquivo=Path("src/data/processed/e2/base_analitica.parquet")
    if not arquivo.exists(): pytest.skip("Base CTI privada não disponível neste ambiente.")
    base=pd.read_parquet(arquivo)
    planilha=next(Path("documentos/Entrega 1/Contabilidade e Finanças").glob("*.xlsx"))
    r=comparar_planilha(base,planilha)
    assert r["kpis_total"]==216 and r["identidades"]==24
    corrompida=base.copy()
    corrompida.loc[corrompida.ano_n.eq(1),"DRE - Receita"]*=1.1
    with pytest.raises(AssertionError): comparar_planilha(corrompida,planilha)
