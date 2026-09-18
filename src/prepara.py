"""
Preparação dos dados (CRISP-DM) - PI CTI, Grupo 6.

Lê a base bruta da CTI, que é somente leitura, e gera a base analítica única
usada por todas as frentes do projeto (Ciência de Dados, Estatística e Finanças).

Uso, a partir da raiz do repositório:
    .venv\\Scripts\\python.exe src\\prepara.py

Saídas em src/data/processed/ (fora do Git, pois contêm valores da CTI):
    base_analitica.parquet       uma linha por cenário e ano, contas em colunas
    base_longa.parquet           uma linha por cenário, ano e conta
    auditoria_sem_conta.parquet  as linhas sem nome de conta, preservadas
    relatorio_qualidade.json     resultado das verificações e identificação da entrada

Saída versionada (não contém valores):
    documentos/Entrega 1/Projeto Interdisciplinar Ciência de Dados/dicionario_dados.md
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path

import pandas as pd

ARQUIVO_BRUTO = "Demonstrativo Fecap v3.csv"
TOLERANCIA = 1.0  # R$; os resíduos observados são de centavos em valores da ordem de bilhões


def caminhos(raiz=None):
    """Monta os caminhos a partir da raiz do repositório (a pasta acima de src/)."""
    raiz = Path(raiz) if raiz else Path(__file__).resolve().parents[1]
    return {
        "bruto": raiz / "src" / "data" / "raw" / ARQUIVO_BRUTO,
        "processed": raiz / "src" / "data" / "processed",
        "dicionario": raiz / "documentos" / "Entrega 1" / "Projeto Interdisciplinar Ciência de Dados"
                      / "dicionario_dados.md",
    }


def hash_arquivo(caminho):
    """SHA-256 do arquivo, para provar que a entrada não mudou entre execuções."""
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


# ---------------------------------------------------------------- coletar
def coletar(caminho):
    """Lê o CSV conforme o contrato de leitura, sem alterar o arquivo."""
    df = pd.read_csv(
        caminho,
        sep=";",
        header=None,
        names=["ano", "cenario", "conta", "valor"],
        encoding="latin-1",
        decimal=",",
        thousands=".",
    )
    df.insert(0, "linha_origem", range(1, len(df) + 1))  # rastreia cada registro até o arquivo
    return df


# ---------------------------------------------------------------- selecionar
def selecionar(df):
    """Separa as contas financeiras das linhas sem nome de conta."""
    df = df.copy()
    df["ano_n"] = df["ano"].str.split().str[1].astype(int)

    sem_conta = df[df["conta"].isna()].copy()
    sem_conta["posicao"] = sem_conta.groupby(["cenario", "ano_n"]).cumcount() + 1

    nomeadas = df[df["conta"].notna()].copy()
    return nomeadas, sem_conta


# ---------------------------------------------------------------- limpar e uniformizar
def uniformizar(nomeadas):
    """Padroniza os nomes das contas e cria os campos de apoio, preservando o original."""
    nomeadas = nomeadas.rename(columns={"conta": "conta_original"})
    # "BAL  - Capital Social" e "BAL - Capital Social" passam a ter o mesmo nome
    nomeadas["conta"] = nomeadas["conta_original"].str.replace(r"\s+", " ", regex=True).str.strip()
    nomeadas["bloco"] = nomeadas["conta"].str.split(" - ").str[0]
    nomeadas["ano_calendario"] = 2026 + nomeadas["ano_n"]  # convenção da CTI: Ano 1 = 2027
    return nomeadas[["linha_origem", "cenario", "ano", "ano_n", "ano_calendario",
                     "bloco", "conta", "conta_original", "valor"]]


def validar_chave(nomeadas):
    """Falha se (cenário, ano, conta) se repetir: o pivot não pode somar duplicatas em silêncio."""
    repetidas = nomeadas.duplicated(subset=["cenario", "ano_n", "conta"], keep=False)
    if repetidas.any():
        exemplo = nomeadas.loc[repetidas, ["cenario", "ano", "conta"]].head(5)
        raise ValueError(f"{int(repetidas.sum())} linhas com chave repetida:\n{exemplo}")


# ---------------------------------------------------------------- formatar e integrar
def formatar(nomeadas):
    """Integra BAL, DRE e FLU numa linha por cenário e ano, com as contas em colunas."""
    ordem_contas = list(pd.unique(nomeadas["conta"]))  # mantém a ordem do arquivo original
    base = nomeadas.pivot(index=["cenario", "ano_n"], columns="conta", values="valor")
    base = base[ordem_contas].reset_index()
    base.columns.name = None
    base.insert(2, "ano_calendario", 2026 + base["ano_n"])
    return base, ordem_contas


# ---------------------------------------------------------------- derivar
def marcar_repeticoes(base, contas):
    """Identifica cenários com trajetória idêntica nos 12 anos e em todas as contas."""
    trajetoria = base.set_index(["cenario", "ano_n"])[contas].unstack("ano_n")

    # Comparação exata: o hash usa os valores completos, sem arredondar
    assinatura = pd.util.hash_pandas_object(trajetoria, index=False)
    assinatura.index = trajetoria.index

    grupos = assinatura[assinatura.duplicated(keep=False)]
    rotulo = {h: f"G{i:02d}" for i, h in enumerate(pd.unique(grupos), start=1)}

    # Confirma, valor a valor, que cada grupo é mesmo idêntico
    for h in rotulo:
        membros = assinatura[assinatura == h].index
        if not (trajetoria.loc[membros].nunique(dropna=False) <= 1).all():
            raise ValueError(f"Colisão de hash no grupo {rotulo[h]}: trajetórias diferentes")

    marcas = pd.DataFrame({
        "cenario": trajetoria.index,
        "grupo_repeticao": assinatura.map(rotulo).values,
        "copia_excedente": assinatura.duplicated(keep="first").values,
    })
    marcas["cenario_repetido"] = marcas["grupo_repeticao"].notna()
    return marcas


def derivar(base, sem_conta, contas):
    """Cria marcações e métricas derivadas, sem alterar as contas originais."""
    base = base.copy()
    base["encerramento"] = base["ano_n"] == 12

    base["residuo_balanco"] = base["BAL - Total do Ativo"] + base["BAL - Total do Passivo"]
    conferencia = (sem_conta[sem_conta["posicao"] == 1]
                   .set_index(["cenario", "ano_n"])["valor"].rename("conferencia_modelo"))
    base = base.join(conferencia, on=["cenario", "ano_n"])

    receita = base["DRE - Receita"].where(base["DRE - Receita"] != 0)  # evita divisão por zero
    base["margem_ebitda"] = base["DRE - EBITDA"] / receita
    base["margem_operacional"] = base["DRE - Resultado Operacional"] / receita
    base["margem_liquida"] = base["DRE - Resultado Líquido"] / receita

    marcas = marcar_repeticoes(base, contas)
    base = base.merge(marcas, on="cenario", how="left")
    return base, marcas


# ---------------------------------------------------------------- verificar
def verificar(bruto, nomeadas, sem_conta, base, marcas):
    """Confere contagens e identidades contábeis. Cada teste informa quantos grupos foram comparáveis."""
    def teste(nome, diferenca):
        comparaveis = int(diferenca.notna().sum())
        ok = int((diferenca.abs() < TOLERANCIA).sum())
        return {"teste": nome, "comparaveis": comparaveis, "aprovados": ok,
                "passou": comparaveis > 0 and ok == comparaveis,
                "maior_diferenca": float(diferenca.abs().max())}

    b = base
    testes = [
        teste("Total do Ativo + Total do Passivo = 0", b["residuo_balanco"]),
        teste("Ativo = Circulante + Realizável LP + Permanente",
              b["BAL - Total do Ativo"] - (b["BAL - Ativo Circulante"] + b["BAL - Realizável a Longo Prazo"]
                                           + b["BAL - Permanente"])),
        teste("Passivo = Circulante + Exigível LP + Patrimônio Líquido",
              b["BAL - Total do Passivo"] - (b["BAL - Passivo Circulante"] + b["BAL - Exigível a Longo Prazo"]
                                             + b["BAL - Patrimônio Líquido"])),
        teste("Saldo Final = Saldo Inicial + Geração de Caixa",
              b["FLU - Saldo Final"] - (b["FLU - Saldo Inicial"] + b["FLU - Geração de Caixa"])),
        teste("Conferência do modelo = resíduo do balanço", b["conferencia_modelo"] - b["residuo_balanco"]),
    ]
    contagens = {
        "linhas_bruto": len(bruto),
        "linhas_contas": len(nomeadas),
        "linhas_sem_conta": len(sem_conta),
        "cenarios": int(b["cenario"].nunique()),
        "anos": int(b["ano_n"].nunique()),
        "linhas_base_analitica": len(b),
        "contas": int(nomeadas["conta"].nunique()),
        "cenarios_repetidos": int(marcas["cenario_repetido"].sum()),
        "copias_excedentes": int(marcas["copia_excedente"].sum()),
        "grupos_repeticao": int(marcas["grupo_repeticao"].nunique()),
        "sem_conta_posicoes_2_e_3_sempre_zero":
            bool((sem_conta.loc[sem_conta["posicao"] > 1, "valor"] == 0).all()),
    }
    return {"contagens": contagens, "testes": testes}


# ---------------------------------------------------------------- dicionário
# Totais e subtotais do balanço, na ordem em que aparecem no arquivo. As contas que vêm
# depois de cada marcador pertencem ao grupo dele (conferido: a soma fecha, exceto no
# Passivo Circulante).
MARCADORES_BAL = {
    "BAL - Total do Ativo": ("Ativo", "total"),
    "BAL - Ativo Circulante": ("Ativo circulante", "subtotal"),
    "BAL - Realizável a Longo Prazo": ("Realizável a longo prazo", "subtotal"),
    "BAL - Permanente": ("Ativo permanente", "subtotal"),
    "BAL - Total do Passivo": ("Passivo e patrimônio líquido", "total"),
    "BAL - Passivo Circulante": ("Passivo circulante", "subtotal"),
    "BAL - Exigível a Longo Prazo": ("Exigível a longo prazo", "subtotal"),
    "BAL - Patrimônio Líquido": ("Patrimônio líquido", "subtotal"),
}
RESULTADOS = {
    "DRE - Resultado Operacional", "DRE - Resultado Financeiro", "DRE - Resultado Antes do Imposto de Renda",
    "DRE - Resultado Líquido", "DRE - Resultado Líquido após Equivalência", "DRE - EBITDA",
    "FLU - Geração de Caixa",
}
# O que cada conta representa. Onde a CTI não detalhou a composição, o texto diz isso.
DEFINICOES = {
    "BAL - Total do Ativo": "Soma de todos os bens e direitos da concessionária",
    "BAL - Ativo Circulante": "Bens e direitos realizáveis em até um ano",
    "BAL - Disponível": "Caixa e equivalentes de caixa",
    "BAL - Contas a Receber - SWAP": "Valores a receber de contratos de swap (derivativos)",
    "BAL - Contas a Receber - Partes Relacionadas": "Valores a receber de empresas do mesmo grupo econômico",
    "BAL - Contas a Receber - Clientes": "Valores a receber pelos serviços prestados na concessão",
    "BAL - Estoques Diversos": "Materiais e insumos em estoque",
    "BAL - Outros Créditos": "Outros direitos de curto prazo",
    "BAL - Realizável a Longo Prazo": "Direitos realizáveis após um ano",
    "BAL - At Fiscal Diferido": "Ativo fiscal diferido: tributos a recuperar em exercícios futuros",
    "BAL - Créditos Tributários": "Tributos a recuperar",
    "BAL - Outorga da Concessão": "Direito de outorga da concessão registrado como ativo",
    "BAL - Outros Créditos LP": "Outros direitos de longo prazo",
    "BAL - Permanente": "Investimentos, imobilizado e intangível, líquidos de depreciação e amortização",
    "BAL - Investimentos - Imobilizado": "Bens físicos usados na operação, pelo valor de aquisição",
    "BAL - Investimentos - Intangível": "Direitos sem forma física, como o de explorar a concessão, pelo valor de aquisição",
    "BAL - Diferido": "Gastos que beneficiam exercícios futuros (ativo diferido)",
    "BAL - Depreciação Acumulada": "Desgaste acumulado do imobilizado",
    "BAL - Amortização Acumulada": "Amortização acumulada de ativos de longo prazo",
    "BAL - Amortização - Intangível": "Amortização acumulada do intangível",
    "BAL - Total do Passivo": "Soma das obrigações com terceiros e do patrimônio líquido",
    "BAL - Passivo Circulante": "Obrigações com vencimento em até um ano",
    "BAL - Empréstimos": "Empréstimos e financiamentos de curto prazo",
    "BAL - Contas a Pagar - Parte Relacionada": "Valores a pagar a empresas do mesmo grupo econômico",
    "BAL - Fornecedores": "Valores a pagar a fornecedores",
    "BAL - Encargos Sociais e Trabalhistas": "Salários, férias e encargos a pagar",
    "BAL - Tributos a pagar": "Tributos a recolher",
    "BAL - Impostos": "Impostos a pagar; a diferença para Tributos a pagar não foi detalhada pela CTI",
    "BAL - Obrigações com o Poder Concedente": "Valores devidos ao poder concedente pelo contrato de concessão",
    "BAL - Outros Débitos": "Outras obrigações de curto prazo",
    "BAL - Provisão Manutenção": "Provisão para a manutenção da infraestrutura prevista no contrato",
    "BAL - Exigível a Longo Prazo": "Obrigações com vencimento após um ano",
    "BAL - Emprést": "Empréstimos e financiamentos de longo prazo",
    "BAL - Prov para Contingências": "Provisão para processos e riscos com perda provável",
    "BAL - Outros deb": "Outras obrigações de longo prazo",
    "BAL - Patrimônio Líquido": "Recursos dos acionistas: capital, reservas e resultados",
    "BAL - Capital Social": "Capital investido pelos acionistas",
    "BAL - Reservas de Capital": "Reservas formadas por aportes que não vêm do resultado",
    "BAL - Reservas Legais": "Reserva obrigatória por lei, formada a partir do lucro",
    "BAL - Reserva de Retenção de Lucros": "Lucros mantidos na empresa em vez de distribuídos",
    "BAL - Dividendos Antecipados": "Dividendos pagos antes do fim do exercício",
    "BAL - Resultado Acumulado": "Resultados de exercícios anteriores ainda não destinados",
    "BAL - Resultado do Período": "Resultado do exercício corrente, registrado no patrimônio líquido",
    "DRE - Receita": "Receita da operação da concessão",
    "DRE - Tributos": "Tributos sobre a receita",
    "DRE - Custos": "Custos da operação",
    "DRE - Depreciação e Amortização": "Despesa de depreciação e amortização do ano",
    "DRE - Resultado Operacional": "Resultado da operação, antes do resultado financeiro",
    "DRE - Receitas Financeiras": "Rendimentos de aplicações e outras receitas financeiras",
    "DRE - Despesas Financeiras": "Juros e outros encargos financeiros",
    "DRE - Resultado Financeiro": "Saldo entre receitas e despesas financeiras",
    "DRE - Outros Resultados Operacionais": "Outras receitas e despesas operacionais",
    "DRE - Resultado Antes do Imposto de Renda": "Resultado antes do imposto de renda e da contribuição social",
    "DRE - Imposto de Renda e Contribuição Social": "IRPJ e CSLL sobre o lucro",
    "DRE - Resultado Líquido": "Lucro ou prejuízo do ano",
    "DRE - Resultado Líquido após Equivalência": "Resultado líquido após a equivalência patrimonial",
    "DRE - EBITDA": "Lucro antes de juros, impostos, depreciação e amortização",
    "FLU - Saldo Inicial": "Caixa no início do ano",
    "FLU - Receita": "Recebimentos da receita no ano",
    "FLU - Tributos": "Pagamentos de tributos sobre a receita",
    "FLU - Custos": "Pagamentos de custos da operação",
    "FLU - Investimentos": "Pagamentos de investimentos em ativos",
    "FLU - Entradas": "Outras entradas de caixa; a composição não foi detalhada pela CTI",
    "FLU - Despesas Financeiras": "Pagamentos de juros e encargos financeiros",
    "FLU - Resultado Financeiro": "Resultado financeiro do ano",
    "FLU - Imposto de Renda e Contribuição Social": "Pagamentos de IRPJ e CSLL",
    "FLU - Distribuição para Acionista": "Dividendos e outras distribuições pagas aos acionistas",
    "FLU - Geração de Caixa": "Variação do caixa no ano",
    "FLU - Saldo Final": "Caixa no fim do ano",
}
# Alertas e fórmulas conferidos no dado, acrescentados depois da definição.
OBSERVACOES = {
    "BAL - Total do Ativo": "Fica negativo em parte dos cenários no Ano 12, no encerramento",
    "BAL - Disponível": "Igual ao FLU - Saldo Final em todos os registros",
    "BAL - Estoques Diversos": "Valores muito pequenos em relação às demais contas",
    "BAL - Depreciação Acumulada": "Conta redutora do ativo",
    "BAL - Amortização Acumulada": "Conta redutora do ativo",
    "BAL - Amortização - Intangível": "Conta redutora do ativo",
    "BAL - Total do Passivo": "Inclui o patrimônio líquido; somado ao Total do Ativo, dá zero",
    "BAL - Passivo Circulante": "Não é igual à soma das contas do seu grupo e o sinal varia. Pergunta pendente à CTI",
    "BAL - Emprést": "Distinta de BAL - Empréstimos: grupo e sinal diferentes",
    "BAL - Outros deb": "Distinta de BAL - Outros Débitos: grupo e sinal diferentes",
    "BAL - Dividendos Antecipados": "Reduz o patrimônio líquido, por isso tem sinal oposto às demais contas do grupo",
    "DRE - Resultado Operacional": "Cálculo: Receita + Tributos + Custos + Depreciação e Amortização",
    "DRE - Resultado Financeiro": "Cálculo: Receitas Financeiras + Despesas Financeiras",
    "DRE - Resultado Antes do Imposto de Renda": "Cálculo: Resultado Operacional + Resultado Financeiro + Outros Resultados Operacionais",
    "DRE - Resultado Líquido": "Cálculo: Resultado Antes do Imposto de Renda + Imposto de Renda e Contribuição Social",
    "DRE - Resultado Líquido após Equivalência": "Igual ao Resultado Líquido em todos os registros",
    "DRE - EBITDA": "Fornecido pela CTI; não reconcilia com o Resultado Operacional somado à Depreciação e Amortização",
    "FLU - Saldo Inicial": "Igual ao Saldo Final do ano anterior",
    "FLU - Resultado Financeiro": "Informativa: não entra na Geração de Caixa",
    "FLU - Geração de Caixa": "Cálculo: Receita + Tributos + Custos + Investimentos + Entradas + Despesas Financeiras + Imposto de Renda + Distribuição para Acionista",
    "FLU - Saldo Final": "Cálculo: Saldo Inicial + Geração de Caixa",
}


def descrever_conta(conta):
    """Definição da conta, seguida do alerta ou da fórmula, quando houver."""
    if conta not in DEFINICOES:
        raise KeyError(f"Conta sem definição no dicionário: {conta}")
    texto = DEFINICOES[conta]
    if conta in OBSERVACOES:
        texto += ". " + OBSERVACOES[conta]
    return texto


def descrever_sinal(valores):
    """Resume o sinal observado de uma conta em todos os registros."""
    total = len(valores)
    contagem = {"positivo": int((valores > 0).sum()), "negativo": int((valores < 0).sum()),
                "zero": int((valores == 0).sum())}
    presentes = {k: n for k, n in contagem.items() if n > 0}
    if len(presentes) == 1:
        return "sempre " + next(iter(presentes))

    def registros(n):
        return f"{n} registro{'s' if n > 1 else ''}"

    # Menos de 1% some no arredondamento: nesses casos mostra a contagem
    raros = {k: n for k, n in presentes.items() if n / total < 0.01}
    comuns = {k: n for k, n in presentes.items() if k not in raros}
    if len(comuns) == 1:
        adjetivo = {"positivo": ("positivo", "positivos"), "negativo": ("negativo", "negativos"),
                    "zero": ("igual a zero", "iguais a zero")}
        excecoes = " e ".join(f"{registros(n)} {adjetivo[k][n > 1]}" for k, n in raros.items())
        return f"sempre {next(iter(comuns))}, exceto {excecoes}"
    partes = [f"{k} em {n / total:.0%}" for k, n in comuns.items()]
    partes += [f"{k} em {registros(n)}" for k, n in raros.items()]
    return ", ".join(partes)


def descrever_cobertura(anos):
    faltam = sorted(set(range(1, 13)) - set(int(a) for a in anos))
    if not faltam:
        return "todos os anos"
    if len(faltam) == 1:
        return f"ausente no Ano {faltam[0]}"
    return "ausente nos anos " + ", ".join(map(str, faltam[:-1])) + f" e {faltam[-1]}"


def gerar_dicionario(nomeadas, contas):
    """Descreve cada campo da base analítica, com grupo, sinal e cobertura calculados do próprio dado."""
    # Ordem das contas num grupo com cobertura completa, para atribuir o grupo do balanço
    completo = nomeadas.groupby(["cenario", "ano_n"])["conta"].transform("size")
    amostra = nomeadas[completo == completo.max()]
    primeiro = amostra[["cenario", "ano_n"]].iloc[0]
    ordem = amostra[(amostra["cenario"] == primeiro["cenario"]) & (amostra["ano_n"] == primeiro["ano_n"])]
    ordem = ordem.sort_values("linha_origem")["conta"].tolist()

    grupo_bal, grupo_atual = {}, None
    for c in ordem:
        if c in MARCADORES_BAL:
            grupo_atual = MARCADORES_BAL[c][0]
            grupo_bal[c] = MARCADORES_BAL[c]
        elif c.startswith("BAL"):
            grupo_bal[c] = (grupo_atual, "detalhe")

    sinais = nomeadas.groupby("conta")["valor"].apply(descrever_sinal)
    anos = nomeadas.groupby("conta")["ano_n"].unique()

    linhas = [
        ("identificacao", "cenario", "texto", "bruto", "", "", "", "", "", "código",
         "Identificador do cenário de Monte Carlo, de Total Cen_00001 a Total Cen_01200"),
        ("identificacao", "ano_n", "inteiro", "derivado", "", "", "", "", "", "ano (1 a 12)",
         "Ano do horizonte, extraído do campo ano"),
        ("identificacao", "ano_calendario", "inteiro", "derivado", "", "", "", "", "", "ano",
         "Ano pela convenção da CTI: Ano 1 = 2027, Ano 12 = 2038"),
    ]
    for c in contas:
        bloco = c.split(" - ")[0]
        if bloco == "BAL":
            grupo, tipo_linha = grupo_bal[c]
            natureza = "saldo no fim do ano"
        else:
            grupo = "Demonstração do resultado" if bloco == "DRE" else "Fluxo de caixa"
            tipo_linha = "resultado" if c in RESULTADOS else "detalhe"
            natureza = "movimento do ano"
            if c in ("FLU - Saldo Inicial", "FLU - Saldo Final"):
                tipo_linha, natureza = "saldo", "saldo de caixa"
        linhas.append(("conta", c, "decimal", "bruto", bloco, grupo, tipo_linha, natureza,
                       sinais[c] + " / " + descrever_cobertura(anos[c]), "reais", descrever_conta(c)))
    linhas += [
        ("derivado", "encerramento", "booleano", "derivado", "", "", "", "", "", "verdadeiro ou falso",
         "Verdadeiro no Ano 12, encerramento da concessão"),
        ("derivado", "residuo_balanco", "decimal", "derivado", "", "", "", "", "", "reais",
         "Total do Ativo + Total do Passivo; deve ser próximo de zero"),
        ("derivado", "conferencia_modelo", "decimal", "bruto", "", "", "", "", "", "reais",
         "Primeira linha sem nome de conta do grupo; coincide com o resíduo do balanço"),
        ("derivado", "margem_ebitda", "decimal", "derivado", "", "", "", "", "", "fração da receita (0,77 = 77%)",
         "EBITDA dividido pela Receita, com o EBITDA como fornecido pela CTI"),
        ("derivado", "margem_operacional", "decimal", "derivado", "", "", "", "", "", "fração da receita (0,77 = 77%)",
         "Resultado Operacional dividido pela Receita"),
        ("derivado", "margem_liquida", "decimal", "derivado", "", "", "", "", "", "fração da receita (0,77 = 77%)",
         "Resultado Líquido dividido pela Receita"),
        ("derivado", "grupo_repeticao", "texto", "derivado", "", "", "", "", "", "rótulo (G01)",
         "Grupo de cenários com trajetória idêntica nos 12 anos; vazio se o cenário é único"),
        ("derivado", "cenario_repetido", "booleano", "derivado", "", "", "", "", "", "verdadeiro ou falso",
         "Verdadeiro se o cenário pertence a um grupo de repetição"),
        ("derivado", "copia_excedente", "booleano", "derivado", "", "", "", "", "", "verdadeiro ou falso",
         "Verdadeiro nas cópias além da primeira de cada grupo; filtrar para analisar sem cópias"),
    ]
    colunas = ["secao", "campo", "tipo", "origem", "bloco", "grupo", "tipo_linha", "natureza",
               "sinal_e_cobertura", "unidade", "descricao"]
    return pd.DataFrame(linhas, columns=colunas)


def salvar_dicionario_md(dicionario, caminho):
    """Grava o dicionário em Markdown, em duas tabelas, legível direto no GitHub."""
    linhas = [
        "# Dicionário de dados da base analítica", "",
        "Gerado por `src/prepara.py`. Uma linha da base analítica = um cenário em um ano (14.400 linhas).",
        "Grupo, tipo de linha, sinal e cobertura de cada conta são calculados a partir do próprio dado.", "",
        "## Identificação e campos derivados", "",
        "| Campo | Tipo | Origem | Unidade | Descrição |", "|---|---|---|---|---|",
    ]
    for r in dicionario[dicionario["secao"] != "conta"].itertuples(index=False):
        linhas.append(f"| `{r.campo}` | {r.tipo} | {r.origem} | {r.unidade} | {r.descricao} |")
    linhas += [
        "", "## Contas contábeis", "",
        "Valores em reais. **Tipo de linha:** total e subtotal já somam as contas do seu grupo, então não devem ser "
        "somados junto com elas. **Sinal e cobertura:** o sinal observado em todos os registros e os anos em que "
        "a conta aparece.", "",
        "| Conta | Descrição | Grupo | Tipo de linha | Natureza | Sinal e cobertura |", "|---|---|---|---|---|---|",
    ]
    for r in dicionario[dicionario["secao"] == "conta"].itertuples(index=False):
        linhas.append(f"| {r.campo} | {r.descricao} | {r.grupo} | {r.tipo_linha} | {r.natureza} | {r.sinal_e_cobertura} |")
    # "$" escapado: vários visualizadores de Markdown tratam "$" como início de fórmula
    # matemática e apagam o texto entre dois cifrões, como em duas linhas seguidas com "R$"
    texto = "\n".join(linhas).replace("$", "\\$")
    caminho.write_text(texto + "\n", encoding="utf-8")


# ---------------------------------------------------------------- execução
def main(raiz=None):
    p = caminhos(raiz)
    p["processed"].mkdir(parents=True, exist_ok=True)
    p["dicionario"].parent.mkdir(parents=True, exist_ok=True)

    hash_antes = hash_arquivo(p["bruto"])
    bruto = coletar(p["bruto"])
    nomeadas, sem_conta = selecionar(bruto)
    nomeadas = uniformizar(nomeadas)
    validar_chave(nomeadas)
    base, contas = formatar(nomeadas)
    base, marcas = derivar(base, sem_conta, contas)
    relatorio = verificar(bruto, nomeadas, sem_conta, base, marcas)
    hash_depois = hash_arquivo(p["bruto"])

    if hash_antes != hash_depois:
        raise RuntimeError("O arquivo bruto mudou durante a execução")

    base.to_parquet(p["processed"] / "base_analitica.parquet", index=False)
    nomeadas.to_parquet(p["processed"] / "base_longa.parquet", index=False)
    sem_conta[["linha_origem", "cenario", "ano", "ano_n", "posicao", "valor"]].to_parquet(
        p["processed"] / "auditoria_sem_conta.parquet", index=False)
    dicionario = gerar_dicionario(nomeadas, contas)
    dicionario.to_csv(p["processed"] / "dicionario_dados.csv", sep=";", index=False, encoding="utf-8-sig")
    salvar_dicionario_md(dicionario, p["dicionario"])

    relatorio["entrada"] = {"arquivo": ARQUIVO_BRUTO, "sha256": hash_antes,
                            "tamanho_bytes": p["bruto"].stat().st_size, "inalterado": True}
    relatorio["execucao"] = {"data": datetime.now().isoformat(timespec="seconds"),
                             "pandas": pd.__version__, "tolerancia_reais": TOLERANCIA}
    with open(p["processed"] / "relatorio_qualidade.json", "w", encoding="utf-8") as f:
        json.dump(relatorio, f, ensure_ascii=False, indent=2)

    c = relatorio["contagens"]
    print(f"Base analítica: {c['linhas_base_analitica']} linhas ({c['cenarios']} cenários x {c['anos']} anos), "
          f"{c['contas']} contas")
    print(f"Cenários repetidos: {c['cenarios_repetidos']} em {c['grupos_repeticao']} grupo(s); "
          f"{c['copias_excedentes']} cópias excedentes")
    for t in relatorio["testes"]:
        situacao = "OK  " if t["passou"] else "FALHA"
        print(f"[{situacao}] {t['teste']}: {t['aprovados']}/{t['comparaveis']}")
    print("Arquivo bruto inalterado (SHA-256 igual antes e depois).")
    return base, relatorio


if __name__ == "__main__":
    main()
