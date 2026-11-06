"""Gera relatórios acadêmicos E2 com evidências agregadas da execução local."""
from pathlib import Path
import json
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"documentos/Entrega 2"
R=json.loads((BASE/"Projeto Interdisciplinar Ciência de Dados/evidencias_e2.json").read_text(encoding="utf-8"))
REG=R["regressao"]
from src.cti.regressao import figuras
FIGURA=figuras(REG,ROOT/"src/data/processed/e2_documentos")
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name="BodyPT",fontName="Helvetica",fontSize=10.3,leading=15,spaceAfter=9,textColor=colors.HexColor("#263746")))
styles.add(ParagraphStyle(name="SmallPT",fontName="Helvetica",fontSize=8.2,leading=11,spaceAfter=5))
styles["Title"].fontSize=25; styles["Title"].leading=30; styles["Title"].textColor=colors.HexColor("#123550")
styles["Heading1"].fontSize=17; styles["Heading1"].leading=22; styles["Heading1"].spaceAfter=13
styles["Heading2"].fontSize=12; styles["Heading2"].leading=16
def p(t,style="BodyPT"): return Paragraph(escape(str(t)).replace("\n","<br/>"),styles[style])
def h(t): return p(t,"Heading1")
def table(rows,widths=None):
    data=[[p(v,"SmallPT") for v in row] for row in rows]
    t=Table(data,colWidths=widths,repeatRows=1,hAlign="LEFT")
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#e5eff4")),
        ("VALIGN",(0,0),(-1,-1),"TOP"),("LINEBELOW",(0,0),(-1,0),.8,colors.HexColor("#176b87")),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#f7f9fb")]),
        ("LEFTPADDING",(0,0),(-1,-1),7),("RIGHTPADDING",(0,0),(-1,-1),7),
        ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7)]))
    return t
def capa(disciplina,professor,subtitulo):
    return [p("FECAP | Ciência da Computação | 2026/2","SmallPT"),Spacer(1,26),
            p("FinSight","Title"),p("Dados financeiros em perspectiva"),
            Spacer(1,12),h(disciplina),p(subtitulo),
            table([["Identificação","Entrega 2"],["Grupo","6 - DevLeaders"],
                   ["Integrantes","Gustavo Pires; Lúcio Vecchio; Luiz Henrique Zaim da Cruz; Eric Aloise"],
                   ["Orientação",professor],["Data de referência","06/11/2026"],
                   ["Código testado (referência)",R["commit_implementacao"][:12]],
                   ["Repositório","github.com/2026-2-NCC4/Projeto6"]],[105,385]),Spacer(1,18)]
def rodape(canvas,doc):
    canvas.setStrokeColor(colors.HexColor("#b8ccd8")); canvas.line(42,42,553,42)
    canvas.setFont("Helvetica",8);canvas.setFillColor(colors.HexColor("#456071"))
    canvas.drawString(42,29,"FinSight | DevLeaders | PI CTI | Entrega 2");canvas.drawRightString(553,29,str(doc.page))
def salvar(pasta,nome,story):
    path=BASE/pasta/nome
    SimpleDocTemplate(str(path),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=42,bottomMargin=56,
                      title=nome.replace("_"," "),author="DevLeaders").build(story,onFirstPage=rodape,onLaterPages=rodape)
    print(path)
def br(): return PageBreak()
def num(x): return f"{x:,.4f}".replace(",","X").replace(".",",").replace("X",".")

def UML(tipo):
    """A figura é renderizada da fonte .puml versionada, sem desenho manual paralelo."""
    arquivo=BASE/"ES e ML"/(tipo+".png")
    w,h=ImageReader(str(arquivo)).getSize()
    escala=min(490/w,475/h)
    return Image(str(arquivo),width=w*escala,height=h*escala)

def tela(nome):
    arquivo=ROOT/"imagens/e2"/(nome+".png")
    w,h=ImageReader(str(arquivo)).getSize()
    return Image(str(arquivo),width=490,height=490*h/w)

PUBLICACAO=R.get("publicacao",{})
URL=PUBLICACAO.get("url")
STATUS_NUVEM=("URL: "+URL+". "+PUBLICACAO.get("descricao","")) if URL else "Publicação externa pendente de autenticação GitHub/Streamlit. Nenhuma URL validada. A execução local não atende sozinha a RF14."
N_TESTES=R["testes"]["tests"]

