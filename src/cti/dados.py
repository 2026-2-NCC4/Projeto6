"""Contrato da base preparada e reprodução da E1 sem sobrescrever seus documentos."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from src import prepara

HASH_REFERENCIA = "a93fb4555eab2eee7a437b98c2ff5cf4c392336d745a835b529974635cf8a3fc"
CONTAS = list(prepara.DEFINICOES)
META = ["cenario", "ano_n", "ano_calendario", "encerramento",
        "grupo_repeticao", "cenario_repetido", "copia_excedente"]

def validar(base):
    if base.empty:
        raise ValueError("Base vazia.")
    faltam = set(CONTAS + META) - set(base.columns)
    if faltam:
        raise ValueError("Colunas obrigatórias ausentes: " + ", ".join(sorted(faltam)))
    if base[["cenario", "ano_n"]].isna().any().any():
        raise ValueError("Chave ausente.")
    if base.duplicated(["cenario", "ano_n"]).any():
        raise ValueError("Chave cenário/ano duplicada.")
    if not pd.api.types.is_numeric_dtype(base.ano_n) or not base.ano_n.isin(range(1, 13)).all():
        raise ValueError("Ano deve ser inteiro de 1 a 12.")
    cobertura = base.groupby("cenario").ano_n.agg(lambda s: set(s) == set(range(1, 13)))
    if not cobertura.all():
        raise ValueError("Cada cenário deve conter exatamente os 12 anos.")
    for col in CONTAS:
        if not pd.api.types.is_numeric_dtype(base[col]):
            raise ValueError(f"Conta não numérica: {col}")
        if np.isinf(base[col].to_numpy(dtype=float)).any():
            raise ValueError(f"Conta contém infinito: {col}")
    # Ausências do encerramento são preservadas; contas essenciais nunca são imputadas.
    essenciais = ["DRE - Receita", "DRE - Custos", "DRE - Resultado Líquido", "FLU - Geração de Caixa"]
    if base[essenciais].isna().any().any():
        raise ValueError("Conta essencial ausente.")
    for col in ["encerramento", "cenario_repetido", "copia_excedente"]:
        if not pd.api.types.is_bool_dtype(base[col]) or base[col].isna().any():
            raise ValueError(f"Flag inválida: {col}")
    if not (base.encerramento == base.ano_n.eq(12)).all():
        raise ValueError("Flag de encerramento inconsistente.")
    if not (base.ano_calendario == 2026 + base.ano_n).all():
        raise ValueError("Calendário difere da convenção acadêmica 2026 + ano.")
    marcas = prepara.marcar_repeticoes(base, CONTAS).set_index("cenario")
    for col in ["grupo_repeticao", "cenario_repetido", "copia_excedente"]:
        esperado = base.cenario.map(marcas[col]).astype("string").fillna("")
        if not esperado.equals(base[col].astype("string").fillna("")):
            raise ValueError(f"Marcação de trajetória inconsistente: {col}")
    return base

def carregar(caminho):
    return validar(pd.read_parquet(caminho))

def preparar_csv(caminho, destino):
    """Reutiliza todas as verificações E1; escreve somente em destino explicitado."""
    caminho, destino = Path(caminho), Path(destino)
    antes = prepara.hash_arquivo(caminho)
    bruto = prepara.coletar(caminho)
    nomeadas, sem_conta = prepara.selecionar(bruto)
    nomeadas = prepara.uniformizar(nomeadas)
    prepara.validar_chave(nomeadas)
    base, contas = prepara.formatar(nomeadas)
    base, marcas = prepara.derivar(base, sem_conta, contas)
    rel = prepara.verificar(bruto, nomeadas, sem_conta, base, marcas)
    prepara.exigir_aprovacao(rel)
    validar(base)
    if prepara.hash_arquivo(caminho) != antes:
        raise RuntimeError("Arquivo de origem mudou.")
    rel["entrada_sha256"] = antes
    rel["corresponde_referencia_E1"] = antes == HASH_REFERENCIA
    rel["cobertura_individual"] = True
    rel["schema"] = "e2-v1"
    destino.mkdir(parents=True, exist_ok=True)
    base.to_parquet(destino / "base_analitica.parquet", index=False)
    (destino / "qualidade.json").write_text(json.dumps(rel, ensure_ascii=False, indent=2), encoding="utf-8")
    return base, rel

def sintetica(n=120, seed=2026):
    """Dados fictícios gerados do zero, sem ajuste aos valores privados da CTI."""
    if n < 20:
        raise ValueError("Usar ao menos 20 cenários fictícios.")
    rng = np.random.default_rng(seed)
    linhas = []
    for c in range(n):
        escala = rng.uniform(.7, 1.3)
        for ano in range(1, 13):
            r = 1_000_000 * escala * (1 + .04 * ano) * rng.uniform(.95, 1.05)
            custo = -r * rng.uniform(.45, .68)
            rl = .76 * (r + custo - .08*r) + rng.normal(0, 35000)
            row = {conta: 0.0 for conta in CONTAS}
            row.update({"cenario": c + 1, "ano_n": ano, "ano_calendario": 2026 + ano,
                        "DRE - Receita": r, "DRE - Custos": custo, "DRE - EBITDA": r+custo,
                        "DRE - Resultado Líquido": rl, "FLU - Geração de Caixa": rl*.8,
                        "BAL - Ativo Circulante": r*.8, "BAL - Disponível": r*.5,
                        "BAL - Estoques Diversos": r*.01, "BAL - Realizável a Longo Prazo": r*.2,
                        "BAL - Permanente": r, "BAL - Total do Ativo": r*2,
                        "BAL - Passivo Circulante": -r*.3, "BAL - Exigível a Longo Prazo": -r*.7,
                        "BAL - Patrimônio Líquido": -r, "BAL - Total do Passivo": -r*2,
                        "encerramento": ano == 12})
            if ano == 12:
                for conta in ["BAL - Estoques Diversos", "BAL - Exigível a Longo Prazo", "BAL - Patrimônio Líquido"]:
                    row[conta] = np.nan
            linhas.append(row)
    base = pd.DataFrame(linhas)
    marcas = prepara.marcar_repeticoes(base, CONTAS)
    return validar(base.merge(marcas, on="cenario", how="left"))
