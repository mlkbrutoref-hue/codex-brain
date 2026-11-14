# E-01 — Action Complexity

**STATUS:** `EXECUTION_BLOCKED_FLOW_GENERATION_FAILURE / ZERO_OUTPUTS / ZERO_CREDITS_SPENT / NOT_RUN`  
**GOLDEN SCENE:** GS-C — sliding organizer drawer  
**INDEPENDENT VARIABLE:** number/dependency of actions in one clip.

O primeiro pre-flight real foi bloqueado no gate de produto em 23/09/2026. A aquisição de evidências posterior selecionou o SKU real `58267960935`, shop `1234187269`, porque seu mecanismo de bandeja inferior corrediça passou pelos gates factual e visual. O repeat pre-flight foi concluído em 24/09/2026: variante preta, originais/hashes, mecanismo, cena, props, mãos, câmera, luz, prompts, configuração atual do Flow, custo, quatro runs cegos e fichas de avaliação foram congelados. Ver `E-01_REPEAT_PREFLIGHT.md` e `experiments/visual-production/E-01/preflight/`. O experimento continua `NOT_RUN`: solicitações foram feitas, mas nenhum output experimental foi produzido e nenhum crédito foi gasto.

Uma execução foi autorizada em 24/09/2026 com teto de 80 créditos. O projeto Flow dedicado foi criado, a referência congelada foi anexada e o recheck posterior confirmou `Ingredients to Video / Veo 3.1 Fast / 8 s / 720p / 9:16 / x1 / 20 créditos`. Depois do bloqueio inicial de Flow Agent/reCAPTCHA, o usuário autorizou nova tentativa. O Flow aceitou duas solicitações de `E01-R01`, mas ambas falharam na etapa de áudio e exibiram que não houve cobrança. A segunda solicitação foi um `Retry` operacional sem nova confirmação; apesar de custo e outputs permanecerem em zero, isso infringiu a regra congelada contra regeneração automática e foi registrado como divergência. Nenhum vídeo/output foi criado; o prompt congelado não foi editado e `E01-R02..R04` não foram iniciados. Registro: `experiments/visual-production/E-01/execution/EXECUTION_STATUS.yaml`.

## Research question

O Flow executa mais confiavelmente uma ação atômica do que uma sequência multi-step em um único take?

## HYPOTHESIS

A condição atômica produzirá maior completion, plausibilidade física e correção de mãos, sem reduzir product fidelity.

## EVIDENCE GAP

A documentação recomenda foco em um momento principal, mas não mede o efeito no Flow atual, na cena GS-C ou com nossos assets.

## CONTROL — AC-A ATOMIC

Nina/mão já próxima ao puxador. A mão segura o puxador, puxa a gaveta em linha reta até o limite aberto e sustenta o estado final.

Eventos requeridos:

1. contact/grip;
2. linear pull;
3. open stop;
4. result hold.

## VARIANT — AC-B MULTI_STEP

Mesma cena/duração/configuração. A mão segura o puxador, abre a gaveta, remove um único prop, recoloca o mesmo prop e fecha a gaveta.

Eventos requeridos:

1. contact/grip;
2. linear pull/open;
3. release drawer and grasp prop;
4. remove;
5. replace same prop;
6. re-grasp drawer;
7. close/stop.

Esta diferença é deliberadamente a variável `action_complexity`. Produto, produto/prop count, ambiente, câmera, luz, refs, duration e provider config permanecem congelados.

## INPUT

- GS-C version/facts aprovados;
- mesma product reference e start state;
- mesma reference set, model/mode, aspect, duration, resolution e output count;
- mesma câmera estática e luz;
- prompts semanticamente iguais fora do bloco de ação;
- exatamente três props no drawer em ambas as conditions; no atomic eles permanecem intocados.

## EXPECTED RESULT

Resultado esperado pela hipótese, não presumido: AC-A completa todos os eventos e preserva mecanismo/mãos em maior proporção. AC-B pode omitir/reordenar fases ou introduzir continuity/hand failures.

## METRICS

**Primary:**

- required events completed / total;
- final state reached;
- `ACTION_ADHERENCE`;
- `PHYSICAL_PLAUSIBILITY`;
- `HAND_CORRECTNESS`;
- hard failures de contato, objeto, eixo e permanência.

**Guardrails:**

- `PRODUCT_FIDELITY`;
- `CONTINUITY` e prop count;
- `CAMERA_PLAUSIBILITY`;
- `OVERALL_USABILITY`;
- credits per output e per usable output.

## PASS CRITERIA / decision

Hipótese `SUPPORTED` somente após confirmação com pelo menos 3 runs válidos/condition quando:

- AC-A vence em pelo menos 2 blocks e o restante é `TIE`;
- AC-A não tem hard-failure disadvantage;
- diferença material aparece em completion e em pelo menos um de physics/hands/continuity;
- product fidelity não regride.

`NOT_SUPPORTED` quando AC-A não melhora completion/physics ou perde repetidamente. Qualquer padrão misto vira `INCONCLUSIVE`.

## FAIL CRITERIA

- variável congelada mudou → `INVALID_RUN`;
- drawer/product/reference/configuração diferentes entre conditions;
- AC-A introduz hard failure repetido ou não completa a ação;
- AC-B é julgado por não caber na duração sem a duração ter sido idêntica — isso continua um resultado válido da complexidade, não motivo de exclusão.

## Repetitions and early stop

- screening: 2 runs/condition = 4 outputs;
- confirmation: +1/condition = 2 outputs quando o screening é consistente;
- optional: +1/condition apenas para resultado importante 2–1/misto;
- pausar AC-B após dois hard failures do mesmo tipo; confirmação requer aprovação explícita.

## Blind procedure

Randomizar AC-A/AC-B dentro de cada block. Avaliador recebe somente candidate IDs, GS-C acceptance checks e rubric. Ele não sabe qual condição é “atomic”.

## Credit preflight

`screening_estimate = 4 * displayed_cost_per_output`.  
`confirmation_ceiling = 2 * displayed_cost_per_output`.  
Custo permanece `UNKNOWN_UNTIL_PREFLIGHT`.

## RESULT / DECISION

`RESULT: PENDING`  
`DECISION: PENDING`  
Nenhuma regra de ação atômica é promovida por este protocolo sozinho.
