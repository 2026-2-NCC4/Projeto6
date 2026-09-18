# Dicionário de dados da base analítica

Gerado por `src/prepara.py`. Uma linha da base analítica = um cenário em um ano (14.400 linhas).
Grupo, tipo de linha, sinal e cobertura de cada conta são calculados a partir do próprio dado.

## Identificação e campos derivados

| Campo | Tipo | Origem | Unidade | Descrição |
|---|---|---|---|---|
| `cenario` | texto | bruto | código | Identificador do cenário de Monte Carlo, de Total Cen_00001 a Total Cen_01200 |
| `ano_n` | inteiro | derivado | ano (1 a 12) | Ano do horizonte, extraído do campo ano |
| `ano_calendario` | inteiro | derivado | ano | Ano pela convenção da CTI: Ano 1 = 2027, Ano 12 = 2038 |
| `encerramento` | booleano | derivado | verdadeiro ou falso | Verdadeiro no Ano 12, encerramento da concessão |
| `residuo_balanco` | decimal | derivado | R$ | Total do Ativo + Total do Passivo; deve ser próximo de zero |
| `conferencia_modelo` | decimal | bruto | R$ | Primeira linha sem nome de conta do grupo; coincide com o resíduo do balanço |
| `margem_ebitda` | decimal | derivado | fração da receita (0,77 = 77%) | EBITDA dividido pela Receita, com o EBITDA como fornecido pela CTI |
| `margem_operacional` | decimal | derivado | fração da receita (0,77 = 77%) | Resultado Operacional dividido pela Receita |
| `margem_liquida` | decimal | derivado | fração da receita (0,77 = 77%) | Resultado Líquido dividido pela Receita |
| `grupo_repeticao` | texto | derivado | rótulo (G01) | Grupo de cenários com trajetória idêntica nos 12 anos; vazio se o cenário é único |
| `cenario_repetido` | booleano | derivado | verdadeiro ou falso | Verdadeiro se o cenário pertence a um grupo de repetição |
| `copia_excedente` | booleano | derivado | verdadeiro ou falso | Verdadeiro nas cópias além da primeira de cada grupo; filtrar para analisar sem cópias |

## Contas contábeis

Todas em R$. **Tipo de linha:** total e subtotal já somam as contas do seu grupo, então não devem ser somados junto com elas. **Sinal e cobertura:** o sinal observado em todos os registros e os anos em que a conta aparece.

