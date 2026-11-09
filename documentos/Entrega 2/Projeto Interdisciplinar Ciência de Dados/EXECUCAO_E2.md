# FinSight — execução do painel E2

Dados financeiros em perspectiva.

Python 3.13. A partir da raiz do projeto:

```bash
python -m venv .venv
# Windows:
.venv\Scripts\python.exe -m pip install -r requirements-e2-dev.txt
.venv\Scripts\python.exe -m streamlit run app/app.py
# Linux/macOS: substituir .venv\Scripts\python.exe por .venv/bin/python
```

Produção: agregados reais CTI em app/dados/agregados_cti.json ou CTI_AGREGADOS. CTI_BASE_LOCAL seleciona a base completa local; CTI_DEMO=1 seleciona explicitamente a demonstração. Fonte ausente ou inválida bloqueia o painel.
Cinco KPIs, filtros, financeiro, metas/ticket simulados, sensibilidade, regressão e metodologia estão no mesmo painel.

## Leitura gerencial e PDF (07/11)

Visão geral inclui resumo de sinais e variações das médias entre anos consecutivos do recorte. O quadro de encerramento compara sempre Anos 11 e 12 da população selecionada e explicita esse recorte independente dos outros gráficos. Não soma percentis nem apresenta uma ponte contábil incompleta como se fosse validada.

Em Metodologia, use **Preparar relatório PDF** e **Baixar relatório PDF**. A saída usa o intervalo, população e ano dos cartões e as hipóteses atuais da Sensibilidade, com evolução, fórmulas, fonte e limites. O PDF está disponível nos modos agregado e fictício; não exporta a base completa local. A dependência ReportLab acompanha `app/requirements.txt`. Para reproduzir uma alteração de hipótese, gere novamente o PDF.

As fórmulas financeiras seguem a planilha E1. Uma comparação numérica local confirmou diferença entre EBITDA fornecido e a alternativa Resultado Operacional menos Depreciação/Amortização assinada; sem confirmação contábil, a conta fornecida não foi substituída. PC com sinal não negativo mantém estados pendentes. Mediana dos KPIs, média das razões e razão das médias são estimadores diferentes: o painel continua usando a última regra, documentada e conferida contra E1.

## Mapa financeiro interativo

O mapa abre na Visão geral e recebe apenas as médias anuais de receita, custos, resultado líquido e geração de caixa; a margem é derivada de receita + custos assinados. Toque nos cinco indicadores para explorar a referência e sua evolução. Linhas sólidas representam a fórmula da margem; as pontilhadas permitem relacionar áreas de análise e não representam derivação ou causalidade.

Os controles do mapa produzem uma prévia local, imediata, de receita/custos/margem. Resultado líquido e caixa não são recalculados. **Aplicar à Sensibilidade** valida o ano, a população e os limites e atualiza os mesmos controles usados pelo cálculo Python e pelo PDF. **Zerar prévia** zera somente os dois controles do mapa até aplicar; o botão Restaurar da aba Sensibilidade continua restaurando as hipóteses completas.

**Apresentar** amplia o mapa em tela cheia ou, quando o navegador a recusa, em uma apresentação dentro da janela. **Sair** e **Escape** encerram os dois modos. Tab e Shift+Tab percorrem os controles da apresentação e o foco retorna ao botão ao sair. Em celular, os controles continuam acessíveis por rolagem interna. A legenda explica os valores compactos: mi são milhões, bi são bilhões; detalhe e evolução ficam em milhões de reais.

A animação respeita a preferência de movimento reduzido. O componente usa HTML, CSS e JavaScript próprios, sem serviços externos, além da API de componentes v2 do Streamlit 1.67 já instalado. Arquivos em `app/componentes/` e contrato Python em `src/cti/mapa.py`. Não há upload ou exposição de cenários individuais.

## Preparação da base CTI local

Use somente uma cópia autorizada:

```bash
python -m src.cti.executar_e2 --csv "src/data/raw/Demonstrativo Fecap v3.csv"
```

