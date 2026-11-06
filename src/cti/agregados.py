"""Agregados publicáveis da base CTI para o painel: médias e percentis por ano, sem cenário individual.

O painel público não recebe a base. Este módulo gera, a partir da base preparada pela E1, um arquivo JSON
só com estatísticas por ano, nas populações "todos" e "sem_copias":
- médias das contas que o painel usa, pela mesma regra de recortes.medias_anuais;
- percentis P1 a P99, média e contagem das contas de distribuicao.CONTAS, pela mesma regra de
  distribuicao.percentis_anuais. Mínimo e máximo ficam de fora.
A parcela de cenários abaixo de um limite é aproximada por interpolação entre esses percentis.

Uso, a partir da raiz do repositório (grava só o arquivo de saída):
    python -m src.cti.agregados --base src/data/processed/e2/base_analitica.parquet
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import re
from datetime import datetime, timezone
import numpy as np
import pandas as pd
from .dados import carregar, validar
from .recortes import filtrar, medias_anuais
from .distribuicao import CONTAS as CONTAS_DISTRIBUICAO, percentis_anuais

SCHEMA = "agregados-e2-v1"
ARQUIVO = Path("app/dados/agregados_cti.json")
BASE_PADRAO = Path("src/data/processed/e2/base_analitica.parquet")
EVIDENCIAS = Path("documentos/Entrega 2/Projeto Interdisciplinar Ciência de Dados/evidencias_e2.json")
ANOS = list(range(1, 13))
POPULACOES = {"todos": False, "sem_copias": True}  # nome -> remove as cópias excedentes de trajetórias
GRADE = {f"P{i}": i / 100 for i in range(1, 100)}
# Só as contas que o painel usa: as 14 entradas da planilha E1 e a geração de caixa dos cartões.
CONTAS_MEDIAS = ["DRE - Receita", "DRE - Custos", "DRE - EBITDA", "DRE - Resultado Líquido",
                 "BAL - Ativo Circulante", "BAL - Disponível", "BAL - Estoques Diversos",
                 "BAL - Realizável a Longo Prazo", "BAL - Permanente", "BAL - Total do Ativo",
                 "BAL - Passivo Circulante", "BAL - Exigível a Longo Prazo", "BAL - Patrimônio Líquido",
                 "BAL - Total do Passivo", "FLU - Geração de Caixa"]
# População do painel -> (chave em evidencias_e2.json, população declarada no resultado)
REGRESSAO_PUBLICADA = {"todos": ("regressao", "todos os cenários"),
                       "sem_copias": ("sensibilidade_sem_copias", "trajetórias únicas")}
REGRAS = [
    "Médias: média de cada conta entre os cenários do ano; se faltar valor em algum cenário, a média fica indisponível (null).",
    "Percentis: P1 a P99 entre os cenários do ano, com interpolação linear; ausências descartadas; mínimo e máximo excluídos.",
    "Distribuição aos acionistas aparece como valor pago (sinal invertido), como no painel.",
    "Populações: todos os cenários; sem_copias remove as cópias excedentes de trajetórias repetidas.",
    "Sem identificador nem linha de cenário. Valores em reais; anos 1 a 12 (Ano 12 = encerramento).",
]


def _lista(valores):
    """Série anual para JSON: float exato (repr) e ausência como null, nunca zero."""
    return [None if pd.isna(v) else float(v) for v in valores]


def _serie(valores):
    return np.array([np.nan if v is None else float(v) for v in valores], dtype=float)


def sha256(caminho):
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def gerar(base, origem=None):
    """Agregados por ano das duas populações; `origem` descreve a base de onde vieram (hashes)."""
    validar(base)
    populacoes = {}
    for nome, unicas in POPULACOES.items():
        recorte = filtrar(base, (1, 12), unicas)
        medias = medias_anuais(recorte).reindex(ANOS)[CONTAS_MEDIAS]
        distribuicao = {}
        for conta in CONTAS_DISTRIBUICAO:
            tabela = percentis_anuais(recorte, conta, GRADE).reindex(ANOS)
            distribuicao[conta] = {"n": [int(x) for x in tabela["n"].fillna(0)],
                                   "media": _lista(tabela["media"]),
                                   **{q: _lista(tabela[q]) for q in GRADE}}
        populacoes[nome] = {"cenarios": int(recorte.cenario.nunique()), "anos": ANOS,
                            "medias": {c: _lista(medias[c]) for c in CONTAS_MEDIAS},
                            "distribuicao": distribuicao}
    return {"schema": SCHEMA, "gerado_em_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "origem": dict(origem or {}), "regras": REGRAS, "populacoes": populacoes}


def salvar(agregados, caminho=ARQUIVO):
    """Grava o JSON com cada série anual numa linha (diff legível no Git)."""
    validar_agregados(agregados)
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    texto = json.dumps(agregados, ensure_ascii=False, indent=1, allow_nan=False)
    # Junta numa linha só as listas sem texto (as séries); a lista de regras fica como está.
    texto = re.sub(r"\[[^\[\]{}\"]*\]",
                   lambda m: "[" + ", ".join(x.strip() for x in m.group(0)[1:-1].split(",")) + "]", texto)
    caminho.write_text(texto + "\n", encoding="utf-8")
    return caminho


def _numero_ou_nulo(x):
    return x is None or (isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x))


def validar_agregados(agregados):
    """Confere versão, populações, anos, séries completas e percentis em ordem; erro claro se não."""
    if not isinstance(agregados, dict) or agregados.get("schema") != SCHEMA:
        raise ValueError("Arquivo de agregados ausente ou de versão desconhecida.")
    populacoes = agregados.get("populacoes")
    if not isinstance(populacoes, dict):
        raise ValueError("Arquivo de agregados sem populações.")
    for nome in POPULACOES:
        pop = populacoes.get(nome)
        if not isinstance(pop, dict) or pop.get("anos") != ANOS:
            raise ValueError(f"População {nome} ausente ou sem os anos 1 a 12.")
        if not isinstance(pop.get("cenarios"), int) or isinstance(pop["cenarios"], bool) or pop["cenarios"] < 1:
            raise ValueError(f"População {nome} sem número de cenários.")
        medias, dist = pop.get("medias") or {}, pop.get("distribuicao") or {}
        series = [medias.get(c) for c in CONTAS_MEDIAS]
        series += [(dist.get(c) or {}).get(k) for c in CONTAS_DISTRIBUICAO for k in ["n", "media", *GRADE]]
        if any(not isinstance(s, list) or len(s) != len(ANOS) or not all(map(_numero_ou_nulo, s)) for s in series):
            raise ValueError(f"População {nome} com série anual ausente, incompleta ou não numérica.")
        for conta in CONTAS_DISTRIBUICAO:
            grade = np.array([_serie(dist[conta][q]) for q in GRADE])  # 99 percentis x 12 anos
            passos = np.diff(grade, axis=0)
            folga = 1e-9 * np.maximum(1.0, np.abs(grade[:-1]))
            if (passos < -folga).any():
                raise ValueError(f"Percentis fora de ordem em {conta} ({nome}).")
    return agregados


def ler(caminho=ARQUIVO):
    return validar_agregados(json.loads(Path(caminho).read_text(encoding="utf-8")))


def _populacao(agregados, populacao):
    if populacao not in POPULACOES:
        raise ValueError(f"População desconhecida: {populacao}")
    return agregados["populacoes"][populacao]


def _anos(pop, anos):
    inicio, fim = anos
    if not 1 <= inicio <= fim <= 12:
        raise ValueError("Intervalo de anos inválido.")
    return [a for a in pop["anos"] if inicio <= a <= fim]


def medias(agregados, populacao="todos", anos=(1, 12)):
    """Mesmo formato de recortes.medias_anuais, só com CONTAS_MEDIAS."""
    pop = _populacao(agregados, populacao)
    tabela = pd.DataFrame({c: _serie(pop["medias"][c]) for c in CONTAS_MEDIAS},
                          index=pd.Index(pop["anos"], name="ano_n"))
    return tabela.loc[_anos(pop, anos)]


def percentis(agregados, conta, populacao="todos", anos=(1, 12)):
    """Mesmo formato de distribuicao.percentis_anuais com a grade P1 a P99; anos sem valor ficam de fora."""
    pop = _populacao(agregados, populacao)
    if conta not in pop["distribuicao"]:
        raise ValueError(f"Conta sem distribuição definida: {conta}")
    d = pop["distribuicao"][conta]
    tabela = pd.DataFrame({**{q: _serie(d[q]) for q in GRADE}, "media": _serie(d["media"]),
                           "n": np.array(d["n"], dtype=int)}, index=pd.Index(pop["anos"], name="ano_n"))
    tabela = tabela.loc[_anos(pop, anos)]
    return tabela[tabela.n > 0]


def proporcao_abaixo(agregados, conta, populacao="todos", limite=0.0, anos=(1, 12)):
    """Por ano: parcela aproximada dos cenários com valor abaixo do limite (mesma escala da conta).

    Interpola linearmente entre os percentis P1 a P99 (erro em torno de 1 ponto percentual).
    faixa: "aproximada"; "ate_1" se o limite não passa de P1; "acima_99" se passa de P99.
    """
    limite = float(limite)
    if not math.isfinite(limite):
        raise ValueError("Limite deve ser um número finito.")
    tabela = percentis(agregados, conta, populacao, anos)
    p = np.array(list(GRADE.values()))
    linhas = []
    for ano, grade in zip(tabela.index, tabela[list(GRADE)].to_numpy(dtype=float)):
        q = np.maximum.accumulate(grade)  # absorve diferenças de arredondamento na ordem
        j = int(np.searchsorted(q, limite, side="left"))  # percentis estritamente abaixo do limite
        if j == 0:
            prop, faixa = 0.0, "ate_1"
        elif j == len(q):
            prop, faixa = 1.0, "acima_99"
        else:
            prop = p[j - 1] + (limite - q[j - 1]) / (q[j] - q[j - 1]) * (p[j] - p[j - 1])
            faixa = "aproximada"
        linhas.append((ano, float(prop), faixa))
    return pd.DataFrame(linhas, columns=["ano_n", "proporcao", "faixa"]).set_index("ano_n")


def regressao_publicada(caminho=EVIDENCIAS):
    """Resultados da regressão já publicados nas evidências da E2 (calculados com a base CTI local)."""
    ev = json.loads(Path(caminho).read_text(encoding="utf-8"))
    if ev.get("modo") != "CTI":
        raise ValueError("As evidências publicadas não vêm da base CTI.")
    saida = {"meta": {"data_utc": ev.get("data_utc"), "commit": ev.get("commit_implementacao")}}
    for nome, (chave, populacao) in REGRESSAO_PUBLICADA.items():
        res = ev.get(chave)
        if not isinstance(res, dict) or res.get("populacao") != populacao:
            raise ValueError(f"Regressão publicada ausente ou de outra população: {chave}.")
        saida[nome] = res
    return saida


def main(argv=None):
    parser = argparse.ArgumentParser(description="Gera o arquivo de agregados publicáveis do painel.")
    parser.add_argument("--base", type=Path, default=BASE_PADRAO, help="base preparada (parquet)")
    parser.add_argument("--saida", type=Path, default=ARQUIVO, help="arquivo JSON de agregados")
    args = parser.parse_args(argv)
    base = carregar(args.base)
    arquivo_qualidade = args.base.with_name("qualidade.json")
    qualidade = json.loads(arquivo_qualidade.read_text(encoding="utf-8")) if arquivo_qualidade.exists() else {}
    origem = {"base": args.base.name, "sha256_base": sha256(args.base),
              "entrada_sha256": qualidade.get("entrada_sha256"),
              "corresponde_referencia_E1": qualidade.get("corresponde_referencia_E1"),
              "schema_base": qualidade.get("schema")}
    caminho = salvar(gerar(base, origem), args.saida)
    agregados = ler(caminho)
    print(json.dumps({"arquivo": str(caminho), "bytes": caminho.stat().st_size,
                      "cenarios": {n: p["cenarios"] for n, p in agregados["populacoes"].items()},
                      "entrada_sha256": origem["entrada_sha256"],
                      "corresponde_referencia_E1": origem["corresponde_referencia_E1"]}, ensure_ascii=True))


if __name__ == "__main__":
    main()
