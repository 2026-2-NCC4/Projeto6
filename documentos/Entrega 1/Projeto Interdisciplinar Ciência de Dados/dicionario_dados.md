# Dicionário de dados da base analítica

Gerado por `src/prepara.py`. Uma linha da base analítica = um cenário em um ano.

| Campo | Tipo | Origem | Descrição | Unidade |
|---|---|---|---|---|
| `cenario` | texto | bruto | Identificador do cenário de Monte Carlo (Total Cen_00001 a Total Cen_01200) |  |
| `ano_n` | inteiro | derivado | Ano do horizonte, de 1 a 12, extraído do campo ano |  |
| `ano_calendario` | inteiro | derivado | Ano por convenção da CTI: Ano 1 = 2027 ... Ano 12 = 2038 |  |
| `BAL - Total do Ativo` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: todos os anos | R$ |
| `BAL - Ativo Circulante` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: todos os anos | R$ |
| `BAL - Disponível` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: todos os anos | R$ |
| `BAL - Contas a Receber - SWAP` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: ausente no(s) ano(s) 12 | R$ |
| `BAL - Contas a Receber - Partes Relacionadas` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: ausente no(s) ano(s) 12 | R$ |
| `BAL - Contas a Receber - Clientes` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: todos os anos | R$ |
| `BAL - Estoques Diversos` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: ausente no(s) ano(s) 12 | R$ |
| `BAL - Outros Créditos` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: todos os anos | R$ |
| `BAL - Realizável a Longo Prazo` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: todos os anos | R$ |
| `BAL - At Fiscal Diferido` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: todos os anos | R$ |
| `BAL - Créditos Tributários` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: ausente no(s) ano(s) 12 | R$ |
| `BAL - Outorga da Concessão` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: ausente no(s) ano(s) 12 | R$ |
| `BAL - Outros Créditos LP` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: ausente no(s) ano(s) 12 | R$ |
| `BAL - Permanente` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: todos os anos | R$ |
| `BAL - Investimentos - Imobilizado` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: todos os anos | R$ |
| `BAL - Investimentos - Intangível` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: todos os anos | R$ |
| `BAL - Diferido` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: ausente no(s) ano(s) 12 | R$ |
| `BAL - Depreciação Acumulada` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: todos os anos | R$ |
| `BAL - Amortização Acumulada` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: ausente no(s) ano(s) 12 | R$ |
| `BAL - Amortização - Intangível` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: todos os anos | R$ |
| `BAL - Total do Passivo` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: todos os anos | R$ |
| `BAL - Passivo Circulante` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: todos os anos | R$ |
| `BAL - Empréstimos` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: todos os anos | R$ |
| `BAL - Contas a Pagar - Parte Relacionada` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: ausente no(s) ano(s) 12 | R$ |
| `BAL - Fornecedores` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: ausente no(s) ano(s) 12 | R$ |
| `BAL - Encargos Sociais e Trabalhistas` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: ausente no(s) ano(s) 12 | R$ |
| `BAL - Tributos a pagar` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: ausente no(s) ano(s) 12 | R$ |
| `BAL - Impostos` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: todos os anos | R$ |
| `BAL - Obrigações com o Poder Concedente` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: ausente no(s) ano(s) 12 | R$ |
| `BAL - Outros Débitos` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: ausente no(s) ano(s) 12 | R$ |
| `BAL - Provisão Manutenção` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: ausente no(s) ano(s) 12 | R$ |
| `BAL - Exigível a Longo Prazo` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: ausente no(s) ano(s) 12 | R$ |
| `BAL - Emprést` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: ausente no(s) ano(s) 12 | R$ |
| `BAL - Prov para Contingências` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: ausente no(s) ano(s) 12 | R$ |
| `BAL - Outros deb` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: ausente no(s) ano(s) 12 | R$ |
| `BAL - Patrimônio Líquido` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: ausente no(s) ano(s) 12 | R$ |
| `BAL - Capital Social` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: ausente no(s) ano(s) 12 | R$ |
| `BAL - Reservas de Capital` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: ausente no(s) ano(s) 12 | R$ |
| `BAL - Reservas Legais` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: ausente no(s) ano(s) 12 | R$ |
| `BAL - Reserva de Retenção de Lucros` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: ausente no(s) ano(s) 12 | R$ |
| `BAL - Resultado Acumulado` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: ausente no(s) ano(s) 12 | R$ |
| `BAL - Resultado do Período` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: ausente no(s) ano(s) 12 | R$ |
| `DRE - Receita` | decimal | bruto | Conta do bloco DRE. Movimento do ano. Receitas positivas; custos e despesas negativos. Cobertura: todos os anos | R$ |
| `DRE - Tributos` | decimal | bruto | Conta do bloco DRE. Movimento do ano. Receitas positivas; custos e despesas negativos. Cobertura: todos os anos | R$ |
| `DRE - Custos` | decimal | bruto | Conta do bloco DRE. Movimento do ano. Receitas positivas; custos e despesas negativos. Cobertura: todos os anos | R$ |
| `DRE - Depreciação e Amortização` | decimal | bruto | Conta do bloco DRE. Movimento do ano. Receitas positivas; custos e despesas negativos. Cobertura: todos os anos | R$ |
| `DRE - Resultado Operacional` | decimal | bruto | Conta do bloco DRE. Movimento do ano. Receitas positivas; custos e despesas negativos. Cobertura: todos os anos | R$ |
| `DRE - Receitas Financeiras` | decimal | bruto | Conta do bloco DRE. Movimento do ano. Receitas positivas; custos e despesas negativos. Cobertura: todos os anos | R$ |
| `DRE - Despesas Financeiras` | decimal | bruto | Conta do bloco DRE. Movimento do ano. Receitas positivas; custos e despesas negativos. Cobertura: todos os anos | R$ |
| `DRE - Resultado Financeiro` | decimal | bruto | Conta do bloco DRE. Movimento do ano. Receitas positivas; custos e despesas negativos. Cobertura: todos os anos | R$ |
| `DRE - Outros Resultados Operacionais` | decimal | bruto | Conta do bloco DRE. Movimento do ano. Receitas positivas; custos e despesas negativos. Cobertura: todos os anos | R$ |
| `DRE - Resultado Antes do Imposto de Renda` | decimal | bruto | Conta do bloco DRE. Movimento do ano. Receitas positivas; custos e despesas negativos. Cobertura: todos os anos | R$ |
| `DRE - Imposto de Renda e Contribuição Social` | decimal | bruto | Conta do bloco DRE. Movimento do ano. Receitas positivas; custos e despesas negativos. Cobertura: todos os anos | R$ |
| `DRE - Resultado Líquido` | decimal | bruto | Conta do bloco DRE. Movimento do ano. Receitas positivas; custos e despesas negativos. Cobertura: todos os anos | R$ |
| `DRE - Resultado Líquido após Equivalência` | decimal | bruto | Conta do bloco DRE. Movimento do ano. Receitas positivas; custos e despesas negativos. Cobertura: todos os anos | R$ |
| `DRE - EBITDA` | decimal | bruto | Conta do bloco DRE. Movimento do ano. Receitas positivas; custos e despesas negativos. Cobertura: todos os anos | R$ |
| `FLU - Saldo Inicial` | decimal | bruto | Conta do bloco FLU. Saldo de caixa (não somar entre anos). Cobertura: todos os anos | R$ |
| `FLU - Receita` | decimal | bruto | Conta do bloco FLU. Movimento do ano. Entradas positivas; saídas negativas. Cobertura: todos os anos | R$ |
| `FLU - Tributos` | decimal | bruto | Conta do bloco FLU. Movimento do ano. Entradas positivas; saídas negativas. Cobertura: todos os anos | R$ |
| `FLU - Custos` | decimal | bruto | Conta do bloco FLU. Movimento do ano. Entradas positivas; saídas negativas. Cobertura: todos os anos | R$ |
| `FLU - Investimentos` | decimal | bruto | Conta do bloco FLU. Movimento do ano. Entradas positivas; saídas negativas. Cobertura: todos os anos | R$ |
| `FLU - Entradas` | decimal | bruto | Conta do bloco FLU. Movimento do ano. Entradas positivas; saídas negativas. Cobertura: todos os anos | R$ |
| `FLU - Despesas Financeiras` | decimal | bruto | Conta do bloco FLU. Movimento do ano. Entradas positivas; saídas negativas. Cobertura: todos os anos | R$ |
| `FLU - Resultado Financeiro` | decimal | bruto | Conta do bloco FLU. Movimento do ano. Entradas positivas; saídas negativas. Cobertura: todos os anos | R$ |
| `FLU - Imposto de Renda e Contribuição Social` | decimal | bruto | Conta do bloco FLU. Movimento do ano. Entradas positivas; saídas negativas. Cobertura: todos os anos | R$ |
| `FLU - Distribuição para Acionista` | decimal | bruto | Conta do bloco FLU. Movimento do ano. Entradas positivas; saídas negativas. Cobertura: todos os anos | R$ |
| `FLU - Geração de Caixa` | decimal | bruto | Conta do bloco FLU. Movimento do ano. Entradas positivas; saídas negativas. Cobertura: todos os anos | R$ |
| `FLU - Saldo Final` | decimal | bruto | Conta do bloco FLU. Saldo de caixa (não somar entre anos). Cobertura: todos os anos | R$ |
| `BAL - Dividendos Antecipados` | decimal | bruto | Conta do bloco BAL. Saldo no fim do ano (não somar entre anos). Ativo positivo; passivo e PL negativos. Cobertura: ausente no(s) ano(s) 1, 2, 12 | R$ |
| `encerramento` | booleano | derivado | Verdadeiro no Ano 12, encerramento da concessão |  |
| `residuo_balanco` | decimal | derivado | BAL - Total do Ativo + BAL - Total do Passivo; deve ser próximo de zero | R$ |
| `conferencia_modelo` | decimal | bruto | Primeira linha sem nome de conta do grupo; coincide com o resíduo do balanço | R$ |
| `margem_ebitda` | decimal | derivado | DRE - EBITDA / DRE - Receita (EBITDA como fornecido pela CTI) | fração |
| `margem_operacional` | decimal | derivado | DRE - Resultado Operacional / DRE - Receita | fração |
| `margem_liquida` | decimal | derivado | DRE - Resultado Líquido / DRE - Receita | fração |
| `grupo_repeticao` | texto | derivado | Grupo de cenários com trajetória idêntica nos 12 anos; vazio se o cenário é único |  |
| `cenario_repetido` | booleano | derivado | Verdadeiro se o cenário pertence a um grupo de repetição |  |
| `copia_excedente` | booleano | derivado | Verdadeiro para as cópias além da primeira de cada grupo; usar para análise sem cópias |  |
