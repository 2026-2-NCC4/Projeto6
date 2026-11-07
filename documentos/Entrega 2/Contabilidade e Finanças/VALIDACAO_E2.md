# Validação financeira E2

Referência independente: dicionário e planilha avaliados na E1, preservados.
Implementação única: `src/cti/indicadores.py`. Agregação: média de cada conta por ano e depois razão dos componentes. Nunca somar cenários alternativos.

Execução CTI em 05/11, repetida em 06/11 e 07/11 com o mesmo resultado:
- 216 KPIs: 161 numéricos e 55 estados indisponíveis/pendentes, sem divergências.
- 24 identidades de balanço aprovadas.
- 168 células de entrada: 165 números e três ausências conferidos.
- Receita alterada deliberadamente em 10% faz a comparação reprovar.
- Não é um novo recálculo do Excel: comparação com valores salvos do recálculo validado na E1.

Para reproduzir, executar `python -m src.cti.executar_e2 --csv "src/data/raw/Demonstrativo Fecap v3.csv"`.
Verificação privada exige a mesma fonte E1; sem a base, os testes fictícios cobrem regras com resultados manuais conhecidos.

Novas regras:
- Ticket = receita simulada / quantidade hipotética positiva, no mesmo ano.
- Meta é um percentual acadêmico editável da receita original, convertido em reais. O padrão é a margem original do ano e da população selecionados: a meta volta a esse padrão quando o recorte muda e em Restaurar hipóteses. Desvio = margem simulada menos meta. Não representa orçamento da CTI.
- Receita simulada = R × (1 - desconto); custo assinado = C × (1 + variação).
- Margem = receita + custo; não substituir resultado líquido, tributos ou EBITDA por essa margem parcial.
- Exemplo fictício independente: R=100, C=-60, desconto=10%, custo=+20%, volume=10 e meta=20 resultam em margem 18, ticket 9 e desvio de -2.
- Zeros, ausências, limites e sinais inválidos têm teste de falha; não são convertidos silenciosamente para zero.

CAC de 4.000 reais, LTV de 45.000 reais e taxa de 10% mantêm as hipóteses E1. MVA segue indisponível sem valor de mercado. Ver PDF para unidades, fórmulas e interpretação.

Revisão de 07/11: comparação local de razão das médias, média das razões e mediana confirmou que representam estimadores diferentes. A regra da planilha E1 foi mantida. A alternativa Resultado Operacional menos Depreciação/Amortização assinada diverge do EBITDA fornecido; sem confirmação contábil, não se substitui a conta de origem. Sinais de PC e contas ausentes continuam identificados, sem imputação arbitrária.

O relatório PDF do painel reutiliza as médias do recorte e as fórmulas acima, registra hipóteses e fonte e foi conferido nos anos 1, 11 e 12 para as duas populações. O quadro de encerramento exibe contas separadas, não uma ponte de caixa; não se somam percentis marginais para construir uma trajetória.
