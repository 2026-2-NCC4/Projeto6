"""Acrescenta um complemento às E2, preservando as páginas anteriores.

Requer reportlab e pypdf. A marca no texto impede inserir o mesmo complemento duas vezes.
"""
from io import BytesIO
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "documentos/Entrega 2"
MARCA = "Complemento de melhorias do FinSight"


def complemento(titulo, paragrafos, imagem=None):
    arquivo = BytesIO()
    styles = getSampleStyleSheet()
    styles["Title"].fontSize = 17
    styles["Title"].leading = 21
    styles["BodyText"].fontSize = 10
    styles["BodyText"].leading = 14
    story = [Paragraph(MARCA, styles["Title"]), Spacer(1, 10),
             Paragraph(titulo, styles["Heading2"]), Spacer(1, 8)]
    for texto in paragrafos:
        story.extend([Paragraph(texto, styles["BodyText"]), Spacer(1, 9)])
    if imagem:
        from reportlab.lib.utils import ImageReader
        w, h = ImageReader(str(imagem)).getSize()
        escala = min(410/w, 480/h)
        story.append(Image(str(imagem), width=w*escala, height=h*escala))
    SimpleDocTemplate(arquivo, pagesize=A4, leftMargin=48, rightMargin=48,
                      topMargin=42, bottomMargin=42).build(story)
    return arquivo.getvalue()


def acrescentar(caminho, titulo, paragrafos, imagem=None):
    arquivo = BASE/caminho
    original = PdfReader(str(arquivo))
    if any(MARCA in (pagina.extract_text() or "") for pagina in original.pages):
        raise ValueError(f"Complemento já existe: {arquivo}")
    anterior = [p.get_contents().get_data() for p in original.pages]
    novo = PdfReader(BytesIO(complemento(titulo, paragrafos, imagem)))
    if len(novo.pages) != 1:
        raise ValueError(f"O complemento deve caber em uma página: {arquivo}")
    writer = PdfWriter()
    writer.append(original)
    writer.append(novo)
    if original.metadata:
        writer.add_metadata({str(k): str(v) for k, v in original.metadata.items() if v is not None})
    saida = BytesIO()
    writer.write(saida)
    verificacao = PdfReader(BytesIO(saida.getvalue()))
    if len(verificacao.pages) != len(anterior)+1 or any(
        p.get_contents().get_data() != conteudo for p, conteudo in zip(verificacao.pages, anterior)
    ):
        raise ValueError(f"As páginas anteriores não foram preservadas: {arquivo}")
    arquivo.write_bytes(saida.getvalue())
    print(arquivo)


def main():
    acrescentar(Path("ES e ML/E2_Engenharia_Software_CTI.pdf"), "Diagrama de casos de uso",
        ["O diagrama complementa os modelos de componentes, sequência e implantação. Gestão, Investidor e Analista são roteiros de leitura, sem autenticação ou permissões distintas. As fontes editáveis e imagens permanecem em src/apoio/documentacao/uml."],
        ROOT/"src/apoio/documentacao/uml/casos_uso.png")
    acrescentar(Path("Contabilidade e Finanças/E2_Painel_Financeiro_CTI.pdf"), "Caixa e custo de capital",
        ["Resultado líquido e geração de caixa são comparados por média anual da mesma população. A diferença não representa, isoladamente, conversão de lucro em caixa ou causa e efeito.",
         "No Ano 12, a ponte soma movimentações assinadas e confere geração e saldo final com as médias de contas autorizadas. Nenhum cenário individual é publicado; não se somam percentis.",
         "A sensibilidade opcional usa EBIT, capital investido, alíquota e WACC informados pelo usuário. NOPAT = EBIT x (1 - alíquota); EVA hipotético = NOPAT - WACC x capital investido. É uma hipótese ilustrativa e não substitui o EVA simplificado da E1 nem o modelo da CTI."])
    acrescentar(Path("Projeto Interdisciplinar Ciência de Dados/E2_PI_Ciencia_de_Dados_CTI.pdf"), "Novas leituras gerenciais",
        ["O painel mantém suas seis abas e acrescenta comparação de resultado e caixa, ponte reconciliada do Ano 12 e roteiros de Gestão, Investidor e Analista. Os roteiros não criam permissões nem alteram o recorte.",
         "A ponte utiliza médias anuais autorizadas para as mesmas duas populações, com verificação de origem, cobertura e identidades contábeis. A fonte individual permanece local.",
         "A sensibilidade de WACC é calculada com premissas inseridas pela pessoa usuária; seus valores não representam parâmetros observados da CTI. O diagrama de casos de uso complementa a documentação de Engenharia."])


if __name__ == "__main__":
    main()