# Inferencial
s=capa("Análise Inferencial de Dados","Rodnil da Silva Moreira Lisboa","Regressão associativa, validação por trajetórias e diagnóstico")
s += [h("1. Problema e desenho"),p(REG["pergunta"]),
      p("Fonte CTI v3: 1.002.000 linhas brutas, 1.200 cenários e 12 anos. A preparação E1 preserva a origem e gera 14.400 linhas por cenário/ano. A análise principal utiliza os Anos 1-11: 13.200 linhas e 1.107 trajetórias distintas."),
      p("Receita e custos são componentes parciais do resultado. O objetivo é descrever associação condicionada ao ano, sem reconstruir todas as parcelas da identidade contábil. Não se trata de previsão futura nem de estimativa causal."),
      p("Valores modelados em milhões de R$, convenção acadêmica. Ano 12 é encerramento e fica numa análise de sensibilidade. Saídas e figuras são agregadas, sem identificadores ou previsões individuais."),br(),
      h("2. Particionamento e escolha")]
rows=[["Conjunto","Linhas","Trajetórias"]]+[[k,v["linhas"],v["grupos"]] for k,v in REG["particoes"].items()]
s += [table(rows,[170,160,160]),Spacer(1,14),
      p("GroupShuffleSplit, semente 20261105: aproximadamente 60/20/20 dos grupos. Todos os anos do cenário e todos os cenários com trajetória idêntica ficam no mesmo grupo. A interseção entre grupos de treino, validação e teste foi zero."),
      p("Modelo simples: intercepto e receita. Modelo múltiplo: intercepto, receita, custos assinados e dez indicadores de ano, com Ano 1 como referência. OLS ajustado somente no treino. Seleção pelo menor RMSE na validação; o teste não escolhe parâmetros. Covariância agrupada por trajetória."),
      table([["Validação","MAE (milhões)","RMSE (milhões)","R²"]]+[[k,num(v["MAE_milhoes"]),num(v["RMSE_milhoes"]),num(v["R2"])] for k,v in REG["validacao"].items()],[130,120,120,120]),
      Spacer(1,14),h("3. Resultado no teste"),
      table([["Método","MAE (milhões)","RMSE (milhões)","R²"],
             ["Múltiplo",num(REG["teste"]["MAE_milhoes"]),num(REG["teste"]["RMSE_milhoes"]),num(REG["teste"]["R2"])],
             ["Média por ano no treino",num(REG["baseline_teste"]["MAE_milhoes"]),num(REG["baseline_teste"]["RMSE_milhoes"]),num(REG["baseline_teste"]["R2"])]],[130,120,120,120]),
      p("O modelo reduz o RMSE em aproximadamente 59,8% frente à referência por ano. O R² elevado de ambos também reflete as tendências anuais comuns; não prova capacidade de prever anos ou operações não observados."),br(),
      h("4. Coeficientes e interpretação")]
s += [table([["Termo","Coeficiente","IC 95% inferior","IC 95% superior"]]+[[c["termo"],num(c["coeficiente"]),num(c["IC95_inferior"]),num(c["IC95_superior"])] for c in REG["coeficientes"]],[148,110,116,116]),Spacer(1,12),
      p("Receita: mantendo ano e custo constantes, mais R$ 1 milhão associa-se a cerca de R$ 0,593 milhão de resultado. O custo é assinado: aumentar a despesa em módulo reduz seu regressor. Seu IC inclui zero; isso não significa ausência de importância econômica, pois há forte colinearidade e condicionamento."),
      p("Os coeficientes de ano são diferenças em relação ao Ano 1. O intercepto não tem interpretação econômica isolada fora do domínio observado. Os intervalos agrupados não resolvem possível dependência entre cenários de um mesmo simulador."),br(),
      p("Auditoria contábil: resultado líquido = receita + tributos + custos + depreciação/amortização + resultado financeiro + outros resultados operacionais + IR/CSLL. Resíduo máximo na base: cerca de R$0,0000505, arredondado a zero. O modelo usa só parte dessas parcelas."),
      p("Taxas agregadas de tributos e IR/CSLL: aproximadamente 8,45% e 34,37%. O produto (1-t)(1-ir) = 0,6008 é comparação descritiva, não demonstra que o coeficiente parcial 0,5929 seja repasse tributário. Taxas variáveis, variáveis omitidas e controles de ano impedem essa conclusão. O intervalo do custo inclui zero; omissão de parcelas é hipótese a investigar, não explicação comprovada."),
      h("5. Diagnósticos e limitações"),
      Image(str(FIGURA),width=490,height=312),
      p(f"Breusch-Pagan exploratório: LM {num(REG['diagnostico']['breusch_pagan_LM'])}; p = {REG['diagnostico']['breusch_pagan_p_exploratorio']:.3g}. A dependência em painel limita a calibração desse p-valor. Correlação defasada dos resíduos dentro de cenário: {num(REG['diagnostico']['correlacao_residuo_defasado'])}."),
      p(f"VIF: receita {num(REG['diagnostico']['VIF']['receita_milhoes'])}; custos {num(REG['diagnostico']['VIF']['custos_milhoes'])}; máximo entre regressores {max(REG['diagnostico']['VIF'].values()):.2f}. Colinearidade alta e dependência temporal tornam inadequada uma interpretação causal dos coeficientes."),
      p("As figuras revelam padrões de resíduos; não se pressupõe normalidade ou homocedasticidade. Médias por faixa e por ano podem ocultar extremos individuais. Os quantis Q-Q são agregados. Erros-padrão agrupados são usados no lugar dos iid."),br(),
      h("6. Sensibilidade e reprodutibilidade")]
