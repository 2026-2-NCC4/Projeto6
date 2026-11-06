"""Simulação parcial: volume e demais contas permanecem constantes."""
import math

def meta_percentual(receita, custo, percentual=None):
    """Meta acadêmica sobre a receita original; padrão igual à margem de referência."""
    if not all(math.isfinite(float(x)) for x in [receita, custo]) or receita <= 0:
        raise ValueError("A referência da meta exige receita positiva e valores finitos.")
    taxa = (receita + custo) / receita if percentual is None else float(percentual)
    if not math.isfinite(taxa) or not -2 <= taxa <= 1:
        raise ValueError("Meta percentual fora do intervalo acadêmico de -200% a 100%.")
    return receita * taxa

def simular(receita, custo, desconto=0., variacao_custo=0., quantidade=10000., meta=0.):
    valores = [receita,custo,desconto,variacao_custo,quantidade,meta]
    if not all(math.isfinite(float(x)) for x in valores):
        raise ValueError("Parâmetros devem ser números finitos.")
    if receita < 0 or custo > 0:
        raise ValueError("Simulação requer receita não negativa e custo assinado não positivo.")
    if not 0 <= desconto <= 1 or not -1 <= variacao_custo <= 2:
        raise ValueError("Desconto deve estar entre 0 e 100%; custo entre -100% e +200%.")
    if quantidade <= 0:
        raise ValueError("Quantidade hipotética deve ser positiva.")
    r = receita*(1-desconto)
    c = custo*(1+variacao_custo)
    margem = r+c
    original = receita+custo
    return {"receita":r,"custo":c,"margem":margem,
            "margem_percentual":margem/r if r else None,
            "margem_original":original,"variacao_margem":margem-original,
            "variacao_percentual":(margem-original)/abs(original) if original else None,
            "ticket_simulado":r/quantidade,"meta_academica":meta,
            "desvio_meta":margem-meta}
