# Avaliação de conversas em PT-BR

O conjunto em `cases.jsonl` é sintético e público. Não contém conversas reais de clientes.
Cada caso traz operação, contexto, critérios semânticos e, quando necessário, trechos
que precisam permanecer literais. Não há uma única frase correta para cada situação.

## Preparar as entradas

```bash
python3 scripts/evaluate.py validate
python3 scripts/evaluate.py prepare --profile compact --output /tmp/compact-inputs.jsonl
python3 scripts/evaluate.py prepare --profile baseline --output /tmp/baseline-inputs.jsonl
python3 scripts/evaluate.py prepare --profile full --output /tmp/full-inputs.jsonl
git show 9862685f575c65a8247f90369951df1b3416e3d6:SKILL.md > /tmp/humanizer-original.md
python3 scripts/evaluate.py prepare --profile original --upstream-file /tmp/humanizer-original.md --output /tmp/original-inputs.jsonl
```

O exportador não envia os critérios esperados ao modelo. `full` inclui a skill e as
duas referências de escrita; é uma condição explícita de avaliação, não a recomendação
de carregar todos esses arquivos em cada turno de produção. Os arquivos em `/tmp` são
intermediários; conservar resultados úteis fora dali. Nenhum comando chama uma API.

Enviar as entradas ao modelo escolhido no ambiente autorizado. Usar o mesmo modelo,
parâmetros, histórico e limite de saída em cada condição. Registrar versão exata,
data, hash do prompt, parâmetros e consumo. Para medir custo, incluir tokens de cache
e todas as chamadas; o script só agrega as métricas básicas informadas.

Salvar uma linha JSON por resposta:

```json
{"case_id":"ptbr-001","variant":"compact","output":"texto produzido","model":"identificador real do modelo","parameters":{"temperature":0},"input_tokens":800,"output_tokens":30,"latency_ms":950}
```

Usar números reais, não estimativas; omitir métricas indisponíveis. Não usar os números
do exemplo como resultado. `parameters` registra apenas parâmetros aceitos pelo modelo.
Para repetições, manter arquivos separados por execução; não escolher só as melhores.

```bash
python3 scripts/evaluate.py score --responses /tmp/responses.jsonl --variants compact baseline --output /tmp/report.json
```

Falta de respostas é erro por padrão. `--allow-partial` identifica um ensaio parcial.
O relatório confere trechos literais e textos que devem permanecer intactos. Uma saída
pode passar e ainda inverter uma condição: estas verificações não são um juiz semântico.

## Avaliação humana

Apresentar saídas embaralhadas a pelo menos dois avaliadores brasileiros, sem nomes
das variantes. Manter uma chave separada para recuperar a condição depois. Usar o
mesmo caso e seus critérios; não premiar a reprodução de um exemplo.

| Dimensão | Como avaliar |
|---|---|
| Fidelidade | Reprovar se mudar fato, condição, negação, certeza, autoria ou estado da ação. |
| Intenção | Reprovar se adicionar ação, promessa, pedido ou convite não autorizado na revisão. |
| Português natural | Dar nota de 1 a 5 para fluidez e adequação brasileira; não exigir gíria. |
| Voz e cordialidade | Dar nota de 1 a 5 para adequação ao tom, à situação e ao público. |
| Continuidade | Verificar uso do histórico, ausência de perguntas repetidas e encerramento adequado. |
| Formato | Verificar saída limpa, variáveis, URLs, código, unidades e mensagens imutáveis. |

Não compensar uma falha crítica de fidelidade com uma nota alta de estilo. Registrar
divergências entre avaliadores e exemplos de regressão. Comparar por categoria, além
da média geral; repetir casos sensíveis para observar variação entre execuções.

## Antes da integração no Dexter

Exigir ausência de falhas críticas nos casos avaliados e revisar as regressões antes
de expandir o uso. Isso é um critério de lançamento, não prova de segurança absoluta.
Incluir conversas reais somente com autorização, anonimização e avaliação em ambiente
apropriado. Não publicar dados de clientes neste repositório.

A v1 contém infraestrutura e casos; testes de scripts não são evidência de ganho
comercial. Ensaios com agentes gerais também não validam o modelo/configuração do Dexter.

Os resultados e as limitações dos exercícios executados no desenvolvimento estão no
[registro de ensaios](smoke/README.md).
