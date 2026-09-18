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
def gerar_dicionario(nomeadas, contas):
    """Descreve cada campo da base analítica. Não contém valores da CTI."""
    natureza_bloco = {
        "BAL": "Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos",
        "DRE": "Movimento do ano. Receitas positivas; custos e despesas negativos",
        "FLU": "Movimento do ano. Entradas positivas; saídas negativas",
    }
    anos_por_conta = nomeadas.groupby("conta")["ano_n"].unique()
    linhas = [
        ("cenario", "texto", "bruto", "Identificador do cenário de Monte Carlo (Total Cen_00001 a Total Cen_01200)", ""),
        ("ano_n", "inteiro", "derivado", "Ano do horizonte, de 1 a 12, extraído do campo ano", ""),
        ("ano_calendario", "inteiro", "derivado", "Ano por convenção da CTI: Ano 1 = 2027 ... Ano 12 = 2038", ""),
    ]
    for c in contas:
        bloco = c.split(" - ")[0]
        natureza = natureza_bloco[bloco]
        if c in ("FLU - Saldo Inicial", "FLU - Saldo Final"):
            natureza = "Saldo de caixa (não somar entre anos)"
        anos = sorted(int(a) for a in anos_por_conta[c])
        faltam = sorted(set(range(1, 13)) - set(anos))
        cobertura = "todos os anos" if not faltam else "ausente no(s) ano(s) " + ", ".join(map(str, faltam))
        linhas.append((c, "decimal", "bruto", f"Conta do bloco {bloco}. {natureza}. Cobertura: {cobertura}", "R$"))
    linhas += [
        ("encerramento", "booleano", "derivado", "Verdadeiro no Ano 12, encerramento da concessão", ""),
        ("residuo_balanco", "decimal", "derivado", "BAL - Total do Ativo + BAL - Total do Passivo; deve ser próximo de zero", "R$"),
        ("conferencia_modelo", "decimal", "bruto", "Primeira linha sem nome de conta do grupo; coincide com o resíduo do balanço", "R$"),
        ("margem_ebitda", "decimal", "derivado", "DRE - EBITDA / DRE - Receita (EBITDA como fornecido pela CTI)", "fração"),
        ("margem_operacional", "decimal", "derivado", "DRE - Resultado Operacional / DRE - Receita", "fração"),
        ("margem_liquida", "decimal", "derivado", "DRE - Resultado Líquido / DRE - Receita", "fração"),
        ("grupo_repeticao", "texto", "derivado", "Grupo de cenários com trajetória idêntica nos 12 anos; vazio se o cenário é único", ""),
        ("cenario_repetido", "booleano", "derivado", "Verdadeiro se o cenário pertence a um grupo de repetição", ""),
        ("copia_excedente", "booleano", "derivado", "Verdadeiro para as cópias além da primeira de cada grupo; usar para análise sem cópias", ""),
    ]
    return pd.DataFrame(linhas, columns=["campo", "tipo", "origem", "descricao", "unidade"])


def salvar_dicionario_md(dicionario, caminho):
    """Grava o dicionário como tabela Markdown, legível direto no GitHub."""
    linhas = ["# Dicionário de dados da base analítica", "",
              "Gerado por `src/prepara.py`. Uma linha da base analítica = um cenário em um ano.", "",
              "| Campo | Tipo | Origem | Descrição | Unidade |", "|---|---|---|---|---|"]
    for r in dicionario.itertuples(index=False):
        linhas.append(f"| `{r.campo}` | {r.tipo} | {r.origem} | {r.descricao} | {r.unidade} |")
    caminho.write_text("\n".join(linhas) + "\n", encoding="utf-8")


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