A rotina reutiliza as verificações E1, acrescenta contrato E2 e grava derivados em `src/data/processed/e2/`, ignorado pelo Git. Não sobrescreve documentos E1. Preserva o SHA da origem.

No PowerShell, para o painel local:
```powershell
$env:CTI_BASE_LOCAL = (Resolve-Path "src/data/processed/e2/base_analitica.parquet").Path
python -m streamlit run app/app.py
```

Para voltar à produção agregada, feche o painel e remova somente essa variável:
```powershell
Remove-Item Env:CTI_BASE_LOCAL -ErrorAction SilentlyContinue
```

Não configurar essa variável em nuvem pública. Não enviar CSV/Parquet CTI ou publicar saídas individuais. Tabelas e gráficos locais apresentam apenas agregados; a exportação de KPIs fica disponível nos modos agregado e fictício.

## Agregados publicáveis

Depois de preparar a base local, gere o arquivo que o painel público usa:

```bash
python -m src.cti.agregados --base src/data/processed/e2/base_analitica.parquet
```

A rotina grava somente `app/dados/agregados_cti.json`, com estatísticas por ano para as populações "todos" e "sem cópias": médias das 15 contas usadas pelo painel (as 14 entradas da planilha E1 e a geração de caixa) e percentis P1 a P99, média e contagem dos seis indicadores da aba Distribuição. Não contém linha, identificador, mínimo nem máximo de cenário. O arquivo registra a data de geração e o SHA-256 da entrada CTI. Nesse modo, a parcela de cenários abaixo de um limite é aproximada por interpolação entre os percentis (erro em torno de 1 ponto percentual), e a aba Regressão mostra os resultados já publicados em `evidencias_e2.json`, sem recalcular o modelo.

O arquivo publicado é conferido contra a base local. Para demonstração, definir CTI_DEMO=1; remover essa variável para voltar à produção.

## Verificações

```bash
python -m pytest -q
python -m src.cti.executar_e2
```

Sem `--csv` ou `--base`, a segunda rotina usa dados fictícios. Suas saídas são identificadas pelo modo; para não substituir a evidência CTI, usar `--saida src/data/processed/e2_ficticio`.
A suíte omite explicitamente o teste privado quando a base não está disponível.

O notebook em Análise Inferencial importa os mesmos módulos. Execute desde o começo, com kernel do ambiente E2. Sem variável CTI_BASE_LOCAL, usa dados fictícios. A execução salva do notebook é CTI local; não foi executada no Colab nesta etapa.

Para regenerar os PDFs a partir das evidências agregadas versionadas:
```bash
python -m tools.gerar_documentos_e2
```
A geração lê evidencias_e2.json e as fórmulas compartilhadas; requer reportlab. Não precisa da base privada e não recalcula ou modifica a planilha E1. Para incorporar uma nova execução, atualizar antes as evidências agregadas e identificar o commit correspondente.

As quatro capas usam a mesma referência: o último commit que alterou código, testes ou configuração do painel. Um commit somente de PDF/captura não troca essa referência. A data da documentação é distinta da data original do enunciado, indicada na Metodologia.

## Publicação

Destino: Streamlit Community Cloud, com agregados reais CTI autorizados por Lúcio em 06/11. Aprovação acadêmica da plataforma ainda não informada.
- Repositório de hospedagem `lucio734/Projeto6`; branch `main`, sincronizada com a main oficial `2026-2-NCC4/Projeto6` antes de cada publicação.
- Arquivo de entrada `app/app.py`; Python 3.13.
- Dependências em `app/requirements.txt`, sem pywinpty.
- Nenhum segredo ou arquivo privado necessário.
- Conferir início limpo, filtros, cinco KPIs, simulação, regressão e CSV agregado real por sessão independente.
- Registrar a URL e o commit efetivamente publicado após o teste externo.

Se uma atualização de módulos não aparecer na interface, [reinicie o aplicativo](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app/reboot-your-app) na administração do Community Cloud. A plataforma também reconstrói o ambiente ao detectar uma alteração no manifesto de dependências. Conferir o caso afetado na tela: o SHA do checkout, isoladamente, não comprova que um módulo já carregado em memória foi atualizado.

