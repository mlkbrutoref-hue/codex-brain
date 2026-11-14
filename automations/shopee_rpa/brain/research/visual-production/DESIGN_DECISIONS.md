# Visual Production — Design Decisions

Estas decisões definem design conceitual. Não são schemas de runtime, migração de pipeline ou autorização de implementação.

## VP-D01 — `Realism Prompting` será dividido

**WHAT DID WE DECIDE?**  
`REALISM_PROMPTING_DECISION = SPLIT` em:

1. `Scene Direction`: planeja a cena de forma filmável, provider-independent.
2. `Generation Specification`: transforma a direção aprovada em um contrato de geração neutro, com inputs, invariantes, proibições contextuais e critérios de QA.
3. `GoogleFlowAdapter`: futuro adapter provider-specific que escolhe e traduz para recursos atuais do Flow.

`CinematographySpec`, `LightingSpec`, `PhysicalInteractionSpec`, `TemporalPlan`, `ContinuitySpec` e `SceneRiskProfile` são seções do aggregate `SceneDirection`, não serviços/capabilities independentes nesta etapa.

**WHY?**  
O nome atual mistura raciocínio de cena, realismo, prompt e sintaxe do provider. A pesquisa mostrou que a maior parte do controle necessário existe antes do prompt e permanece válida para qualquer gerador ou filmagem real.

**EVIDENCE?**  
FINDINGS seções 1–11; S-FILM-03/05, S-FLOW-01/06/07.

**ALTERNATIVES CONSIDERED?**  
`KEEP` preservaria uma responsabilidade ampla e acoplada. `RENAME` para Scene Direction ainda misturaria tradução e operação. Criar seis serviços separados seria overengineering sem evidência operacional.

**NEEDS FUTURE VALIDATION?**  
Sim. Testar se os campos propostos são suficientes e mínimos em jobs reais antes de schema/runtime.

## VP-D02 — Responsabilidade e limites de `Scene Direction`

**WHAT DID WE DECIDE?**  
A capability recebe intenção/fatos/storyboard/referências e produz um plano visual executável e verificável. Ela não escolhe claims, não gera mídia, não opera provider e não edita o master.

**Inputs conceituais mínimos:**

- `CreativeGoal` e função da cena no vídeo;
- `ProductFacts`, unknowns e superfícies/ações permitidas;
- identidade canônica da Nina e limites da persona;
- beat do script/storyboard, duração alvo e plataforma/aspect intent;
- `StyleDNA` ou `ReferenceDNA` aprovado, quando existir;
- estado herdado do take anterior;
- restrições de segurança/originalidade e recursos desejáveis, não presumidos.

**Output: `SceneDirection` aggregate**

- `scene_intent` e `proof_moment`;
- `initial_state` e `final_state` para Nina/produto/props;
- `blocking`: posições, orientação corporal, gaze/eyeline e relações espaciais;
- `product_presentation`: face crítica, escala, visibilidade e estado;
- `action_plan`: ação dominante e primitives ordenadas;
- `environment` e anchors estáveis;
- `cinematography`;
- `lighting`;
- `physical_interaction`;
- `temporal_plan`;
- `continuity`;
- `risk_profile`;
- `expected_visual_result` e checks observáveis;
- `unknowns` e `assumptions` explicitamente classificados.

**WHY?**  
Esse é o menor conjunto que responde às 12 perguntas do gate sem transformar cada disciplina em componente operacional.

**EVIDENCE?**  
FINDINGS Gate; S-FILM-02..05, S-HAND-01..03, S-LIGHT-01/02.

**ALTERNATIVES CONSIDERED?**  
Uma string de prompt não preserva estado, evidência, risco nem QA. Objetos separados por microdisciplina aumentariam handoffs sem ganho comprovado.

**NEEDS FUTURE VALIDATION?**  
Sim, por walkthrough dos quatro casos e depois por jobs experimentais.

## VP-D03 — Subespecificações mínimas

**WHAT DID WE DECIDE?**

