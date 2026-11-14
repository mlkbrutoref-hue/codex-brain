# Scoring Rubric and Hard Failures

**STATUS:** `DEFINED / NOT_USED`  
**Principle:** independent criteria plus `PASS / REVIEW / FAIL`; no summed “quality score”.

## 1. Per-criterion rating

Cada critério recebe:

- `PASS`: atende ao acceptance check sem defeito material observável;
- `REVIEW`: desvio real, mas potencialmente utilizável; exige decisão humana e descrição precisa;
- `FAIL`: não atende ao objetivo, exige regeneração/redesign ou constitui hard failure;
- `N/A`: critério fora do escopo da scene; nunca convertido em pass.

O avaliador registra `evidence_timestamp_or_frame`, descrição e confiança `LOW/MEDIUM/HIGH`. “Parece melhor” não é avaliação válida.

## 2. Critérios comuns

### IDENTITY_FIDELITY

- **PASS:** Nina permanece reconhecível e consistente com referência em rosto, cabelo, idade aparente, roupa e corpo visíveis.
- **REVIEW:** microdrift não estrutural, ainda inequivocamente Nina e sem mudança durante ação crítica.
- **FAIL:** identidade troca, rosto/hair/wardrobe muda materialmente ou há drift durante o take.
- **N/A:** Nina/identidade não aparece.

### PRODUCT_FIDELITY

- **PASS:** geometria, partes, proporções, cor, acabamento e face crítica permanecem coerentes com referências/fatos.
- **REVIEW:** detalhe secundário instável sem afetar função/identificação.
- **FAIL:** parte funcional, contorno, tamanho relativo, material aparente ou cor muda materialmente.

### PHYSICAL_PLAUSIBILITY

- **PASS:** gravidade, apoio, contato, colisão, eixo, peso aparente e resposta do material são causalmente coerentes.
- **REVIEW:** pequena irregularidade que não falsifica a demonstração.
- **FAIL:** interpenetração, movimento sem força, mecanismo impossível, volume/massa/permanência violados ou física torna a prova falsa.

### ACTION_ADHERENCE

- **PASS:** todos e somente os eventos requeridos ocorrem na ordem e alcançam o final state.
- **REVIEW:** ação principal termina, mas timing/hold/microfase difere sem mudar significado.
- **FAIL:** ação omitida, incompleta, fora de ordem, adicionada de forma material ou contraditória à função.

### INSTRUCTION_ADHERENCE

- **PASS:** os requisitos observáveis relevantes da condition, além da ação, são atendidos sem contradição.
- **REVIEW:** desvio secundário não afeta a hipótese nem a prova.
- **FAIL:** requisito-alvo da variável independente foi ignorado ou interpretado de modo incompatível.

### HAND_CORRECTNESS

- **PASS:** anatomia, contagem aparente, separação, grip, contato, oclusão e trajetória são plausíveis.
- **REVIEW:** pose estranha ou dedo parcialmente ambíguo fora do momento crítico.
- **FAIL:** dedos extras/ausentes/fundidos, mão atravessa objeto ou grip impossível na ação crítica.

### CONTINUITY

- **PASS:** identidade, produto, props, environment, roupa, luz, screen direction e estados persistem ou mudam por evento visível.
- **REVIEW:** drift secundário localizado sem quebrar a prova.
- **FAIL:** objeto/prop aparece, some, duplica, teleporta; fundo/roupa/luz muda materialmente sem causa.

### CAMERA_PLAUSIBILITY

- **PASS:** altura, perspectiva, movimento, estabilidade, foco/DOF e exposição são compatíveis com o capture profile pedido e mantêm leitura.
- **REVIEW:** ajuste um pouco excessivo, mas plausível e não distrativo.
- **FAIL:** câmera flutua/teleporta, perspectiva muda sem movimento, focus hunting ou exposição impede a demonstração.

### LIGHTING_PLAUSIBILITY

- **PASS:** fontes, direção, sombras, highlights, reflexos, WB e exposição são coerentes e contínuos.
- **REVIEW:** pequeno cast/highlight inconsistente sem alterar produto/pele materialmente.
- **FAIL:** fonte impossível, sombra/reflexo contraditório, flicker severo ou cor/exposição falsifica produto/pele.

### SKIN_PLAUSIBILITY

- **PASS:** textura, cor, detalhe, exposição e movimento da pele parecem humanos e coerentes com a luz.
- **REVIEW:** suavização/cast perceptível, mas identidade e leitura continuam plausíveis.
- **FAIL:** pele plástica/encerada, textura móvel, clipping/cor impossível ou aparência dominante de CGI.
- **N/A:** nenhuma pele visível.

### TEMPORAL_COHERENCE

