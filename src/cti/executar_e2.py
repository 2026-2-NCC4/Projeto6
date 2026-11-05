"""Executa pipeline, comparação independente com E1 e regressão. Não altera E1."""
from pathlib import Path
import argparse
import json
import platform
import importlib.metadata
from datetime import datetime, timezone
import math
import pandas as pd
import openpyxl
from src.cti.dados import preparar_csv, sintetica, carregar
from src.cti.recortes import medias_anuais
from src.cti.indicadores import calcular
from src.cti.regressao import executar, figuras

def comparar_planilha(base, planilha):
    wb=openpyxl.load_workbook(planilha,data_only=True)
    medias=medias_anuais(base)
    entradas=wb["Entradas"]; kpis=wb["KPIs"]
    taxa,cac,ltv=[entradas[c].value for c in ["E20","E18","E19"]]
    if not all(isinstance(v,(int,float)) for v in [taxa,cac,ltv]):
        raise ValueError("Premissas da planilha sem valor numérico.")
    numeric,estados,inputs,identidades=0,0,0,0
    divergencias=[]
    for ano,row in medias.iterrows():
        for r in range(2,16):
            conta=" ".join(entradas.cell(r,2).value.split())
            esperado=entradas.cell(r,int(ano)+4).value
            valor=row[conta]
            if esperado is None:
                ok=pd.isna(valor)
            else:
                ok=isinstance(esperado,(int,float)) and math.isclose(valor,esperado,rel_tol=1e-9,abs_tol=.01)
                inputs+=1
            if not ok: divergencias.append(f"Entrada {r}, ano {ano}")
        resultados=calcular(row,taxa=taxa,cac=cac,ltv=ltv)
        for i,k in enumerate(resultados,2):
            esperado=kpis.cell(i,int(ano)+3).value
            if isinstance(esperado,(int,float)):
                ok=k.valor is not None and math.isclose(k.valor,esperado,rel_tol=1e-6,abs_tol=.01)
                numeric+=1
            else:
                status=str(esperado).lower()
                ok=k.valor is None and (("pendente" in status and k.estado.startswith("pendente")) or
                     ("indisponível" in status and k.estado.startswith("indisponível")))
                estados+=1
            if not ok: divergencias.append(f"KPI {i}, ano {ano}")
        erros=[row["BAL - Total do Ativo"]-(row["BAL - Ativo Circulante"]+row["BAL - Realizável a Longo Prazo"]+row["BAL - Permanente"]),
               row["BAL - Total do Ativo"]+row["BAL - Total do Passivo"]]
        for erro in erros:
            if pd.isna(erro) or abs(erro)>=1.: divergencias.append(f"Identidade ano {ano}")
            else: identidades+=1
    if numeric+estados!=216 or identidades!=24 or divergencias:
        raise AssertionError("Conferência E1 falhou: "+str(divergencias))
    return {"kpis_numericos":numeric,"estados_indisponiveis_pendentes":estados,
            "kpis_total":numeric+estados,"identidades":identidades,"entradas_numericas":inputs,
            "divergencias":divergencias,"origem":"Comparação com valores salvos da planilha E1; não é novo recálculo do Excel.",
            "premissas":{"taxa":taxa,"cac":cac,"ltv":ltv}}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--csv",type=Path)
    parser.add_argument("--base",type=Path)
    parser.add_argument("--saida",type=Path,default=Path("src/data/processed/e2"))
    args=parser.parse_args()
    args.saida.mkdir(parents=True,exist_ok=True)
    if args.csv:
        base,qualidade=preparar_csv(args.csv,args.saida)
        modo="CTI"
    elif args.base:
        base=carregar(args.base); qualidade={"origem":"base preparada"}; modo="CTI"
    else:
        base=sintetica(); qualidade={"origem":"fictícia independente"}; modo="fictício"
    rel={"data_utc":datetime.now(timezone.utc).isoformat(),"modo":modo,"qualidade":qualidade,
         "ambiente":{"python":platform.python_version(),**{x:importlib.metadata.version(x) for x in ["pandas","numpy","scikit-learn","statsmodels","streamlit"]}}}
    if modo=="CTI":
        planilha=next(Path("documentos/Entrega 1/Contabilidade e Finanças").glob("*.xlsx"))
        rel["financas"]=comparar_planilha(base,planilha)
    rel["regressao"]=executar(base)
    rel["sensibilidade_sem_copias"]=executar(base,unicas=True)
    rel["sensibilidade_com_encerramento"]=executar(base,incluir_encerramento=True)
    figuras(rel["regressao"],args.saida)
    (args.saida/"resultados_e2.json").write_text(json.dumps(rel,ensure_ascii=False,indent=2,allow_nan=False),encoding="utf-8")
    print(json.dumps({k:v for k,v in rel.items() if k in ["data_utc","modo","ambiente","financas"]},ensure_ascii=True))
    print(json.dumps({k:{"modelo":rel[k]["modelo"],"teste":rel[k]["teste"],"baseline":rel[k]["baseline_teste"]} for k in ["regressao","sensibilidade_sem_copias","sensibilidade_com_encerramento"]}))
if __name__=="__main__": main()
