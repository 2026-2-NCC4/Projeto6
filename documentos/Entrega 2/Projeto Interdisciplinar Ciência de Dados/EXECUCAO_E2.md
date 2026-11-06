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

## Base CTI local

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

## Publicação provisória

Destino: Streamlit Community Cloud, com agregados reais CTI autorizados por Lúcio em 06/11. Aprovação acadêmica da plataforma ainda não informada.
- Repositório de hospedagem `lucio734/Projeto6`; branch `main`, sincronizada com a main oficial `2026-2-NCC4/Projeto6` antes de cada publicação.
- Arquivo de entrada `app/app.py`; Python 3.13.
- Dependências em `app/requirements.txt`, sem pywinpty.
- Nenhum segredo ou arquivo privado necessário.
- Conferir início limpo, filtros, cinco KPIs, simulação, regressão e CSV agregado real por sessão independente.
- Registrar a URL e o commit efetivamente publicado após o teste externo.

**URL pública verificada:** https://projeto6cti.streamlit.app/ — acesso sem login, seis abas e CSV conferidos em 06/11/2026. Logs internos de instalação não foram auditados; não confundir o teste funcional externo com inspeção de logs.

## Atualização de 06/11/2026
Produção real agregada como padrão; demonstração somente com CTI_DEMO=1. Contrato valida origem, contagens e ausências. Meta acadêmica é percentual da receita original; padrão igual à margem original. Ticket usa quantidade hipotética. A versão local usa dados reais; publicação externa exige URL acessível e commit conferido.

Cópia pessoal de publicação: https://github.com/lucio734/Projeto6, sincronizada com a versão oficial. O usuário concluiu a autenticação e publicou em https://projeto6cti.streamlit.app/. O GPT verificou o acesso por sessão independente.

## Evidências técnicas desta revisão
40 testes aprovados, sem falhas ou omissões, no código fcb6f7d03d4b. Pipeline CTI reexecutado sem divergências em 216 KPIs e 24 identidades; notebook reexecutado em kernel local limpo, 6/6 células sem erro. Agregados versionados conferidos contra a base reprocessada. Download CSV pelo navegador: 198 linhas (18 indicadores × 11 anos), idênticas ao cálculo do mesmo recorte. Capturas das seis abas em imagens/e2; são evidências locais.

A aba Metodologia consulta o HEAD do checkout Git. Se o servidor não disponibilizar Git, informa a indisponibilidade sem inventar versão. O commit de referência dos testes/artefatos não precisa coincidir com o commit documental que os incorpora; alterações posteriores no código exigem nova verificação.

Para atualizar UML, renderizar componentes.puml e sequencia.puml com PlantUML e substituir os PNG de mesmo nome antes de gerar os PDFs. Os PDFs incorporam esses PNG; não há desenho manual paralelo.

## Verificação externa de 06/11/2026
URL aberta sem login do proprietário. Seis abas acessíveis; agregados CTI reais e cinco cartões coerentes com o local. CSV público de 198 linhas igual à exportação local (Ano 1-11). Commit observado inicialmente 707af174ffc9, contendo a implementação fcb6f7d03d4b e a configuração de desenvolvimento adicionada pelo Streamlit. A configuração foi preservada e alinhada para Python 3.13 e dependências E2; execução do devcontainer não foi realizada.

Imagens em imagens/e2 são capturas da URL pública; a descrição de cada PDF identifica o contexto. O commit dos documentos incorpora evidências anteriores e não exige auto-referência circular em seus próprios arquivos. A versão atual pode ser consultada na aba Metodologia. A aprovação docente da plataforma segue sem confirmação.
