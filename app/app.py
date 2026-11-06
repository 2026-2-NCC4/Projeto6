"""Painel E2: CTI agregada por padrão; base completa local ou demo somente por configuração explícita.
Fonte de produção ausente ou inválida interrompe a aplicação, sem fallback fictício.
"""
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
from src.cti.sensibilidade import simular, meta_percentual
from src.cti.regressao import executar
from src.cti.distribuicao import CONTAS as CONTAS_DIST, percentis_anuais, proporcao_abaixo
from src.cti import agregados as ag
from src.cti.formatacao import numero, reais_mi, valor_kpi, parcela, data_hora
from src.cti.versao import commit_em_execucao

# Números dos gráficos no padrão brasileiro: vírgula decimal e ponto de milhar
LOCALE=alt.Locale(number=alt.NumberLocale(decimal=",",thousands=".",grouping=[3],currency=["R$ ",""]))

st.set_page_config(page_title="FinSight | Dados financeiros em perspectiva",page_icon="📊",layout="wide")
st.markdown("<style>.block-container{max-width:1350px;padding-top:2rem} div[data-testid='stMetric']{border:1px solid #94a3b8;border-radius:10px;padding:12px} div[data-testid='stMetricValue']{font-size:1.3rem}</style>",unsafe_allow_html=True)

@st.cache_data
def dados(caminho, assinatura):
    return carregar(caminho) if caminho else sintetica()

@st.cache_data
def ler_agregados(caminho, assinatura):
    return ag.ler(caminho)

@st.cache_data
def ler_regressao_publicada(caminho, assinatura):
    return ag.regressao_publicada(caminho)

@st.cache_data
def modelo(base, unicas):
    return executar(base, unicas=unicas)

def mostrar_regressao(res):
    st.write(f"Modelo selecionado na validação: **{res['modelo']}**. Teste com grupos independentes do treino.")
    st.dataframe(pd.DataFrame({"Modelo":res["teste"],"Referência por ano":res["baseline_teste"]}).T.map(lambda x:numero(x,4)),width="stretch")
    coefs=pd.DataFrame(res["coeficientes"])
    for col in coefs.columns:
        if col != "termo": coefs[col]=coefs[col].map(lambda x:numero(x,4))
    st.dataframe(coefs,hide_index=True,width="stretch")
    series=pd.DataFrame(res["medias_teste_ano"])[["ano_n","observado","estimado"]].melt("ano_n",var_name="Série",value_name="valor")
    st.altair_chart(alt.Chart(series).mark_line(point=True).encode(x=alt.X("ano_n:O",title="Ano"),y=alt.Y("valor:Q",title="Resultado (R$ milhões)",axis=alt.Axis(format=",.2f")),color="Série:N",tooltip=["ano_n:O","Série:N",alt.Tooltip("valor:Q",format=",.2f")]).configure(locale=LOCALE),width="stretch")
    st.json(res["diagnostico"],expanded=False)
    st.caption("Coeficientes monetários: variação no resultado em milhões por milhão da explicativa; ano compara com Ano 1, mantendo demais variáveis. IC agrupado por trajetória.")
    st.warning("Associação contemporânea entre projeções simuladas; não é previsão futura nem causalidade. Receita e custos integram parcialmente a identidade contábil.")
    st.caption("O resultado líquido reúne sete parcelas contábeis. O modelo usa apenas receita, custos e ano: o ajuste alto reflete parte dessa ligação e tendências comuns. O produto de taxas tributárias agregadas (cerca de 0,601 na base) é uma comparação descritiva; não demonstra o significado do coeficiente parcial de receita nem causalidade.")

def dinheiro(v):
    if v is None or pd.isna(v): return "Indisponível"
    v=round(float(v),2)+0.0  # evita "R$ -0,00" por resíduo de arredondamento
    return ("R$ {:,.2f}".format(v)).replace(",","X").replace(".",",").replace("X",".")

HIPOTESES={"desconto":0.0,"custo_delta":0.0,"volume":10000.0}

def resetar():
    """Volta às hipóteses padrão; a meta volta à margem de referência do ano e da população atuais."""
    st.session_state.update(HIPOTESES)
    st.session_state.pop("meta_contexto",None)

