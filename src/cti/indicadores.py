"""KPIs da planilha E1, com estados explícitos e denominadores protegidos."""
from dataclasses import dataclass
import math
import pandas as pd

@dataclass(frozen=True)
class KPI:
    nome: str
    valor: float | None
    unidade: str
    formula: str
    estado: str = "calculado"

def calcular(contas, taxa=.10, cac=4000., ltv=45000.):
    """Um período; contas devem ser médias da população selecionada, nunca somas."""
    def v(nome):
        x = contas.get(nome, float("nan"))
        return float(x) if pd.notna(x) and math.isfinite(float(x)) else None
    r,c,e,rl = [v("DRE - "+s) for s in ["Receita","Custos","EBITDA","Resultado Líquido"]]
    ac,disp,est,rlp,at,pc,elp,pl = [v("BAL - "+s) for s in
        ["Ativo Circulante","Disponível","Estoques Diversos","Realizável a Longo Prazo",
         "Total do Ativo","Passivo Circulante","Exigível a Longo Prazo","Patrimônio Líquido"]]
    out=[]
    def add(nome,unit,formula,args,fn,den=None,passivo=False,estado="calculado"):
        status=estado
        value=None
        if any(x is None for x in args): status="indisponível: conta ausente"
        elif passivo and pc >= 0: status="pendente: PC com sinal positivo"
        elif den is not None and den == 0: status="indisponível: denominador zero"
        else:
            value=float(fn())
            if not math.isfinite(value): value=None; status="indisponível: resultado não finito"
        out.append(KPI(nome,value,unit,formula,status))
    add("Receita","R$","DRE - Receita",[r],lambda:r)
    add("Custos variáveis (premissa)","R$","-Custos; classificação variável é hipótese",[c],lambda:-c,estado="premissa acadêmica")
    add("Margem de contribuição","R$","Receita + Custos; antes de tributos e demais despesas",[r,c],lambda:r+c,estado="premissa acadêmica")
    add("Margem de contribuição (%)","%","(Receita + Custos)/Receita",[r,c],lambda:(r+c)/r,den=r,estado="premissa acadêmica")
    add("EBITDA","R$","EBITDA fornecido; memória de cálculo não reconciliada",[e],lambda:e)
    add("Margem EBITDA","%","EBITDA/Receita",[e,r],lambda:e/r,den=r)
    add("Margem líquida","%","Resultado Líquido/Receita",[rl,r],lambda:rl/r,den=r)
    add("Liquidez corrente","índice","AC/(-PC)",[ac,pc],lambda:ac/-pc,den=pc,passivo=True)
    add("Liquidez seca","índice","(AC-Estoques)/(-PC)",[ac,est,pc],lambda:(ac-est)/-pc,den=pc,passivo=True)
    add("Liquidez imediata","índice","Disponível/(-PC)",[disp,pc],lambda:disp/-pc,den=pc,passivo=True)
    div = -pc-elp if pc is not None and elp is not None else None
    add("Liquidez geral","índice","(AC+RLP)/(-PC-ELP)",[ac,rlp,pc,elp],lambda:(ac+rlp)/div,den=div,passivo=True)
    add("Endividamento geral","%","(-PC-ELP)/Ativo",[pc,elp,at],lambda:div/at,den=at,passivo=True)
    add("Participação de capital de terceiros","índice","(-PC-ELP)/(-PL)",[pc,elp,pl],lambda:div/-pl,den=pl,passivo=True)
    add("Composição do endividamento","%","(-PC)/(-PC-ELP)",[pc,elp],lambda:-pc/div,den=div,passivo=True)
    add("EVA simplificado","R$","Resultado Líquido - taxa*(-PL); não é EVA econômico completo",[rl,pl,taxa],lambda:rl-taxa*-pl,estado="premissa acadêmica")
    add("CAC simulado","R$ por cliente","Hipótese editável, não observado",[cac],lambda:cac,estado="simulado")
    add("LTV simulado","R$ por cliente","Hipótese editável, não observado",[ltv],lambda:ltv,estado="simulado")
    add("LTV / CAC","vezes","LTV/CAC",[ltv,cac],lambda:ltv/cac,den=cac,estado="simulado")
    return out

def tabela(medias, **premissas):
    return pd.DataFrame([{"ano":int(ano), **k.__dict__}
                         for ano,row in medias.iterrows() for k in calcular(row,**premissas)])
