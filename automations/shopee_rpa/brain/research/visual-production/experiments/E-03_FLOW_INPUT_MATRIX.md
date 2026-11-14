# E-03 — Google Flow Input Matrix

**STATUS:** `READY / NOT_RUN`  
**GOLDEN SCENE:** GS-D — Nina presents product  
**INDEPENDENT VARIABLE:** documented Flow input configuration.  
**PROVIDER SNAPSHOT:** 23/09/2026; `FAST_CHANGING`, refresh required before run.

## Research question

Quais inputs oficialmente suportados melhoram identidade, produto e aderência na mesma scene, e quais introduzem conflito ou custo sem benefício?

## Official evidence boundary

Documentação oficial atual declara criação por texto, ingredients/references e frames; visual ingredients podem representar personagem e objetos, inclusive múltiplos elementos. First frame e first+last frames são workflows documentados. Vídeo pode entrar como ingredient/referência; uploaded-video editing é também documentado, mas é outro workflow e não uma condition diretamente comparável à criação do zero.

Suporte varia por modelo/região/conta. A página oficial de features consultada em 23/09/2026 documenta text/frames/ingredients em modelos compatíveis e video-to-video editing no workflow compatível. A UI corrente decide execução.

Evidência: S-FLOW-01, S-FLOW-02, S-FLOW-03. Links oficiais: <https://support.google.com/flow/answer/16353334?hl=en>, <https://support.google.com/flow/answer/16352836?hl=en>, <https://support.google.com/labs/answer/16935718?hl=en>.

## Input matrix

`CREDIT_COST_IF_KNOWN` permanece `UNKNOWN_UNTIL_PREFLIGHT`; custo depende da configuração visível e não será fixado no Brain.

| ID | Input configuration | SUPPORTED_STATUS | DOCUMENTATION_EVIDENCE | EXPECTED_ADVANTAGE | EXPECTED_RISK | CREDIT_COST_IF_KNOWN | TEST_PRIORITY |
|---|---|---|---|---|---|---|---|
| IM-0 | `TEXT_ONLY` | `DOCUMENTED_SUPPORTED`, model-dependent | S-FLOW-01/03 | baseline; sem competição entre assets | baixa fidelidade à Nina/produto específico | unknown until UI | `MUST_RUN` |
| IM-1 | `PRODUCT_IMAGE_AS_INGREDIENT` | `DOCUMENTED_SUPPORTED_CONDITIONAL` | S-FLOW-01/03 | geometria/cor do produto | reference ignorada, background/estilo contaminante | unknown until UI | `MUST_RUN` |
| IM-2 | `PERSONA_IMAGE_AS_INGREDIENT` | `DOCUMENTED_SUPPORTED_CONDITIONAL` | S-FLOW-01/03 | identidade da Nina | produto ainda dependerá de texto; competing subject cues | unknown until UI | `USEFUL` |
| IM-3 | `PERSONA_PLUS_PRODUCT_IMAGES_AS_INGREDIENTS` | `DOCUMENTED_SUPPORTED_CONDITIONAL` | S-FLOW-01 documenta character/key object e múltiplos ingredients; S-FLOW-03 | identidade + produto na mesma geração | competição/blending entre refs, estilo/fundo incompatíveis | unknown until UI | `MUST_RUN` |
| IM-4 | `FIRST_FRAME` | `DOCUMENTED_SUPPORTED_CONDITIONAL` | S-FLOW-01/03 | fixa composição/estado inicial | motion ou identidade podem derivar depois do frame | unknown until UI | `USEFUL` |
| IM-5 | `FIRST_PLUS_LAST_FRAMES` | `DOCUMENTED_SUPPORTED_CONDITIONAL` | S-FLOW-01/03 | limita boundary states/final result | transição impossível, morph entre frames, frames incompatíveis | unknown until UI | `USEFUL` |
| IM-6 | `VIDEO_AS_INGREDIENT_REFERENCE` | `DOCUMENTED_SUPPORTED_CONDITIONAL` | S-FLOW-01 permite drag de image ou video como ingredient | movimento/style reference potencial | semântica/prioridade e aderência ainda unknown; pode confundir identidade/produto | unknown until UI | `OPTIONAL` |
| IM-7 | `UPLOADED_VIDEO_TO_VIDEO_EDIT` | `DOCUMENTED_SUPPORTED_SEPARATE_WORKFLOW`, model/region-dependent | S-FLOW-02/03 | preserva movimento/composição do source e altera atributo alvo | não é criação comparável; source domina e introduz outra causalidade | unknown until UI | `OPTIONAL / SEPARATE_PROTOCOL` |
| IM-X | “reference frame” sem papel | `NOT_A_DISTINCT_MODE` | docs distinguem ingredient, first e last frame | nenhum até o papel ser definido | comparação ambígua | n/a | `DO_NOT_RUN` |