inicio=time.perf_counter()
caminho=os.environ.get("CTI_BASE_LOCAL","")
arquivo_agregados=Path(os.environ.get("CTI_AGREGADOS") or ROOT/ag.ARQUIVO)
modo="ficticio" if os.environ.get("CTI_DEMO")=="1" else "local" if caminho else "agregados"
base=agg=None
try:
    if modo=="agregados":
        agg=ler_agregados(str(arquivo_agregados),arquivo_agregados.stat().st_mtime_ns)
    else:
        assinatura=Path(caminho).stat().st_mtime_ns if caminho else 0
        base=dados(caminho,assinatura)
except (OSError,ValueError,TypeError,KeyError) as exc:
    st.error("Não foi possível carregar uma base válida. Confira o arquivo e o contrato de dados.")
    st.caption(type(exc).__name__)
    st.stop()
st.image(str(ROOT/"imagens/logo_finsight.png"),width=280)
st.title("FinSight")
st.caption("Dados financeiros em perspectiva")
st.caption("DevLeaders · PI CTI · Entrega 2")
if modo=="local":
    st.info("BASE CTI LOCAL · projeções simuladas da concessão. Acesso restrito a este ambiente; não publicar o arquivo.")
elif modo=="agregados" and agg["origem"].get("corresponde_referencia_E1") is True:
    st.info(f"BASE CTI AGREGADA · médias e percentis por ano das projeções simuladas da concessão, gerados pelo pipeline da E1 em {data_hora(agg['gerado_em_utc'])}. Nenhum cenário individual é publicado.")
elif modo=="agregados":
    st.warning("AGREGADOS SEM CONFERÊNCIA COM A BASE DA E1 · o arquivo não comprova a origem dos dados. Não representam resultados da CTI.")
else:
    st.warning("DEMONSTRAÇÃO FICTÍCIA · dados gerados do zero para demonstrar a aplicação. Não representam resultados da CTI.")
st.sidebar.header("Recorte da análise")
anos=st.sidebar.slider("Intervalo de anos",1,12,(1,11),key="anos")
unicas=st.sidebar.checkbox("Remover cópias de trajetórias",False,key="unicas")
populacao="sem_copias" if unicas else "todos"
if agg:
    recorte=None
    medias=ag.medias(agg,populacao,anos)
    n_cenarios=agg["populacoes"][populacao]["cenarios"]
else:
    recorte=filtrar(base,anos,unicas)
    medias=medias_anuais(recorte)
    n_cenarios=recorte.cenario.nunique()
if medias.empty:
    st.warning("Não há dados para esse recorte."); st.stop()
ano=st.sidebar.selectbox("Ano dos cartões e da simulação",list(medias.index),index=len(medias)-1,key="ano")
contas=medias.loc[ano]
if agg:
    st.sidebar.caption(f"{numero(n_cenarios,0)} cenários resumidos em médias e percentis por ano. Cartões: Ano {ano}.")
