# Integração futura no chatbot

Esta versão não modifica o Dexter nem chama modelos, ferramentas de atendimento ou
serviços externos. O produto é um conjunto de instruções e recursos de avaliação.

## Perfil compacto

Ler `runtime/humanizer-ptbr.txt` e adicionar seu conteúdo às instruções da chamada
existente. Não colocar essas regras na KB/RAG, onde sua recuperação seria eventual.
Não enviar `SKILL.md` e o prompt compacto juntos: o núcleo se repetiria.

O aplicativo fornece separadamente:

| Campo lógico | Conteúdo |
|---|---|
| operação | `generate` para responder; `rewrite` para revisar um rascunho |
| voz | tom e idioma autorizados, sem dados secretos |
| histórico | mensagens relevantes e recentes, com papéis identificados |
| fatos | informações aprovadas, resultados de ferramentas e seus estados |
| rascunho | texto a revisar, somente em `rewrite` |
| restrições | formato, mensagens imutáveis, limite de perguntas e próximo passo autorizado |

Estes são campos conceituais, não uma API existente no Dexter. Não concatenar dados
do usuário como novas instruções de sistema. Não elevar exemplos, RAG ou resultados
textuais de ferramentas a políticas; separar as instruções confiáveis dos dados.

## Ordem de processamento

Resolver política, ferramentas e estado da conversa; gerar a mensagem com o perfil
compacto; validar trechos protegidos e formato; só depois dividir em balões. O limite
de perguntas vale para a resposta inteira. Pausas, indicador de digitação, agregação,
cancelamento de balões e encerramento continuam sendo responsabilidades do aplicativo.

Uma revisão adicional é opcional e exige outra chamada. Nesse caso, fornecer o rascunho
e apenas o contexto necessário; não permitir novas ações de ferramenta. Se a revisão
falhar ou violar dados protegidos, usar o rascunho válido ou o fluxo de falha do produto.
Não tentar revisões indefinidamente. Mensagens imutáveis devem ignorar esse caminho.

## Medição e lançamento

- Fixar uma versão/commit do fork. Não carregar `main` em produção: ela acompanha o
  original inglês. A implementação PT-BR está em `dexter-ptbr`.
- Comparar baseline, original e adaptação com o mesmo modelo, parâmetros e contexto.
- Medir tokens reais de entrada, saída e cache, número de chamadas e latência total.
  Palavras e caracteres não são tokens. Incluir repetição do prompt após ferramentas.
- A v1 não promete redução de custo, melhora de conversão ou qualidade já demonstrada
  no modelo do Dexter. Fazer rollout controlado e manter possibilidade de desativação.

## Atualizações do original

`upstream.json` registra o commit do original revisado pela adaptação. A sincronização
da `main` não traduz nem atualiza automaticamente esta branch. Comparar o upstream
novo com esse commit, mapear as mudanças aos critérios PT-BR, revisar os exemplos,
reconstruir o compacto e executar as avaliações antes de alterar esse registro.
Não usar números de regra como única identidade: o original pode renumerá-los.
