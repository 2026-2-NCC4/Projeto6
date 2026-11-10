# FECAP - Fundação de Comércio Álvares Penteado

<p align="center">
<a href="https://github.com/2026-2-NCC4/Projeto6"><img src="imagens/logo_finsight.png" alt="FinSight" width="50%" border="0"></a>
</p>

# FinSight

**Dados financeiros em perspectiva**

## Grupo: DevLeaders

## Integrantes: <a href="https://www.linkedin.com/in/gustavo-pires0/">Gustavo Pires</a>, <a href="https://www.linkedin.com/in/lucio-vecchio/">Lúcio Vecchio</a>, <a href="https://www.linkedin.com/in/luiz-zaim-9867b224b/">Luiz Henrique</a>, <a href="https://www.linkedin.com/in/eric-aloise/">Eric Aloise</a>

## Professores Orientadores: <a href="https://www.linkedin.com/in/eduardo-savino/">Eduardo Savino</a>, <a href="https://www.linkedin.com/in/luisspires/">Luis Pires</a>, <a href="https://www.linkedin.com/in/mauricio-lopes-42b8b33a3/">Mauricio Lopes</a>, <a href="https://www.linkedin.com/in/professorrodnil/">Rodnil da Silva</a>

## Sobre o projeto

Este projeto desenvolve uma plataforma analítica para apoiar o planejamento financeiro a partir da base fornecida pela **CTI Global**. O trabalho combina preparação de dados, análise estatística, indicadores financeiros e engenharia de software para transformar projeções em informações que permitam comparar cenários e avaliar desempenho, liquidez, risco e retorno.

Os dados representam projeções de uma concessão de infraestrutura, com cenários de simulação de Monte Carlo. Cada cenário é uma alternativa para a mesma operação. A primeira entrega concentra a preparação e as análises iniciais; a segunda integra regressão, indicadores e visualizações em um dashboard publicado.

### Objetivos

- Organizar uma **base analítica única**, utilizada por todas as disciplinas.
- Descrever a distribuição e a variabilidade dos dados com medidas estatísticas e gráficos.
- Estruturar balanço patrimonial (BP), demonstração do resultado (DRE) e fluxo de caixa (DFC), validando sua interpretação.
- Calcular indicadores financeiros com fórmulas, premissas e critérios de validação documentados.
- Comparar e classificar cenários segundo regras definidas com os professores e a CTI.
- Disponibilizar um dashboard com pelo menos cinco indicadores, filtros e notas metodológicas.
- Documentar requisitos, decisões de projeto, resultados e limitações.

## Entregas das disciplinas

| Disciplina | Entrega 1 | Entrega 2 |
|---|---|---|
| Análise Inferencial de Dados | [Acessar entrega 1](documentos/Entrega%201/An%C3%A1lise%20Inferencial%20de%20Dados) | [Acessar entrega 2](documentos/Entrega%202/An%C3%A1lise%20Inferencial%20de%20Dados) |
| Contabilidade e Finanças | [Acessar entrega 1](documentos/Entrega%201/Contabilidade%20e%20Finan%C3%A7as) | [Acessar entrega 2](documentos/Entrega%202/Contabilidade%20e%20Finan%C3%A7as) |
| Engenharia de Software e Arquitetura de Sistemas | [Acessar entrega 1](documentos/Entrega%201/ES%20e%20ML) | [Acessar entrega 2](documentos/Entrega%202/ES%20e%20ML) |
| Projeto Interdisciplinar: Ciência de Dados | [Acessar entrega 1](documentos/Entrega%201/Projeto%20Interdisciplinar%20Ci%C3%AAncia%20de%20Dados) | [Acessar entrega 2](documentos/Entrega%202/Projeto%20Interdisciplinar%20Ci%C3%AAncia%20de%20Dados) |

## Entrega 2: painel integrado

O dashboard reúne indicadores financeiros, evolução anual, filtros, distribuição entre cenários, análise de sensibilidade, regressão e exportação de relatórios. Utiliza agregados autorizados da CTI; a base completa permanece local.

O mapa financeiro interativo permite explorar os indicadores, simular desconto e custos e aplicar as hipóteses à análise de sensibilidade. O modo **Apresentar** amplia a visualização para demonstrações e apresentações.

O painel também reúne perspectivas de leitura, comparação entre resultado e caixa, ponte de caixa do Ano 12 e uma análise hipotética de WACC e EVA.

