"""Painel E2: modo público fictício por padrão; base CTI somente por configuração local."""
from pathlib import Path
import sys
import os
import time
import json
import altair as alt
import pandas as pd
import streamlit as st

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from src.cti.dados import carregar, sintetica
from src.cti.recortes import filtrar, medias_anuais
from src.cti.indicadores import calcular, tabela
from src.cti.sensibilidade import simular
from src.cti.regressao import executar
from src.cti.distribuicao import CONTAS as CONTAS_DIST, percentis_anuais, proporcao_abaixo
from src.cti.formatacao import numero, reais_mi, valor_kpi

# Números dos gráficos no padrão brasileiro: vírgula decimal e ponto de milhar
LOCALE=alt.Locale(number=alt.NumberLocale(decimal=",",thousands=".",grouping=[3],currency=["R$ ",""]))

st.set_page_config(page_title="CTI | Planejamento financeiro",page_icon="📊",layout="wide")
st.markdown("<style>.block-container{max-width:1350px;padding-top:2rem} div[data-testid='stMetric']{border:1px solid #94a3b8;border-radius:10px;padding:12px} div[data-testid='stMetricValue']{font-size:1.3rem}</style>",unsafe_allow_html=True)

@st.cache_data
def dados(caminho, assinatura):
    return carregar(caminho) if caminho else sintetica()

@st.cache_data
def modelo(base, unicas):
    return executar(base, unicas=unicas)

def dinheiro(v):
    if v is None or pd.isna(v): return "Indisponível"
    return ("R$ {:,.2f}".format(v)).replace(",","X").replace(".",",").replace("X",".")

def resetar():
    for k,v in {"desconto":0.0,"custo_delta":0.0,"volume":10000.0,"meta":0.0}.items():
        st.session_state[k]=v

inicio=time.perf_counter()
caminho=os.environ.get("CTI_BASE_LOCAL","")
privado=bool(caminho)
try:
    assinatura=Path(caminho).stat().st_mtime_ns if caminho else 0
    base=dados(caminho,assinatura)
except (OSError,ValueError,TypeError) as exc:
    st.error("Não foi possível carregar uma base válida. Confira o arquivo e o contrato de dados.")
    st.caption(type(exc).__name__)
    st.stop()
st.title("Planejamento financeiro")
st.caption("DevLeaders · PI CTI · Entrega 2")
if privado:
    st.info("BASE CTI LOCAL · projeções simuladas da concessão. Acesso restrito a este ambiente; não publicar o arquivo.")
else:
    st.warning("DEMONSTRAÇÃO FICTÍCIA · dados gerados do zero para demonstrar a aplicação. Não representam resultados da CTI.")
st.sidebar.header("Recorte da análise")
anos=st.sidebar.slider("Intervalo de anos",1,12,(1,11),key="anos")
unicas=st.sidebar.checkbox("Remover cópias de trajetórias",False,key="unicas")
recorte=filtrar(base,anos,unicas)
medias=medias_anuais(recorte)
if medias.empty:
    st.warning("Não há dados para esse recorte."); st.stop()
ano=st.sidebar.selectbox("Ano dos cartões e da simulação",list(medias.index),index=len(medias)-1,key="ano")
contas=medias.loc[ano]
st.sidebar.caption(f"{numero(recorte.cenario.nunique(),0)} cenários · {numero(len(recorte),0)} linhas. Cartões: Ano {ano}.")
if ano == 12: st.warning("Ano 12: encerramento. Contas ausentes e indicadores patrimoniais indisponíveis são preservados.")
st.caption("Média de cada conta entre cenários por ano; razões calculadas depois das médias. Cenários alternativos não são somados.")
overview,distribuicao,financeiro,sensibilidade,regressao,metodologia=st.tabs(["Visão geral","Distribuição","Financeiro","Sensibilidade","Regressão","Metodologia"])

