# Validação financeira E2

Referência independente: dicionário e planilha avaliados na E1, preservados.
Implementação única: `src/cti/indicadores.py`. Agregação: média de cada conta por ano e depois razão dos componentes. Nunca somar cenários alternativos.

Execução CTI em 05/11:
- 216 KPIs: 161 numéricos e 55 estados indisponíveis/pendentes, sem divergências.
- 24 identidades de balanço aprovadas.
- 168 células de entrada: 165 números e três ausências conferidos.
- Receita alterada deliberadamente em 10% faz a comparação reprovar.
- Não é um novo recálculo do Excel: comparação com valores salvos do recálculo validado na E1.

Para reproduzir, executar `python -m src.cti.executar_e2 --csv "src/data/raw/Demonstrativo Fecap v3.csv"`.
Verificação privada exige a mesma fonte E1; sem a base, os testes fictícios cobrem regras com resultados manuais conhecidos.

Novas regras:
- Ticket = receita simulada / quantidade hipotética positiva, no mesmo ano.
- Meta é um percentual acadêmico editável da receita original, convertido em R$. O padrão é a margem original; desvio = margem simulada menos meta. Não representa orçamento da CTI.
- Receita simulada = R × (1 − desconto); custo assinado = C × (1 + variação).
- Margem = receita + custo; não substituir resultado líquido, tributos ou EBITDA por essa margem parcial.
- Exemplo fictício independente: R=100, C=−60, desconto=10%, custo=+20%, volume=10, meta=20 → margem18, ticket9, desvio−2.
- Zeros, ausências, limites e sinais inválidos têm teste de falha; não são convertidos silenciosamente para zero.

CAC R$4.000, LTV R$45.000 e taxa10% mantêm as hipóteses E1. MVA segue indisponível sem valor de mercado. Ver PDF para unidades, fórmulas e interpretação.