s += [table([["Recorte","RMSE de teste (milhões)","R² de teste"]]+[[label,num(R[key]["teste"]["RMSE_milhoes"]),num(R[key]["teste"]["R2"])] for label,key in [("Anos 1-11","regressao"),("Sem cópias","sensibilidade_sem_copias"),("Inclui Ano 12","sensibilidade_com_encerramento")]],[200,165,125]),
      Spacer(1,12),p("As 93 cópias excedentes estão no grupo destinado à validação nesta semente. Retirá-las não altera treino nem teste, e o múltiplo segue escolhido; por isso as métricas finais são idênticas. Não generalizar essa igualdade a outras divisões."),
      p("Ao incluir Ano 12, o erro absoluto aumenta. Seu R² maior não implica melhoria: há outra escala de variabilidade e outro regime. Manter a análise principal em 1-11 evita misturar encerramento com operação."),
      p("Notebook E2_Regressao_CTI.ipynb: seis células de código executadas integralmente em kernel local limpo, sem erros. Não foi executado no Google Colab nesta etapa. O formato também é utilizável em Jupyter/Colab após instalar dependências e disponibilizar dados autorizados."),
      p("Reprodução: python -m src.cti.executar_e2 --csv <cópia autorizada>. Saídas em src/data/processed/e2, fora do Git. SHA-256 da origem: "+R["qualidade"]["entrada_sha256"]),
      p("Ambiente: "+json.dumps(R["ambiente"],ensure_ascii=False)),
      p("Referências: enunciado FINAL FECAP; src/prepara.py e planilha E1; scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupShuffleSplit.html; statsmodels.org/stable/regression.html. Código e evidências agregadas estão nas pastas da E2.") ]
salvar("Análise Inferencial de Dados","E2_Analise_Inferencial_CTI.pdf",s)

# Finanças
s=capa("Contabilidade e Finanças","Orientadores do PI: Eduardo Savino, Luis Pires, Mauricio Lopes e Rodnil da Silva","Painel operacional, regras de cálculo e sensibilidade")
s += [h("1. Decisões apoiadas"),p("O painel integra receita, custos, margem após custos, resultado líquido e geração de caixa. As abas Financeiro e Sensibilidade oferecem os indicadores E1, ticket hipotético, meta acadêmica, evolução anual e comparação entre referência e simulação."),
      p("Os cenários são alternativas da mesma concessão. Para cada ano, calculamos a média de cada conta e depois o indicador. Não somamos faturamento entre cenários nem saldos patrimoniais entre anos. O padrão mantém todos os 1.200 cenários; a opção sem cópias retém 1.107 trajetórias."),
      p("A versão de produção utiliza médias e percentis reais da CTI, conferidos com a base preparada E1. O arquivo completo permanece local. O painel identifica a fonte e oferece a comparação de 1.200 cenários com 1.107 trajetórias únicas."),br(),
      h("2. Dicionário operacional")]
