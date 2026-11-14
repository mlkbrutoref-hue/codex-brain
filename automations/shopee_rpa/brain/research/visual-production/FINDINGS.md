# Visual Production — Findings

**RESEARCH_DATE:** 23/09/2026  
**Capability scope:** transformar intenção criativa, fatos do produto, Nina e referências aprovadas em uma descrição filmável/gerável, fisicamente plausível, social-native e verificável.  
**Status do conhecimento:** `DESIGN_RESEARCHED`; implementação continua `PARTIAL`/`PLANNED` conforme a subcapability.

## WHAT WE KNOW

### 1. Planejamento de cena e ação

- **[DOCUMENTED; S-FILM-02, S-FILM-03, S-FILM-05]** Uma cena legível precisa de blocking e estados espaciais, não apenas de uma intenção como “Nina usa o produto”. O plano deve declarar sujeito, produto, ambiente, relação espacial, ação observável e estado final.
- **[DOCUMENTED; S-FLOW-07]** Para vídeos gerados curtos, uma cena/momento principal reduz ambiguidade. Várias ações sequenciais competindo no mesmo take aumentam risco de ação omitida ou incompleta.
- **[INFERRED]** A forma operacional mais clara é: `INITIAL_STATE -> APPROACH -> CONTACT/GRASP -> PRIMARY_MOTION -> SETTLE/RELEASE -> FINAL_STATE`. Etapas sem mudança visual relevante podem ser omitidas; ações complexas devem virar mais de um clip.
- **[INFERRED]** Toda instrução de movimento deve ter agente, verbo, objeto/alvo, trajetória/eixo, limite e resultado. “Move naturalmente” é insuficiente; “a mão direita segura o corpo rígido pelo centro, a esquerda gira a tampa no sentido anti-horário até ela se separar” é verificável.
- **[INFERRED]** Conflitos são evitados com prioridades explícitas: produto/fato e anatomia > ação principal > legibilidade > câmera > atmosfera. Se duas instruções disputarem a mesma variável, a cena precisa ser reescrita ou dividida.

### 2. Produto visível e demonstração compreensível

- **[OBSERVED; S-UGC-02, S-UGC-03, S-UGC-04]** Conteúdo social-commerce recorrente mostra o produto cedo, em uso e no momento de prova, em vez de depender de um establishing shot genérico.
- **[INFERRED]** `ProductVisibility` precisa identificar quais superfícies são críticas: mecanismo, botão, tampa, textura, aplicação, resultado ou marca quando autorizado. Mãos e corpo podem ocluir partes secundárias, não o mecanismo que prova a ação.
- **[INFERRED]** Quando a pegada plausível esconde a função, a correção é trocar ângulo, rotação do produto ou etapa de demonstração — nunca pedir uma pegada anatomicamente impossível.

### 3. Câmera e composição

- **[DOCUMENTED; S-FILM-01, S-FLOW-06]** O plano de câmera pode ser descrito por tamanho do plano, ângulo/altura, posição/distância relativa, perspectiva, composição, movimento, foco/DOF e comportamento de exposição/white balance.
- **[DOCUMENTED; S-CAMERA-01, S-CAMERA-02]** Focal, distância, abertura e perspectiva interagem. Números exatos de lente não garantem um resultado em geradores; a intenção visível deve acompanhar qualquer termo técnico.
- **[INFERRED]** Default UGC para produto: câmera na altura dos olhos ou da bancada, distância humana de celular, perspectiva moderadamente ampla/normal, produto e mãos legíveis, profundidade de campo moderada/alta e movimento estático ou handheld leve.
- **[INFERRED]** Close/insert serve para mecanismo e textura; medium contextualiza Nina usando; wide só quando ambiente/transformação espacial importam. Extreme close e DOF rasa são escolhas, não sinônimos de qualidade.
- **[DOCUMENTED; S-PHONE-01, S-PHONE-02, S-PHONE-03]** Autofocus, autoexposure, white balance, estabilização/crop e rolling shutter fazem parte do comportamento possível de smartphone.
- **[INFERRED]** “Casual” não significa tecnicamente ruim. Pequena deriva handheld, microcorreção motivada e enquadramento humano ajudam; tremor, focus hunting, horizonte instável e exposição pulsante prejudicam credibilidade e prova.

### 4. Photorealism versus believable social video

