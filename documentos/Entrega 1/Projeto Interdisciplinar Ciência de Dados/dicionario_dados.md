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
| `residuo_balanco` | decimal | derivado | reais | Total do Ativo + Total do Passivo; deve ser próximo de zero |
| `conferencia_modelo` | decimal | bruto | reais | Primeira linha sem nome de conta do grupo; coincide com o resíduo do balanço |
| `margem_ebitda` | decimal | derivado | fração da receita (0,77 = 77%) | EBITDA dividido pela Receita, com o EBITDA como fornecido pela CTI |
| `margem_operacional` | decimal | derivado | fração da receita (0,77 = 77%) | Resultado Operacional dividido pela Receita |
| `margem_liquida` | decimal | derivado | fração da receita (0,77 = 77%) | Resultado Líquido dividido pela Receita |
| `grupo_repeticao` | texto | derivado | rótulo (G01) | Grupo de cenários com trajetória idêntica nos 12 anos; vazio se o cenário é único |
| `cenario_repetido` | booleano | derivado | verdadeiro ou falso | Verdadeiro se o cenário pertence a um grupo de repetição |
| `copia_excedente` | booleano | derivado | verdadeiro ou falso | Verdadeiro nas cópias além da primeira de cada grupo; filtrar para analisar sem cópias |

## Contas contábeis

Valores em reais. **Tipo de linha:** total e subtotal já somam as contas do seu grupo, então não devem ser somados junto com elas. **Sinal e cobertura:** o sinal observado em todos os registros e os anos em que a conta aparece.