else:
    st.sidebar.caption(f"{numero(n_cenarios,0)} cenários · {numero(len(recorte),0)} linhas. Cartões: Ano {ano}.")
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
    pct=ag.percentis(agg,rotulos[nome_dist],populacao,anos) if agg else percentis_anuais(recorte,rotulos[nome_dist])
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
        if agg:
            prop=ag.proporcao_abaixo(agg,rotulos[nome_dist],populacao,limite*1e6,anos)
        else:
            prop=proporcao_abaixo(recorte,rotulos[nome_dist],limite*1e6).to_frame().assign(faixa="exata")
        prop["texto"]=[parcela(p,f) for p,f in zip(prop.proporcao,prop.faixa)]
        prop["valor_grafico"]=prop.proporcao.where(prop.faixa.ne("ate_1"),.01).where(prop.faixa.ne("acima_99"),.99)
        if ano in prop.index:
            st.metric(f"Cenários com {nome_dist.lower()} abaixo de R$ {numero(limite)} mi · Ano {ano}"+(" (aproximado)" if agg else ""),prop.loc[ano,"texto"])
        barras=alt.Chart(prop.rename_axis("ano").reset_index()).mark_bar(color="#176b87").encode(
            x=alt.X("ano:O",title="Ano",axis=alt.Axis(labelAngle=0)),y=alt.Y("valor_grafico:Q",title="Parcela dos cenários (limites nas caudas)",axis=alt.Axis(format=".0%"),scale=alt.Scale(domain=[0,1])),
            tooltip=[alt.Tooltip("ano:O",title="Ano"),alt.Tooltip("texto:N",title="Parcela")])
        st.altair_chart(barras.configure(locale=LOCALE),width="stretch")
        st.caption("Parcela dos cenários simulados de cada ano com valor abaixo do limite. Mede a frequência na simulação, não uma probabilidade observada.")
        if agg:
            st.caption("Modo agregado: a parcela é aproximada por interpolação entre os percentis P1 a P99 (erro em torno de 1 ponto percentual). Abaixo de P1 aparece como 1% ou menos; acima de P99, como 99% ou mais.")
            st.caption("Nas caudas, a barra representa o limite de 1% ou 99%, não uma estimativa de 0% ou 100%. Consulte o texto do indicador e do tooltip.")
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
    # Padrões entram pelo Session State, e os controles não recebem value=: assim o Restaurar não gera o
    # aviso de valor duplicado do Streamlit.
    for k,v in HIPOTESES.items(): st.session_state.setdefault(k,v)
    referencia_pct=(r+c)/r*100 if r>0 else 0.0
    if st.session_state.get("meta_contexto")!=(ano,populacao):
        # Novo ano ou nova população: a meta volta à margem de referência desse recorte.
        st.session_state["meta_pct"]=min(100.0,max(-200.0,float(referencia_pct)))
        st.session_state["meta_contexto"]=(ano,populacao)
    cols=st.columns(2)
    desconto=cols[0].slider("Desconto na receita (%)",0.0,100.0,key="desconto")/100
    delta=cols[1].slider("Variação dos custos (%)",-100.0,200.0,key="custo_delta")/100
    volume=cols[0].number_input("Quantidade hipotética de transações no ano",min_value=1.0,key="volume")
    alvo_pct=cols[1].number_input("Meta acadêmica de margem (% da receita original)",min_value=-200.0,max_value=100.0,key="meta_pct")
    try:
        meta=meta_percentual(r,c,alvo_pct/100)
        st.caption(f"Meta em valor: {dinheiro(meta)}. Referência original: {numero(referencia_pct)}%. O percentual é uma hipótese do exercício, aplicada à receita original; mantém a comparação após desconto. Ao trocar o ano ou a população, a meta volta à margem de referência.")
        resultado=simular(r,c,desconto,delta,volume,meta)
        a,b,d=st.columns(3)
        a.metric("Margem simulada",dinheiro(resultado["margem"]),dinheiro(resultado["variacao_margem"]))
        b.metric("Ticket simulado por transação",dinheiro(resultado["ticket_simulado"]))
        d.metric("Desvio da meta acadêmica",dinheiro(resultado["desvio_meta"]))
        comparacao=pd.DataFrame({"Medida":["Receita","Custos assinados","Margem após custos"],"Referência":[r,c,r+c],"Simulação":[resultado["receita"],resultado["custo"],resultado["margem"]]})
        for col in ["Referência","Simulação"]: comparacao[col]=comparacao[col].map(dinheiro)
        st.dataframe(comparacao,hide_index=True,width="stretch")
        st.caption("Ticket = receita simulada / quantidade hipotética. Meta e quantidade são entradas acadêmicas, não observações ou metas da CTI.")
    except ValueError as exc: st.warning(str(exc))
with regressao:
    st.subheader("Associação entre receita, custos e resultado")
    st.caption("Ajuste fixo nos Anos 1–11; o filtro anual da visão financeira não altera o desenho estatístico. A opção de trajetórias altera a população do modelo.")
    if agg:
        evidencias=ROOT/ag.EVIDENCIAS
        try:
            publicada=ler_regressao_publicada(str(evidencias),evidencias.stat().st_mtime_ns)
        except (OSError,ValueError) as exc:
            publicada=None
            st.info(f"Resultados publicados da regressão indisponíveis neste ambiente ({type(exc).__name__}).")
        if publicada:
            mostrar_regressao(publicada[populacao])
            st.caption(f"Resultados publicados em evidencias_e2.json: calculados com a base CTI local pelo pipeline executar_e2 em {data_hora(publicada['meta']['data_utc'])}. O modo agregado não recalcula o modelo, porque não tem as linhas da base.")
    else:
        if st.button("Calcular análise de regressão",key="rodar_modelo"):
            with st.spinner("Ajustando e avaliando por trajetórias..."):
                try:
                    res=modelo(base,unicas)
                    st.session_state["modelo_resultado"]=(modo,unicas,res)
                except (ValueError,RuntimeError) as exc: st.warning(str(exc))
        salvo=st.session_state.get("modelo_resultado")
        if salvo and salvo[:2]==(modo,unicas):
            mostrar_regressao(salvo[2])
        else: st.info("Calcule a análise para esta população. Métricas são geradas com os dados deste modo, nunca copiadas da base CTI para a demonstração.")
