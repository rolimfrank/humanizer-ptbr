# Humanizer PT-BR

Skill para escrever e revisar respostas de chatbots em português brasileiro com
naturalidade, preservando fatos, condições, intenção e voz. Adaptação do
[Humanizer de blader](https://github.com/blader/humanizer), com foco conversacional.

A implementação está na branch **dexter-ptbr**. A branch **main** acompanha o original
e permanece em inglês. Esta v1 ainda não está integrada ao Dexter Agents.

## O que muda

- Fidelidade a valores, limites, negações, incerteza, responsáveis e estado das ações.
- Português brasileiro sem proibir gerúndio, sujeito subentendido, hífen ou travessão.
- Cordialidade, empatia, convites e despedidas conforme a função do turno.
- Continuidade com o histórico fornecido, sem perguntas e aberturas repetidas.
- Revisão que preserva mensagens boas e não cria ações, perguntas ou promessas.
- Saída final por padrão, sem expor rascunho e análise ao contato.
- Prompt compacto gerado a partir do núcleo da skill e 60 casos sintéticos de avaliação.

Não é detector de autoria por IA. Não substitui a estratégia de vendas, a KB ou as
políticas do agente. Os exemplos não descrevem preços ou recursos do Dexter.

## Usar a versão PT-BR

O caminho mais previsível é clonar a branch correta:

```bash
git clone --branch dexter-ptbr --single-branch https://github.com/frankrolim/humanizer-ptbr.git
cd humanizer-ptbr
npx skills add . --list
npx skills add .
```

Usar o instalador compatível com o seu agente. Para instalação manual, copiar a pasta
com `SKILL.md`, `references/` e `runtime/`; preservar caminhos relativos. Não copiar
apenas o SKILL.md se o agente precisar das referências.

Para Claude Code, adicionar o checkout local como marketplace e instalar o plugin:

```text
/plugin marketplace add /caminho/absoluto/humanizer-ptbr
/plugin install humanizer-ptbr@humanizer-ptbr
```

O nome da skill é `humanizer-ptbr`. Em clientes OpenAI compatíveis, invocar
`$humanizer-ptbr`; no plugin Claude, `/humanizer-ptbr:humanizer-ptbr`.
Fixar um commit/versão na integração do produto. Instalar o fork sem selecionar a
branch pode carregar o original inglês.

## Exemplos

| Entrada | Resultado possível |
|---|---|
| “Solicitamos que nos informe qual mensagem de erro é apresentada.” | “Qual mensagem de erro aparece?” |
| “Vou estar encaminhando seu pedido para análise.” | “Vou encaminhar seu pedido para análise.” |
| “Estamos analisando seu pedido.” | Manter: o gerúndio informa uma ação em andamento. |
| “O desconto vale na implantação, não na mensalidade.” | Manter: o contraste esclarece a condição. |
| “Obrigado, era só isso.”, em uma conversa encerrada | “Por nada!”; não criar outra oferta. |

Uma reescrita não deve transformar “pode reduzir” em “elimina”, “mais de 3.000” em
“3.000”, “não confirmado” em “não funciona” ou “vou verificar” em “verifiquei”.

## Conteúdo

| Arquivo | Uso |
|---|---|
| [SKILL.md](SKILL.md) | Instruções principais e fonte do núcleo conversacional. |
| [Critérios PT-BR](references/pt-br.md) | Adaptação rastreável dos 25 padrões do original. |
| [Conversas](references/conversas.md) | Exemplos e limites para atendimento. |
| [Prompt compacto](runtime/humanizer-ptbr.txt) | Texto autossuficiente para a chamada do chatbot. |
| [Integração](references/integracao.md) | Contexto de entrada, ordem de processamento e limites. |
| [Avaliações](evals/README.md) | Casos, comparação de variantes e avaliação humana. |
| [Upstream](upstream.json) | Versão e commit do original revisados neste fork. |

Os 25 critérios ficam na referência linguística; não são carregados automaticamente
na API. Usar o compacto na geração existente acrescenta entrada, sem exigir outra
chamada. Uma segunda revisão acrescenta consumo e latência. Medir tokens com o modelo
real; tamanho em caracteres não equivale a custo.

## Desenvolvimento e validação

```bash
python3 scripts/build-runtime.py
python3 scripts/validate-package.py
python3 -m unittest discover -s tests -v
python3 scripts/evaluate.py validate
npx skills add . --list
claude plugin validate .
```

Os scripts Python usam apenas a biblioteca padrão (Python 3.10+). O workflow fixa as
versões dos validadores externos. As verificações estruturais e literais não demonstram
que a skill melhora o atendimento; o protocolo de avaliação mede isso separadamente.

## Atualizações do original

Acompanhar `blader/humanizer` na `main`. Desenvolver PT-BR em `dexter-ptbr`; revisar
mudanças do upstream antes de incorporá-las à adaptação. A sincronização automática
da `main` não atualiza a tradução nem a versão compacta. Preservar `LICENSE` e a
atribuição original. O histórico Git mantém o código e as versões anteriores.

## Histórico

- **1.0.0** — Primeira adaptação conversacional PT-BR, baseada no Humanizer 3.0.0.
  Regras de fidelidade, 25 critérios contextualizados, exemplos brasileiros,
  perfil compacto derivado, identidade própria de instalação e avaliação offline.

## Origem e licença

Baseado no Humanizer, de Siqi Chen (blader), originalmente inspirado em
[Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing).
Adaptação PT-BR mantida por Frank Rolim. Licença [MIT](LICENSE), com atribuição
original preservada. A lista de padrões é uma referência editorial, não evidência
estatística de autoria ou frequência no português brasileiro.