with overview:
    r=float(contas["DRE - Receita"]); c=float(contas["DRE - Custos"])
    indicadores=[("Receita",r),("Custos",-c),("Margem",r+c),
                 ("Resultado líquido",contas["DRE - Resultado Líquido"]),
                 ("Geração de caixa",contas["FLU - Geração de Caixa"])]
    for inicio_linha in (0,3):
        linha=indicadores[inicio_linha:inicio_linha+3]
        for col,(nome,v) in zip(st.columns(len(linha)),linha):
            col.metric(nome,reais_mi(v))
    st.caption("Cartões em milhões de reais. Custos têm o sinal invertido para apresentação; margem = receita + custo assinado. Valores completos na tabela abaixo.")
    st.subheader("Evolução anual da população selecionada")
    series={"DRE - Receita":"Receita","DRE - Resultado Líquido":"Resultado líquido","FLU - Geração de Caixa":"Geração de caixa"}
    evolucao=(medias[list(series)].rename(columns=series).div(1e6).rename_axis("ano").reset_index()
              .melt("ano",var_name="Indicador",value_name="valor"))
    grafico=alt.Chart(evolucao).mark_line(point=True).encode(
        x=alt.X("ano:O",title="Ano",axis=alt.Axis(labelAngle=0)),
        y=alt.Y("valor:Q",title="R$ milhões (média entre cenários)",axis=alt.Axis(format=",.0f")),
        color=alt.Color("Indicador:N",title=None,legend=alt.Legend(orient="bottom")),
        tooltip=[alt.Tooltip("ano:O",title="Ano"),"Indicador:N",alt.Tooltip("valor:Q",title="R$ milhões",format=",.2f")])
    st.altair_chart(grafico.configure(locale=LOCALE),width="stretch")
    st.caption("Margem após custos exclui tributos e demais despesas; não equivale a lucro líquido.")
    st.dataframe(pd.DataFrame({"Ano":[int(a) for a in medias.index],
                               **{nome:[reais_mi(v) for v in medias[conta]] for conta,nome in
                                  {"DRE - Receita":"Receita","DRE - Custos":"Custos (assinado)",
                                   "DRE - Resultado Líquido":"Resultado líquido","FLU - Geração de Caixa":"Geração de caixa"}.items()}}),
                 width="stretch",hide_index=True)
with distribuicao:
    st.subheader("Distribuição entre os cenários")
    st.caption("Os cenários são futuros alternativos simulados para a mesma concessão. A faixa mostra como eles se espalham em cada ano; não é intervalo de confiança nem probabilidade real.")
    rotulos={v[0]:k for k,v in CONTAS_DIST.items()}
    nome_dist=st.selectbox("Indicador",list(rotulos),index=list(rotulos).index("Geração de caixa"),key="conta_dist")
    pct=percentis_anuais(recorte,rotulos[nome_dist])
    if pct.empty:
        st.warning("Não há valores desse indicador no recorte.")
    else:
        faixa=pct.copy()
        colunas_mi=["P5","P25","P50","P75","P95","media"]
        faixa[colunas_mi]=faixa[colunas_mi]/1e6
        faixa=faixa.rename_axis("ano").reset_index()
        base_graf=alt.Chart(faixa).encode(x=alt.X("ano:O",title="Ano",axis=alt.Axis(labelAngle=0)))
        eixo_y=alt.Axis(format=",.0f")
        grafico=alt.layer(
            base_graf.mark_area(opacity=.18,color="#176b87").encode(y=alt.Y("P5:Q",title="R$ milhões",axis=eixo_y),y2="P95:Q"),
            base_graf.mark_area(opacity=.38,color="#176b87").encode(y="P25:Q",y2="P75:Q"),
            base_graf.mark_line(point=True,color="#0b3c49").encode(y="P50:Q",
                tooltip=[alt.Tooltip("ano:O",title="Ano"),
                         *[alt.Tooltip(f"{q}:Q",title=f"{q} (R$ mi)",format=",.2f") for q in ["P5","P25","P50","P75","P95"]],
                         alt.Tooltip("media:Q",title="Média (R$ mi)",format=",.2f"),alt.Tooltip("n:Q",title="Cenários")]),
            base_graf.mark_line(strokeDash=[5,4],color="#b45309").encode(y="media:Q"))
        st.altair_chart(grafico.configure(locale=LOCALE),width="stretch")
        st.caption("Faixa clara: 90% centrais dos cenários (P5 a P95). Faixa escura: 50% centrais (P25 a P75). Linha contínua: mediana. Linha tracejada: média, a mesma usada nos cartões.")
        if ano in pct.index:
            linha_ano=pct.loc[ano]
            st.dataframe(pd.DataFrame({"Medida":["P5","P25","Mediana (P50)","P75","P95","Média","Cenários"],
                                       f"Ano {ano}":[*[reais_mi(linha_ano[q]) for q in ["P5","P25","P50","P75","P95","media"]],numero(linha_ano["n"],0)]}),
                         hide_index=True,width="stretch")
        st.markdown("**Risco: cenários abaixo de um limite**")
        limite=st.number_input("Limite (R$ milhões)",value=0.0,step=100.0,key="limite_dist")
        prop=proporcao_abaixo(recorte,rotulos[nome_dist],limite*1e6)
        if ano in prop.index:
            st.metric(f"Cenários com {nome_dist.lower()} abaixo de R$ {numero(limite)} mi · Ano {ano}",f"{numero(prop.loc[ano]*100,1)}%")
        barras=alt.Chart(prop.rename_axis("ano").reset_index()).mark_bar(color="#176b87").encode(
            x=alt.X("ano:O",title="Ano",axis=alt.Axis(labelAngle=0)),y=alt.Y("proporcao:Q",title="Parcela dos cenários",axis=alt.Axis(format=".0%"),scale=alt.Scale(domain=[0,1])),
            tooltip=[alt.Tooltip("ano:O",title="Ano"),alt.Tooltip("proporcao:Q",title="Parcela",format=".1%")])
        st.altair_chart(barras.configure(locale=LOCALE),width="stretch")
        st.caption("Parcela dos cenários simulados de cada ano com valor abaixo do limite. Mede a frequência na simulação, não uma probabilidade observada.")