from src.cti.indicadores import calcular
s += [table([["KPI","Unidade","Regra"]]+[[k.nome,k.unidade,k.formula] for k in calcular({})],[160,65,265]),
      Spacer(1,10),p("Fonte das contas: CTI v3 e dicionário E1; periodicidade anual; dimensão: ano e população de trajetórias. Custos variáveis e margem de contribuição seguem a premissa simplificada da E1; não há separação observada entre fixos e variáveis."),br(),
      h("3. Novos indicadores e controles")]
s += [table([["Indicador","Fórmula / interpretação","Validação"],
             ["Ticket simulado","Receita simulada / quantidade hipotética anual; R$/transação","Quantidade finita e positiva; não inventar transações observadas."],
             ["Meta acadêmica","Percentual acadêmico da receita original, convertido em R$; padrão igual à margem original","Desvio = margem simulada - percentual × receita original; não é orçamento CTI."],
             ["Resultado líquido","DRE - Resultado Líquido","Conta da base, sem substituir por margem parcial."],
             ["Geração de caixa","FLU - Geração de Caixa","Conta anual; não equivale a EBITDA."],
             ["MVA","Indisponível","Falta valor de mercado; não atribuir zero."]],[115,220,155]),
      Spacer(1,15),p("Denominador zero ou conta ausente deixa o indicador indisponível. PC não negativo mantém os indicadores dependentes pendentes. Ano 12 preserva ausência de estoques, PL e ELP. EBITDA é fornecido, sem memória de cálculo reconciliada. EVA simplificado é hipótese sobre capital próprio, não cálculo completo de EVA econômico."),
      h("4. Sensibilidade implementada"),
      p("Com receita R e custo assinado C: R_sim = R × (1 - desconto); C_sim = C × (1 + variação); margem = R_sim + C_sim. Mantém volume e demais contas constantes. Não recalcula tributos, EBITDA ou resultado líquido."),
      p("Desconto permitido: 0-100%; variação de custo: -100% a +200%. São limites do exercício, não elasticidades estimadas. Parâmetros nulos reproduzem a referência. Restaurar hipóteses e trocar ano/população devolvem a meta à margem do recorte. Receita simulada zero torna a margem percentual indisponível."),
      p("Exemplo de teste fictício: R=100, C=-60, desconto=10%, custo=+20%, quantidade=10, meta=20. Receita=90, custo=-72, margem=18, ticket=9, desvio da meta=-2. Valores servem à validação da regra, sem relação com CTI."),br(),
      h("5. Validação e uso")]
s += [table([["Verificação atual","Resultado"],["KPIs numéricos vs. planilha E1","161 conferidos"],["Indisponibilidades / pendências","55 estados coerentes"],["Total de KPIs","216/216, sem divergência"],["Identidades por ano","24/24"],["Entradas da planilha","165 valores numéricos + 3 ausências conferidos"],["Teste negativo","Receita alterada em 10% detectada; validação reprovou como esperado"]],[230,260]),
      Spacer(1,15),p("A referência independente é a planilha avaliada da E1, preservada. Comparação dos valores salvos após recálculo histórico, com tolerância de KPI relativa 1e-6 e absoluta R$0,01. As identidades devem ter resíduo inferior a R$1. Esta etapa não afirma um novo recálculo do Excel."),
      p("Testes sintéticos também cobrem fórmulas com valores esperados calculados manualmente, receita zero, sinal de PC, conta ausente, quantidade zero, limites dos controles e restauração da referência. Fórmulas são compartilhadas pelo painel e pela rotina de validação; os relatórios documentam as mesmas regras."),
      p("Uso: escolher anos e política de repetição; escolher o ano dos cartões; consultar evolução; ajustar somente as hipóteses acadêmicas em Sensibilidade; ler estados na tabela Financeiro. Download de KPIs agregados reais disponível na produção; demo fictícia exige CTI_DEMO=1."),
      p("Referências: dicionário e planilha de Contabilidade e Finanças E1; enunciado FINAL FECAP, seções 5.4, 10 e 11. Implementação: src/cti/indicadores.py, recortes.py e sensibilidade.py; teste independente: src/cti/executar_e2.py.") ]
salvar("Contabilidade e Finanças","E2_Painel_Financeiro_CTI.pdf",s)