| Conta | Descrição | Grupo | Tipo de linha | Natureza | Sinal e cobertura |
|---|---|---|---|---|---|
| BAL - Total do Ativo | Soma de todos os bens e direitos da concessionária. Fica negativo em parte dos cenários no Ano 12, no encerramento | Ativo | total | saldo no fim do ano | positivo em 95%, negativo em 5% / todos os anos |
| BAL - Ativo Circulante | Bens e direitos realizáveis em até um ano | Ativo circulante | subtotal | saldo no fim do ano | sempre positivo, exceto 22 registros negativos / todos os anos |
| BAL - Disponível | Caixa e equivalentes de caixa. Igual ao FLU - Saldo Final em todos os registros | Ativo circulante | detalhe | saldo no fim do ano | sempre positivo, exceto 1 registro negativo / todos os anos |
| BAL - Contas a Receber - SWAP | Valores a receber de contratos de swap (derivativos) | Ativo circulante | detalhe | saldo no fim do ano | sempre positivo / ausente no Ano 12 |
| BAL - Contas a Receber - Partes Relacionadas | Valores a receber de empresas do mesmo grupo econômico | Ativo circulante | detalhe | saldo no fim do ano | sempre positivo / ausente no Ano 12 |
| BAL - Contas a Receber - Clientes | Valores a receber pelos serviços prestados na concessão | Ativo circulante | detalhe | saldo no fim do ano | positivo em 92%, negativo em 8% / todos os anos |
| BAL - Estoques Diversos | Materiais e insumos em estoque. Valores muito pequenos em relação às demais contas | Ativo circulante | detalhe | saldo no fim do ano | sempre positivo / ausente no Ano 12 |
| BAL - Outros Créditos | Outros direitos de curto prazo | Ativo circulante | detalhe | saldo no fim do ano | positivo em 17%, negativo em 83% / todos os anos |
| BAL - Realizável a Longo Prazo | Direitos realizáveis após um ano | Realizável a longo prazo | subtotal | saldo no fim do ano | sempre positivo / todos os anos |
| BAL - At Fiscal Diferido | Ativo fiscal diferido: tributos a recuperar em exercícios futuros | Realizável a longo prazo | detalhe | saldo no fim do ano | positivo em 92%, negativo em 8% / todos os anos |
| BAL - Créditos Tributários | Tributos a recuperar | Realizável a longo prazo | detalhe | saldo no fim do ano | sempre positivo / ausente no Ano 12 |
| BAL - Outorga da Concessão | Direito de outorga da concessão registrado como ativo | Realizável a longo prazo | detalhe | saldo no fim do ano | sempre positivo / ausente no Ano 12 |
| BAL - Outros Créditos LP | Outros direitos de longo prazo | Realizável a longo prazo | detalhe | saldo no fim do ano | sempre positivo / ausente no Ano 12 |
| BAL - Permanente | Investimentos, imobilizado e intangível, líquidos de depreciação e amortização | Ativo permanente | subtotal | saldo no fim do ano | positivo em 92%, negativo em 8% / todos os anos |
| BAL - Investimentos - Imobilizado | Bens físicos usados na operação, pelo valor de aquisição | Ativo permanente | detalhe | saldo no fim do ano | sempre positivo, exceto 27 registros negativos e 5 registros iguais a zero / todos os anos |
| BAL - Investimentos - Intangível | Direitos sem forma física, como o de explorar a concessão, pelo valor de aquisição | Ativo permanente | detalhe | saldo no fim do ano | sempre positivo / todos os anos |
| BAL - Diferido | Gastos que beneficiam exercícios futuros (ativo diferido) | Ativo permanente | detalhe | saldo no fim do ano | sempre positivo / ausente no Ano 12 |
| BAL - Depreciação Acumulada | Desgaste acumulado do imobilizado. Conta redutora do ativo | Ativo permanente | detalhe | saldo no fim do ano | positivo em 8%, negativo em 92% / todos os anos |
| BAL - Amortização Acumulada | Amortização acumulada de ativos de longo prazo. Conta redutora do ativo | Ativo permanente | detalhe | saldo no fim do ano | sempre negativo / ausente no Ano 12 |
| BAL - Amortização - Intangível | Amortização acumulada do intangível. Conta redutora do ativo | Ativo permanente | detalhe | saldo no fim do ano | sempre negativo / todos os anos |
| BAL - Total do Passivo | Soma das obrigações com terceiros e do patrimônio líquido. Inclui o patrimônio líquido; somado ao Total do Ativo, dá zero | Passivo e patrimônio líquido | total | saldo no fim do ano | positivo em 5%, negativo em 95% / todos os anos |
| BAL - Passivo Circulante | Obrigações com vencimento em até um ano. Não é igual à soma das contas do seu grupo e o sinal varia. Pergunta pendente à CTI | Passivo circulante | subtotal | saldo no fim do ano | positivo em 62%, negativo em 38% / todos os anos |
| BAL - Empréstimos | Empréstimos e financiamentos de curto prazo | Passivo circulante | detalhe | saldo no fim do ano | positivo em 67%, negativo em 33% / todos os anos |
| BAL - Contas a Pagar - Parte Relacionada | Valores a pagar a empresas do mesmo grupo econômico | Passivo circulante | detalhe | saldo no fim do ano | sempre negativo / ausente no Ano 12 |
| BAL - Fornecedores | Valores a pagar a fornecedores | Passivo circulante | detalhe | saldo no fim do ano | sempre negativo / ausente no Ano 12 |
| BAL - Encargos Sociais e Trabalhistas | Salários, férias e encargos a pagar | Passivo circulante | detalhe | saldo no fim do ano | sempre negativo / ausente no Ano 12 |
| BAL - Tributos a pagar | Tributos a recolher | Passivo circulante | detalhe | saldo no fim do ano | sempre negativo / ausente no Ano 12 |
| BAL - Impostos | Impostos a pagar; a diferença para Tributos a pagar não foi detalhada pela CTI | Passivo circulante | detalhe | saldo no fim do ano | sempre negativo / todos os anos |
| BAL - Obrigações com o Poder Concedente | Valores devidos ao poder concedente pelo contrato de concessão | Passivo circulante | detalhe | saldo no fim do ano | sempre negativo / ausente no Ano 12 |
| BAL - Outros Débitos | Outras obrigações de curto prazo | Passivo circulante | detalhe | saldo no fim do ano | sempre negativo / ausente no Ano 12 |
| BAL - Provisão Manutenção | Provisão para a manutenção da infraestrutura prevista no contrato | Passivo circulante | detalhe | saldo no fim do ano | positivo em 4%, negativo em 96% / ausente no Ano 12 |
| BAL - Exigível a Longo Prazo | Obrigações com vencimento após um ano | Exigível a longo prazo | subtotal | saldo no fim do ano | sempre negativo / ausente no Ano 12 |
| BAL - Emprést | Empréstimos e financiamentos de longo prazo. Distinta de BAL - Empréstimos: grupo e sinal diferentes | Exigível a longo prazo | detalhe | saldo no fim do ano | sempre negativo / ausente no Ano 12 |
| BAL - Prov para Contingências | Provisão para processos e riscos com perda provável | Exigível a longo prazo | detalhe | saldo no fim do ano | sempre negativo / ausente no Ano 12 |
| BAL - Outros deb | Outras obrigações de longo prazo. Distinta de BAL - Outros Débitos: grupo e sinal diferentes | Exigível a longo prazo | detalhe | saldo no fim do ano | sempre negativo / ausente no Ano 12 |
| BAL - Patrimônio Líquido | Recursos dos acionistas: capital, reservas e resultados | Patrimônio líquido | subtotal | saldo no fim do ano | sempre negativo, exceto 63 registros positivos / ausente no Ano 12 |
| BAL - Capital Social | Capital investido pelos acionistas | Patrimônio líquido | detalhe | saldo no fim do ano | sempre negativo / ausente no Ano 12 |
| BAL - Reservas de Capital | Reservas formadas por aportes que não vêm do resultado | Patrimônio líquido | detalhe | saldo no fim do ano | sempre negativo / ausente no Ano 12 |
| BAL - Reservas Legais | Reserva obrigatória por lei, formada a partir do lucro | Patrimônio líquido | detalhe | saldo no fim do ano | sempre negativo / ausente no Ano 12 |
| BAL - Reserva de Retenção de Lucros | Lucros mantidos na empresa em vez de distribuídos | Patrimônio líquido | detalhe | saldo no fim do ano | sempre negativo / ausente no Ano 12 |
| BAL - Resultado Acumulado | Resultados de exercícios anteriores ainda não destinados | Patrimônio líquido | detalhe | saldo no fim do ano | sempre positivo / ausente no Ano 12 |
| BAL - Resultado do Período | Resultado do exercício corrente, registrado no patrimônio líquido | Patrimônio líquido | detalhe | saldo no fim do ano | positivo em 7%, negativo em 93% / ausente no Ano 12 |
| DRE - Receita | Receita da operação da concessão | Demonstração do resultado | detalhe | movimento do ano | sempre positivo / todos os anos |
| DRE - Tributos | Tributos sobre a receita | Demonstração do resultado | detalhe | movimento do ano | sempre negativo / todos os anos |
| DRE - Custos | Custos da operação | Demonstração do resultado | detalhe | movimento do ano | sempre negativo / todos os anos |
| DRE - Depreciação e Amortização | Despesa de depreciação e amortização do ano | Demonstração do resultado | detalhe | movimento do ano | sempre negativo / todos os anos |
| DRE - Resultado Operacional | Resultado da operação, antes do resultado financeiro. Cálculo: Receita + Tributos + Custos + Depreciação e Amortização | Demonstração do resultado | resultado | movimento do ano | sempre positivo / todos os anos |
| DRE - Receitas Financeiras | Rendimentos de aplicações e outras receitas financeiras | Demonstração do resultado | detalhe | movimento do ano | positivo em 85%, zero em 15% / todos os anos |
| DRE - Despesas Financeiras | Juros e outros encargos financeiros | Demonstração do resultado | detalhe | movimento do ano | sempre negativo / todos os anos |
| DRE - Resultado Financeiro | Saldo entre receitas e despesas financeiras. Cálculo: Receitas Financeiras + Despesas Financeiras | Demonstração do resultado | resultado | movimento do ano | positivo em 21%, negativo em 79% / todos os anos |
| DRE - Outros Resultados Operacionais | Outras receitas e despesas operacionais | Demonstração do resultado | detalhe | movimento do ano | sempre positivo / todos os anos |
| DRE - Resultado Antes do Imposto de Renda | Resultado antes do imposto de renda e da contribuição social. Cálculo: Resultado Operacional + Resultado Financeiro + Outros Resultados Operacionais | Demonstração do resultado | resultado | movimento do ano | sempre positivo / todos os anos |
| DRE - Imposto de Renda e Contribuição Social | IRPJ e CSLL sobre o lucro | Demonstração do resultado | detalhe | movimento do ano | sempre negativo / todos os anos |
| DRE - Resultado Líquido | Lucro ou prejuízo do ano. Cálculo: Resultado Antes do Imposto de Renda + Imposto de Renda e Contribuição Social | Demonstração do resultado | resultado | movimento do ano | sempre positivo / todos os anos |
| DRE - Resultado Líquido após Equivalência | Resultado líquido após a equivalência patrimonial. Igual ao Resultado Líquido em todos os registros | Demonstração do resultado | resultado | movimento do ano | sempre positivo / todos os anos |
| DRE - EBITDA | Lucro antes de juros, impostos, depreciação e amortização. Fornecido pela CTI; não reconcilia com o Resultado Operacional somado à Depreciação e Amortização | Demonstração do resultado | resultado | movimento do ano | sempre positivo / todos os anos |
| FLU - Saldo Inicial | Caixa no início do ano. Igual ao Saldo Final do ano anterior | Fluxo de caixa | saldo | saldo de caixa | sempre positivo / todos os anos |
| FLU - Receita | Recebimentos da receita no ano | Fluxo de caixa | detalhe | movimento do ano | sempre positivo / todos os anos |
| FLU - Tributos | Pagamentos de tributos sobre a receita | Fluxo de caixa | detalhe | movimento do ano | sempre negativo / todos os anos |
| FLU - Custos | Pagamentos de custos da operação | Fluxo de caixa | detalhe | movimento do ano | sempre negativo / todos os anos |
| FLU - Investimentos | Pagamentos de investimentos em ativos | Fluxo de caixa | detalhe | movimento do ano | sempre negativo / todos os anos |
| FLU - Entradas | Outras entradas de caixa; a composição não foi detalhada pela CTI | Fluxo de caixa | detalhe | movimento do ano | positivo em 91%, zero em 9% / todos os anos |
| FLU - Despesas Financeiras | Pagamentos de juros e encargos financeiros | Fluxo de caixa | detalhe | movimento do ano | sempre negativo / todos os anos |
| FLU - Resultado Financeiro | Resultado financeiro do ano. Informativa: não entra na Geração de Caixa | Fluxo de caixa | detalhe | movimento do ano | positivo em 3%, negativo em 97% / todos os anos |
| FLU - Imposto de Renda e Contribuição Social | Pagamentos de IRPJ e CSLL | Fluxo de caixa | detalhe | movimento do ano | sempre negativo / todos os anos |
| FLU - Distribuição para Acionista | Dividendos e outras distribuições pagas aos acionistas | Fluxo de caixa | detalhe | movimento do ano | sempre negativo / todos os anos |
| FLU - Geração de Caixa | Variação do caixa no ano. Cálculo: Receita + Tributos + Custos + Investimentos + Entradas + Despesas Financeiras + Imposto de Renda + Distribuição para Acionista | Fluxo de caixa | resultado | movimento do ano | positivo em 57%, negativo em 43% / todos os anos |
| FLU - Saldo Final | Caixa no fim do ano. Cálculo: Saldo Inicial + Geração de Caixa | Fluxo de caixa | saldo | saldo de caixa | sempre positivo, exceto 1 registro negativo / todos os anos |
| BAL - Dividendos Antecipados | Dividendos pagos antes do fim do exercício. Reduz o patrimônio líquido, por isso tem sinal oposto às demais contas do grupo | Patrimônio líquido | detalhe | saldo no fim do ano | sempre positivo / ausente nos anos 1, 2 e 12 |
