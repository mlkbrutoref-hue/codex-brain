---
name: nina-reels-content-director
description: Transforme Product, ProductFacts, Platform e ContentGoal em um CreativePackage original para Reels narrativos de descoberta e demonstração da Nina, com score, roteiro desenvolvido, cenas, prompts para Google Flow, CTA, legenda, hashtags e conceito textual de capa. Use para direção criativa de vídeo da Nina; não use para posts estáticos, carrosséis, publicação ou geração real no Flow.
---

# Nina Reels Content Director

Crie um pacote criativo executável para um único Reel da Nina. A referência editorial informa a engenharia do conteúdo, nunca a execução literal.

## Escopo

Aceite `Product`, `ProductFacts` com `CONFIRMED_FACTS`, `Platform`, `ContentGoal` e referências visuais fornecidas. Entregue `ProductScore`, `ContentFormat`, `Hook`, `FinalScript`, `ScenePlan`, `FlowPrompt`, `NegativePrompt`, `OnScreenText`, `CTA`, `Caption`, `Hashtags`, `CoverConcept` e auditorias de segurança.

Não crie, proponha ou altere geradores de post estático, carrossel ou sistema de design. Mantenha:

```text
POSTS_MANUAL = TRUE
CAROUSELS_MANUAL = TRUE
REELS_CREATIVE_SKILL_READY = YES
FLOW_INTEGRATED_WITH_SKILL = NO
FLOW_GENERATIONS = 0
```

Defina `REELS_PIPELINE_INTEGRATED = YES` somente quando o pipeline real tiver executado `Product -> ProductFacts -> nina-reels-content-director -> CreativePackage` e os testes focados tiverem passado. Não use `REELS_AUTOMATED = YES` antes de existir integração autorizada com o Flow.

Esta skill prepara o pacote. Não publica, não abre geração e não clica em `Generate`. Só use uma ferramenta externa de geração quando o usuário pedir isso em outra etapa e autorizar a execução.

## Referências internas

- Leia [references/style-dna.md](references/style-dna.md) ao decidir formato, hook, takes, CTA e legenda.
- Leia [references/creative-package-schema.md](references/creative-package-schema.md) antes de estruturar ou validar a saída.
- Use `scripts/validate_creative_package.py` para validar pacotes JSON e `tests/test_validator.py` para regressão.

## Princípios editoriais

1. Mostre produto, problema ou efeito no primeiro quadro.
2. Use prova visual antes de explicação longa.
3. Mantenha o produto como elemento principal; Nina é curadora e âncora.
4. Faça o vídeo parecer UGC fotorealista, com luz e movimento humanos naturais.
5. Desenvolva uma promessa central em linguagem simples e concreta, usando contexto, demonstração, benefícios e objeções quando sustentados por fatos.
6. Termine com uma única ação.
7. Preserve a identidade da Nina. Não copie nome, logo, bordão, aparência, voz, figurino, cenário, thumbnail, capa ou roteiro do perfil de referência.

## Coerência com o perfil e prova visual

Um Reel de utilidade só pode ser recomendado quando a ação principal ou o resultado visual estiver confirmado. Título, foto do anúncio e Nina segurando ou apontando para o produto não contam como prova de funcionamento.

- Para produto funcional, exija `VISUAL_PROOF_BASIS = CONFIRMED_OPERATION` ou `CONFIRMED_RESULT`.
- Use `APPEARANCE_LED_REVEAL` apenas quando a aparência confirmada do produto for, por si só, a atração central; nunca para contornar mecanismo, uso ou resultado desconhecido.
- Se o apelo depender de operação, encaixe, transformação, antes/depois ou resultado ainda desconhecido, defina `PROFILE_COHERENCE_STATUS = FAIL`, `FLOW_PROMPT_READY = false`, `DECISION = RESEARCH_REQUIRED` e `RECOMMEND_REEL = false`.
- Registre em `RESEARCH_REQUIRED` a evidência exata que falta. O roteiro pode permanecer como rascunho, mas não deve ser apresentado como pronto para produção.
- Não aprove hooks de catálogo como “Isso aqui é...” ou “Olha este achado...” isoladamente. O hook precisa apontar para tensão, contraste, ação ou payoff visível e confirmado.
- Não substitua demonstração ausente por uma cena em que Nina apenas apresenta o produto.

## Fact safety

Use como fatos somente valores presentes em `CONFIRMED_FACTS`. Um nome de produto pode confirmar sua categoria lexical, mas não especificações ausentes.

Nunca invente preço, desconto, vendas, avaliação, potência, autonomia, bateria, capacidade, dimensões, material, resistência, acessórios, compatibilidade, velocidade, mecanismo específico, benefício clínico, desempenho ou resultado garantido.

