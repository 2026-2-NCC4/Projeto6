# Código e análises do PI FinSight

## Declaração de uso de inteligência artificial

Documento único do grupo 6 DevLeaders para as Entregas 1 e 2 das quatro disciplinas do PI FinSight, Ciência da Computação, 4º semestre, 2026/2. Os registros por disciplina são reproduzidos em documentos/README.md e src/README.md.

Os modelos foram informados pelo grupo em 09/11/2026. Os registros de prompts resumem as instruções de desenvolvimento, análise e revisão relacionadas a cada disciplina e entrega; não constituem transcrições literais dos históricos individuais. O apoio à identidade visual, ao banner, à extensão e a esta declaração também é registrado na E2.

Declaração coletiva: [PDF](../documentos/Declaracao_Uso_IA_FinSight.pdf) · [Word editável](../documentos/Declaracao_Uso_IA_FinSight.docx). O documento contém as quatro assinaturas manuscritas em imagem, com data de 09/11/2026.

Referência: [Guia oficial da FECAP, versão 2.0, de 29/07/2026](https://www.fecap.br/wp-content/uploads/2026/08/Guia-para-o-Uso-Responsavel-de-IA-na-FECAP.pdf). Os seis campos do artigo 7º e o responsável são registrados para cada disciplina e entrega.

## Entrega 1

### Engenharia de Software e Arquitetura de Sistemas

| Campo | Registro |
|---|---|
| **Aluno(s) responsável(veis)** | Lúcio Vecchio — RA 25027869 |
| **Ferramenta utilizada** | ChatGPT / Codex e Claude. |
| **Versão/modelo** | GPT-6 Astra e Claude Opus 5.5. |
| **Disciplina / Trabalho** | Engenharia de Software e Arquitetura de Sistemas — Entrega 1 — PI FinSight |
| **Finalidade de uso** | Estruturação e revisão dos requisitos, critérios de aceitação e backlog; apoio à redação técnica e conferência das evidências de execução e dos documentos de Engenharia. |
| **Prompts principais utilizados** | Estruture os requisitos funcionais e não funcionais da solução analítica da CTI. Relacione-os a critérios de aceitação verificáveis e às tarefas do backlog Kanban, deixando explícitos o escopo, as responsabilidades e a preservação da base original. |
| **Trechos ou entregas afetadas** | Relatório E1 de Engenharia em DOCX/PDF e backlog_E1.md: requisitos, aceitação, responsabilidades e evidências de integração. |

### Projeto Interdisciplinar Ciência de Dados

| Campo | Registro |
|---|---|
| **Aluno(s) responsável(veis)** | Gustavo Felizardo Pires — RA 25027188 |
| **Ferramenta utilizada** | ChatGPT / Codex e Claude. |
| **Versão/modelo** | GPT-6 Astra e Claude Opus 5.5. |
| **Disciplina / Trabalho** | Projeto Interdisciplinar Ciência de Dados — Entrega 1 — PI FinSight |
| **Finalidade de uso** | Apoio à programação, revisão e execução do pipeline de preparação; conferência dos notebooks, dicionário, validações e relatório de Ciência de Dados, preservando a fonte CTI. |
| **Prompts principais utilizados** | Prepare o CSV CTI com codificação Latin-1 e números no padrão brasileiro. Separe as linhas sem nome de conta para auditoria, valide a chave cenário/ano/conta e gere a base analítica e o dicionário sem modificar a fonte. |
| **Trechos ou entregas afetadas** | src/prepara.py; notebooks 01_perfil.ipynb e 02_preparacao.ipynb; relatório E1 de Ciência de Dados e dicionario_dados.md. |

### Análise Inferencial de Dados

| Campo | Registro |
|---|---|
| **Aluno(s) responsável(veis)** | Luiz Henrique Zaim da Cruz — RA 26028907 |
| **Ferramenta utilizada** | Gemini e ChatGPT. |
| **Versão/modelo** | Gemini 4 Argos; GPT-6 Astra. |
| **Disciplina / Trabalho** | Análise Inferencial de Dados — Entrega 1 — PI FinSight |
| **Finalidade de uso** | Apoio à revisão e correção do notebook e do relatório descritivo, conferência de agrupamentos, medidas e gráficos e execução no Colab sobre a cópia autorizada. |
| **Prompts principais utilizados** | Calcule média, mediana, moda, variância e desvio padrão por conta e ano. Compare Receita, Custos, Resultado Líquido e Total do Ativo com histogramas e boxplots; explique as distribuições e confira a correspondência entre notebook, tabelas e relatório. |
| **Trechos ou entregas afetadas** | Notebook Entrega_1_Analise_Descritiva_CTI_(1).ipynb e Relatorio Entrega1 Analise Inferencial de Dados.pdf: medidas, agrupamentos, figuras e explicações. |

### Contabilidade e Finanças

| Campo | Registro |
|---|---|
| **Aluno(s) responsável(veis)** | Eric Aloise — RA 25027482 |
| **Ferramenta utilizada** | Gemini e Claude. |
| **Versão/modelo** | Gemini (versão não informada); Claude Opus 5.5. |
| **Disciplina / Trabalho** | Contabilidade e Finanças — Entrega 1 — PI FinSight |
| **Finalidade de uso** | Apoio à revisão e correção das fórmulas, rótulos e controles da planilha de KPIs e do dicionário financeiro, com recálculo e comparação dos resultados. |
| **Prompts principais utilizados** | Relacione cada KPI às contas da CTI e documente fórmula, unidade, periodicidade e regra de validação. Confira os sinais de passivos, as contas ausentes no Ano 12 e os denominadores; recalcule a planilha e os controles de balanço. |
| **Trechos ou entregas afetadas** | Planilha E1 de validação de KPIs e PDF do dicionário de KPIs: fórmulas, fonte, sinais, controles de validação e explicações financeiras. |

## Entrega 2

### Engenharia de Software e Arquitetura de Sistemas

| Campo | Registro |
|---|---|
| **Aluno(s) responsável(veis)** | Lúcio Vecchio — RA 25027869 |
| **Ferramenta utilizada** | ChatGPT / Codex, recurso de imagens do ChatGPT e Claude. |
| **Versão/modelo** | GPT-6 Astra; Claude Opus 5.5. |
| **Disciplina / Trabalho** | Engenharia de Software e Arquitetura de Sistemas — Entrega 2 — PI FinSight |
| **Finalidade de uso** | Apoio à implementação e revisão da arquitetura, UML, interface e testes, com conferência dos artefatos e correções pelo grupo. Apoio à criação e revisão da identidade visual FinSight e à apresentação do mapa no banner. |
| **Prompts principais utilizados** | Represente a arquitetura implementada nos diagramas UML de componentes, sequência e implantação. Verifique a separação entre interface, dados e cálculos e o fluxo do mapa para a Sensibilidade; mantenha diagramas, código e relatório coerentes. Documente o mapa interativo e seu uso no banner. |
| **Trechos ou entregas afetadas** | Relatório de Engenharia, diagramas de componentes, sequência e implantação, dashboard, mapa financeiro e verificações técnicas. Nome e logotipo FinSight, tutorial do mapa, README e banner. |

### Projeto Interdisciplinar Ciência de Dados

| Campo | Registro |
|---|---|
| **Aluno(s) responsável(veis)** | Gustavo Felizardo Pires — RA 25027188 |
| **Ferramenta utilizada** | ChatGPT / Codex e Claude. |
| **Versão/modelo** | GPT-6 Astra e Claude Opus 5.5. |
| **Disciplina / Trabalho** | Projeto Interdisciplinar Ciência de Dados — Entrega 2 — PI FinSight |
| **Finalidade de uso** | Apoio à revisão do pipeline, integração das análises ao painel e revisão cruzada das entregas, sem substituir a conferência dos resultados. Apoio à redação e integração dos documentos comuns do PI. |
| **Prompts principais utilizados** | Integre as saídas da preparação ao painel publicado, distinguindo a base local dos agregados autorizados. Organize as perguntas de negócio, os filtros de ano e população, os percentis e as exportações; documente a avaliação e a implantação no CRISP-DM. |
| **Trechos ou entregas afetadas** | Relatório de Ciência de Dados, documentação de execução, pipeline e painel integrado; revisão cruzada dos relatórios e UML. Banner, documento do projeto de extensão, declaração coletiva de IA e registros nos READMEs. |

### Análise Inferencial de Dados

| Campo | Registro |
|---|---|
| **Aluno(s) responsável(veis)** | Luiz Henrique Zaim da Cruz — RA 26028907 |
| **Ferramenta utilizada** | Gemini e ChatGPT. |
| **Versão/modelo** | Gemini 4 Argos; GPT-6 Astra. |
| **Disciplina / Trabalho** | Análise Inferencial de Dados — Entrega 2 — PI FinSight |
| **Finalidade de uso** | Apoio à organização e interpretação da regressão, métricas e diagnósticos, seguido de revisão das premissas e conferência dos resultados. |
| **Prompts principais utilizados** | Compare regressões simples e múltipla do resultado líquido com receita, custos assinados e efeitos de ano. Separe treino, validação e teste por trajetórias, selecione pelo RMSE e examine resíduos, colinearidade e sensibilidade ao Ano 12, sem interpretação causal. |
| **Trechos ou entregas afetadas** | Notebook E2 de regressão e relatório de Análise Inferencial: escolha do modelo, coeficientes, métricas, diagnósticos e limitações. |

### Contabilidade e Finanças

| Campo | Registro |
|---|---|
| **Aluno(s) responsável(veis)** | Eric Aloise — RA 25027482 |
| **Ferramenta utilizada** | Gemini e Claude. |
| **Versão/modelo** | Gemini (versão não informada); Claude Opus 5.5. |
| **Disciplina / Trabalho** | Contabilidade e Finanças — Entrega 2 — PI FinSight |
| **Finalidade de uso** | Apoio à revisão dos KPIs, fórmulas, metas e sensibilidade, com comparação à planilha E1 e conferência das premissas e valores calculados. |
| **Prompts principais utilizados** | Implemente no painel os indicadores do dicionário E1, calculados após as médias das contas por ano. Simule desconto na receita e variação de custos, mantendo o volume constante; diferencie ticket hipotético, meta acadêmica e valores indisponíveis, sem recalcular o resultado líquido. |
| **Trechos ou entregas afetadas** | Relatório do painel financeiro, regras de validação e abas Financeiro e Sensibilidade do dashboard. |

## Responsabilidade autoral

O grupo declara o apoio de IA na programação, preparação e análise de dados, redação e revisão técnica dos relatórios, integração e interface. A responsabilidade pela conferência das fontes, premissas, fórmulas, resultados e conteúdo final é dos integrantes. Os registros são os mesmos da ficha coletiva e do README da outra pasta.

## Localização dos artefatos

- [Preparação de dados](prepara.py) e [notebooks executados](notebooks).
- [Módulos de análise](cti), [testes e ferramentas](apoio) e [interface do dashboard](../app).
- [Relatórios das entregas e declaração coletiva](../documentos/README.md).