with financeiro:
    st.subheader(f"Indicadores · Ano {ano}")
    st.caption("Mesmas regras da planilha E1. Premissas: CAC R$ 4.000, LTV R$ 45.000, custo do capital próprio 10% a.a.")
    tab=pd.DataFrame([{"Indicador":k.nome,"Valor":valor_kpi(k.valor,k.unidade,k.estado),"Unidade":k.unidade,
                       "Fórmula":k.formula,"Situação":k.estado} for k in calcular(contas)])
    st.dataframe(tab,width="stretch",hide_index=True)
    st.info("PC com sinal não negativo permanece pendente. Estoques, PL e ELP ausentes não são tratados como zero. EBITDA fornecido não foi reconciliado.")
    st.caption("Ticket e metas acadêmicas estão na aba Sensibilidade. MVA indisponível sem valor de mercado; custos variáveis são hipótese simplificada.")
with sensibilidade:
    st.subheader("Desconto, custo e meta")
    st.caption(f"Referência: Ano {ano}, mesma população dos cartões. Volume e demais contas constantes. Não recalcula tributos, EBITDA ou lucro líquido.")
    st.button("Restaurar hipóteses",on_click=resetar)
    cols=st.columns(2)
    desconto=cols[0].slider("Desconto na receita (%)",0.0,100.0,0.0,key="desconto")/100
    delta=cols[1].slider("Variação dos custos (%)",-100.0,200.0,0.0,key="custo_delta")/100
    volume=cols[0].number_input("Quantidade hipotética de transações no ano",min_value=1.0,value=10000.0,key="volume")
    meta=cols[1].number_input("Meta acadêmica de margem após custos (R$)",value=0.0,key="meta")
    try:
        resultado=simular(r,c,desconto,delta,volume,meta)
        a,b,d=st.columns(3)
        a.metric("Margem simulada",dinheiro(resultado["margem"]),dinheiro(resultado["variacao_margem"]))
        b.metric("Ticket simulado por transação",dinheiro(resultado["ticket_simulado"]))
        d.metric("Desvio da meta acadêmica",dinheiro(resultado["desvio_meta"]))
        st.dataframe(pd.DataFrame({"Medida":["Receita","Custos assinados","Margem após custos"],"Referência":[r,c,r+c],"Simulação":[resultado["receita"],resultado["custo"],resultado["margem"]]}),hide_index=True,width="stretch")
        st.caption("Ticket = receita simulada / quantidade hipotética. Meta e quantidade são entradas acadêmicas, não observações ou metas da CTI.")
    except ValueError as exc: st.warning(str(exc))