# Engenharia
s=capa("Engenharia de Software e Arquitetura de Sistemas","Luis Pires","Design de software e UML aplicados ao produto")
s += [h("1. Arquitetura implementada"),p("Arquitetura modular em Python: a interface Streamlit coordena serviços de domínio; preparação e validação isolam os dados; cálculos financeiros e regressão são reutilizáveis por CLI, notebook e painel. O sistema não exige banco nem API próprios para o volume atual."),
      p("Entradas: CSV CTI autorizado ou Parquet preparado; gerador fictício independente para demonstração; filtros de ano e repetição; hipóteses de desconto, custo, volume e meta. Processamento: validação, recorte, médias anuais, KPIs, simulação e ajuste por trajetórias. Saídas: tabelas, gráficos, indicadores com estado, PDF, evidências e CSV de indicadores agregados reais."),
      p("Decisões: reaproveitar prepara.py evita divergência com E1; funções puras separam regra e apresentação; Parquet reduz custo de leitura; cache evita repetir carga e ajuste sem alteração de dados. O modo público não inclui upload ou exportação de dados privados."),
      p("Alternativa de banco/API aumentaria manutenção sem requisito atual de concorrência de escrita. A arquitetura admite substituição futura do carregador sem duplicar fórmulas."),br(),
      h("2. UML de componentes"),UML("componentes"),p("O consumidor aponta para o provedor por dependência tracejada. app utiliza dados/recortes, agregados, indicadores, sensibilidade, distribuição, formatação, regressão e versão. executar_e2 prepara e avalia; a versão pública lê agregados_cti.json e evidencias_e2.json. A base completa é local; demonstração é uma opção explícita."),
      p("Fontes editáveis: componentes.puml e sequencia.puml; figuras PNG renderizadas dessas fontes. O gerador PDF incorpora as mesmas figuras, eliminando um desenho manual independente. Dependências representam consumo de módulos e artefatos; não são ordem de execução."),br(),
      h("3. UML de sequência"),UML("sequencia"),
      p("Participantes: usuário, app, dados/agregados e sensibilidade. Linhas de vida tracejadas, mensagens e retornos; fragmento alt distingue entrada inválida e válida. Resultado com falha é apresentado como mensagem, nunca substituído silenciosamente por zero."),
      p("O processamento da simulação recebe cópia dos valores de referência. Restaurar hipóteses e a troca de ano/população reinicializam a meta na margem do recorte; não escrevem na base. No modo agregado, a regressão lê evidências já calculadas; no modo local, é iniciada por comando explícito. Seu recorte 1-11 é informado separadamente."),br(),
      h("4. Rastreabilidade e qualidade")]
s += [table([["Requisitos FECAP","Implementação / evidência"],
             ["RF01-RF05: fontes e preparação","prepara.py E1 + dados.py; hash preservado, 15 verificações e cobertura por cenário"],
             ["RF06-RF07: análise e regressão","E1 descritiva preservada; regressao.py + notebook E2 com 6/6 células"],
             ["RF08 / RF11: KPIs e cenários","indicadores.py e sensibilidade.py; 216 KPIs + 24 identidades conferidos"],
             ["RF09-RF10 / RF13: relatório e painel","Quatro PDFs; cinco cartões, evolução, tabelas, filtros e notas"],
             ["RF12: exportação autorizada","CSV agregado real disponível; base completa e linhas individuais não exportadas"],
             ["RF14: execução e publicação",STATUS_NUVEM],
             ["Confiabilidade / manutenção",f"{N_TESTES} testes aprovados, incluindo entradas inválidas, recortes, fórmulas, modelo, interface, versão e teste negativo real"],
             ["Reprodução / segurança","Dependências específicas E2; base completa ignorada pelo Git; produção CTI agregada como padrão"]],[155,335]),
      Spacer(1,15),p("A suíte utiliza casos independentes com valores conhecidos e comparação com planilha E1; não verifica apenas que o código executa. Dados essenciais ausentes, chave duplicada, cobertura incompleta e simulação inválida bloqueiam os respectivos resultados."),
      p("O acompanhamento operacional e as trocas entre ferramentas são privados, por orientação do grupo. Este PDF registra requisitos implementados e evidências do produto, sem publicar o planejamento interno."),br(),
      h("5. Resultados e reflexão")]
