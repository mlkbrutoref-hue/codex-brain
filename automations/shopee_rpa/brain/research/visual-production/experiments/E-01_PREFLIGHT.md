# E-01 — Pre-flight Record

**PREFLIGHT_DATE:** 23/09/2026  
**EXPERIMENT:** E-01 — Action Complexity  
**GOLDEN_SCENE:** GS-C — physics / mecanismo  
**STATUS:** `BLOCKED_FACTS_AND_ASSETS / NOT_READY / NOT_RUN`  
**PRE_FLIGHT_BLOCKED:** `YES`

> **FOLLOW-UP 23/09/2026:** este registro continua correto como fotografia do primeiro pre-flight. A etapa posterior de aquisição de evidências selecionou o produto real `ITEM_ID 58267960935 / SHOP_ID 1234187269` e passou os gates factual e visual. O resultado abaixo não é editado retroativamente: o próximo passo é repetir o pre-flight completo com esse SKU. Ver `evidence/E-01/DECISION.md`.

Este registro documenta o gate de produto do primeiro pre-flight real. A regra de parada foi aplicada antes de criar prompts, congelar configuração do Flow, preparar runs ou abrir uma geração. Nenhum vídeo foi gerado e nenhum crédito foi gasto.

## 1. Gate aplicado

Antes de qualquer prompt, o produto precisava ter evidência suficiente para confirmar:

1. função exata;
2. funcionamento exato;
3. zona correta de grip;
4. partes móveis;
5. partes estáticas;
6. interação física visualmente verificável;
7. referências visuais oficiais/autorizadas suficientes para preservar geometria e mecanismo.

Nenhum produto real já presente nos assets/dados do projeto passou por todos esses checks. Portanto, conforme o protocolo solicitado, o trabalho parou neste gate.

## 2. Auditoria dos candidatos existentes

| Candidato | Evidência encontrada | Motivo da rejeição para GS-C |
|---|---|---|
| Mini processador 250 ml — `product_id 22849182312`, `shop_id 392019481` | `data/products/sample_product.json`; URLs remotas de imagem; descrição de botão, lâminas e copo | O arquivo é carregado pelo `LocalFixtureShopeeProvider` e é usado como `sample_product` nos testes/offline. Não há originais de produto persistidos localmente nem prova live confiável para validar o SKU, a geometria, a zona de grip e o mecanismo exato. Não pode ser promovido de fixture a fato real. |
| Escova de limpeza elétrica 12 em 1 — `product_id 58261505729`, `shop_id 1661007426` | Consulta LIVE preservada em `output/reels_creative_live_escova/product.json` e uma imagem oficial em `output/reels_creative_live_escova/qa/official_product.jpg` | A própria base aprovada registra `mecanismo de operação`, `detalhes dos acessórios` e `desempenho de limpeza` como desconhecidos. O roteiro vigente proíbe ativar, desmontar ou mostrar resultado. Uma imagem composta não é suficiente para provar qual parte gira, como cada cabeça fixa ou qual grip é correto durante ativação. |
| Touca de cetim com tubos | Frames produzidos em `output/nina-touca-video/` | Não há `ProductFacts` rastreáveis suficientes para função/mecanismo e não é o mecanismo rígido de translação da GS-C. |
| Produtos estáticos de bolsas/beleza/placa | Pesquisa ou imagens isoladas | Não oferecem uma interação física mecanicamente verificável e decomponível sem introduzir claims ou trocar a golden scene. |

## 3. Resultado da validação factual

| Check obrigatório | Estado | Evidência necessária para desbloquear |
|---|---|---|
| `PRODUCT_IDENTITY` | `FAIL` | SKU real selecionado e registro live/primário rastreável. |
| `EXACT_FUNCTION` | `FAIL` | Fonte oficial que descreva a função usada na cena. |
| `OPERATING_MECHANISM` | `FAIL` | Manual, anúncio oficial detalhado ou sequência oficial que demonstre o mecanismo. |
| `GRIP_ZONE` | `FAIL` | Referência visual mostrando onde a mão segura durante a ação. |
| `MOVING_PARTS` | `FAIL` | Vistas suficientes para identificar eixo/trilho/encaixe e limites de curso. |
| `STATIC_PARTS` | `FAIL` | Referência que fixe estrutura, suporte e partes que não devem mover. |
| `VISUALLY_VERIFIABLE_INTERACTION` | `FAIL` | Evidência de estado inicial, transição mecânica e estado final do mesmo SKU. |
| `REFERENCE_COVERAGE` | `FAIL` | Arquivos oficiais/autorizados, preservados localmente, cobrindo frente, lateral e mecanismo. |

`FACTS_VALIDATED = NO`.

## 4. Itens deliberadamente não produzidos

Para não contornar o gate nem fabricar certeza, não foram criados:

- base scene congelada para um SKU;
- prompts `E01_ATOMIC_PROMPT` e `E01_MULTISTEP_PROMPT`;
- hashes ou manifest de referências inexistentes;
- configuração/custo do Flow apresentada como executável;
- mapa cego `E01-R01..E01-R04`;
- formulários de runs ou outputs vazios que aparentem uma execução preparada;
- pasta de runtime `experiments/visual-production/E-01/`.

A rubric existente em `SCORING_RUBRIC.md` continua sendo a ficha normativa futura. Ela já contém os critérios pedidos, ratings `PASS / REVIEW / FAIL`, precedência de hard failures e campos mínimos de avaliação cega, mas não foi instanciada porque não existem candidatos válidos.

## 5. Cena e ações — somente intenção de protocolo

Estas definições continuam sendo templates, não variáveis congeladas nem prompts prontos:

- **BASE_SCENE:** GS-C, câmera 3/4 lateral estática, mecanismo de translação legível, estrutura fixa e curso visível. `NOT_FROZEN` enquanto não houver SKU e referências aprovados.
- **ATOMIC_ACTION:** mão segura o puxador, desliza a gaveta em eixo único até o limite aberto e sustenta o estado final.
- **MULTISTEP_ACTIONS:** segurar puxador → abrir → soltar puxador → pegar um prop → retirar → recolocar o mesmo prop → segurar novamente → fechar até o limite.
- **RISK PROFILE PROVISÓRIO:** hand `MEDIUM`, product morph `HIGH`, physics `HIGH`, identity `NONE`, continuity `HIGH`. Não é baseline congelada de um produto real.

## 6. Preflight validation

| Item | Estado |
|---|---|
| `PRODUCT_FACTS_VALID` | `NO` |
| `ASSETS_VALID` | `NO` |
| `NINA_REFERENCE_VALID` | `N/A` — GS-C enquadra apenas mão/antebraço; nenhuma referência deve ser selecionada antes do produto |
| `VARIABLES_FROZEN` | `NO` |
| `PROMPTS_READY` | `NO` |
| `RISK_PROFILE_READY` | `NO` — somente perfil teórico da golden scene |
| `FLOW_CONFIG_KNOWN` | `NO` — checagem operacional não executada após o gate de parada |
| `CREDIT_COST_KNOWN_OR_EXPLICITLY_UNKNOWN` | `YES — UNKNOWN` |
| `STORAGE_READY` | `NO` — somente este registro de bloqueio foi criado |
| `EVALUATION_READY` | `PARTIAL` — rubric normativa existe; formulários/candidates não foram instanciados |

## 7. Condições mínimas para reabrir o pre-flight

1. adicionar aos dados do projeto um produto real adequado à GS-C, com SKU/URL e fonte primária;
2. preservar localmente imagens oficiais/autorizadas suficientes para frente, lateral, trilho/eixo, puxador/grip e estados aberto/fechado;
3. registrar fatos explícitos sobre função, mecanismo, partes móveis/estáticas e uso permitido;
4. somente então congelar a cena, gerar os dois prompts, verificar a interface atual do Flow, ler o custo exibido e preparar os quatro IDs cegos.

## 8. Resultado obrigatório

```text
E01_PREFLIGHT_READY: NO
SELECTED_PRODUCT: NONE — nenhum produto real existente no projeto passou o gate factual e visual da GS-C
WHY_THIS_PRODUCT: N/A — selecionar o fixture ou a escova exigiria inferir mecanismo não validado
FACTS_VALIDATED: NO
BASE_SCENE: GS-C permanece apenas como template; NOT_FROZEN
ATOMIC_ACTION: template — segurar o puxador, deslizar em eixo único até abrir e sustentar
MULTISTEP_ACTIONS: template — segurar, abrir, retirar um prop, recolocar o mesmo prop, segurar novamente e fechar
VARIABLES_FROZEN: NO
REFERENCE_INPUTS: NONE APPROVED — faltam referências oficiais/autorizadas do produto e do mecanismo
FLOW_MODE: NOT_CHECKED_DUE_TO_PRODUCT_GATE
FLOW_MODEL: NOT_CHECKED_DUE_TO_PRODUCT_GATE
CREDIT_COST_PER_OUTPUT: UNKNOWN
SCREENING_OUTPUTS: 4
SCREENING_TOTAL_COST: UNKNOWN
ATOMIC_PROMPT_PATH: NOT_CREATED
MULTISTEP_PROMPT_PATH: NOT_CREATED
RISK_PROFILE: THEORETICAL_ONLY — hand MEDIUM; product morph HIGH; physics HIGH; identity NONE; continuity HIGH
STORAGE_PATH: brain/research/visual-production/experiments/E-01_PREFLIGHT.md; runtime storage NOT_CREATED
BLOCKERS: produto real GS-C ausente; função/mecanismo/grip/partes móveis e estáticas não validados; cobertura visual oficial insuficiente
SAFE_TO_EXECUTE: NO
```