with regressao:
    st.subheader("Associação entre receita, custos e resultado")
    st.caption("Ajuste fixo nos Anos 1–11; o filtro anual da visão financeira não altera o desenho estatístico. A opção de trajetórias altera a população do modelo.")
    if st.button("Calcular análise de regressão",key="rodar_modelo"):
        with st.spinner("Ajustando e avaliando por trajetórias..."):
            try:
                res=modelo(base,unicas)
                st.session_state["modelo_resultado"]=(privado,unicas,res)
            except (ValueError,RuntimeError) as exc: st.warning(str(exc))
    salvo=st.session_state.get("modelo_resultado")
    if salvo and salvo[:2]==(privado,unicas):
        res=salvo[2]
        st.write(f"Modelo selecionado na validação: **{res['modelo']}**. Teste com grupos independentes do treino.")
        st.dataframe(pd.DataFrame({"Modelo":res["teste"],"Referência por ano":res["baseline_teste"]}).T,width="stretch")
        st.dataframe(pd.DataFrame(res["coeficientes"]),hide_index=True,width="stretch")
        st.line_chart(pd.DataFrame(res["medias_teste_ano"]).set_index("ano_n")[["observado","estimado"]])
        st.json(res["diagnostico"],expanded=False)
        st.caption("Coeficientes monetários: variação no resultado em milhões por milhão da explicativa; ano compara com Ano 1, mantendo demais variáveis. IC agrupado por trajetória.")
        st.warning("Associação contemporânea entre projeções simuladas; não é previsão futura nem causalidade. Receita e custos integram parcialmente a identidade contábil.")
    else: st.info("Calcule a análise para esta população. Métricas são geradas com os dados deste modo, nunca copiadas da base CTI para a demonstração.")
with metodologia:
    st.subheader("Fonte, fórmulas e limites")
    st.write("Modo: " + ("CTI local, preparada pelo pipeline E1." if privado else "Gerador fictício independente, semente 2026."))
    st.write("Versão do contrato: e2-v1. Versão da entrega: E2, 05/11/2026. Calendário 2026 + Ano e R$ são convenções acadêmicas; os filtros usam Ano 1 a 12.")
    st.write("A base bruta é preservada. A preparação valida chaves e identidades; a entrada E2 confere os 12 anos por cenário e a marcação de trajetórias repetidas.")
    st.write("Contas são agregadas por média dentro de cada ano. Não somamos saldos patrimoniais ao longo dos anos. Dados ausentes permanecem indisponíveis.")
    st.write("Distribuição: percentis P5, P25, P50, P75 e P95 de cada indicador entre os cenários do recorte, ano a ano, e parcela dos cenários abaixo de um limite. São agregados; nenhum cenário individual é exibido. A distribuição aos acionistas é uma saída de caixa e aparece como valor pago.")
    st.write("Sensibilidade: R' = R × (1 − desconto); C' = C × (1 + variação); margem = R' + C'. Controles limitam desconto a 0–100% e custo a −100–200% para evitar custos com sinal invertido.")
    st.write("Fonte institucional: enunciado FINAL FECAP. Biblioteca financeira compartilhada com testes independentes contra a planilha E1.")
    st.link_button("Código e documentação","https://github.com/2026-2-NCC4/Projeto6")
    if privado:
        st.caption("Não exportamos a base CTI nem linhas individuais. As tabelas e os gráficos exibem apenas agregados da população selecionada.")
    else:
        st.download_button("Exportar KPIs fictícios (CSV)",tabela(medias).to_csv(index=False).encode("utf-8-sig"),"kpis_ficticios.csv","text/csv")
st.caption(f"Processamento desta interação: {time.perf_counter()-inicio:.2f} s · Valores são projeções/simulações, não resultados realizados.")
