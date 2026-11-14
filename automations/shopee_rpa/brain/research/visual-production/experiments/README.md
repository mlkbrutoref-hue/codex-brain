# Visual Production — Experimental Framework

**DESIGN_DATE:** 23/09/2026  
**STATUS:** `PROTOCOL_READY / NO_RUNS_EXECUTED`  
**PROVIDER UNDER TEST:** Google Flow, atual `REQUIRED_CURRENT_PRODUCTION_PROVIDER`  
**EVIDENCE CLASS BEFORE EXECUTION:** hipóteses `INFERRED` ou `UNKNOWN`; nenhum resultado `EXPERIMENTAL` existe ainda.

Este framework transforma os unknowns da deep research em comparações controladas. Ele não é contrato de runtime, não autoriza geração e não fixa permanentemente modelos, custos ou recursos do Flow.

## 1. Princípio causal

`ONE VARIABLE AT A TIME` é a regra de validade.

Cada protocolo define:

- `FROZEN_VARIABLES`: produto, referências, Nina, ambiente, ação semântica, duração, aspecto, câmera/luz base, creative intent, modelo/modo e output count;
- `INDEPENDENT_VARIABLE`: único fator alterado entre condições;
- `PRIMARY_OUTCOMES`: métricas diretamente ligadas à hipótese;
- `GUARDRAIL_OUTCOMES`: fidelidade, anatomia, física, custo e hard failures que não podem piorar silenciosamente;
- `KNOWN_CONFOUNDERS`: diferenças inevitáveis, como uma diretiva mínima para apontar um ingredient.

Se mais de uma variável material mudar, a execução é `INVALID_RUN`; ela não entra no resultado e só pode ser refeita após corrigir o protocolo. Repetir porque o take ficou feio é proibido: falha válida é dado.

## 2. Unidade experimental

- Um `run` corresponde a **um output clip**, não a um clique na interface.
- O default experimental futuro é `output_count = 1`. Se a UI exigir outro valor, o preflight recalcula custo e registra cada output como run separado, ligado ao mesmo request.
- Um `block` contém uma execução de cada condição, em ordem aleatorizada.
- Comparações são feitas dentro de blocks sempre que possível para reduzir drift de configuração/tempo.
- Seeds só são congelados se a UI realmente os expuser. Ausência de seed é registrada, nunca simulada.

## 3. Preflight obrigatório antes de qualquer geração futura

1. Revalidar as páginas oficiais de criação, modelos/features e edição do Flow.
2. Conferir na conta e região visíveis: modelo, modo, duração, aspecto, resolução, número de outputs e inputs aceitos.
3. Registrar `provider_snapshot_at`, configuração completa e incompatibilidades.
4. Conferir referências autorizadas, hashes e `ProductFacts` suficientes.
5. Renderizar os prompts finais de todas as condições e executar diff: somente a variável declarada pode mudar.
6. Ler o custo exibido por output/configuração. Não usar memória ou tabela antiga.
7. Calcular `planned_outputs` e `estimated_credits`.
8. Solicitar aprovação humana inicial daquele experimento e daquele teto. Aprovação de um experimento não autoriza os demais.
9. Criar blinding key e ordem aleatória antes da geração.

Se custo não estiver visível ou houver ambiguidade de cobrança, o status permanece `BLOCKED_FOR_BUDGET_APPROVAL`.

## 4. Estratégia mínima de repetição

### Screening

- `MIN_RUNS = 2 outputs independentes por condição`.
- Duas repetições detectam apenas diferenças grandes e evitam tomar um output isolado como prova.
- Screening sozinho pode produzir `INCONCLUSIVE`; não promove best practice.

### Confirmação

- Se os dois blocks apontarem materialmente na mesma direção, executar `+1 output por condição` após confirmar saldo/teto.
- `MIN_FOR_SUPPORTED = 3 outputs por condição`.
- Para três condições, a confirmação adiciona uma repetição a cada condição ainda competitiva; condição com hard failure repetido pode ser interrompida pela regra de segurança.

### Optional extra

- `OPTIONAL_EXTRA_RUNS = no máximo +1 output por condição` quando o resultado 2–1/misto for importante o suficiente para justificar custo.
- Cap prático: `4 outputs por condição` neste ciclo. Persistindo ambiguidade, concluir `INCONCLUSIVE`; não aumentar n indefinidamente.

