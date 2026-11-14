# E-04 — UGC Believability

**STATUS:** `READY / NOT_RUN`  
**GOLDEN SCENE:** GS-D — Nina presents product  
**INDEPENDENT VARIABLE:** categorical `capture_style_profile`.

## Research question

Qual capture-style profile faz a mesma geração parecer mais um vídeo social real gravado por celular, sem degradar produto, Nina ou clareza?

## Causal limitation

Cada profile é um pacote deliberado. E-04 pode concluir qual pacote funciona melhor, não qual componente isolado causou o resultado. Se um profile vencer, follow-ups devem isolar camera movement, DOF, lighting ou imperfection amplitude um de cada vez.

## HYPOTHESIS

O profile `REALISTIC_SMARTPHONE_CONTROLLED` será mais social-native que o polished/cinematic. Imperfeições casuais mais fortes podem ajudar até um limite, mas podem reduzir legibilidade ou parecer erro.

## Frozen scene

- mesma Nina, produto, one-hand hold, amplitude e final state;
- mesmo quarto/banheiro e composição sem espelho;
- mesma duração/aspect/model/mode/refs/output count;
- mesmo creative intent e produto visível;
- nenhuma fala, copy, música ou edição.

## CONDITION UGC-A — POLISHED_CINEMATIC

- composição precisa e simétrica;
- câmera muito estável com movimento deliberado mínimo;
- key/fill mais controladas e separação mais publicitária;
- DOF mais rasa, mantendo ainda produto e rosto legíveis;
- pele/acabamento polidos, sem pedir artificialidade.

## CONDITION UGC-B — REALISTIC_SMARTPHONE_CONTROLLED

- eye-level/phone-distance plausível;
- câmera estática ou micro-handheld estabilizado muito leve;
- composição funcional levemente orgânica;
- janela/practical motivadas, DOF moderada, pele com textura natural;
- foco/exposição estáveis no gesto principal.

## CONDITION UGC-C — STRONGER_CASUAL_IMPERFECTIONS

Parte de UGC-B e aumenta somente o parâmetro composto `casual_imperfection_level`:

- microderiva handheld mais perceptível, ainda limitada;
- framing discretamente off-center;
- breve settle motivado de foco/exposição antes da ação, nunca durante a prova;
- timing corporal ligeiramente menos ensaiado.

Não inclui resolução baixa, blur inútil, horizonte quebrado, shake caótico, focus hunting, flicker, clipping ou produto ilegível.

## INPUT

- GS-D scene freeze e references idênticas;
- três prompts com diff limitado ao capture-style block;
- base action/environment descriptions idênticas;
- technical output configuration idêntica.

## EXPECTED RESULT

UGC-B pode superar UGC-A em human-recorded/social-native impression. UGC-C pode superar B se as imperfeições permanecerem motivadas, ou perder se virarem distração/erro.

## METRICS

### Primary

- `HUMAN_RECORDED_IMPRESSION`: `PASS` quando um avaliador cego considera plausível ter sido capturado por pessoa/celular, sem artefato dominante;
- `CAMERA_PLAUSIBILITY`;
- `LIGHTING_PLAUSIBILITY`;
- `SKIN_PLAUSIBILITY` dentro de identity review;
- `UGC_BELIEVABILITY`;
- AI-look indicators marcados: floating camera, plastic skin, perfect symmetry, unmotivated studio light, extreme bokeh, motion viscosity, CGI surface.

### Guardrails

- `IDENTITY_FIDELITY`;
- `PRODUCT_FIDELITY`;
- `ACTION_ADHERENCE`;
- product visibility/readability;
- `AI_ARTIFACTS` e hard failures.

## PASS CRITERIA / decision

Um profile é `SUPPORTED` como default provisório se, com ≥3 valid runs/profile:

- vence em pelo menos 2 blocks e empata no restante para UGC believability/human-recorded impression;
- não reduz identity/product/action guardrails;
- não aumenta hard failures;
- segundo avaliador cego confirma a conclusão potencial.

Se B e C forem equivalentes, preferir B por menor risco/complexidade, mas registrar resultado como `NOT_SUPPORTED` para “imperfeições mais fortes ajudam”. Se A vencer, a hipótese inicial é `NOT_SUPPORTED` naquele escopo.

## FAIL CRITERIA

- mudar ação, environment, input mode ou refs entre profiles;
- C usar defeitos proibidos como “autenticidade”;
- julgar apenas frame estático ou preferência estética sem playback;
- atribuir vitória a um componente individual do pacote sem follow-up.

## Repetitions and early stop

- screening: 2 runs × 3 profiles = 6 outputs;
- confirmation: +1 por profile competitivo, ceiling 3 outputs;
- optional: +1/profile apenas para empate de alto valor;
- profile com dois hard failures ou product/identity regressions repetidos é pausado.

## Blind procedure

Evaluator vê candidatos em ordem aleatória e não recebe os termos “cinematic”, “controlled” ou “imperfections”. Depois da rubric absoluta, responde: “Qual clip parece mais plausivelmente gravado por uma pessoa para social?” e justifica com indicadores visíveis.

## Credit preflight

`screening_estimate = 6 * displayed_cost_per_output`.  
`confirmation_ceiling = 3 * displayed_cost_per_output`.  
Custo permanece `UNKNOWN_UNTIL_PREFLIGHT`.

## RESULT / DECISION

`RESULT: PENDING`  
`DECISION: PENDING`