| Conta | Grupo | Tipo de linha | Natureza | Sinal e cobertura | Observação |
|---|---|---|---|---|---|
| BAL - Total do Ativo | Ativo | total | saldo no fim do ano | positivo em 95%, negativo em 5% / todos os anos | Fica negativo em parte dos cenários no Ano 12, no encerramento |
| BAL - Ativo Circulante | Ativo circulante | subtotal | saldo no fim do ano | sempre positivo, exceto 22 registros negativos / todos os anos |  |
| BAL - Disponível | Ativo circulante | detalhe | saldo no fim do ano | sempre positivo, exceto 1 registro negativo / todos os anos |  |
| BAL - Contas a Receber - SWAP | Ativo circulante | detalhe | saldo no fim do ano | sempre positivo / ausente no Ano 12 |  |
| BAL - Contas a Receber - Partes Relacionadas | Ativo circulante | detalhe | saldo no fim do ano | sempre positivo / ausente no Ano 12 |  |
| BAL - Contas a Receber - Clientes | Ativo circulante | detalhe | saldo no fim do ano | positivo em 92%, negativo em 8% / todos os anos |  |
| BAL - Estoques Diversos | Ativo circulante | detalhe | saldo no fim do ano | sempre positivo / ausente no Ano 12 |  |
| BAL - Outros Créditos | Ativo circulante | detalhe | saldo no fim do ano | positivo em 17%, negativo em 83% / todos os anos |  |
| BAL - Realizável a Longo Prazo | Realizável a longo prazo | subtotal | saldo no fim do ano | sempre positivo / todos os anos |  |
| BAL - At Fiscal Diferido | Realizável a longo prazo | detalhe | saldo no fim do ano | positivo em 92%, negativo em 8% / todos os anos |  |
| BAL - Créditos Tributários | Realizável a longo prazo | detalhe | saldo no fim do ano | sempre positivo / ausente no Ano 12 |  |
| BAL - Outorga da Concessão | Realizável a longo prazo | detalhe | saldo no fim do ano | sempre positivo / ausente no Ano 12 |  |
| BAL - Outros Créditos LP | Realizável a longo prazo | detalhe | saldo no fim do ano | sempre positivo / ausente no Ano 12 |  |
| BAL - Permanente | Ativo permanente | subtotal | saldo no fim do ano | positivo em 92%, negativo em 8% / todos os anos |  |
| BAL - Investimentos - Imobilizado | Ativo permanente | detalhe | saldo no fim do ano | sempre positivo, exceto 27 registros negativos e 5 registros iguais a zero / todos os anos |  |
| BAL - Investimentos - Intangível | Ativo permanente | detalhe | saldo no fim do ano | sempre positivo / todos os anos |  |
| BAL - Diferido | Ativo permanente | detalhe | saldo no fim do ano | sempre positivo / ausente no Ano 12 |  |
| BAL - Depreciação Acumulada | Ativo permanente | detalhe | saldo no fim do ano | positivo em 8%, negativo em 92% / todos os anos | Conta redutora do ativo |
| BAL - Amortização Acumulada | Ativo permanente | detalhe | saldo no fim do ano | sempre negativo / ausente no Ano 12 | Conta redutora do ativo |
| BAL - Amortização - Intangível | Ativo permanente | detalhe | saldo no fim do ano | sempre negativo / todos os anos | Conta redutora do ativo |
| BAL - Total do Passivo | Passivo e patrimônio líquido | total | saldo no fim do ano | positivo em 5%, negativo em 95% / todos os anos | Inclui o patrimônio líquido. Somado ao Total do Ativo, dá zero |
| BAL - Passivo Circulante | Passivo circulante | subtotal | saldo no fim do ano | positivo em 62%, negativo em 38% / todos os anos | Não é igual à soma das contas do seu grupo; o sinal também varia. Pergunta pendente à CTI |
| BAL - Empréstimos | Passivo circulante | detalhe | saldo no fim do ano | positivo em 67%, negativo em 33% / todos os anos |  |
| BAL - Contas a Pagar - Parte Relacionada | Passivo circulante | detalhe | saldo no fim do ano | sempre negativo / ausente no Ano 12 |  |
| BAL - Fornecedores | Passivo circulante | detalhe | saldo no fim do ano | sempre negativo / ausente no Ano 12 |  |
| BAL - Encargos Sociais e Trabalhistas | Passivo circulante | detalhe | saldo no fim do ano | sempre negativo / ausente no Ano 12 |  |
| BAL - Tributos a pagar | Passivo circulante | detalhe | saldo no fim do ano | sempre negativo / ausente no Ano 12 |  |
| BAL - Impostos | Passivo circulante | detalhe | saldo no fim do ano | sempre negativo / todos os anos |  |
| BAL - Obrigações com o Poder Concedente | Passivo circulante | detalhe | saldo no fim do ano | sempre negativo / ausente no Ano 12 |  |
| BAL - Outros Débitos | Passivo circulante | detalhe | saldo no fim do ano | sempre negativo / ausente no Ano 12 |  |
| BAL - Provisão Manutenção | Passivo circulante | detalhe | saldo no fim do ano | positivo em 4%, negativo em 96% / ausente no Ano 12 |  |
| BAL - Exigível a Longo Prazo | Exigível a longo prazo | subtotal | saldo no fim do ano | sempre negativo / ausente no Ano 12 |  |
| BAL - Emprést | Exigível a longo prazo | detalhe | saldo no fim do ano | sempre negativo / ausente no Ano 12 | Distinta de BAL - Empréstimos: grupo e sinal diferentes |
| BAL - Prov para Contingências | Exigível a longo prazo | detalhe | saldo no fim do ano | sempre negativo / ausente no Ano 12 |  |
| BAL - Outros deb | Exigível a longo prazo | detalhe | saldo no fim do ano | sempre negativo / ausente no Ano 12 | Distinta de BAL - Outros Débitos: grupo e sinal diferentes |
| BAL - Patrimônio Líquido | Patrimônio líquido | subtotal | saldo no fim do ano | sempre negativo, exceto 63 registros positivos / ausente no Ano 12 |  |
| BAL - Capital Social | Patrimônio líquido | detalhe | saldo no fim do ano | sempre negativo / ausente no Ano 12 |  |
| BAL - Reservas de Capital | Patrimônio líquido | detalhe | saldo no fim do ano | sempre negativo / ausente no Ano 12 |  |
| BAL - Reservas Legais | Patrimônio líquido | detalhe | saldo no fim do ano | sempre negativo / ausente no Ano 12 |  |
| BAL - Reserva de Retenção de Lucros | Patrimônio líquido | detalhe | saldo no fim do ano | sempre negativo / ausente no Ano 12 |  |
| BAL - Resultado Acumulado | Patrimônio líquido | detalhe | saldo no fim do ano | sempre positivo / ausente no Ano 12 |  |
| BAL - Resultado do Período | Patrimônio líquido | detalhe | saldo no fim do ano | positivo em 7%, negativo em 93% / ausente no Ano 12 |  |
| DRE - Receita | Demonstração do resultado | detalhe | movimento do ano | sempre positivo / todos os anos |  |
| DRE - Tributos | Demonstração do resultado | detalhe | movimento do ano | sempre negativo / todos os anos |  |
| DRE - Custos | Demonstração do resultado | detalhe | movimento do ano | sempre negativo / todos os anos |  |
| DRE - Depreciação e Amortização | Demonstração do resultado | detalhe | movimento do ano | sempre negativo / todos os anos |  |
| DRE - Resultado Operacional | Demonstração do resultado | resultado | movimento do ano | sempre positivo / todos os anos | Receita + Tributos + Custos + Depreciação e Amortização |
| DRE - Receitas Financeiras | Demonstração do resultado | detalhe | movimento do ano | positivo em 85%, zero em 15% / todos os anos |  |
| DRE - Despesas Financeiras | Demonstração do resultado | detalhe | movimento do ano | sempre negativo / todos os anos |  |
| DRE - Resultado Financeiro | Demonstração do resultado | resultado | movimento do ano | positivo em 21%, negativo em 79% / todos os anos | Receitas Financeiras + Despesas Financeiras |
| DRE - Outros Resultados Operacionais | Demonstração do resultado | detalhe | movimento do ano | sempre positivo / todos os anos |  |
| DRE - Resultado Antes do Imposto de Renda | Demonstração do resultado | resultado | movimento do ano | sempre positivo / todos os anos | Resultado Operacional + Resultado Financeiro + Outros Resultados Operacionais |
| DRE - Imposto de Renda e Contribuição Social | Demonstração do resultado | detalhe | movimento do ano | sempre negativo / todos os anos |  |
| DRE - Resultado Líquido | Demonstração do resultado | resultado | movimento do ano | sempre positivo / todos os anos | Resultado Antes do Imposto de Renda + Imposto de Renda e Contribuição Social |
| DRE - Resultado Líquido após Equivalência | Demonstração do resultado | resultado | movimento do ano | sempre positivo / todos os anos | Igual ao Resultado Líquido em todos os registros |
| DRE - EBITDA | Demonstração do resultado | resultado | movimento do ano | sempre positivo / todos os anos | Fornecido pela CTI. Não reconcilia com o Resultado Operacional somado à Depreciação e Amortização |
| FLU - Saldo Inicial | Fluxo de caixa | saldo | saldo de caixa | sempre positivo / todos os anos |  |
| FLU - Receita | Fluxo de caixa | detalhe | movimento do ano | sempre positivo / todos os anos |  |
| FLU - Tributos | Fluxo de caixa | detalhe | movimento do ano | sempre negativo / todos os anos |  |
| FLU - Custos | Fluxo de caixa | detalhe | movimento do ano | sempre negativo / todos os anos |  |
| FLU - Investimentos | Fluxo de caixa | detalhe | movimento do ano | sempre negativo / todos os anos |  |
| FLU - Entradas | Fluxo de caixa | detalhe | movimento do ano | positivo em 91%, zero em 9% / todos os anos |  |
| FLU - Despesas Financeiras | Fluxo de caixa | detalhe | movimento do ano | sempre negativo / todos os anos |  |
| FLU - Resultado Financeiro | Fluxo de caixa | detalhe | movimento do ano | positivo em 3%, negativo em 97% / todos os anos | Informativa: não entra na Geração de Caixa |
| FLU - Imposto de Renda e Contribuição Social | Fluxo de caixa | detalhe | movimento do ano | sempre negativo / todos os anos |  |
| FLU - Distribuição para Acionista | Fluxo de caixa | detalhe | movimento do ano | sempre negativo / todos os anos |  |
| FLU - Geração de Caixa | Fluxo de caixa | resultado | movimento do ano | positivo em 57%, negativo em 43% / todos os anos | Soma de Receita, Tributos, Custos, Investimentos, Entradas, Despesas Financeiras, Imposto de Renda e Distribuição para Acionista |
| FLU - Saldo Final | Fluxo de caixa | saldo | saldo de caixa | sempre positivo, exceto 1 registro negativo / todos os anos | Saldo Inicial + Geração de Caixa |
| BAL - Dividendos Antecipados | Patrimônio líquido | detalhe | saldo no fim do ano | sempre positivo / ausente nos anos 1, 2 e 12 |  |