## 5. Early-stop rules

Interromper uma condição ou o experimento quando:

1. **invalid protocol/configuration:** variável congelada mudou, input incorreto, custo/configuração divergente ou arquivo de referência errado;
2. **safety/factual issue:** a condição pede uso incorreto, claim não sustentado ou risco não autorizado;
3. **two repeated hard failures of the same target type:** pausar a condição; a terceira execução só ocorre se for necessária para uma decisão importante e houver aprovação explícita;
4. **mixed screening:** uma vitória para cada lado ou diferenças apenas cosméticas → `INCONCLUSIVE`, salvo prioridade que justifique confirmação;
5. **clear screening direction:** não gerar extras além da única rodada confirmatória prevista;
6. **budget cap reached:** parar, mesmo que a comparação esteja incompleta;
7. **provider changed:** se modelo/modo/feature mudar entre blocks, encerrar a coorte e não misturar resultados.

## 6. Decision rule

Todo experimento termina em exatamente um estado:

- `SUPPORTED`: pelo menos 3 outputs válidos por condição; a condição prevista vence em pelo menos 2 dos 3 blocks e o terceiro é empate, não derrota; melhora aparece nos primary outcomes; nenhum hard failure/guardrail relevante piora; avaliação cega confirmada.
- `NOT_SUPPORTED`: com pelo menos 3 outputs válidos por condição, a hipótese não melhora os primary outcomes ou a condição proposta perde em pelo menos 2 blocks sem vitória compensatória, ou introduz hard failure repetido.
- `INCONCLUSIVE`: amostra incompleta, resultados mistos, mudança de provider/configuração, discordância de avaliação, efeito pequeno ou custo interrompido.

`SUPPORTED` significa regra **provisória e escopada** ao provider/modelo/modo/data/cena testados. Não significa verdade universal.

## 7. Blind comparison

1. Um coordenador cria códigos aleatórios, por exemplo `CANDIDATE-K7`, sem `control/variant` no nome.
2. A blinding key fica fora do pacote entregue ao avaliador.
3. Ordem de apresentação muda por block.
4. O avaliador faz primeiro a rubric absoluta sem ver o par; só depois registra preferência pareada e confiança `LOW/MEDIUM/HIGH`.
5. Prompts, nomes de variante e hipótese ficam ocultos até o formulário ser fechado.
6. Um avaliador primário é suficiente para screening. Possível `SUPPORTED`, hard failure contestado ou discordância relevante exige segundo avaliador cego.
7. A chave só é revelada após avaliação congelada. Mudança posterior vira nova versão, nunca edição silenciosa.

## 8. Credit budget

Custos por modelo/modo/resolução são `UNKNOWN_UNTIL_PREFLIGHT` e `FAST_CHANGING`. A documentação oficial orienta conferir o custo atual nas configurações antes da geração. O orçamento é controlado primeiro por outputs:

| Tier | Conteúdo | Screening outputs | Confirmation ceiling | Observação |
|---|---|---:|---:|---|
| `MUST_RUN` | E-01, E-02, core E-03, E-04, core E-05 | 26 | +12 | executar sequencialmente, nunca como autorização única |
| `USEFUL` | frames adicionais no E-03; riscos product/identity no E-05; desempates de alto valor | 0 inicialmente | até +20 | somente após aprender com MUST_RUN |
| `OPTIONAL` | video-as-ingredient/edit, líquidos, tecido, reflexos, quarto repeat | 0 | definido por aprovação específica | alto custo/risco ou workflow não comparável |

### Breakdown do screening `MUST_RUN`

| Experimento | Condições | Outputs por condição | Total inicial |
|---|---:|---:|---:|
| E-01 Action Complexity | 2 | 2 | 4 |
| E-02 Temporal Direction | 3 | 2 | 6 |
| E-03 Input Matrix core | 3 | 2 | 6 |
| E-04 UGC Believability | 3 | 2 | 6 |
| E-05 Hand-risk mitigation core | 2 | 2 | 4 |
| **Total** |  |  | **26 outputs** |

Antes de aprovar:

```text
estimated_credits = SUM(planned_outputs_by_configuration * displayed_credit_cost_per_output)
```