- **PASS:** movimento inicia, progride, assenta e termina sem saltos; ritmo/eventos correspondem à representação pedida.
- **REVIEW:** ritmo/hold diverge, mas ação e causalidade permanecem claras.
- **FAIL:** salto de estado, teleporte, loop, movimento viscoso severo ou evento ocorre fora de ordem.

### UGC_BELIEVABILITY

- **PASS:** impressão global plausível de vídeo social humano: captura, gesto, pele, luz, enquadramento e ritmo compatíveis com smartphone/social.
- **REVIEW:** parece polido/artificial em algum eixo, mas pode funcionar como anúncio social.
- **FAIL:** aparência dominante de IA/CGI/stock/commercial incompatível com o objetivo.

### HUMAN_RECORDED_IMPRESSION

- **PASS:** conjunto de captura, gesto e ambiente é plausível como gravação humana real, sem depender de aceitar um defeito de IA.
- **REVIEW:** há sinais artificiais, mas a origem humana ainda é plausível.
- **FAIL:** camera/subject/material motion ou acabamento denuncia geração de forma dominante.

### AI_ARTIFACTS

- **PASS:** nenhum artefato material detectado.
- **REVIEW:** artefato breve/secundário que não toca identidade, produto, mãos ou prova.
- **FAIL:** morph, flicker, textura derretida, anatomia, duplicação, popping ou outro artefato compromete uso.

### OVERALL_USABILITY

Este campo é derivado, não uma média:

- **PASS:** todos os required criteria são `PASS`; nenhum hard failure.
- **REVIEW:** nenhum hard failure/required `FAIL`, mas existe pelo menos um `REVIEW`.
- **FAIL:** qualquer hard failure ou required criterion `FAIL`.

## 3. Hard failures

Um take recebe `OVERALL_USABILITY = FAIL` independentemente de seus outros méritos quando houver:

1. produto errado ou funcionalmente incorreto;
2. mudança grave de geometria, parte, escala, cor/material factual ou face crítica;
3. Nina perde identidade ou muda materialmente durante o take;
4. mão impossível no contato/gesto crítico;
5. ação contradiz facts, mecanismo ou uso permitido do produto;
6. produto/prop/pessoa desaparece, duplica ou teleporta de modo material;
7. física torna a demonstração falsa: eixo/hinge/slide impossível, líquido/cloth/material incompatível, colisão/interpenetração grave;
8. ação principal não conclui ou final state essencial não é alcançado;
9. claim visual não sustentado, resultado inventado ou condição insegura;
10. texto/logo essencial falsificado quando fidelidade textual é requisito explícito;
11. output corrompido, incompleto ou não reproduzível para avaliação;
12. violação de política, direitos/autorização ou uso de referência incorreta.

`INVALID_RUN` é diferente de hard failure: configuração/protocolo errado exclui o run da análise, mas continua registrado. Um output ruim produzido por protocolo válido não é excluído.

## 4. Primary metrics por experimento

| Experimento | Primary outcomes | Guardrails |
|---|---|---|
| E-01 | action completion, physical plausibility, hand correctness | product fidelity, continuity, identity se aplicável |
| E-02 | instruction adherence, timing coherence, temporal coherence, completion | product/hand/continuity |
| E-03 | identity fidelity, product fidelity, input adherence | action, physics, cost/output |
| E-04 | human-recorded impression, camera/light/skin plausibility, UGC believability, AI indicators | identity, product, action |
| E-05 | target failure incidence and target criterion status | all non-target criteria and hard failures |

## 5. Pairwise comparison record

Após a avaliação absoluta, comparar os candidatos do mesmo block:

- `preferred_candidate`: A, B ou `TIE`;
- `preference_reason`: primary outcome específico;
- `material_difference`: YES/NO;
- `guardrail_regression`: YES/NO + criterion;
- `confidence`: LOW/MEDIUM/HIGH.

Uma preferência estética sem diferença material nos primary outcomes conta como `TIE` para a hipótese.

## 6. Decision aggregation without magic score

Não somar ratings nem produzir média geral.

Para cada condition, relatar:

- valid runs / invalid runs;
- hard-failure count e tipos;
- `PASS/REVIEW/FAIL` count por critério;
- overall usability count;
- completion/event counts quando aplicável;
- pairwise wins/ties/losses;
- custo observado por output e por usable output;
- discordância entre avaliadores.

A decisão segue as regras do framework, não um threshold agregado escondido.

## 7. Blind evaluation form — campos mínimos

```text
evaluation_id
reviewer_id_or_role
reviewer_blinded = true/false
candidate_id
viewing_conditions
criteria[]:
  name
  status: PASS | REVIEW | FAIL | N/A
  evidence_timestamp_or_frame
  note
  confidence
hard_failures[]
overall_usability
pairwise_preference (filled only after absolute review)
submitted_at
rubric_version
```

O avaliador não recebe hypothesis, condition names, prompts nem a direção esperada do efeito.
