"""PDF gerencial gerado exclusivamente das médias e hipóteses apresentadas no painel."""
from io import BytesIO
from datetime import datetime, timezone
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.lineplots import LinePlot
from .indicadores import calcular
from .formatacao import reais_mi, valor_kpi, numero
from .leitura import resumo, CONTAS


def gerar_pdf(medias, ano, populacao, origem, commit, simulacao=None, hipoteses=None):
    """`medias` deve conter somente o recorte agregado que será exportado."""
    if medias.empty or ano not in medias.index:
        raise ValueError("Recorte vazio ou ano fora do recorte.")
    arquivo = BytesIO()
    estilos = getSampleStyleSheet()
    corpo = estilos["BodyText"]
    corpo.fontSize = 9
    corpo.leading = 13
    def p(t, estilo="BodyText"):
        return Paragraph(escape(str(t)), estilos[estilo])
    def tabela(linhas, larguras):
        t = Table([[p(v) for v in l] for l in linhas], colWidths=larguras, repeatRows=1, hAlign="LEFT")
        t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#e5eff4")),
                              ("VALIGN",(0,0),(-1,-1),"TOP"),
                              ("BOTTOMPADDING",(0,0),(-1,-1),7),
                              ("TOPPADDING",(0,0),(-1,-1),7),
                              ("LINEBELOW",(0,0),(-1,0),.5,colors.grey)]))
        return t
    story = [p("FinSight", "Title"),p("Dados financeiros em perspectiva"),
             p("Relatório gerencial do recorte", "Heading1"),
             p(f"Anos {min(medias.index)} a {max(medias.index)}; cartões: Ano {ano}; população: {populacao}."),
             p("Exportado em " + datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC") + "."),
             p(origem),p("Código: " + (commit or "versão indisponível neste ambiente")),
             p("Unidades indicadas em cada valor; evolução e gráfico em milhões de reais. Médias entre futuros alternativos simulados; cenários não são somados."),
             p("Leitura do recorte", "Heading2")]
    story += [p(t) for t in resumo(medias, ano)]
    story += [p("Evolução anual", "Heading2")]
    if len(medias) > 1:
        desenho = Drawing(490, 200)
        plot = LinePlot()
        plot.x, plot.y, plot.width, plot.height = 55, 35, 410, 145
        plot.data = [[(int(a),float(row[c])/1e6) for a,row in medias.iterrows()] for c in CONTAS.values()]
        plot.xValueAxis.valueMin, plot.xValueAxis.valueMax = int(min(medias.index)), int(max(medias.index))
        plot.xValueAxis.valueSteps = [int(a) for a in medias.index]
        for i,cor in enumerate(["#0077ad", "#044363", "#b45309"]):
            plot.lines[i].strokeColor = colors.HexColor(cor)
            plot.lines[i].strokeWidth = 1.5
        desenho.add(plot)
        story += [desenho,p("Linhas: receita (azul), resultado líquido (azul escuro), geração de caixa (ocre). Eixo horizontal: Ano; vertical: R$ milhões.")]
    story += [PageBreak(),p(f"Indicadores do Ano {ano}","Heading1"),
              p("Mesmas regras da planilha E1: razões das médias, não média das razões. Contas ausentes e denominadores inválidos preservam seus estados.")]
    story += [tabela([["Indicador", "Valor / situação", "Fórmula"]] +
                    [[k.nome,valor_kpi(k.valor,k.unidade,k.estado),k.formula+"; "+k.estado] for k in calcular(medias.loc[ano])], [130,150,210])]
    story += [PageBreak(),p("Evolução e hipóteses", "Heading1"),
              tabela([["Ano",*CONTAS]] + [[int(a),*[reais_mi(row[c]) for c in CONTAS.values()]] for a,row in medias.iterrows()], [40,150,150,150])]
    if simulacao is not None and hipoteses is not None:
        story += [p("Sensibilidade acadêmica", "Heading2"),
                  p("Hipóteses de tela: " + "; ".join(f"{k}: {numero(v)}" for k,v in hipoteses.items())),
                  p("Valores simulados: margem " + reais_mi(simulacao["margem"]) + "; ticket R$ " + numero(simulacao["ticket_simulado"]) + "; desvio da meta " + reais_mi(simulacao["desvio_meta"]) + "."),
                  p("Volume e meta são hipóteses acadêmicas. A simulação mantém demais contas constantes e não recalcula tributos, EBITDA ou resultado líquido.")]
    story += [p("Limitações", "Heading2"),
              p("Projeções da CTI, não resultados realizados. Margem após custos não é lucro líquido. Ano 12 é encerramento, com contas ausentes e outro regime; não extrapolar sua dinâmica para operação regular. EBITDA fornecido ainda requer reconciliação da memória de cálculo. Indicadores dependentes de PC com sinal não negativo permanecem pendentes. Não há causalidade ou recomendação de investimento implícita."),
              p("A exportação contém apenas estatísticas agregadas. Não contém cenários individuais ou ranking. As análises de distribuição e regressão estão nas abas e nos documentos técnicos; este relatório resume o recorte financeiro selecionado.")]
    def rodape(canvas,doc):
        canvas.setFont("Helvetica",8)
        canvas.drawString(42,25,"FinSight | Resumo do recorte | fonte CTI ou demonstração identificada acima")
        canvas.drawRightString(553,25,str(doc.page))
    SimpleDocTemplate(arquivo,pagesize=A4,leftMargin=42,rightMargin=42,topMargin=36,bottomMargin=45,
                      title="FinSight - Relatório gerencial",author="DevLeaders").build(story,onFirstPage=rodape,onLaterPages=rodape)
    return arquivo.getvalue()