Registrar também créditos gratuitos/promocionais apenas se a UI os mostrar; nunca tratá-los como custo zero permanente. Cada experimento recebe teto próprio em outputs e créditos.

## 9. Artifact storage — estrutura futura

Nenhuma pasta de runs é criada nesta etapa. Ao executar:

```text
experiments/
  visual-production/
    registry.json
    assets/
      references/
        <asset_id>/
          original.<ext>
          provenance.json
    E-01/
      protocol.json
      frozen/
        scene-spec.json
        variable-lock.json
        prompt-diff.txt
      blinding/
        key.json
        presentation-order.json
      runs/
        <run_id>/
          input-spec.json
          prompt.txt
          references.json
          provider-config.json
          output.<ext>
          output-metadata.json
          qa.json
      evaluations/
        <evaluation_id>.json
      results.json
      conclusion.md
```

### Required run evidence

- `experiment_id`, `protocol_version`, `run_id`, `block_id`, blinded candidate ID;
- hypothesis, condition, independent variable, frozen variables and known confounders;
- complete input specification and exact prompt;
- references with role, provenance, authorization, file hash and paths;
- visible Flow/model/mode/aspect/duration/resolution/output configuration;
- displayed estimated cost, actual observed debit when available, date/time and operator;
- original output file plus provider asset/project reference when available;
- QA rubric, hard-failure flags, human evaluation and confidence;
- run validity, result and reason for exclusion if invalid.

Hashes, timestamps and versioned protocols make reconstruction possible. Chat text may explain a run, but cannot be its only record.

## 10. Reproducibility and contamination control

- Freeze all source assets before block 1; do not replace a “bad” product photo mid-experiment.
- Reuse exact files, not visually similar copies.
- Persist exact prompts including whitespace-relevant structure.
- Do not mix models, modes, durations or provider releases in one result.
- If Flow silently switches model or rejects a feature, mark run invalid/conditional and record the visible event.
- Record failures/timeouts/cost before retrying; first confirm whether an asset/output was created.
- Do not crop, grade or edit outputs before raw QA. Edited derivatives are separate artifacts.

## 11. Knowledge promotion

```text
EXPERIMENT RESULT (SUPPORTED / NOT_SUPPORTED / INCONCLUSIVE)
  -> PROJECT_LEARNING with evidence class EXPERIMENTAL
  -> proposed change to BEST_PRACTICES and/or FAILURE_MODES
  -> DESIGN_DECISION when architecture/contract behavior changes
  -> capability update only after human review
```

Promotion requirements:

- conclusion links every run/evaluation;
- provider/model/mode/date and scene scope are explicit;
- `SUPPORTED` is provisional and lists exceptions/residual risk;
- contradictory evidence is preserved;
- a single output never creates a rule;
- `INCONCLUSIVE` does not modify a best practice;
- future production incidents can reopen the decision through `PROJECT_LEARNING`.

## 12. Protocol registry

| ID | Question | Golden scene | Independent variable | Status |
|---|---|---|---|---|
| E-01 | atomic action beats multi-step? | GS-C | action complexity | `PRODUCT_EVIDENCE_ACQUIRED / PREFLIGHT_REPEAT_REQUIRED / NOT_RUN` |
| E-02 | which temporal description adheres best? | GS-C | temporal representation | `READY / NOT_RUN` |
| E-03 | which documented input workflow helps? | GS-D | input configuration | `READY / NOT_RUN` |
| E-04 | which capture profile appears social-native? | GS-D | capture-style profile | `READY / NOT_RUN` |
| E-05 | does contextual mitigation reduce target failures? | GS-B core; GS-C/GS-D useful | mitigation block | `READY / NOT_RUN` |

## 13. Provider documentation snapshot

As of 23/09/2026, official Flow documentation declares text-to-video, first-frame, first+last-frame and ingredients/references workflows, with support varying by model. It also documents video ingredients/references and a separate uploaded-video editing workflow under compatible models/regions. This snapshot supports protocol design only; preflight must refresh it immediately before execution.

Sources: S-FLOW-01, S-FLOW-02 and S-FLOW-03 in `../SOURCES.md`; official pages: <https://support.google.com/flow/answer/16353334?hl=en>, <https://support.google.com/flow/answer/16352836?hl=en>, <https://support.google.com/labs/answer/16935718?hl=en>.