“Product reference” e “persona reference” são papéis semânticos de ingredients, não dois modos oficiais diferentes. `REFERENCE_FRAME` deve ser operacionalizado como ingredient, first frame ou last frame; não pode permanecer rótulo vago.

## Current feature snapshot — not an execution contract

Na documentação consultada, modelos Veo compatíveis variam entre text, first frame, first+last e ingredients; o workflow Quality listado não aceita ingredients, enquanto outros listados aceitam. Gemini Omni compatível documenta text, frames, ingredients e video editing. Nomes, durações, resoluções e compatibilidades devem ser recapturados no preflight; não misturar modelos em uma comparison.

## HYPOTHESIS

Inputs visuais coerentes aumentarão fidelidade do atributo que representam, mas mais inputs não serão automaticamente melhores. First+last frames podem melhorar boundary adherence enquanto aumentam risco de transição quando os estados são distantes.

## Core comparison chain

Para preservar one-variable-at-a-time, não comparar todas as células entre si:

1. **P-track:** IM-0 vs IM-1 — adicionar somente product ingredient.
2. **I-track:** IM-1 vs IM-3 — adicionar somente persona ingredient, mantendo product ingredient.
3. **F-track:** IM-4 vs IM-5 — adicionar somente end frame.
4. **Persona isolation useful:** IM-0 vs IM-2 — adicionar somente persona ingredient.
5. **Video workflows:** IM-6 e IM-7 recebem protocolos separados; não entram no ranking core.

## INPUT / frozen variables

- GS-D, Nina/product assets e facts versionados;
- mesma ação curta, environment, camera, lighting, duration/aspect e output count;
- mesmo provider model dentro de cada track e apenas se suportar ambas conditions;
- prompt semanticamente equivalente; somente a diretiva mínima para apontar o input varia;
- ingredient files devem ter background/style compatíveis e hashes congelados;
- frames IM-4/IM-5 devem vir da mesma canonical scene design.

## EXPECTED RESULT

IM-1 pode melhorar product fidelity sobre IM-0; IM-3 pode melhorar identity sobre IM-1, com possível risco de blending; IM-5 pode melhorar final state sobre IM-4, mas não é presumido superior em motion/physics.

## METRICS

- `IDENTITY_FIDELITY` e identity drift;
- `PRODUCT_FIDELITY` por landmarks;
- input/reference adherence por papel;
- `ACTION_ADHERENCE`;
- `CONTINUITY` e `AI_ARTIFACTS`;
- hard failures;
- usable outputs / generated outputs;
- observed credits per output and per usable output.

## PASS CRITERIA / decision

Cada track recebe decisão própria; não existe “winner universal”. Um input addition é `SUPPORTED` quando, com ≥3 valid runs/cell:

- melhora o atributo-alvo em ≥2 blocks e o restante é tie;
- não piora hard failures/guardrails;
- o ganho compensa custo/complexidade observados naquele escopo.

Se o atributo não melhora, `NOT_SUPPORTED` para aquela scene/model/mode. Resultados mistos ou modelo incompatível são `INCONCLUSIVE`.

## Core repetitions and budget

Screening core econômico:

- IM-0, IM-1 e IM-3: 2 runs/cell = 6 outputs;
- se P-track e/ou I-track forem consistentes, +1 nas duas cells daquele track; como cells são compartilhadas, confirmation ceiling core = até 3 outputs adicionais, porém executar somente os necessários;
- F-track: 2 runs/cell = 4 outputs no tier `USEFUL`, +2 confirmation;
- IM-2 isolation: 4 screening outputs incluindo baseline compartilhável somente se provider snapshot/cohort forem idênticos;
- IM-6/IM-7: `OPTIONAL`, novo orçamento/protocolo.

Não reutilizar IM-0 de outro experimento se modelo, modo, data/coorte ou prompt base diferirem.

## Early stop

- feature/model indisponível ou Flow troca modelo → stop/`INCONCLUSIVE`;
- dois outputs ignoram totalmente o input-alvo → pausar cell e confirmar apenas com aprovação;
- references incompatíveis ou contaminadas → invalidar protocolo, não culpar o provider;
- hard failure repetido novo na multi-reference condition → pausar antes de mais credits.

## Blind procedure

Avaliação oculta input configuration e prompts. O avaliador conhece as canonical Nina/product references porque precisa medir fidelidade, mas não sabe quais foram fornecidas ao generator.

## RESULT / DECISION

`RESULT: PENDING`  
`DECISION: PENDING`
