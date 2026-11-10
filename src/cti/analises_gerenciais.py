"""Comparações e hipóteses gerenciais sem alterar as contas da fonte."""
import math
import json
from pathlib import Path
import pandas as pd

FLUXOS = (
    ("Recebimentos", "FLU - Receita"),
    ("Tributos", "FLU - Tributos"),
    ("Custos", "FLU - Custos"),
    ("Investimentos", "FLU - Investimentos"),
    ("Outras entradas", "FLU - Entradas"),
    ("Despesas financeiras", "FLU - Despesas Financeiras"),
    ("IR e contribuição social", "FLU - Imposto de Renda e Contribuição Social"),
    ("Distribuição aos acionistas", "FLU - Distribuição para Acionista"),
)
CONTAS_PONTE = ("FLU - Saldo Inicial", *(nome for _, nome in FLUXOS),
                "FLU - Geração de Caixa", "FLU - Saldo Final")
# As duas outras contas necessárias já constam da distribuição publicada;
# a distribuição aos acionistas é restaurada ao sinal original negativo.
CONTAS_ADICIONAIS = CONTAS_PONTE[:8]
ARQUIVO_PONTE = Path("app/dados/ponte_cti.json")


def ponte_caixa(contas, tolerancia=0.01):
    """Reconcilia médias da mesma população; nunca soma percentis ou cenários."""
    valores = {}
    for nome in CONTAS_PONTE:
        valor = contas.get(nome)
        if valor is None or pd.isna(valor) or not math.isfinite(float(valor)):
            raise ValueError("Não há contas completas para conciliar a ponte de caixa.")
        valores[nome] = float(valor)
    inicial = valores["FLU - Saldo Inicial"]
    geracao = valores["FLU - Geração de Caixa"]
    final = valores["FLU - Saldo Final"]
    soma = sum(valores[chave] for _, chave in FLUXOS)
    if abs(soma-geracao) > tolerancia or abs(inicial+geracao-final) > tolerancia:
        raise ValueError("As médias não reconciliam a geração e o saldo final de caixa.")
    acumulado = inicial
    linhas = [{"Etapa": "Saldo inicial", "Início": 0.0, "Fim": inicial, "Valor": inicial, "Tipo": "Saldo"}]
    for rotulo, chave in FLUXOS:
        valor = valores[chave]
        linhas.append({"Etapa": rotulo, "Início": acumulado, "Fim": acumulado+valor,
                       "Valor": valor, "Tipo": "Entrada" if valor >= 0 else "Saída"})
        acumulado += valor
    linhas.append({"Etapa": "Saldo final", "Início": 0.0, "Fim": final, "Valor": final, "Tipo": "Saldo"})
    return pd.DataFrame(linhas)


def eva_hipotetico(ebit_milhoes, aliquota, capital_milhoes, wacc):
    """EVA ilustrativo em milhões, usando apenas premissas fornecidas pelo usuário."""
    valores = [ebit_milhoes, aliquota, capital_milhoes, wacc]
    if any(v is None for v in valores) or not all(math.isfinite(float(v)) for v in valores):
        raise ValueError("Informe EBIT e capital investido finitos para calcular.")
    ebit, aliquota, capital, wacc = map(float, valores)
    if capital < 0 or not 0 <= aliquota <= 1 or not 0 <= wacc <= 1:
        raise ValueError("Capital deve ser não negativo e as taxas devem estar entre 0% e 100%.")
    nopat = ebit * (1-aliquota)
    custo = capital * wacc
    return {"nopat": nopat, "custo_capital": custo, "eva": nopat-custo}


def medias_adicionais(base, agregados):
    """Gera somente as oito médias de caixa autorizadas para as duas populações."""
    from .dados import validar
    from .recortes import filtrar
    validar(base)
    saida = {"schema": "ponte-v1", "sha256_base": agregados["origem"]["sha256_base"],
             "populacoes": {}}
    for nome, unicas in (("todos", False), ("sem_copias", True)):
        recorte = filtrar(base, (1, 12), unicas)
        medias = recorte.groupby("ano_n")[list(CONTAS_ADICIONAIS)].agg(
            lambda serie: serie.mean() if serie.notna().all() else float("nan")).reindex(range(1, 13))
        saida["populacoes"][nome] = {conta: [None if pd.isna(v) else float(v) for v in medias[conta]]
                                      for conta in CONTAS_ADICIONAIS}
    validar_medias_ponte(saida, agregados)
    return saida


def contas_ponte_publica(ponte, agregados, populacao, ano):
    """Combina médias adicionais com três médias previamente publicadas."""
    if populacao not in ("todos", "sem_copias") or ano not in range(1, 13):
        raise ValueError("População ou ano inválido para a ponte.")
    i = ano-1
    dados = {conta: ponte["populacoes"][populacao][conta][i] for conta in CONTAS_ADICIONAIS}
    pop = agregados["populacoes"][populacao]
    dist = pop["distribuicao"]
    for conta in ("FLU - Saldo Final", "FLU - Distribuição para Acionista"):
        if dist[conta]["n"][i] != pop["cenarios"]:
            raise ValueError("Cobertura incompleta de uma conta da ponte.")
    dados["FLU - Saldo Final"] = dist["FLU - Saldo Final"]["media"][i]
    pagos = dist["FLU - Distribuição para Acionista"]["media"][i]
    dados["FLU - Distribuição para Acionista"] = -pagos if pagos is not None else None
    dados["FLU - Geração de Caixa"] = pop["medias"]["FLU - Geração de Caixa"][i]
    return dados


def validar_medias_ponte(ponte, agregados):
    """Rejeita campos extras, origem diferente, dados incompletos e reconciliações inválidas."""
    if not isinstance(ponte, dict) or set(ponte) != {"schema", "sha256_base", "populacoes"}:
        raise ValueError("Contrato das médias de caixa inválido.")
    if ponte["schema"] != "ponte-v1" or ponte["sha256_base"] != agregados["origem"].get("sha256_base"):
        raise ValueError("Origem das médias de caixa não corresponde aos agregados do painel.")
    pops = ponte["populacoes"]
    if not isinstance(pops, dict) or set(pops) != {"todos", "sem_copias"}:
        raise ValueError("Populações incompletas na ponte.")
    for pop, series in pops.items():
        if not isinstance(series, dict) or set(series) != set(CONTAS_ADICIONAIS):
            raise ValueError("Contas ausentes ou não autorizadas na ponte.")
        if any(not isinstance(v, list) or len(v) != 12 or
               any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) for x in v)
               for v in series.values()):
            raise ValueError("Série de médias de caixa incompleta ou inválida.")
        for ano in range(1, 13):
            ponte_caixa(contas_ponte_publica(ponte, agregados, pop, ano))
    return ponte


def ler_medias_ponte(caminho, agregados):
    with Path(caminho).open(encoding="utf-8") as arquivo:
        return validar_medias_ponte(json.load(arquivo), agregados)