| Seção | Campos conceituais necessários | O que deliberadamente não promete |
|---|---|---|
| `CinematographySpec` | shot size, height/angle, placement/distance, perspective intent, composition, product/subject framing, camera motion, focus/DOF behavior, exposure/WB behavior, capture character | focal/apertura exatas quando provider não as controla |
| `LightingSpec` | motivated sources, dominant/secondary, direction, quality, color family, skin/product exposure priorities, shadows, reflections, continuity | “studio quality” sem fonte física |
| `PhysicalInteractionSpec` | active/support hand, grip/contact points, anchor/support, affordance, axis/path, force intent, occlusion budget, material response, release/end | propriedades do produto ausentes dos fatos |
| `TemporalPlan` | phases, relative order, beat windows, event markers, result hold, allowed simultaneity | aderência do provider a timestamps literais |
| `ContinuitySpec` | immutable Nina/product/environment attributes, hand/grip, screen direction, lighting, inherited/handed-off states | consistência garantida pelo gerador |
| `SceneRiskProfile` | active risks, evidence/trigger, severity band, compound risk, mitigation, required QA, fallback | score numérico calibrado inexistente |

**WHY?**  
Cada seção corresponde a uma classe diferente de decisão e falha; ainda assim pode viver em um único aggregate.

**EVIDENCE?**  
FINDINGS seções 3–10; FAILURE_MODES.

**ALTERNATIVES CONSIDERED?**  
Prosa livre é difícil de validar; schema excessivamente técnico cria precisão falsa.

**NEEDS FUTURE VALIDATION?**  
Sim, especialmente nomes, cardinalidade e defaults antes de contrato executável.

## VP-D04 — `GenerationSpecification` permanece provider-independent

**WHAT DID WE DECIDE?**  
`GenerationSpecification` empacota o que um gerador precisa satisfazer, sem selecionar sintaxe/modelo do Flow.

**Conteúdo conceitual:**

- referência à `SceneDirection` aprovada e sua versão;
- aspecto/duração desejados como constraints de entrega, com tolerâncias quando cabível;
- assets/referências aprovados, função de cada um e prioridade;
- invariantes `must_preserve`;
- resultados `must_show`;
- resultados contextuais `must_avoid`, derivados do risk profile;
- movimentos separados por entidade;
- boundary states/frames desejados;
- acceptance checks e fallback strategy;
- unknowns que impedem ou limitam geração.

**WHY?**  
Permite testar, trocar provider e comparar saídas sem reescrever direção criativa.

**EVIDENCE?**  
S-FLOW-01/03/07 mostram variação de inputs/modes; S-AIV-01..04 mostram necessidade de checks multidimensionais.

**ALTERNATIVES CONSIDERED?**  
Gerar diretamente um prompt elimina rastreabilidade. Colocar feature matrix no contrato universal acopla a missão ao provider.

**NEEDS FUTURE VALIDATION?**  
Sim, com dois adapters hipotéticos ou um adapter + renderização humana para provar neutralidade.

## VP-D05 — `GoogleFlowAdapter` é uma tradução atual e volátil

**WHAT DID WE DECIDE?**  
Um futuro adapter traduz `GenerationSpecification` para a configuração suportada atualmente: modelo/modo, prompt, negative guidance contextual, ingredients/references, start/end frames, aspect, duração/resolução, camera control e scene workflow quando disponíveis.

Ele também deve registrar feature matrix/data, escolhas, incompatibilidades, degradações e os metadados recuperáveis. Nesta pesquisa, nenhum adapter será implementado.

**WHY?**  
Flow é essencial à produção atual, mas seus recursos variam e mudam; isolar tradução evita contaminar contratos duráveis.

**EVIDENCE?**  
S-FLOW-01..08; relatos S-FLOW-09 exigem validação e observabilidade.

**ALTERNATIVES CONSIDERED?**  
Embeddar sintaxe Flow em `SceneDirection` impediria portabilidade. Tratar Flow como opcional hoje negaria a realidade operacional.

