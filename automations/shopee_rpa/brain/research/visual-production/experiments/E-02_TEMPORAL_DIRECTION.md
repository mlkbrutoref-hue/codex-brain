# E-02 — Temporal Direction

**STATUS:** `READY / NOT_RUN`  
**GOLDEN SCENE:** GS-C atomic open-and-hold  
**INDEPENDENT VARIABLE:** representation of the same temporal semantics.

## Research question

Qual forma de descrever exatamente a mesma ação produz melhor instruction adherence, motion/timing coherence, continuity e completion?

## HYPOTHESIS

O state model poderá melhorar ordem e final state em relação à prosa natural. Timestamps explícitos não são presumidos melhores e podem não produzir aderência adicional.

## Semantic event lock

Todas as conditions exigem os mesmos eventos:

1. início: drawer fechado, mão no puxador;
2. movimento: puxar em linha reta pelo trilho;
3. fim: drawer aberto no limite;
4. hold final.

Não adicionar approach, remover prop, fechar, camera motion ou segunda ação.

## CONDITION TD-A — NATURAL_DESCRIPTION

Uma frase natural contínua descreve os quatro eventos em ordem, sem headings e sem segundos.

## CONDITION TD-B — STATE_MODEL

O mesmo conteúdo é estruturado como:

```text
INITIAL STATE
ACTION
FINAL STATE
```

Vocabulário e quantidade de informação permanecem equivalentes à TD-A; apenas a representação muda.

## CONDITION TD-C — EXPLICIT_TIMING

Os mesmos eventos recebem intervalos baseados na duração `D` selecionada no preflight:

```text
0–0.25D: initial state
0.25D–0.75D: linear pull
0.75D–D: final state and hold
```

Na execução, as frações são convertidas para segundos exatos da duração suportada e congelada. Não se escolhe uma duração diferente para acomodar esta condition.

## INPUT / frozen variables

- mesma GS-C version, refs e start state;
- mesma string semântica para sujeito, produto, ambiente, câmera e luz;
- mesmo model/mode/aspect/duration/resolution/output count;
- mesma action amplitude/eixo/final state;
- nenhum start/end frame diferente entre conditions;
- somente formatação temporal muda.

## EXPECTED RESULT

TD-B pode melhorar estado final; TD-C pode melhorar, não alterar ou piorar timing. Qualquer conclusão sobre timestamps depende dos outputs, não da documentação.

## METRICS

- required events completed and ordered;
- event-onset and event-end normalized by `D`;
- final-hold presence and approximate duration;
- `ACTION_ADHERENCE`;
- `TEMPORAL_COHERENCE`;
- `PHYSICAL_PLAUSIBILITY`;
- `CONTINUITY`;
- hard failures;
- blind pairwise preference for temporal clarity.

Timing coherence não exige frame-perfect adherence. Antes da execução, definir tolerância operacional relativa ao `D` e ao frame rate do output; não escolhê-la depois de ver resultados.

## PASS CRITERIA / decision

Uma representação é `SUPPORTED` como preferida somente com ≥3 valid runs/condition se:

- vence pelo menos 2 blocks e não perde o terceiro nos primary outcomes;
- preserva completion/final state;
- não aumenta hard failures nem reduz product/hand/physics guardrails;
- para TD-C, intervalos observados são materialmente mais próximos do plano, não apenas a ação “parece boa”.

Se nenhuma dominar, `INCONCLUSIVE`. Se timestamps não melhorarem ou piorarem coerência de forma confirmada, a hipótese “explicit timing ajuda” é `NOT_SUPPORTED` naquele escopo.

## FAIL CRITERIA

- conteúdo semântico diferente entre condições;
- uma condition recebe mais detalhe físico/câmera/luz;
- duração/configuração muda;
- evaluator vê headings/variant identity antes do score;
- inferir suporte a timestamps apenas porque um run coincidiu.

## Repetitions and early stop

- screening: 2 runs × 3 conditions = 6 outputs;
- confirmation: +1 por condition ainda competitiva; ceiling de 3 outputs para confirmar todas;
- optional: +1/condition somente para hipótese temporal de alta prioridade;
- condition com 2 hard failures repetidos pausa; restante pode continuar se comparação ainda for válida.

## Blind procedure

Candidate IDs ocultam TD-A/B/C. O avaliador recebe o event lock e a duração, mas não o formato do prompt. A ordem das três conditions muda a cada block.

## Credit preflight

`screening_estimate = 6 * displayed_cost_per_output`.  
`confirmation_ceiling = 3 * displayed_cost_per_output`.  
Custo permanece `UNKNOWN_UNTIL_PREFLIGHT`.

## RESULT / DECISION

`RESULT: PENDING`  
`DECISION: PENDING`