**URL pública verificada:** https://projeto6cti.streamlit.app/ — acesso sem login, seis abas e CSV conferidos em 06/11/2026. Logs internos de instalação não foram auditados; não confundir o teste funcional externo com inspeção de logs.

## Atualização de 06/11/2026
Produção real agregada como padrão; demonstração somente com CTI_DEMO=1. Contrato valida origem, contagens e ausências. Meta acadêmica é percentual da receita original; padrão igual à margem original. Ticket usa quantidade hipotética. A versão local usa dados reais; publicação externa exige URL acessível e commit conferido.

Cópia pessoal de publicação: https://github.com/lucio734/Projeto6, sincronizada com a versão oficial. O usuário concluiu a autenticação e publicou em https://projeto6cti.streamlit.app/. O GPT verificou o acesso por sessão independente.

## Verificação técnica de 08/11/2026

65 testes aprovados, sem falhas, erros ou omissões (22,45 s), incluindo a comparação financeira privada disponível e nove casos novos de formatação. Zero arredondado é exibido sem sinal negativo, mantendo negativos visíveis e valores de cálculo. O modo alternativo foi conferido nas cinco seleções em 1280×720 e 1920×1080 sem rolagem; teclado, Escape, foco, tela cheia real e celular emulado também foram exercitados. A aplicação de desconto de 10% continuou produzindo margem de R$ 7.746.537.944,97 no Ano 11 da população completa.

Na produção, CSV principal de 198 linhas comparado por dados/estados ao cálculo local e PDF gerencial de três páginas baixados pelo navegador. O P5 da geração de caixa do Ano 7 foi conferido visualmente como R$ 0,00 mi nas duas populações após reconstrução do ambiente. As quatro capturas usadas no PDF do PI foram atualizadas. PDFs acadêmicos: 5/4/6/7 páginas, mesma referência de código 658a6b47574d. Não houve nova execução integral do pipeline ou notebook nesta etapa; os resultados numéricos anteriores foram preservados.

## Histórico de evidências técnicas de 06/11
40 testes aprovados, sem falhas ou omissões, no código fcb6f7d03d4b. Pipeline CTI reexecutado sem divergências em 216 KPIs e 24 identidades; notebook reexecutado em kernel local limpo, 6/6 células sem erro. Agregados versionados conferidos contra a base reprocessada. Download CSV pelo navegador: 198 linhas (18 indicadores × 11 anos), idênticas ao cálculo do mesmo recorte. Capturas das seis abas em imagens/e2; são evidências locais.

A aba Metodologia consulta o HEAD do checkout Git. Se o servidor não disponibilizar Git, informa a indisponibilidade sem inventar versão. O commit de referência dos testes/artefatos não precisa coincidir com o commit documental que os incorpora; alterações posteriores no código exigem nova verificação.

Para atualizar UML, renderizar componentes.puml, sequencia.puml e implantacao.puml com PlantUML local em UTF-8 e substituir os PNG de mesmo nome antes de gerar os PDFs. Os PDFs incorporam esses PNG; não há desenho manual paralelo.

## Verificação externa de 06/11/2026
URL aberta sem login do proprietário. Seis abas acessíveis; agregados CTI reais e cinco cartões coerentes com o local. CSV público de 198 linhas igual à exportação local (Ano 1-11). Commit observado inicialmente 707af174ffc9, contendo a implementação fcb6f7d03d4b e a configuração de desenvolvimento adicionada pelo Streamlit. A configuração foi preservada e alinhada para Python 3.13 e dependências E2; execução do devcontainer não foi realizada.

Imagens em imagens/e2 são capturas da URL pública; a descrição de cada PDF identifica o contexto. O commit dos documentos incorpora evidências anteriores e não exige auto-referência circular em seus próprios arquivos. A versão atual pode ser consultada na aba Metodologia. A aprovação docente da plataforma segue sem confirmação.