- **[INFERRED a partir de S-PHONE-01..03 e S-UGC-01..05]** `PHOTOREALISM` é plausibilidade de superfície/frame: pele, geometria, luz, material e detalhe. `BELIEVABLE_SOCIAL_VIDEO` acrescenta coerência temporal, captura plausível por telefone, gesto humano, ambiente cotidiano, linguagem da plataforma, prova compreensível e ausência de perfeição publicitária desmotivada.
- Um frame pode ser fotorrealista e o vídeo ainda parecer IA por movimento viscoso, simetria perfeita, câmera flutuante, pele excessivamente lisa, oclusão impossível, objeto que muda ou demonstração sem força/contato.
- **[INFERRED]** O objetivo padrão do projeto é `BELIEVABLE_SOCIAL_VIDEO`; acabamento cinematográfico entra apenas quando a direção criativa o exige e não sacrifica autenticidade/função.

### 5. Iluminação doméstica traduzida para especificação

- **[DOCUMENTED; S-LIGHT-01, S-LIGHT-02]** Luz deve ser descrita como fontes motivadas com direção, qualidade, cor e intensidade relativa. Luz mista pode produzir casts distintos; uma white balance global não neutraliza todas as regiões.
- **[DOCUMENTED; S-MAT-01, S-MAT-02]** Sombra, reflexão e refração precisam responder às fontes, orientação e material.
- **[INFERRED]** `LightingSpec` mínimo: fonte dominante, fontes secundárias/practicals, direção, qualidade (soft/hard), família de cor, prioridade de exposição para pele/produto, comportamento esperado de sombras/reflexos e continuidade.
- Exemplo cozinha/geladeira: janela lateral = key suave dominante; teto = fill ambiente mais fraco; interior da geladeira = practical local que ilumina rosto/produto do lado da porta. O fundo distante não deve receber arbitrariamente a mesma luz interna; reflexos no plástico/metal precisam acompanhar essas fontes. Pele e rótulo não podem clipar.
- Traduções recorrentes:
  - **cozinha/bancada:** janela lateral suave + teto ambiente; highlights controlados em metal/vidro;
  - **banheiro/espelho:** practical frontal/superior real, risco de múltiplos reflexos e cast misto;
  - **sala/quarto:** janela ou abajur motivado, fundo ligeiramente menos exposto, sem key invisível de estúdio;
  - **área externa:** céu/sol como fontes físicas, sombra coerente e exposição adaptada ao contraste.

### 6. Materiais e comportamento físico

| Material | Comportamento relevante | Regra visual/temporal | Evidência |
|---|---|---|---|
| plástico rígido | forma estável; brilho depende do acabamento | não amassar/flexionar sem mecanismo | `INFERRED` de mecânica/material; óptica `DOCUMENTED` em S-MAT-01 |
| plástico transparente | reflexão + transmissão/refração; bordas legíveis | preservar contorno, conteúdo e distorção coerente do fundo | `DOCUMENTED`, S-MAT-01 |
| vidro | rígido, transparente, highlights especulares | não parecer plástico leitoso nem deformar durante pegada | `DOCUMENTED` óptica + `INFERRED` aplicada |
| metal | opaco, forte resposta ao ambiente, rigidez | highlight/reflexo muda com orientação, sem textura “derretendo” | `DOCUMENTED`, S-MAT-02 |
| tecido | deformável, dobras, stretch/compression, damping | pontos de pegada ancoram; gravidade e movimento propagam dobras | `DOCUMENTED`, S-MAT-04 |
| líquido | fluxo contínuo, gravidade, viscosidade, coesão/adesão | fonte e volume persistem; gotas/menisco e velocidade combinam com material | `DOCUMENTED`, S-MAT-03 |
| madeira | corpo rígido, grão pertence à superfície | padrão não desliza independentemente da geometria | óptica `INFERRED` |
| borracha | grip e deformação elástica limitada | comprime na força e recupera forma; não vira tecido/líquido | `INFERRED`, precisa teste por produto |
| glossy | reflexo especular e highlights definidos | reflexos seguem fonte/câmera/superfície | `DOCUMENTED`, S-MAT-01/02 |
| matte | reflexão mais difusa | highlight amplo/fraco, microtextura estável | `DOCUMENTED`, S-MAT-01 |

Material real e composição específica devem vir de `ProductFacts`; a direção não pode inferir “vidro” ou “à prova d'água” por aparência.

### 7. Interação humano-produto