**NEEDS FUTURE VALIDATION?**  
Sim, obrigatoriamente contra UI/documentação/modelos correntes antes de implementação e em todo refresh relevante.

## VP-D06 — O objetivo padrão é `BELIEVABLE_SOCIAL_VIDEO`

**WHAT DID WE DECIDE?**  
O style intent padrão prioriza captura social humana plausível; `PHOTOREALISM` é condição necessária, mas insuficiente. Cinematic commercial só entra por direção criativa explícita.

**WHY?**  
Movimento, gesto, captura, ambiente e linguagem de plataforma podem denunciar IA mesmo quando frames isolados parecem reais.

**EVIDENCE?**  
FINDINGS seção 4; S-PHONE-01..03 e S-UGC-01..05.

**ALTERNATIVES CONSIDERED?**  
“Maximum cinematic realism” como default produz look desalinhado ao nicho e confunde acabamento com confiança.

**NEEDS FUTURE VALIDATION?**  
Sim, com avaliação humana e, posteriormente, sinais de performance; nunca inferir conversão só de estética.

## VP-D07 — Risk profile contextual com bands, não score fictício

**WHAT DID WE DECIDE?**  
Cada eixo recebe `NONE | LOW | MEDIUM | HIGH | CRITICAL`, justificativa/evidência, mitigação e checks. Não há soma linear. Um risco crítico ou combinação de riscos altos pode exigir split/redesign.

**Eixos iniciais:**

- `HAND_INTERACTION_RISK`;
- `IDENTITY_RISK`;
- `PRODUCT_MORPH_RISK`;
- `PHYSICS_RISK`;
- `REFLECTION_RISK` (inclui refração/transparência quando aplicável);
- `LIQUID_RISK`;
- `CLOTH_RISK`;
- `CONTINUITY_RISK`;
- `OCCLUSION_RISK`;
- `TEXT_LOGO_RISK` quando reprodução fiel for necessária/autorizada.

**Estratégia por contexto:**

| Perfil | Estratégia inicial de design |
|---|---|
| baixo | cena simples; referências conforme necessidade; QA padrão |
| médio | ação única, referências/boundary state mais fortes, checks específicos |
| alto | câmera simples, clip mais curto, desoclusão, split ou take alternativo, QA evento a evento |
| crítico | redesenhar antes de gerar; se indispensável, experimento isolado e aprovação humana |

`compound_risk` registra combinações como `hands + glass + liquid + moving_camera`, pois o máximo isolado não descreve toda a dificuldade.

**WHY?**  
Negative prompt universal não representa risco da cena e cria ruído. Bands sem números evitam falsa calibração.

**EVIDENCE?**  
S-AIV-01..04 e FAILURE_MODES; política específica é `INFERRED`.

**ALTERNATIVES CONSIDERED?**  
Score 0–100 sem dataset seria arbitrário. Um campo único “high risk” perderia diagnóstico e mitigação.

**NEEDS FUTURE VALIDATION?**  
Sim. Calibrar bands, compound triggers, retries e fallbacks com experimentos e Project Learnings.

## VP-D08 — Temporal plan usa fases; timestamps não são garantia

**WHAT DID WE DECIDE?**  
Usar fases relativas e beat windows no planejamento/QA/edição. Timestamps literais são uma possível tática do adapter, marcada experimental até teste atual.

**WHY?**  
O sistema precisa de timing, mas não foi encontrada garantia oficial de aderência precisa do Flow a intervalos textuais.

**EVIDENCE?**  
S-FLOW-06/07; FINDINGS seção 8.

**ALTERNATIVES CONSIDERED?**  
Remover tempo empobrece edição/QA. Tratar timestamps como controle comprovado inventa capacidade.

**NEEDS FUTURE VALIDATION?**  
Sim, experimento E-02.

## VP-D09 — Reference analysis produz evidência, não imitação

**WHAT DID WE DECIDE?**  
`ReferenceDNA` futuro será derivado de shots/keyframes/timestamps e separará gramática reutilizável de elementos proibidos. Nina, ProductFacts e originalidade têm precedência.