Mantenha campos desconhecidos em `UNKNOWN_FACTS`. Não transforme desconhecimento em linguagem vaga que ainda implique um fato, como “superpotente”, “dura muito” ou “remove tudo”.

Inclua `FACT_LEDGER`: para cada afirmação factual do roteiro, cena, prompt, legenda ou capa, registre a chave exata em `CONFIRMED_FACTS`. Se uma afirmação não puder ser ligada a uma chave, remova-a.

Se a confiabilidade falhar, defina `DECISION = REJECT`, `FACT_SAFETY = FAIL` e não recomende Reel.

## Nina safety

Nina é uma personagem virtual curadora, não uma consumidora real alegando experiência própria. Proíba afirmações equivalentes a “eu comprei”, “eu testei”, “uso todo dia”, “chegou pra mim”, “resolveu minha vida” e “foi o meu resultado”.

Prefira “olha esse achado”, “encontrei esta opção”, “confere como funciona”, “olha isso em ação” e “uma opção interessante para...”. Se a cópia implicar vivência real inexistente, reescreva antes de marcar `NINA_SAFETY = PASS`.

## Product score

Pontue com justificativa específica:

| Critério | Máximo |
|---|---:|
| `VISUAL_PROOF` | 25 |
| `PROBLEM_CLARITY` | 20 |
| `CURIOSITY` | 15 |
| `AUDIENCE_BREADTH` | 10 |
| `COMPRESSIBILITY` | 10 |
| `ORIGINALITY` | 10 |
| `RELIABILITY` | 10 |

Some os sete critérios para obter `TOTAL` de 0 a 100.

- Se `RELIABILITY_STATUS = FAIL`, rejeite independentemente do total.
- Se `TOTAL < 70`, defina `RECOMMEND_REEL = false` e explique a limitação sem criar post ou carrossel.
- Se `TOTAL >= 70` e a confiabilidade passar, prossiga.

Uma nota mede adequação ao formato, não qualidade absoluta do produto. Não aumente `RELIABILITY` só para ultrapassar o corte.

`RELIABILITY` mede a qualidade e a cobertura da evidência, não apenas a ausência de invenções:

- `0–2`: dado ausente, inferido ou sem procedência verificável;
- `3–5`: fixture ou uma única fonte incompleta;
- `6–8`: registro estruturado e atual do provedor oficial, ainda com lacunas relevantes;
- `9–10`: múltiplas evidências oficiais atuais e concordantes, com cobertura dos fatos usados.

Uma resposta pode ser factualmente segura e ainda ter confiabilidade moderada ou baixa.

## Escolha do formato

Escolha por evidência, nunca aleatoriamente:

- `ANTES_DEPOIS`: há estados inicial e final visualmente confirmáveis.
- `TRANSFORMACAO`: o valor principal é uma mudança gradual ou expressiva confirmável.
- `PROBLEMA_SOLUCAO`: existe dor cotidiana clara e o fato confirmado liga o produto ao uso.
- `DEMONSTRACAO`: o funcionamento confirmado é visualmente interessante.
- `PRODUTO_CURIOSO`: forma ou mecanismo confirmado cria curiosidade real.
- `ACHADINHO_RAPIDO`: benefício simples e demonstrável em poucos segundos.

Registre `FORMAT_REASONING`. Na dúvida, escolha o formato que exige menos alegações e produz a prova visual mais clara.

Se nenhuma opção produzir prova visual confirmada e coerente com o perfil, não escolha um formato genérico para forçar aprovação: use `RESEARCH_REQUIRED`.

## Hook e roteiro

Faça o hook acontecer entre 0 e 1,5 segundo. Tipos permitidos: `PROBLEMA`, `CURIOSIDADE`, `DEMONSTRACAO`, `TRANSFORMACAO`, `DESCOBERTA`, `PERGUNTA` e `SURPRESA`.

Não comece com saudação, apresentação ou promessa genérica. “Uma ideia principal” significa uma dor ou desejo central, não uma fala de uma frase.

Construa um arco de venda conversacional, escolhendo os blocos que o produto sustenta:

`HOOK -> IDENTIFICAÇÃO DO PROBLEMA/DESEJO -> DESCOBERTA DO PRODUTO -> DEMONSTRAÇÃO -> BENEFÍCIOS E OBJEÇÕES -> PAYOFF/RESULTADO -> CTA`

O roteiro deve soar como uma amiga mostrando por que o achado merece atenção, com perguntas retóricas, observações concretas e progressão. Evite enumeração de catálogo, repetição do nome do produto e frases genéricas ligadas apenas por “olha”. Use de dois a quatro benefícios confirmados quando isso aprofundar a promessa central.