s += [p("Esperado: integrar as disciplinas em um único painel, preservar a base original, manter consistência de números e preparar publicação. Obtido: aplicação local com cinco KPIs, filtros, financeiro, sensibilidade e regressão; preparação real e comparação financeira sem divergências; notebook executado; documentos gerados."),
      p("Divergência relevante: a regressão apresenta colinearidade alta e forte dependência temporal. A solução adotou divisão por trajetória, erros-padrão agrupados e interpretação associativa. Não escondemos essa limitação para obter um indicador de ajuste mais atraente."),
      p("Revisão cruzada: a meta ficou presa ao primeiro ano e o botão Restaurar gerou aviso de estado; ambos foram corrigidos e retestados. Os desenhos UML manuais do PDF divergiam das fontes: as figuras agora são renderizadas diretamente dos .puml versionados. A identificação do commit passou a ser consultada no checkout em execução."),
      p("As datas e o método de E1 foram mantidos como história, sem inventar reuniões, validação empresarial ou aceites. A nova preparação não sobrescreve relatórios E1. Código específico de plataforma foi separado do ambiente antigo de Windows."),
      p("Melhorias futuras: esclarecer convenções CTI, testar estabilidade do modelo em outras partições, avaliar modelos de dependência temporal e acrescentar autenticação somente se houver publicação autorizada de dados restritos. O protótipo não sustenta decisão econômica real sem validação do domínio."),
      p(STATUS_NUVEM),p("Aprovação acadêmica da plataforma não informada. Banner e documento de extensão permanecem pendentes, em etapa posterior conforme prioridade do grupo."),
      p("Referências: enunciado FINAL FECAP, seções 4-6 e 11; artefatos E1; módulos e testes E2 do repositório. Diagramas e descrições foram confrontados com os arquivos existentes.") ]
salvar("ES e ML","E2_Engenharia_Software_CTI.pdf",s)

# Dados
s=capa("Projeto Interdisciplinar: Ciência de Dados","Eduardo Savino Gomes","Integração de dados, dashboard e reprodução")
s += [h("1. Percurso dos dados"),p("A entrada privada CTI é lida como CSV Latin-1, delimitador ponto e vírgula, sem cabeçalho e com convenção numérica brasileira. A base bruta é apenas lida. Nomes de contas são uniformizados nos derivados; linhas sem conta são preservadas pela preparação E1 e não participam de KPIs."),
      p("Nova execução E2: 1.002.000 linhas, 958.800 nomeadas, 43.200 sem conta; 1.200 cenários, 12 anos e 69 contas. Base analítica: 14.400 x 81. As 15 verificações E1 passaram novamente; chave, cobertura individual e marcas de repetição foram verificadas pela camada E2."),
      p("SHA-256 antes/depois da origem: "+R["qualidade"]["entrada_sha256"]),
      p("Produção: arquivo de agregados reais CTI. Alternativas: Parquet local completo ou demonstração fictícia explicitamente configurada. Ausência ou falha na fonte de produção bloqueia o painel; não há troca silenciosa para dados fictícios."),br(),
      h("2. Painel e funcionalidades"),
      p("Decisões apoiadas: avaliar frequência simulada de baixa geração de caixa; comparar faixas de distribuição aos acionistas; examinar saldo final no encerramento; avaliar impacto de desconto/custo na margem; comparar resultados com e sem cópias de trajetórias."),
      p("Distribuição: médias, mediana, faixas P5-P95 e P25-P75, mais risco aproximado por interpolação P1-P99. No teste de 3.093 limites da base real, erro máximo observado de 1,0082 ponto percentual. Não é garantia universal nem probabilidade empírica de acontecimentos reais.")]
s += [table([["Área","Comportamento"],["Visão geral","Cinco indicadores: receita, custos, margem após custos, resultado líquido e geração de caixa; evolução anual e tabela de apoio"],
             ["Filtros","Intervalo Ano 1-12, população com/sem cópias e ano de referência dos cartões"],
             ["Financeiro","18 indicadores e estados da E1, regras, premissas e limitações"],
             ["Sensibilidade","Desconto, custo, volume hipotético, ticket e meta; comparação referência/simulação e restauração"],
             ["Regressão","Evidências publicadas no modo agregado; ajuste sob demanda no modo local, com validação por trajetória"],
             ["Metodologia","Origem, esquema, unidade, atualização, regras e CSV agregado real"]],[125,365]),
      Spacer(1,15),p("Todos os indicadores financeiros usam o mesmo recorte e as mesmas médias. O modelo usa Anos 1-11 para manter desenho fixo e informa isso explicitamente, sem aparentar responder ao filtro anual do financeiro. A política de cópias afeta sua população."),
      p("Metadados: versão e2-v1, data da entrega, modo da base, unidade por indicador, fórmula e estado. Calendário 2026 + ano e R$ são convenções acadêmicas. As telas alertam sobre ausência, encerramento e indisponibilidades."),br(),
      h("3. Execução e implantação")]