- **[DOCUMENTED; S-HAND-01, S-HAND-02]** Tipo de grip e força dependem de tamanho, peso/dinâmica e precisão da tarefa. Objetos grandes/pesados pedem power grip/duas mãos ou apoio; controles pequenos pedem precision grip.
- **[DOCUMENTED; S-HAND-03]** Decompor manipulação por mão, objeto e ambiente torna o movimento verificável.
- **[INFERRED]** Campos mínimos: mão ativa, mão de suporte, posição/pontos de contato, affordance usada, eixo/curso, suporte ambiental, força qualitativa, oclusão permitida e estado de release.
- Exemplos:
  - **botão:** produto apoiado; ponta do indicador se aproxima, contacta uma vez, percorre pequeno curso e recua; indicador/feedback visível se factual;
  - **tampa:** uma mão estabiliza o corpo, outra segura a tampa; declarar twist/flip/pull, eixo e estado final;
  - **gaveta:** estrutura permanece ancorada; mão no puxador; translação sobre trilho; conteúdo não atravessa parede;
  - **líquido:** recipiente sustentado, rotação progressiva, fluxo começa no bico e termina antes de retornar à vertical;
  - **tecido/roupa:** duas mãos em pontos separados para mostrar queda/elasticidade; corpo e tecido mantêm contato/oclusão plausíveis;
  - **objeto pequeno:** precision pinch visível, macro moderado, mão apoiada quando necessário.

### 8. Direção temporal

- **[DOCUMENTED; S-FLOW-07]** Um momento principal por clip é mais confiável que uma cadeia longa. Em I2V, descrever mudança/movimento sem reescrever a imagem reduz contradição.
- **[INFERRED]** O `TemporalPlan` deve usar fases relativas mesmo sem timestamps: estado inicial, início, progressão, conclusão, hold do resultado e estado final.
- **[UNKNOWN]** Não há garantia oficial encontrada de aderência do Flow a intervalos exatos como `0.0–1.0s`.
- **[INFERRED]** Beat windows são úteis internamente para roteiro, edição e QA. O adapter só deve emitir timestamps literais se experimento por modo/modelo comprovar ganho. Antes disso, usar ordem clara, uma ação dominante e start/end frames quando disponíveis.

### 9. Continuidade

- **[DOCUMENTED; S-FILM-02, S-FILM-04, S-AIV-01]** Continuidade inclui posição, screen direction, blocking, composição, identidade, fundo e ação — não apenas rosto.
- O `ContinuitySpec` deve congelar:
  - identidade/aparência da Nina, cabelo, roupa e acessórios;
  - identidade, geometria, cor, escala e estado do produto;
  - mão ativa, grip, lado do frame, eyeline e direção de movimento;
  - layout de props/ambiente;
  - fontes de luz, direção de sombra, WB e exposição;
  - estado inicial herdado e estado final oferecido ao próximo take.
- **[INFERRED]** Mudanças deliberadas precisam de evento visível ou corte. Sem evento, são drift.

### 10. Falhas de vídeo por IA

- **[DOCUMENTED; S-AIV-01..04]** Consistência temporal, múltiplos objetos, relações espaciais, ações, permanência/oclusão, colisões e fluidos são dimensões separadas de risco.
- **[OBSERVED; S-FLOW-09]** Alguns operadores relatam controles/referências ignorados ou comportamento alterado após updates; incidência e causa não são conhecidas.
- **[INFERRED]** Risco cresce com duração, oclusão, múltiplas mãos/objetos, manipulação fina, transparência/reflexo, líquido/tecido, estados inicial/final muito distantes e movimento simultâneo de câmera+sujeito+ambiente.
- **[UNKNOWN]** A causa interna de face drift, dedos extras, morphing ou teleporte não pode ser inferida da saída. O projeto registra gatilho correlacionado e resposta, não pseudoexplicação do modelo.
- Prevenção geral: referência limpa, estado explícito, ação atômica, produto desocluído, câmera mais simples em interação de alto risco, clip curto, start/end frame quando adequado e opção de redesign.
- Detecção: comparar primeiro/meio/último e frames de contato; checar identidade, contagem, geometria, escala, cor, grip, colisão, permanência, sombra/reflexo, fluxo e estado final.

### 11. Google Flow: universal versus provider-specific

**Universal/provider-independent:** intenção, blocking, estado espacial, ação, câmera desejada, luz motivada, material/física, tempo relativo, continuidade, referências aprovadas, riscos, invariantes e checks de aceitação.