with metodologia:
    st.subheader("Fonte, fórmulas e limites")
    # Consulta o checkout atual em cada interação: cache poderia manter SHA antigo após sync do servidor.
    commit=commit_em_execucao(ROOT)
    if commit:
        st.caption(f"Commit do código em execução: {commit}")
        st.link_button("Consultar esta versão do código",f"https://github.com/2026-2-NCC4/Projeto6/tree/{commit}")
    else:
        st.caption("Commit do código em execução: indisponível neste ambiente. Não confundir com a versão da geração dos dados.")
    st.write("Modo: " + {"local":"CTI local, preparada pelo pipeline E1.",
                         "agregados":"agregados publicáveis da base CTI preparada pelo pipeline E1 (médias e percentis P1 a P99 por ano).",
                         "ficticio":"Gerador fictício independente, semente 2026."}[modo])
    if agg:
        origem=agg["origem"]
        st.write(f"Arquivo de agregados: versão {agg['schema']}, gerado em {data_hora(agg['gerado_em_utc'])} (horário de Brasília). "
                 f"SHA-256 da entrada CTI: {origem.get('entrada_sha256') or 'não informado'}. "
                 f"Corresponde à referência da E1: {'sim' if origem.get('corresponde_referencia_E1') is True else 'não comprovado'}.")
    st.write("Versão do contrato: e2-v1. Versão da entrega: E2, 06/11/2026. Calendário 2026 + Ano e R$ são convenções acadêmicas; os filtros usam Ano 1 a 12.")
    st.write("A base bruta é preservada. A preparação valida chaves e identidades; a entrada E2 confere os 12 anos por cenário e a marcação de trajetórias repetidas.")
    st.write("Contas são agregadas por média dentro de cada ano. Não somamos saldos patrimoniais ao longo dos anos. Dados ausentes permanecem indisponíveis.")
    st.write("Distribuição: percentis P5, P25, P50, P75 e P95 de cada indicador entre os cenários do recorte, ano a ano, e parcela dos cenários abaixo de um limite. São agregados; nenhum cenário individual é exibido. A distribuição aos acionistas é uma saída de caixa e aparece como valor pago.")
    st.write("Sensibilidade: R' = R × (1 − desconto); C' = C × (1 + variação); margem = R' + C'. Controles limitam desconto a 0–100% e custo a −100–200% para evitar custos com sinal invertido.")
    st.write("Fonte institucional: enunciado FINAL FECAP. Biblioteca financeira compartilhada com testes independentes contra a planilha E1.")
    st.link_button("Código e documentação","https://github.com/2026-2-NCC4/Projeto6")
    if modo=="local":
        st.caption("Não exportamos a base CTI nem linhas individuais. As tabelas e os gráficos exibem apenas agregados da população selecionada.")
    elif agg:
        st.caption("O arquivo publicado tem só médias e percentis por ano das contas usadas no painel: nenhuma linha, identificador, mínimo ou máximo de cenário. A exportação abaixo traz os KPIs calculados dessas médias.")
        st.download_button("Exportar KPIs agregados (CSV)",tabela(medias).to_csv(index=False).encode("utf-8-sig"),"kpis_agregados_cti.csv","text/csv")
    else:
        st.download_button("Exportar KPIs fictícios (CSV)",tabela(medias).to_csv(index=False).encode("utf-8-sig"),"kpis_ficticios.csv","text/csv")
st.caption(f"Processamento desta interação: {time.perf_counter()-inicio:.2f} s · Valores são projeções/simulações, não resultados realizados.")
