"""Regressão associativa com divisão de trajetórias, diagnóstico e saída agregada."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from .dados import validar

SEED = 20261105
COLUNAS = {"DRE - Receita":"receita_milhoes", "DRE - Custos":"custos_milhoes",
           "DRE - Resultado Líquido":"resultado_milhoes"}

def grupos(base):
    return pd.Series(np.where(base.grupo_repeticao.notna(),
        "repeticao:" + base.grupo_repeticao.astype("string").fillna(""),
        "cenario:" + base.cenario.astype(str)), index=base.index)

def separar(df):
    g = grupos(df)
    if g.nunique() < 10:
        raise ValueError("Regressão requer pelo menos dez trajetórias distintas.")
    dev_idx, test_idx = next(GroupShuffleSplit(n_splits=1,test_size=.2,random_state=SEED).split(df,groups=g))
    treino_idx, val_idx = next(GroupShuffleSplit(n_splits=1,test_size=.25,random_state=SEED+1).split(df.iloc[dev_idx],groups=g.iloc[dev_idx]))
    indices = {"treino":dev_idx[treino_idx], "validacao":dev_idx[val_idx], "teste":test_idx}
    sets = {k:set(g.iloc[v]) for k,v in indices.items()}
    if sets["treino"] & sets["validacao"] or sets["treino"] & sets["teste"] or sets["validacao"] & sets["teste"]:
        raise RuntimeError("Vazamento de trajetórias.")
    return indices, g

def desenho(df, modelo, anos):
    partes = [df[["receita_milhoes"]].astype(float)]
    if modelo == "multipla":
        partes.append(df[["custos_milhoes"]].astype(float))
        partes.append(pd.DataFrame({f"ano_{a}":df.ano_n.eq(a).astype(float) for a in anos[1:]},index=df.index))
    return sm.add_constant(pd.concat(partes,axis=1),has_constant="add")

def metricas(y,p):
    return {"MAE_milhoes":float(mean_absolute_error(y,p)),
            "RMSE_milhoes":float(np.sqrt(mean_squared_error(y,p))),
            "R2":float(r2_score(y,p))}

def executar(base, unicas=False, incluir_encerramento=False):
    validar(base)
    b = base.loc[(~base.copia_excedente if unicas else pd.Series(True,index=base.index)) &
                 (base.ano_n.le(12 if incluir_encerramento else 11))].copy()
    df=b.rename(columns=COLUNAS)
    for col in COLUNAS.values():
        df[col]=df[col]/1e6
    if df[list(COLUNAS.values())].isna().any().any():
        raise ValueError("Modelo não aceita ausências nas variáveis selecionadas.")
    idx,g=separar(df)
    anos=sorted(df.ano_n.unique())
    tr,va,te=[df.iloc[idx[k]] for k in ["treino","validacao","teste"]]
    candidatos={}
    modelos={}
    for nome in ["simples","multipla"]:
        x=desenho(tr,nome,anos)
        if np.linalg.matrix_rank(x.to_numpy()) < x.shape[1]:
            raise ValueError("Matriz de desenho sem posto completo.")
        mod=sm.OLS(tr.resultado_milhoes,x).fit(cov_type="cluster",cov_kwds={"groups":g.loc[tr.index]})
        modelos[nome]=mod
        candidatos[nome]=metricas(va.resultado_milhoes,mod.predict(desenho(va,nome,anos)))
    escolhido=min(candidatos,key=lambda n:candidatos[n]["RMSE_milhoes"])
    # Teste é aberto somente depois da escolha por validação. Não refaz ajuste no teste.
    mod=modelos[escolhido]
    xtr=desenho(tr,escolhido,anos)
    xte=desenho(te,escolhido,anos)
    p=mod.predict(xte)
    baseline_ano=tr.groupby("ano_n").resultado_milhoes.mean()
    baseline=te.ano_n.map(baseline_ano).fillna(tr.resultado_milhoes.mean())
    resid=tr.resultado_milhoes-mod.fittedvalues
    bp=het_breuschpagan(resid,xtr)
    vif={col:float(variance_inflation_factor(xtr.to_numpy(),i)) for i,col in enumerate(xtr.columns) if col!="const"}
    coefs=pd.DataFrame({"termo":mod.params.index,"coeficiente":mod.params.values,
                        "erro_padrao_cluster":mod.bse.values,"IC95_inferior":mod.conf_int().iloc[:,0].values,
                        "IC95_superior":mod.conf_int().iloc[:,1].values})
    diag=te[["ano_n"]].copy()
    diag["observado"]=te.resultado_milhoes
    diag["estimado"]=p
    diag["residuo"]=diag.observado-diag.estimado
    # Apenas estatísticas agregadas são exportadas: sem ID, linhas ou previsões individuais.
    por_ano=diag.groupby("ano_n")[["observado","estimado","residuo"]].mean().reset_index()
    # Correlação defasada dentro de cenário, nunca entre fim de um e início de outro.
    resid_tr=pd.DataFrame({"cenario":tr.cenario,"ano_n":tr.ano_n,"residuo":resid}).sort_values(["cenario","ano_n"])
    anterior=resid_tr.groupby("cenario").residuo.shift()
    lag=float(resid_tr.residuo.corr(anterior))
    bins=pd.qcut(pd.Series(mod.fittedvalues,index=tr.index),q=10,duplicates="drop")
    residuos_bins=pd.DataFrame({"ajustado":mod.fittedvalues,"residuo":resid,"faixa":bins}).groupby("faixa",observed=True)[["ajustado","residuo"]].agg(["mean","std","count"])
    hist_counts,hist_edges=np.histogram(diag.residuo,bins=20)
    saida={
        "pergunta":"Associação contemporânea de receita, custos e ano com resultado líquido em projeções simuladas.",
        "unidade":"milhões de R$ (convenção acadêmica)", "seed":SEED, "modelo":escolhido,
        "populacao":"trajetórias únicas" if unicas else "todos os cenários",
        "anos":[int(a) for a in anos],"linhas":len(df),"trajetorias":int(g.nunique()),
        "particoes":{k:{"linhas":len(v),"grupos":int(g.iloc[v].nunique()),
                       "sha_grupos":hashlib.sha256("\n".join(sorted(set(g.iloc[v]))).encode()).hexdigest()} for k,v in idx.items()},
        "intersecao_grupos":0, "validacao":candidatos,
        "teste":metricas(te.resultado_milhoes,p),"baseline_teste":metricas(te.resultado_milhoes,baseline),
        "R2_treino":float(mod.rsquared),"coeficientes":coefs.to_dict(orient="records"),
        "diagnostico":{"breusch_pagan_LM":float(bp[0]),"breusch_pagan_p_exploratorio":float(bp[1]),
                      "correlacao_residuo_defasado":lag,"VIF":vif,
                      "nota":"BP é exploratório: dependência em painel afeta sua calibração. IC agrupado por trajetória; nenhuma conclusão causal."},
        "medias_teste_ano":por_ano.to_dict(orient="records"),
        "histograma_residuos_teste":{"contagens":hist_counts.tolist(),"limites":hist_edges.tolist()},
        "residuos_treino_faixas":[{"ajustado_medio":float(row[("ajustado","mean")]),"residuo_medio":float(row[("residuo","mean")]),"n":int(row[("residuo","count")])} for _,row in residuos_bins.iterrows()],
        "qq_residuos_treino":{"probabilidades":np.linspace(.01,.99,49).tolist(),
                              "quantis":np.quantile(resid,np.linspace(.01,.99,49)).tolist()},
        "limites":["Associação contemporânea, não previsão de anos futuros.",
                   "Receita/custos são componentes parciais do resultado; associação contábil esperada não é descoberta causal.",
                   "Cenários simulados, repetição e dependência temporal limitam inferência externa.",
                   "Ano 12 é encerramento; análise principal exclui esse regime.",
                   "Modelos foram ajustados só no treino; escolha na validação; métricas finais no teste."]
    }
    return saida

def figuras(resultado, destino):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from scipy.stats import norm
    destino=Path(destino); destino.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({"font.size":10, "axes.spines.top":False, "axes.spines.right":False})
    fig,axs=plt.subplots(2,2,figsize=(11,7))
    anual=pd.DataFrame(resultado["medias_teste_ano"])
    axs[0,0].plot(anual.ano_n,anual.observado,label="Observado",marker="o")
    axs[0,0].plot(anual.ano_n,anual.estimado,label="Estimado",marker="s")
    axs[0,0].set(title="Médias por ano no teste",xlabel="Ano",ylabel="Resultado (R$ milhões)")
    axs[0,0].legend()
    rb=pd.DataFrame(resultado["residuos_treino_faixas"])
    axs[0,1].plot(rb.ajustado_medio,rb.residuo_medio,marker="o"); axs[0,1].axhline(0,c="gray")
    axs[0,1].set(title="Resíduo médio por faixa (treino)",xlabel="Ajustado médio (R$ milhões)",ylabel="Resíduo médio (R$ milhões)")
    h=resultado["histograma_residuos_teste"]
    axs[1,0].stairs(h["contagens"],h["limites"],fill=True)
    axs[1,0].set(title="Resíduos no teste",xlabel="Resíduo (R$ milhões)",ylabel="Frequência")
    qq=resultado["qq_residuos_treino"]
    axs[1,1].plot(norm.ppf(qq["probabilidades"]),qq["quantis"],marker=".",linestyle="")
    axs[1,1].set(title="Q-Q agregado de resíduos (treino)",xlabel="Quantis normais teóricos",ylabel="Quantis empíricos (R$ milhões)")
    fig.suptitle("Regressão associativa CTI | " + resultado["populacao"])
    fig.tight_layout()
    path=destino/"diagnosticos_regressao.png"
    fig.savefig(path,dpi=160); plt.close(fig)
    return path