**Google Flow/provider-specific e `FAST_CHANGING`:** modelo disponível, modo text/image/video-to-video, ingredients, start/end frames, suporte de aspect/duração/resolução, camera controls, prompt/negative format, Scenebuilder, extensão/edição e custo/créditos.

O Flow é `REQUIRED_CURRENT_PRODUCTION_PROVIDER` e hoje é operado manualmente, com preparação parcial local. Ele continua arquiteturalmente substituível. A documentação confirma recursos, mas a combinação ótima para cada classe de cena requer experimento.

### 12. Análise de vídeo de referência

- **[DOCUMENTED; S-REF-01, S-REF-02]** Shot detection e análise por frame/shot ajudam a indexar, mas mudanças de luz/movimento podem gerar limites falsos.
- Modelo futuro de análise:
  1. registrar origem, direitos/permissão e objetivo;
  2. normalizar metadados sem destruir o original;
  3. detectar candidatos de scene/shot boundary e revisar;
  4. extrair keyframes inicial, crítico e final, mais amostras em eventos;
  5. separar movimento da câmera, sujeito, produto e ambiente;
  6. anotar `SHOT_GRAMMAR`, `CAMERA_GRAMMAR`, `MOVEMENT_GRAMMAR`, `LIGHTING_CHARACTER`, `SUBJECT_BEHAVIOR`, `PRODUCT_INTERACTION`, `SCENE_PROGRESSION`, `EDITING_RHYTHM` e `HOOK_STRUCTURE`;
  7. distinguir padrões reutilizáveis de identidade, marca e composição copiável;
  8. produzir `ReferenceDNA` com timestamps, evidência e confiança.
- **[INFERRED]** Fatos do produto e identidade canônica da Nina sempre vencem uma referência incompatível.

### 13. Padrões observados no nicho

- **[OBSERVED; S-UGC-01..05]** Padrões repetidos: produto/problema/resultado no primeiro momento; mãos ou pessoa dando escala; demonstração curta; progressão problema → mecanismo → resultado; close/medium funcional; luz cotidiana; resultado sustentado; UI-safe framing.
- Cozinha/casa enfatizam função, transformação espacial e before/after verificável; beleza enfatiza textura/aplicação e evita promessa não sustentada; moda/acessório enfatiza fit, movimento e múltiplas formas de uso.
- **[UNKNOWN]** Esses padrões não garantem performance e envelhecem rápido. Seleção deve usar pesquisa de tendência atual quando o job for `TREND_SELECTED`.

## WHAT SEEMS TO WORK

1. Uma ação dominante por clip, com estado inicial/final e hold do resultado.
2. Movimento descrito separadamente para câmera, pessoa, produto e ambiente.
3. Referência limpa para identidade/produto; texto não contradiz o frame.
4. Câmera simples quando mãos, líquido, vidro ou tecido já concentram risco.
5. Composição orientada à prova: função visível durante contato e transformação.
6. Luz doméstica motivada, com direção/sombra/reflexo verificáveis.
7. “Phone-like” expresso por perspectiva, altura, estabilidade e comportamento plausível, não por ruído aleatório.
8. Decomposição física do gesto e grip apropriado à tarefa.
9. Continuidade como ledger de atributos e estados entre clips.
10. QA temporal em pontos críticos, não aprovação pelo thumbnail mais bonito.

Itens 1 e 3 têm suporte oficial do provider; os demais combinam princípios documentados com aplicação `INFERRED` e precisam de benchmark no contexto do projeto.

## WHAT IS UNCERTAIN

- aderência atual do Flow a timestamps literais e beat windows;
- confiabilidade relativa de ingredients, start/end frames e camera controls por modelo/conta/região;
- limite prático de quantas referências preservam identidade e produto sem competição;
- comportamento do Flow atual para mãos, tampas, trilhos, líquidos, vidro, metal e tecido;
- se repetir câmera/lente em linguagem técnica melhora ou piora cenas I2V específicas;
- taxa de drift da Nina e de morphing de produto por duração, oclusão e tipo de movimento;
- quais imperfeições aumentam autenticidade sem reduzir confiança/conversão;
- relação entre padrões observados e performance no público real do projeto;
- thresholds úteis do risk profile e política de retry/redesign;
- análise automatizada suficiente para continuidade sem falso positivo relevante.