Registre `SCRIPT_STRUCTURE` com os beats usados e `SCRIPT_WORD_COUNT`. O texto falado precisa ocupar naturalmente a duração estimada, sem fala acelerada.

## Duração e takes

Escolha a duração editorial pela quantidade de argumento e prova disponíveis:

- `30–45 s`: um problema, uma demonstração central, dois ou três pontos de valor e CTA;
- `45–60 s`: contexto mais desenvolvido, demonstração em etapas, benefícios e uma objeção;
- `60–90 s`: micro-história ou descoberta, demonstração completa, múltiplas provas, objeções e payoff.

Use `VIDEO_DURATION_TARGET` em uma dessas faixas. O padrão de referência é narrativo; não reduza automaticamente o Reel a 8–10 segundos.

Separe duração editorial de limitação técnica. Defina `FLOW_TAKE_DURATION_TARGET = 5–10 s` e decomponha o Reel em 4–12 takes curtos que, montados, formem o vídeo de 30–90 segundos. Cada take precisa corresponder a um beat narrativo e acrescentar informação, prova ou reação.

Inclua `MULTI_TAKE_JUSTIFICATION` explicando como os takes sustentam a progressão, não apenas por que o Flow tem limite de duração.

## Scene plan

Para cada cena, especifique tempo, ação de Nina, ação e posição do produto, enquadramento, câmera, ambiente, luz, fala/áudio e fatos que sustentam a cena.

Se não houver imagem de referência do produto, declare que `PRODUCT_FIDELITY` depende de referência futura. Não invente botões, cores, acessórios ou geometria.

## Prompt para Google Flow

Escreva uma direção mestre e um prompt autocontido por take, com a identidade da Nina definida pelo projeto, continuidade visual, produto fiel à referência, ambiente, ação, interação, enquadramento, câmera, luz, expressão, movimento humano natural, duração, 9:16 e trecho de fala correspondente.

Priorize `PHOTOREALISTIC`, `UGC`, `NATURAL_LIGHT`, `REALISTIC_HUMAN_MOTION` e `PRODUCT_FIDELITY`. Não peça ao Flow para renderizar textos complexos. Defina texto para pós-produção.

O prompt precisa ser executável com a evidência já disponível. Nunca instrua o Flow a “verificar”, “confirmar” ou decidir condicionalmente o modo de uso durante a geração. Se essa verificação ainda for necessária, mantenha `FLOW_PROMPT_READY = false` e não envie o pacote para geração.

O `NegativePrompt` deve incluir: `CGI, 3D render, plastic skin, doll appearance, deformed hands, extra fingers, product deformation, floating objects, impossible motion, AI-looking background, unreadable text, logos not present in reference`.

## Texto na tela e CTA

Forneça `ON_SCREEN_TEXT_START` curto e `ON_SCREEN_TEXT_END = COMENTA QUERO`. Presuma aplicação posterior no pipeline.

CTA padrão: `Quer o link? Comenta QUERO.` Não use “link na bio”, “clica na sacola” ou “link aqui embaixo” sem nova instrução explícita.

## Legenda, hashtags e capa

Escreva legenda curta em três blocos: benefício/curiosidade confirmada, CTA `Comenta QUERO` e hashtags. Gere de quatro a oito hashtags semânticas, preferencialmente seis. Proíba `#fyp`, `#fy` e `#viral`.

O conceito textual de capa deve fornecer `COVER_TITLE`, `COVER_SUBTITLE`, `PRODUCT_POSITION` e `NINA_POSITION`. Produto dominante, texto curto e leitura rápida; não gere a imagem.

## Verificação final

Antes de entregar:

1. compare cada fato com `CONFIRMED_FACTS`;
2. confirme a soma do score;
3. confirme formato baseado no produto;
4. confirme que a duração editorial está entre 30 e 90 segundos e que os takes curtos cobrem todo o arco;
5. revise experiência pessoal falsa;
6. confirme CTA `QUERO` e hashtags permitidas;
7. confirme ausência de post/carrossel;
8. registre `FLOW_GENERATIONS = 0` até autorização separada.
9. confirme `PROFILE_COHERENCE_STATUS = PASS` e uma base real de prova visual antes de recomendar o Reel;
10. confirme que o `FlowPrompt` não contém instruções condicionais de verificação.
11. confirme que o roteiro tem progressão narrativa e densidade de fala compatível com a duração, sem virar apresentação de catálogo.

No projeto real, `scripts/build_creative_package.py` é o transformador determinístico usado pelo adaptador do pipeline. Quando houver JSON, rode `python scripts/validate_creative_package.py caminho\pacote.json`. Entregue o CreativePackage e aguarde aprovação antes de integrar geração real.
