# Ensaios iniciais da v1

Data: 2026-09-19. Execução em sessões de agentes independentes para as condições
completa e compacta. Os agentes receberam instruções e entradas, sem critérios esperados.
As tarefas foram agrupadas por sessão; isso não equivale a chamadas de modelo isoladas
com parâmetros de amostragem controlados. Modelo de produção do Dexter não foi usado.

## Primeira rodada

24 casos distintos, em duas variantes: 48 respostas registradas em
[initial-responses.jsonl](initial-responses.jsonl). As entradas e os critérios estão
em [cases.jsonl](../cases.jsonl). Nenhuma falha nas verificações literais; revisão
qualitativa feita pelo agente implementador, sem avaliação humana cega.

O caso ptbr-018 revelou uma falha de estilo na variante compacta: a frase de efeito
foi transferida para a abertura como alegação de diferencial. A variante completa
removeu o fecho redundante. As duas preservaram as restrições comerciais, os estados
de ação, os trechos imutáveis e os pedidos de silêncio nos casos executados.

Hash SHA-256 do compacto usado nesta rodada:
`0b047a4b85f98f5775781f24251705e10fa7e649084904e249d85276dd1b1a5a`.

O núcleo foi ajustado para explicitar a remoção de frases de efeito redundantes,
sem transferi-las para a abertura ou inventar diferenciação. Foi a única mudança
nas instruções de escrita entre as duas rodadas.

## Verificação do ajuste

Quatro entradas novas, em uma terceira sessão independente, somente com o compacto.
Os dois fechos vazios foram removidos; os dois contrastes informativos foram preservados.
Ver [entradas](final-inputs.jsonl) e [respostas](final-responses.jsonl).

Hash SHA-256 do compacto final:
`c64679c680a13977a087669afc143f5ce99ef657899250e908afaf5e29629eaa`.

Não houve repetição completa dos 60 casos após o ajuste. O ensaio cobre regressões
pontuais e não demonstra superioridade sobre o original ou sobre um modelo sem skill.
Não houve medição confiável de custo, latência ou conversão, nem teste com clientes.

## Verificações do pacote

- 12 testes Python dos scripts passaram.
- Validação estrutural, referências e geração do compacto passaram.
- Os 60 casos sintéticos passaram na validação de estrutura.
- `skills@1.5.20 add . --list` descobriu a skill `humanizer-ptbr`.
- Claude Code 2.1.237 validou os manifests de plugin e marketplace.

Antes de usar no Dexter, executar o protocolo completo com o modelo, ferramentas,
contexto e orçamento reais. Tratar estes registros como evidência limitada de desenvolvimento.
