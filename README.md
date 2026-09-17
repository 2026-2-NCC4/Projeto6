<div align="center">

# CTI — Plataforma Analítica de Planejamento Financeiro

**[FECAP — Fundação Escola de Comércio Álvares Penteado](https://www.fecap.br/)**  
Ciência da Computação · 4º semestre · 2026/2  
**Projeto Interdisciplinar · Grupo 6 · CTI Global**

[Sobre o projeto](#sobre-o-projeto) · [Equipe](#equipe) · [Entregas](#entregas-das-disciplinas) · [Execução](#execução-local) · [Documentação](#documentação)

</div>

## Sobre o projeto

Este projeto desenvolve uma plataforma analítica para apoiar o planejamento financeiro a partir da base fornecida pela **CTI Global**. O trabalho combina preparação de dados, análise estatística, indicadores financeiros e engenharia de software para transformar projeções em informações que permitam comparar cenários e avaliar desempenho, liquidez, risco e retorno.

Conforme o contexto registrado no notebook do grupo, os dados representam projeções de uma concessão de infraestrutura, com cenários de simulação de Monte Carlo. Cada cenário é uma alternativa para a mesma operação. A solução será construída progressivamente: a primeira entrega concentra a preparação e as análises iniciais; a segunda integra regressão, indicadores e visualizações em um dashboard publicado.

### Objetivos

- Organizar uma **base analítica única**, utilizada por todas as disciplinas.
- Descrever a distribuição e a variabilidade dos dados com medidas estatísticas e gráficos.
- Estruturar balanço patrimonial (BP), demonstração do resultado (DRE) e fluxo de caixa (DFC), validando sua interpretação.
- Calcular indicadores financeiros com fórmulas, premissas e critérios de validação documentados.
- Comparar e classificar cenários segundo regras definidas com os professores e a CTI.
- Disponibilizar um dashboard com pelo menos cinco indicadores, filtros e notas metodológicas.
- Documentar requisitos, decisões de projeto, resultados e limitações.

## Equipe

| Integrante |
|---|
| Gustavo Pires |
| Lúcio Vecchio |
| Luiz Henrique |
| Eric Aloise |

**Professor orientador indicado na entrega de Engenharia:** Luis Pires.

A identificação acima segue o documento de Engenharia publicado pelo grupo. A relação dos demais professores das disciplinas e os links dos integrantes serão complementados após confirmação.

## Entregas das disciplinas

| Disciplina | Entrega 1 — 25/09/2026 | Entrega 2 — 06/11/2026 |
|---|---|---|
| Análise Inferencial de Dados | Análise descritiva: média, mediana, moda, variância, desvio padrão, histogramas e boxplots, com interpretação. | Modelo de regressão, interpretação dos coeficientes, avaliação do ajuste, diagnóstico e limitações. |
| Contabilidade e Finanças | Dicionário de KPIs e planilha de validação, com fórmulas, fontes, unidades e premissas. Incorporar os demonstrativos, índices e ranking orientados em aula. | Visão financeira integrada ao dashboard e análise de sensibilidade, coerentes com os indicadores validados. |
| Engenharia de Software e Arquitetura de Sistemas | Métodos ágeis, engenharia de requisitos, entradas, processamento, saídas e reflexões do grupo. [PDF publicado](documentos/Entrega%201/ES%20e%20ML/E1_Engenharia_Software_CTI.pdf). | Design de software e pelo menos dois diagramas UML, com resultados e reflexões sobre a evolução do projeto. |
| Projeto Interdisciplinar: Ciência de Dados | Identificação e exploração das fontes, preparação dos dados e relatório em Word/PDF, com a etapa analítica em notebook/Colab. | Código Python e dashboard funcional publicado na nuvem, com pelo menos cinco indicadores, filtros e documentação. |

As datas seguem a matriz do enunciado e devem ser acompanhadas no cronograma oficial dos professores. A apresentação final inclui **demonstração, banner e pitch de até quatro minutos**, durante a Semana FECAP de Tecnologia.

## Situação atual

**Atualização: 17/09/2026.**

| Frente | Situação |
|---|---|
| Perfil e auditoria dos dados | Notebook disponível, com sete verificações de qualidade e duas visualizações exploratórias. A verificação do balanço foi corrigida para respeitar a convenção de sinais. |
| Engenharia — E1 | Documento publicado em PDF e DOCX; revisão e integração com as demais frentes continuam. |
| Preparação dos dados | Próxima etapa: transformar a exploração em um processo reproduzível, com base derivada e dicionário. |
| Estatística — E1 | Exploração inicial disponível; faltam completar as medidas, os gráficos e o relatório exigidos. |
| Finanças — E1 | Demonstrativos, indicadores e planilha de validação ainda pendentes; decisões de sinais, EBITDA e ranking permanecem em aberto. |
| Dashboard e regressão | Planejados para a E2. Ainda não há aplicação publicada. |

A prioridade é preparar uma versão comum dos dados para que notebook, planilha e relatórios utilizem os mesmos números e critérios.

## Dados e preservação da fonte

A entrada utilizada pelo notebook é `Demonstrativo Fecap v3.csv`. A estrutura registrada na exploração contém:

| Característica | Descrição |
|---|---|
| Campos de entrada | `ano`, `cenario`, `conta` e `valor` |
| Volume registrado | 1.002.000 linhas, 1.200 cenários e 12 anos de horizonte |
| Contas nomeadas distintas | 69, distribuídas entre BAL, DRE e FLU |
| Leitura | CSV sem cabeçalho, separado por ponto e vírgula, codificação Latin-1 e números no formato brasileiro |
| Granularidade analítica pretendida | Uma linha por cenário e ano: 14.400 combinações |

**A base original da CTI é somente leitura e não é distribuída neste repositório.** O acesso deve ser obtido pelos canais autorizados do projeto. Transformações e cálculos devem gerar arquivos separados, preservando os registros originais.

Alguns cuidados orientam a preparação:

- Ausência de uma conta não equivale automaticamente a zero.
- Cenários são alternativas e não devem ser somados como partes de uma mesma operação.
- A cobertura de contas varia ao longo do horizonte, especialmente no Ano 12.
- O notebook identifica 95 cenários envolvidos em repetição e 94 cópias excedentes por comparação de assinaturas após arredondamento a seis casas. O tratamento dessas trajetórias deve ser documentado; não há exclusão automática.
- Fórmulas, sinais, critérios de ranking e premissas financeiras dependem de validação.

Os resultados atualmente disponíveis são os registrados no notebook. A reprodução independente e a validação integrada devem acompanhar as próximas versões.

## Tecnologias

| Uso | Tecnologia / situação |
|---|---|
| Linguagem | Python; o notebook registra ambiente Python 3.13.5 |
| Exploração e preparação | Pandas, com notebook Jupyter |
| Visualização exploratória | Matplotlib |
| Dependências | [requirements.txt](requirements.txt) |
| Modelagem estatística | SciPy, Statsmodels e Scikit-learn constam nas dependências; implementação prevista para a E2 |
| Dashboard | Streamlit, Plotly e Altair constam nas dependências; aplicação ainda não implementada |
| Documentação e versionamento | Markdown, Word/PDF, Git e GitHub |

A presença de uma biblioteca nas dependências não significa que sua funcionalidade já foi implementada.

## Estrutura de pastas

| Caminho | Conteúdo |
|---|---|
| [documentos/Entrega 1](documentos/Entrega%201) | Documentos da primeira entrega, separados por disciplina |
| [documentos/Entrega 1/ES e ML](documentos/Entrega%201/ES%20e%20ML) | PDF e DOCX da E1 de Engenharia |
| [documentos/Entrega 2](documentos/Entrega%202) | Estrutura reservada aos documentos da segunda entrega |
| [src/notebooks](src/notebooks) | Notebook de perfil, auditoria e exploração |
| [src/data/raw](src/data/raw) | Cópia local autorizada dos dados de entrada, preservada |
| [src/data/staging](src/data/staging) | Destino previsto para dados intermediários |
| [src/data/processed](src/data/processed) | Destino previsto para a base analítica preparada |
| [imagens](imagens) | Visualizações exportadas pelo notebook |
| [.gitignore](.gitignore) | Regras de exclusão de dados, ambientes e arquivos locais |
| [requirements.txt](requirements.txt) | Dependências declaradas do ambiente Python |
| [README.md](README.md) | Apresentação, navegação e instruções do projeto |

As pastas de dados são mantidas no GitHub por arquivos `.gitkeep`; seus dados não acompanham o clone. Ainda não há script de preparação nem diretório de aplicação do dashboard publicado.

## Execução local

### Pré-requisitos

- Git.
- Python 3.13, correspondente à versão principal/secundária registrada no notebook.
- Acesso autorizado a uma **cópia** da base CTI.

O roteiro abaixo usa **Windows**, ambiente registrado na execução existente. O arquivo de dependências inclui `pywinpty`; sua instalação em Linux/macOS exige revisão das dependências específicas de plataforma.

### 1. Clonar o projeto

No terminal:

```bash
git clone https://github.com/2026-2-NCC4/Projeto6.git
cd Projeto6
```

### 2. Criar o ambiente e instalar as dependências

No Prompt de Comando do Windows, a partir da raiz do projeto:

```bat
py -3.13 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Os comandos usam diretamente o Python do ambiente virtual, sem exigir a ativação por script do PowerShell. As versões fixadas em `requirements.txt` refletem o ambiente declarado; a instalação em outro computador ainda precisa ser validada pelo grupo.

### 3. Disponibilizar a entrada autorizada

Coloque uma **cópia** do arquivo, mantendo o nome esperado, em:

```text
src/data/raw/Demonstrativo Fecap v3.csv
```

Não mova nem substitua o arquivo original da CTI. Antes de qualquer commit, confira as alterações e a regra de exclusão:

```bash
git status --short
git check-ignore "src/data/raw/Demonstrativo Fecap v3.csv"
```

### 4. Abrir o notebook

Na raiz do projeto:

```bat
.venv\Scripts\python.exe -m jupyter lab
```

Abra [src/notebooks/01_perfil.ipynb](src/notebooks/01_perfil.ipynb), selecione o kernel do ambiente criado e execute as células em ordem.

O notebook carrega os dados, apresenta o perfil, executa verificações e gera duas figuras em `imagens/`. Uma nova execução pode atualizar essas figuras. Sem acesso à base, é possível consultar o código e as saídas já salvas no GitHub, mas não reproduzir integralmente a análise.

## Documentação

- [E1 de Engenharia — PDF](documentos/Entrega%201/ES%20e%20ML/E1_Engenharia_Software_CTI.pdf)
- [E1 de Engenharia — versão editável DOCX](documentos/Entrega%201/ES%20e%20ML/E1_Engenharia_Software_CTI.docx)
- [Notebook de perfil e auditoria](src/notebooks/01_perfil.ipynb)
- [Documentos da Entrega 1](documentos/Entrega%201)
- [Documentos da Entrega 2](documentos/Entrega%202)
- [Issues do projeto](https://github.com/2026-2-NCC4/Projeto6/issues)

## Licença e uso dos dados

A licença de distribuição do código e da documentação ainda será definida pelo grupo; não há arquivo de licença publicado nesta versão.

Os dados fornecidos pela CTI não estão incluídos em uma licença de código. Seu acesso, uso e divulgação seguem as condições da empresa e as orientações do projeto. A publicação de planilhas, figuras ou resultados deve respeitar essas condições.

## Referências

- **FECAP.** `PI_4CCOMP_202602_CTI_Ciencia_de_Dados_FINAL.pdf` — enunciado institucional do PI 2026/2, disponibilizado à turma.
- **Grupo 6.** Documento da E1 de Engenharia e notebook de perfil, disponíveis nos links acima.
- [Template institucional de PI da FECAP](https://github.com/fecaphub/Template_PI) — referência de organização do README.
- [Projeto10 da turma 2026-2-NCC4](https://github.com/2026-2-NCC4/Projeto10) — referência de apresentação e da tabela de entregas por disciplina.
