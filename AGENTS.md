# Manutenção do Humanizer PT-BR

Trabalhar na branch `dexter-ptbr`. A `main` acompanha o original inglês e não recebe
customizações PT-BR. Não alterar o Dexter Agents neste repositório.

## Fontes de verdade

- `SKILL.md`: finalidade, modos e núcleo conversacional.
- `references/pt-br.md`: 25 critérios ligados aos padrões do upstream 3.0.0.
- `runtime/humanizer-ptbr.txt`: gerado; editar o núcleo no SKILL.md e reconstruir.
- `evals/cases.jsonl`: situações sintéticas, critérios semânticos e trechos protegidos.
- `upstream.json`: commit efetivamente revisado, não apenas o mais recente disponível.

Manter um único SKILL.md na raiz e o loader do plugin em `./`. Não duplicar as regras
em um segundo prompt mantido à mão. Não adicionar regras de vendas específicas de
uma empresa à skill geral. Não publicar dados de clientes ou credenciais.

## Alterações

Preservar fatos, condições, incertezas, objetivos e estados de ações. Exemplos devem
obedecer às próprias regras: nenhuma fonte, pesquisa, prazo ou implementação inventada.
Não tratar toda palavra formal ou pontuação como defeito. Preservar construções boas.

Manter a versão em `metadata.version`, plugin, upstream.fork_version e primeira
entrada do histórico do README. Os números dos critérios ficam na referência, de 1
a 25; uma mudança de mapeamento exige revisão da documentação e do validador.

Quando adaptar atualizações do original, comparar o commit registrado com o novo,
incorporar apenas mudanças compreendidas e registrar a nova base após avaliação.
Preservar atribuição e licença original. Usar português claro na documentação.

## Validação antes de publicar

Executar `python3 scripts/build-runtime.py --check`, `python3 scripts/validate-package.py`,
`python3 -m unittest discover -s tests -v`, `python3 scripts/evaluate.py validate`,
`npx skills add . --list` e `claude plugin validate .`.
Se um validador externo não estiver disponível, tentar a versão fixada no workflow e
informar o resultado real; não substituir por uma alegação de validação.

Em mudanças substanciais, usar sessões independentes para exercícios realistas,
fornecendo somente as instruções e os dados, sem critérios esperados. Guardar resultados
e limitações. Não equiparar testes de scripts ou de outro agente a testes no Dexter.
Não usar checagem de palavras como substituto de avaliação semântica.