**WHY?**  
Análise precisa ser auditável e não pode transformar referência em template de cópia.

**EVIDENCE?**  
S-REF-01/02, S-FILM-05 e missão do projeto.

**ALTERNATIVES CONSIDERED?**  
Resumo livre perde evidência; style transfer literal viola o objetivo.

**NEEDS FUTURE VALIDATION?**  
Sim, com referências autorizadas e revisão de similaridade/originalidade.

## VP-D10 — QA será derivado do design

**WHAT DID WE DECIDE?**  
Cada `SceneDirection`/`GenerationSpecification` fornece checks observáveis. QA avalia frames inicial/crítico/final e eventos de contato, além de reprodução contínua.

**WHY?**  
Benchmarks mostram dimensões independentes; um frame bonito não prova identidade, ação ou física ao longo do tempo.

**EVIDENCE?**  
S-AIV-01..04.

**ALTERNATIVES CONSIDERED?**  
Checklist global único perde risco contextual. Avaliação puramente estética não cobre produto/física.

**NEEDS FUTURE VALIDATION?**  
Sim, calibrar concordância humana e automação auxiliar.

## Experimentos registrados — não executados

### E-01 — Ação atômica versus multi-etapa

**HYPOTHESIS:** uma ação dominante aumenta conclusão e integridade física.  
**EVIDENCE_GAP:** documentação orienta simplicidade, mas não há taxa no contexto Nina/produtos.  
**TEST:** mesmo produto/referências, variante atômica e multi-etapa.  
**CONTROL_OR_BASELINE:** configurações/modelo/data idênticos; múltiplas amostras.  
**SUCCESS_CRITERIA:** maior aderência, menos falhas de mão/produto, estado final correto.  
**RESULT:** pendente.  
**DECISION:** pendente.  
**LIMITATIONS:** resultados específicos do modelo/modo/data.

### E-02 — Sintaxe temporal

**HYPOTHESIS:** fases ordenadas ajudam; timestamps literais podem não oferecer controle adicional.  
**EVIDENCE_GAP:** não há garantia oficial de timestamp.  
**TEST:** prosa ordenada vs. fases rotuladas vs. intervalos em segundos.  
**CONTROL_OR_BASELINE:** mesma cena simples e duração, configuração fixa.  
**SUCCESS_CRITERIA:** ordem correta e erro temporal de eventos menor, sem perda de identidade/física.  
**RESULT:** pendente.  
**DECISION:** pendente.  
**LIMITATIONS:** repetir após mudanças relevantes do provider.

### E-03 — Matriz de inputs do Flow

**HYPOTHESIS:** o melhor modo depende de identidade, boundary state e ação; mais referências não é sempre melhor.  
**EVIDENCE_GAP:** recurso documentado não equivale a confiabilidade comparativa.  
**TEST:** text-only, ingredient, start frame, start/end frames nos modos disponíveis.  
**CONTROL_OR_BASELINE:** mesma direção e acceptance checks.  
**SUCCESS_CRITERIA:** fidelidade à Nina/produto, aderência à ação, custo/retry e física.  
**RESULT:** pendente.  
**DECISION:** pendente.  
**LIMITATIONS:** disponibilidade por conta/região/modelo.

### E-04 — Camera e social believability

**HYPOTHESIS:** handheld leve e DOF moderada parecem mais social-native sem prejudicar leitura; movimento complexo reduz física em cenas difíceis.  
**EVIDENCE_GAP:** princípio de captura não prova percepção/conversão no output gerado.  
**TEST:** static, stabilized micro-handheld e moving camera; DOF moderada/extrema.  
**CONTROL_OR_BASELINE:** mesma ação, luz e refs.  
**SUCCESS_CRITERIA:** avaliação cega de naturalidade + QA técnico/visual.  
**RESULT:** pendente.  
**DECISION:** pendente.  
**LIMITATIONS:** naturalidade depende do nicho e audiência.

