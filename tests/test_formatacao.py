"""Regressão da apresentação de valores próximos de zero, sem perder negativos visíveis."""
import pytest
from src.cti.formatacao import numero, reais_mi, percentual


@pytest.mark.parametrize("valor,casas,esperado",[
    (-0.0,2,"0,00"),(-0.004,2,"0,00"),(-0.006,2,"-0,01"),
    (0.006,2,"0,01"),(-0.4,0,"0"),(-0.6,0,"-1"),
    (-1234567.89,2,"-1.234.567,89"),(-0.00004,4,"0,0000"),
])
def test_zero_arredondado_e_negativos_visiveis(valor,casas,esperado):
    assert numero(valor,casas)==esperado


def test_unidades_e_ausencias_preservadas():
    assert reais_mi(-49)=="R$ 0,00 mi"
    assert reais_mi(-6000)=="R$ -0,01 mi"
    assert percentual(-0.000001)=="0,00%"
    assert percentual(-0.0001)=="-0,01%"
    for valor in [None,float("nan"),float("inf")]:
        assert numero(valor)==reais_mi(valor)==percentual(valor)=="Indisponível"
