# E-05 — Contextual Risk Profile

**STATUS:** `READY / NOT_RUN`  
**CORE GOLDEN SCENE:** GS-B hand/product  
**USEFUL EXTENSIONS:** GS-C product/physics; GS-D identity/product  
**INDEPENDENT VARIABLE:** addition of one contextual mitigation block targeted to one predeclared risk.

## Research questions

1. O risk profile previsto antes da geração identifica onde failures aparecem?
2. Uma mitigação contextual reduz o failure-alvo sem criar regressões?
3. As bands `NONE/LOW/MEDIUM/HIGH/CRITICAL` são úteis para decidir estratégia, sem score mágico?

## HYPOTHESIS

Mitigação curta, específica e ligada ao risco diminuirá failures-alvo em relação ao base prompt. Giant generic negatives não são necessários e podem adicionar conflito.

## Important scope

A amostra pequena não calibra probabilidades universais das cinco bands. E-05 valida primeiro direção e utilidade operacional. `CRITICAL` continua sendo design gate: default é redesenhar, não gastar créditos para provar que uma cena crítica falha.

## Part A — Predictive risk logging

Antes de ver outputs, congelar para cada golden scene:

- band por eixo e evidência/trigger;
- target failure esperado;
- mitigation candidate;
- QA checkpoints;
- fallback/redesign;
- compound risks.

Após a avaliação, comparar predicted vs observed failure types. Nunca ajustar a previsão retroativamente; mudança cria nova version.

## Part B — Pairwise mitigation tests

### E05-HAND — `MUST_RUN`, GS-B

**BASE:** prompt completo sem bloco defensivo de mãos, além da ação necessária.  
**CONTEXTUAL MITIGATION:** acrescentar somente:

- uma mão direita ativa;
- zona lateral de grip definida;
- polegar oposto aos dedos, contato contínuo;
- face crítica do produto permanece desocluída;
- produto apoiado até o grip se estabelecer.

**Target outcomes:** `HAND_CORRECTNESS`, occlusion e product contact.  
**Guardrails:** product fidelity, action adherence, camera/light.

### E05-PRODUCT_PHYSICS — `USEFUL`, GS-C

**BASE:** ação de puxar drawer, sem bloco adicional de mecanismo.  
**CONTEXTUAL MITIGATION:** acrescentar somente:

- estrutura superior fixa;
- gaveta mantém geometria e translação em eixo único sobre o trilho;
- três props acompanham a gaveta sem duplicar/mover sozinhos;
- parar no limite aberto.

**Target outcomes:** product morph, physics, continuity.  
**Guardrails:** hands, action completion, framing.

### E05-IDENTITY — `USEFUL`, GS-D

**BASE:** Nina e produto descritos/referenciados sem ledger adicional.  
**CONTEXTUAL MITIGATION:** acrescentar somente invariantes canônicas de identidade estritamente necessárias e continuidade de rosto/cabelo/roupa ao longo do take.

**Target outcomes:** identity fidelity/drift.  
**Guardrails:** product fidelity, action, naturalness.

### Future material risks — `OPTIONAL`

Reflection, liquid e cloth exigem protocolos próprios quando houver assets/facts e orçamento. Não combiná-los com E05-HAND no mesmo prompt e chamar o resultado de causal.

## INPUT / frozen variables

- mesma golden scene version, refs, facts e input mode dentro de cada pair;
- mesmo model/mode/duration/aspect/resolution/output count;
- prompt diff contém apenas o mitigation block;
- nenhuma generic negative list adicionada ao variant;
- risk band é definida antes dos outputs e não revelada ao evaluator.

## EXPECTED RESULT

Mitigation pode reduzir failure-alvo, não ter efeito ou introduzir overconstraint/conflito. Todas as três possibilidades são válidas.

## METRICS

- target criterion `PASS/REVIEW/FAIL`;
- target hard-failure count/type;
- non-target guardrail criteria;
- overall usability;
- prompt/input adherence;
- pairwise preference fundamentada no target, não estética;
- credits per output and usable output;
- predicted-vs-observed risk match.

## Risk-band interpretation under test

| Band | Design meaning | Evidence needed later |
|---|---|---|
| `NONE` | eixo ausente da cena | zero target events/failures; não prova taxa universal zero |
| `LOW` | failure pouco plausível e sem compound trigger | failures raros na coorte; QA padrão suficiente |
| `MEDIUM` | interação presente, mas simples/visível | review/hard failure ocasional; mitigation/check específico pode ajudar |
| `HIGH` | failure compromete cena e há trigger forte/compound | target failures/reviews recorrentes; simplificação/mitigation melhora utilidade |
| `CRITICAL` | combinação pode invalidar conceito/custo | redesign obrigatório por política; execução só em protocolo isolado aprovado |

Não inferir percentuais com a amostra desta etapa. Bands só são recalibradas após acumular Project Learnings de várias cenas.

## PASS CRITERIA / decision

Uma mitigation é `SUPPORTED` para seu risco/cena se, com ≥3 valid runs/condition:

- variant melhora target criterion em pelo menos 2 blocks e o terceiro é tie;
- target hard failures não aumentam;
- nenhum guardrail crítico piora;
- prompt não impede ação natural nem cria aparência artificial material.

`NOT_SUPPORTED` se não reduz target failures ou causa regressão repetida. Mixed effect = `INCONCLUSIVE`.

O risk model como um todo só pode ser chamado de calibrado depois de múltiplas scenes/cohorts; E05 inicial pode no máximo `SUPPORT` eixos/mitigações específicos.

## FAIL CRITERIA

- mitigation muda câmera, luz, action complexity ou input mode;
- mais de um risk axis é mitigado no mesmo pair core;
- base prompt remove a descrição mínima necessária e vira strawman;
- avaliação conhece qual prompt é “safer”;
- giant negative prompt substitui contexto;
- hard failure é excluído como “azar”.

## Repetitions and early stop

Por pair:

- screening: 2 runs/condition = 4 outputs;
- confirmation: +1/condition = 2 outputs;
- optional: +1/condition apenas para decisão de alto valor;
- pausar após dois target hard failures idênticos na mesma condition ou qualquer factual/safety failure.

Portfolio:

- `MUST_RUN`: E05-HAND screening 4, confirmation ceiling +2;
- `USEFUL`: E05-PRODUCT_PHYSICS e E05-IDENTITY, cada um 4 +2;
- `OPTIONAL`: material-specific protocols, orçamento separado.

## Blind procedure

Evaluator recebe a action/facts/acceptance checks, mas não risk band, target mitigation ou prompt. O target criterion é avaliado como parte da rubric comum antes da pairwise preference.

## Credit preflight

Core screening: `4 * displayed_cost_per_output`.  
Core confirmation: `2 * displayed_cost_per_output`.  
Cada useful extension exige aprovação independente. Custo permanece `UNKNOWN_UNTIL_PREFLIGHT`.

## RESULT / DECISION

`RESULT: PENDING`  
`DECISION: PENDING`
