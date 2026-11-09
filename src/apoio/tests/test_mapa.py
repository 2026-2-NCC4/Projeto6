"""Contrato público do mapa e validação dos comandos antes de alterar hipóteses."""
import json
import pandas as pd
import pytest
from src.cti.mapa import preparar_mapa, validar_aplicacao
from src.cti.sensibilidade import simular


def test_mapa_apenas_agregados_e_contas_explicitas():
    medias=pd.DataFrame({"DRE - Receita":[100.,120.],"DRE - Custos":[-60.,-70.],
                         "DRE - Resultado Líquido":[15.,20.],"FLU - Geração de Caixa":[-2.,4.],
                         "campo_privado":[999.,999.]}, index=[1,2])
    payload=preparar_mapa(medias,2,"todos",30,"ficticio")
    assert payload["valores"]=={"receita":120.,"custos":-70.,"resultado":20.,"caixa":4.,"margem":50.}
    assert "campo_privado" not in json.dumps(payload,allow_nan=False)
    assert set(payload["series"])=={"receita","custos","margem","resultado","caixa"}
    medias.loc[2,"FLU - Geração de Caixa"]=float("nan")
    assert preparar_mapa(medias,2,"todos",30,"ficticio")["valores"]["caixa"] is None


def test_aplicacao_preserva_o_contrato_da_sensibilidade():
    e={"ano":1,"populacao":"todos","desconto":10.,"custo":20.}
    d,c=validar_aplicacao(e,1,"todos")
    assert simular(100,-60,d/100,c/100)["margem"]==pytest.approx(18.)


@pytest.mark.parametrize("mudanca",[{"ano":2},{"ano":True},{"populacao":"sem_copias"},
                                   {"desconto":101},{"custo":-101},{"custo":201},
                                   {"desconto":float("nan")},{"custo":True},
                                   {"cenario":1},{"desconto":"10"}])
def test_comando_invalido_ou_recorte_antigo_nao_altera_hipoteses(mudanca):
    e={"ano":1,"populacao":"todos","desconto":10.,"custo":20.};e.update(mudanca)
    with pytest.raises(ValueError): validar_aplicacao(e,1,"todos")