s += [p("Python 3.13. Criar ambiente virtual; instalar app/requirements.txt para o painel ou requirements-e2-dev.txt para análise, testes e geração de documentos. O requirements.txt E1 permanece preservado."),
      p("Produção CTI agregada: python -m streamlit run app/app.py. O arquivo real app/dados/agregados_cti.json acompanha o código. A base completa não precisa ser enviada para o servidor."),
      p('Preparação e análise CTI: python -m src.cti.executar_e2 --csv "src/data/raw/Demonstrativo Fecap v3.csv". O processo grava somente a saída ignorada src/data/processed/e2. Depois configure CTI_BASE_LOCAL para o Parquet dessa pasta ao iniciar o painel local.'),
      p("Testes: python -m pytest -q. A conferência privada é omitida automaticamente em ambiente sem o Parquet CTI; os testes fictícios continuam executáveis. Notebook inferencial tem instruções e modo fictício padrão."),
      p("Nuvem: Streamlit Community Cloud, entrada app/app.py, dependências app/requirements.txt e Python 3.13. Acesso público e seis abas verificados por navegador independente. Não são necessários arquivos privados ou segredos. Logs internos de instalação não foram auditados; aprovação docente da plataforma ainda não informada."),
      p(STATUS_NUVEM),br(),
      h("4. Evidências, limites e fontes")]
s += [p("Reexecução E2: pipeline aprovado com origem inalterada; 216 KPIs e 24 identidades conferidos; notebook 6/6 células sem erro em kernel local; testes sintéticos e teste negativo com dados reais. Evidências numéricas agregadas ficam junto aos artefatos disciplinares."),
      p("As 94 trajetórias repetidas incluem 93 cópias excedentes. A opção de removê-las é explícita, não altera a fonte. Saldos patrimoniais não são acumulados entre anos. Ausências no Ano 12 são mantidas. PC e EBITDA conservam as ressalvas da E1."),
      p("O sistema não conhece volume real de clientes, metas CTI ou divisão real entre custos fixos e variáveis. Ticket, CAC/LTV e metas usam hipóteses identificadas. A sensibilidade é parcial, não reproduz todo o simulador empresarial."),
      p("Fontes: arquivo CTI v3 e src/prepara.py; dicionário de dados e planilha E1; enunciado FINAL FECAP. Bibliotecas: pandas, NumPy, PyArrow, Streamlit, scikit-learn e statsmodels, com versões fixadas no ambiente E2."),
      p("Publicação, revisão independente e feedback dos professores devem ser conferidos antes de declarar entrega final. Nenhuma validação da empresa ou aprovação de plataforma foi presumida.") ]
s += [br(),h("5. Evidências visuais do produto"),
      p("Capturas da versão local com identidade FinSight. Agregados reais CTI; Ano 11, população completa e intervalo 1-11. A execução anterior do painel público foi validada conforme os registros de publicação abaixo."),
      tela("visao_geral"),p("Visão geral: cinco cartões e evolução anual. Valores monetários em milhões de reais.", "SmallPT"),
      br(),h("6. Simulação e validação da interface"),tela("sensibilidade"),
      p("Sensibilidade com hipóteses iniciais: margem igual à referência e desvio da meta zero. A meta acompanha ano/população; quantidade e percentual são hipóteses acadêmicas.", "SmallPT"),
      p(f"Suíte local: {N_TESTES} testes aprovados, sem falhas ou omissões. Notebook: 6/6 células sem erro em kernel local limpo. As seis abas e o CSV foram conferidos na URL pública, além da inspeção em largura de celular."),
      p("Código em execução é identificado na aba Metodologia quando o checkout Git está disponível. O SHA da análise numérica identifica a execução do pipeline; não deve ser confundido com a versão do deploy."),
      p(STATUS_NUVEM)]
salvar("Projeto Interdisciplinar Ciência de Dados","E2_PI_Ciencia_de_Dados_CTI.pdf",s)