### E-05 — Risk profile calibration

**HYPOTHESIS:** axes/bands predizem retries e categorias de falha melhor que uma lista global de negatives.  
**EVIDENCE_GAP:** não há dataset interno.  
**TEST:** rotular cenas antes da geração e comparar com falhas/retries/custo/aprovação.  
**CONTROL_OR_BASELINE:** rubric fixa e reviewer agreement.  
**SUCCESS_CRITERIA:** associação útil e repetível que altere estratégia/fallback.  
**RESULT:** pendente.  
**DECISION:** pendente.  
**LIMITATIONS:** evitar score numérico até amostra suficiente.

## Expertise gate do padrão global

1. **Responsabilidade:** planejamento visual filmável/gerável e verificável; definida em VP-D02.
2. **Inputs:** intenção, fatos, Nina, storyboard, refs/DNA, tempo/plataforma, estado e restrições; VP-D02.
3. **Outputs:** `SceneDirection` e `GenerationSpecification`; VP-D02/04.
4. **Best practices:** regras BP-01..18 em `BEST_PRACTICES.md`.
5. **Failure modes:** FM-01..18 em `FAILURE_MODES.md`.
6. **Provider-specific:** seleção/tradução/configuração do Flow; VP-D05.
7. **Uncertainty:** documentada em `FINDINGS.md` e nos experimentos pendentes.
8. **Testing:** E-01..05, acceptance checks e future QA derivado; VP-D10.

**GATE RESULT:** `PASS / DESIGN_RESEARCHED`. Isto encerra a fase de research e capability design, não a implementação.

## VP-D11 — Experimentos usam screening econômico e confirmação separada

**WHAT DID WE DECIDE?**  
Cada condition começa com dois outputs independentes. Screening nunca promove regra. Diferença grande e consistente pode receber uma terceira repetição por condition; um quarto output é exceção de alto valor. Comparação usa one-variable-at-a-time, blocks randomizados, avaliação cega, hard failures e decisão `SUPPORTED | NOT_SUPPORTED | INCONCLUSIVE`.

**WHY?**  
Uma geração isolada não demonstra comportamento, enquanto uma amostra acadêmica ampla consumiria créditos antes de sabermos se há sinal relevante. O desenho em duas fases encontra diferenças grandes com teto explícito e preserva incerteza quando o efeito é misto.

**EVIDENCE?**  
Lacunas e experimentos E-01..E-05 registrados nesta pesquisa; protocolo detalhado em `experiments/README.md` e rubric em `experiments/SCORING_RUBRIC.md`.

**ALTERNATIVES CONSIDERED?**  
Um output por condition foi rejeitado por fragilidade. N grande fixo foi rejeitado por custo prematuro. Score agregado foi rejeitado porque esconderia hard failures.

**NEEDS FUTURE VALIDATION?**  
Sim. Repetition count, decision thresholds e evaluator agreement devem ser revistos após as primeiras coortes; nenhum experimento foi executado.

## VP-D12 — Feature e custo do Flow são recapturados por experimento

**WHAT DID WE DECIDE?**  
Protocolos registram a feature matrix oficial consultada, mas o preflight deve recapturar modelo, modo, inputs, duração, aspecto, resolução, output count e custo visíveis antes de pedir autorização humana. Configurações diferentes não pertencem à mesma coorte.

**WHY?**  
Flow é `FAST_CHANGING` e varia por modelo, região e conta. Congelar conhecimento antigo como contrato invalidaria comparações e orçamento.

**EVIDENCE?**  
S-FLOW-01..03 e `experiments/E-03_FLOW_INPUT_MATRIX.md`.

**ALTERNATIVES CONSIDERED?**  
Hardcode de custo/modelo foi rejeitado. Operar sem estimativa/teto foi rejeitado.

**NEEDS FUTURE VALIDATION?**  
Sim, em todo preflight. Nesta etapa, custo permanece `UNKNOWN_UNTIL_PREFLIGHT`.