**[Acessar o FinSight](https://projeto6cti.streamlit.app/)**

- [Como executar e preparar a publicação](src/apoio/documentacao/EXECUCAO_E2.md)
- [Regressão: notebook executado](src/notebooks/E2_Regressao_CTI.ipynb) e [relatório](documentos/Entrega%202/An%C3%A1lise%20Inferencial%20de%20Dados/E2_Analise_Inferencial_CTI.pdf)
- [Painel financeiro e regras](documentos/Entrega%202/Contabilidade%20e%20Finan%C3%A7as/E2_Painel_Financeiro_CTI.pdf) e [validação](src/apoio/documentacao/VALIDACAO_E2.md)
- [Design de software e UML](documentos/Entrega%202/ES%20e%20ML/E2_Engenharia_Software_CTI.pdf) · [fontes dos diagramas](src/apoio/documentacao/uml)
- [Integração de Ciência de Dados](documentos/Entrega%202/Projeto%20Interdisciplinar%20Ci%C3%AAncia%20de%20Dados/E2_PI_Ciencia_de_Dados_CTI.pdf)
- Banner FinSight: [arquivo editável](documentos/Banner_FinSight.pptx) · [imagem](documentos/Banner_FinSight.png)
- Documento de extensão: [PDF](documentos/Documento_Projeto_de_Extensao_FinSight.pdf) · [arquivo editável](documentos/Documento_Projeto_de_Extensao_FinSight.docx)
- Declaração coletiva de uso de IA, E1 e E2: [PDF](documentos/Declaracao_Uso_IA_FinSight.pdf) · [Word editável](documentos/Declaracao_Uso_IA_FinSight.docx). Registros por disciplina em [documentos](documentos/README.md) e [código](src/README.md).

Para executar o dashboard localmente, instale `src/apoio/requirements-e2-dev.txt` em Python 3.13 e execute `python -m streamlit run app/app.py`. Consulte o guia de execução acima para mais detalhes.

## Estrutura de pastas

```text
Projeto6/
├── app/                  # Interface e agregados publicáveis
├── documentos/
│   ├── Entrega 1/
│   │   ├── Análise Inferencial de Dados/
│   │   ├── Contabilidade e Finanças/
│   │   ├── ES e ML/
│   │   └── Projeto Interdisciplinar Ciência de Dados/
│   └── Entrega 2/
│       ├── Análise Inferencial de Dados/
│       ├── Contabilidade e Finanças/
│       ├── ES e ML/
│       └── Projeto Interdisciplinar Ciência de Dados/
├── imagens/
├── src/
│   ├── apoio/            # Testes, ferramentas e configuração de testes
│   │   ├── documentacao/ # Guias e fontes UML
│   │   ├── tests/
│   │   ├── tools/
│   │   ├── pytest.ini
│   │   ├── requirements.txt
│   │   └── requirements-e2-dev.txt
│   ├── data/
│   │   ├── raw/
│   │   ├── staging/
│   │   └── processed/
│   ├── notebooks/
│   └── prepara.py
├── LICENSE
└── README.md
```

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
.venv\Scripts\python.exe -m pip install -r src/apoio/requirements.txt
```

Os comandos usam diretamente o Python do ambiente virtual, sem exigir a ativação por script do PowerShell. As versões fixadas em `src/apoio/requirements.txt` refletem o ambiente declarado; a instalação em outro computador ainda precisa ser validada pelo grupo.

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

### 4. Gerar a base analítica

Na raiz do projeto:

```bat
.venv\Scripts\python.exe src\prepara.py
```

O script lê a cópia da base, executa 15 verificações e gera os arquivos analíticos em `src/data/processed/`, além do dicionário de dados. Se alguma verificação falhar, a execução é interrompida antes da gravação.

### 5. Abrir os notebooks

Na raiz do projeto:

```bat
.venv\Scripts\python.exe -m jupyter lab
```

Abra [01_perfil.ipynb](src/notebooks/01_perfil.ipynb) (perfil e auditoria) e [02_preparacao.ipynb](src/notebooks/02_preparacao.ipynb) (preparação passo a passo), selecione o kernel do ambiente criado e execute as células em ordem.

No Google Colab, ajuste `CSV_NO_DRIVE` na célula de configuração de cada notebook para o caminho da cópia autorizada no seu Drive. Essa célula clona o repositório e copia a base para o ambiente de execução.

O notebook 01 gera duas figuras em `imagens/`, que podem ser atualizadas ao executar novamente. Sem acesso à base, é possível consultar o código e as saídas já salvas no GitHub, mas não reproduzir integralmente a análise.

## Licença

<a href="https://github.com/2026-2-NCC4/Projeto6">FinSight (DevLeaders)</a> © 2026 by

<a href="https://www.linkedin.com/in/gustavo-pires0/">Gustavo Pires</a>, <a href="https://www.linkedin.com/in/lucio-vecchio/">Lúcio Vecchio</a>, <a href="https://www.linkedin.com/in/luiz-zaim-9867b224b/">Luiz Henrique</a>, <a href="https://www.linkedin.com/in/eric-aloise/">Eric Aloise</a>, <a href="https://www.fecap.br/">FECAP</a>
is licensed under <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a> <img src="https://mirrors.creativecommons.org/presskit/icons/cc.svg" width="20" height="20" valign="middle"> <img src="https://mirrors.creativecommons.org/presskit/icons/by.svg" width="20" height="20" valign="middle"></p>

Os dados fornecidos pela CTI não estão incluídos nesta licença. Seu acesso, uso e divulgação seguem as condições da empresa e as orientações do projeto. A publicação de planilhas, figuras ou resultados deve respeitar essas condições.