## WHAT NEEDS TESTING

1. **Ação atômica vs. multi-etapa:** mesma cena/fatos/referências; comparar aderência, anatomia e conclusão.
2. **Temporal syntax:** ordem em prosa vs. fases rotuladas vs. timestamps; medir evento e estado final.
3. **Inputs do Flow:** text-only vs. ingredient vs. start frame vs. start/end frames nos modos atuais.
4. **Camera strategy:** estática vs. handheld leve vs. movimento controlado durante manipulação.
5. **Referências:** quantidade, limpeza de fundo, consistência visual e prioridade Nina/produto.
6. **Mãos:** botão, twist cap, slide drawer, pour e fabric stretch, isoladamente.
7. **Materiais:** glossy/matte, metal, vidro/transparente, líquido e tecido sob a mesma luz.
8. **UGC look:** estabilização perfeita vs. microderiva limitada; DOF moderada vs. extrema; luz prática vs. comercial.
9. **Continuidade multi-clip:** identidade, roupa, mão ativa, posição do produto, luz e direção de tela.
10. **Risk profile:** calibrar níveis com taxa de aprovação, retries, custo e motivos de rejeição.

Todo teste futuro deve registrar modelo/modo/data/configuração, inputs, custo conhecido, seeds quando expostos, outputs completos e avaliação cega quando viável.

Em 23/09/2026, os protocolos E-01 a E-05, golden scenes, rubric, hard failures, budget, storage e promotion flow foram desenhados em `experiments/`. O status permanece `NOT_RUN`: nenhum finding abaixo foi promovido por evidência experimental.

## Gate de expertise — 12 respostas

| Pergunta | Resposta de design | Evidência principal |
|---|---|---|
| 1. Como planejamos uma cena? | Intenção + estados espacial/visual inicial e final + blocking + ação atômica + resultado/prova + checks. | seções 1–2; S-FILM-02..05 |
| 2. Como descrevemos câmera? | Plano, altura/ângulo, posição/distância, perspectiva, composição, movimento, foco/DOF, exposição/WB e intenção observável. | seção 3; S-FILM-01, S-FLOW-06, S-CAMERA-01/02 |
| 3. Como descrevemos luz? | Fontes motivadas, dominância, direção, qualidade, cor, exposição, sombras/reflexos e continuidade. | seção 5; S-LIGHT-01/02, S-MAT-01/02 |
| 4. Como descrevemos movimento? | Agente + verbo + alvo + trajetória/eixo + progressão + limite + estado final; movimentos separados por entidade. | seções 1 e 8; S-FLOW-07 |
| 5. Como descrevemos interação física? | Mão ativa/suporte, grip, contatos, apoio, força, eixo, oclusão, material e release. | seções 6–7; S-HAND-01..03 |
| 6. Como controlamos continuidade? | Ledger de identidade, produto, roupa, espaço, grip, screen direction, props, luz e handoff de estados. | seção 9; S-FILM-02/04, S-AIV-01 |
| 7. Quais erros são mais prováveis? | Drift/morph, mãos, contagem/permanência, física, reflexo/sombra, mudança de fundo/roupa/luz e movimento artificial. | seção 10 e `FAILURE_MODES.md` |
| 8. Como mitigamos? | Simplificar, desocluir, referenciar, encurtar, reduzir movimentos concorrentes, usar boundary frames e redesenhar cenas críticas. | seção 10; S-FLOW-01/07, S-AIV-01..04 |
| 9. O que é universal? | Intenção, direção de cena, física, câmera/luz desejadas, continuidade, riscos, invariantes e QA. | seção 11 |
| 10. O que é específico do Flow? | Modelo/modo, ingredients/frames, formatos/duração, controles, prompt syntax, Scenebuilder e custos. | seção 11; S-FLOW-01..08 |
| 11. O que ainda não sabemos? | Confiabilidade e limites atuais por modo/material, timestamps, referências, thresholds e efeito de imperfeições. | `WHAT IS UNCERTAIN` |
| 12. O que precisará de experimento? | Dez famílias de teste controlado, começando por ação temporal, inputs e gestos/materiais críticos. | `WHAT NEEDS TESTING` |

**EXPERTISE_GATE:** `PASS`. Há evidência suficiente para capability design e contrato conceitual. O gate não autoriza implementação, não torna o runtime `READY` e não transforma táticas provider-specific não testadas em best practices.
