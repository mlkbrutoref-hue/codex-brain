# Visual Production — Failure Modes

`TRIGGER` significa condição correlacionada ou complexidade observável; não é alegação sobre mecanismo interno do modelo. Benchmarks S-AIV-01..04 sustentam as categorias gerais. Comportamento e frequência no Google Flow atual permanecem sujeitos a teste.

## FM-01 — Face/identity drift

**CAPABILITY:** Scene Direction / Visual Generation / Continuity  
**FAILURE:** rosto, cabelo, idade aparente ou identidade da Nina muda durante o take ou entre takes.  
**TRIGGER:** oclusão, rotação extrema, duração/movimento maiores, referências competindo; correlação `INFERRED`.  
**IMPACT:** quebra da persona e do uso comercial.  
**EVIDENCE:** categoria de consistência `DOCUMENTED` em S-AIV-01; relatos específicos do provider insuficientes.  
**DETECTION:** comparar keyframes com referência canônica e entre eventos.  
**MITIGATION:** referência limpa, aparência invariável, pose/oclusão mais simples, clip curto, redesign do enquadramento; eficácia por modo precisa teste.  
**RESIDUAL_RISK:** médio/alto até benchmark da Nina.

## FM-02 — Product morph / geometry, size or color drift

**CAPABILITY:** Visual Production  
**FAILURE:** produto muda forma, peças, proporção, tamanho ou cor.  
**TRIGGER:** rotação, oclusão, transparência, detalhe fino, mudança grande entre estados; `INFERRED`.  
**IMPACT:** produto incorreto, potencial problema factual/comercial.  
**EVIDENCE:** consistência/objetos e conservação `DOCUMENTED` em S-AIV-01/03/04.  
**DETECTION:** comparar contorno, landmarks, dimensões relativas, peças e cor nos frames críticos.  
**MITIGATION:** referência de produto limpa, ângulo limitado, superfícies críticas visíveis, ação atômica, boundary frames, rejeitar em vez de corrigir por copy.  
**RESIDUAL_RISK:** alto para produto complexo/transparente.

## FM-03 — Extra/missing fingers and hand fusion

**CAPABILITY:** Physical Interaction / Visual QA  
**FAILURE:** anatomia inválida, dedos fundidos/ausentes/extras ou mão incorporada ao objeto.  
**TRIGGER:** duas mãos próximas, grip fino, oclusão, twist, objeto pequeno; `INFERRED`.  
**IMPACT:** sinal imediato de IA e demonstração impossível.  
**EVIDENCE:** interação/ação/consistência temporal cobertas por S-AIV-01/04; causa interna `UNKNOWN`.  
**DETECTION:** inspeção antes/durante/depois do contato, contagem e separação visual de dedos.  
**MITIGATION:** grip simples, uma mão ativa, mão de suporte afastada, ângulo que revela contato, apoiar produto, dividir ação.  
**RESIDUAL_RISK:** alto em manipulação fina.

## FM-04 — Object duplication, disappearance or teleportation

**CAPABILITY:** Physical Interaction / Continuity  
**FAILURE:** objeto aparece/desaparece, duplica ou atravessa espaço sem trajetória.  
**TRIGGER:** oclusão total, múltiplos objetos semelhantes, entrada/saída de frame, contato; `INFERRED`.  
**IMPACT:** quebra causal e de confiança.  
**EVIDENCE:** permanência/oclusão `DOCUMENTED` em S-AIV-03/04.  
**DETECTION:** contagem e rastreamento de posição antes/depois de oclusões.  
**MITIGATION:** reduzir objetos, evitar oclusão total, manter landmark visível, declarar origem/destino e estado final.  
**RESIDUAL_RISK:** médio/alto.

## FM-05 — Background, prop or environment mutation

**CAPABILITY:** Continuity  
**FAILURE:** bancada, parede, puxador, objeto de fundo ou layout muda sem evento.  
**TRIGGER:** câmera/subject motion, reflexos, muita textura/props, duração; `INFERRED`.  
**IMPACT:** aparência artificial e inconsistência entre takes.  
**EVIDENCE:** background consistency `DOCUMENTED` em S-AIV-01.  
**DETECTION:** landmarks fixos no primeiro/meio/último frame.  
**MITIGATION:** fundo simples mas real, anchors explícitos, menos camera motion, referência de cenário/start frame.  
**RESIDUAL_RISK:** médio.

## FM-06 — Clothing/wardrobe/hair change

**CAPABILITY:** Continuity / Nina identity  
**FAILURE:** roupa, estampa, acessórios ou penteado mudam no take/sequência.  
**TRIGGER:** oclusão, giro, tecido complexo, cortes; `INFERRED`.  
**IMPACT:** quebra de identidade/continuidade.  
**EVIDENCE:** subject consistency `DOCUMENTED` em S-AIV-01.  
**DETECTION:** checklist de atributos canônicos em keyframes e handoff entre clips.  
**MITIGATION:** descrição/ref visual invariável, detalhes distintivos limitados, poses menos oclusivas, regenerar take inconsistente.  
**RESIDUAL_RISK:** alto em cenas de vestir.

## FM-07 — Lighting, shadow or reflection mismatch

**CAPABILITY:** Lighting / Materials  
**FAILURE:** luz muda, sombra aponta para fonte impossível ou reflexo não acompanha câmera/objeto.  
**TRIGGER:** fontes mistas, glossy/metal/vidro, rotação, espelho; complexidade física conhecida, resposta do gerador `UNKNOWN`.  
**IMPACT:** produto parece CGI/colado e material pode parecer errado.  
**EVIDENCE:** óptica `DOCUMENTED` S-MAT-01/02; avaliação temporal S-AIV-04.  
**DETECTION:** mapear fonte→highlight/sombra/reflexo em frames de orientação diferente.  
**MITIGATION:** reduzir fontes, declarar dominância/direção, evitar movimento simultâneo complexo, trocar ângulo/material de prova.  
**RESIDUAL_RISK:** alto em reflexivos/transparentes.

## FM-08 — Impossible contact/collision/hinge/slide/rotation

**CAPABILITY:** Physical Interaction  
**FAILURE:** interpenetração, eixo muda, dobradiça desloca, gaveta sai do trilho ou objeto desliza sem força.  
**TRIGGER:** mecanismo oculto, múltiplos graus de liberdade, câmera móvel; `INFERRED`.  
**IMPACT:** função demonstrada incorretamente.  
**EVIDENCE:** interação física/collision `DOCUMENTED` S-AIV-02/04.  
**DETECTION:** verificar anchor, eixo, contato, trajetória e limite mecânico frame a frame.  
**MITIGATION:** explicitar parte fixa/móvel, eixo/curso e apoio; mostrar mecanismo; uma ação por clip; redesign se crítico.  
**RESIDUAL_RISK:** alto para mecanismos finos.

## FM-09 — Implausible liquid

**CAPABILITY:** Materials / Physical Interaction  
**FAILURE:** fluxo nasce fora do bico, vira sólido, ignora gravidade, muda volume ou atravessa recipiente.  
**TRIGGER:** transparência + recipiente + mão + fluxo + câmera, viscosidade não definida; `INFERRED`.  
**IMPACT:** demonstração inverossímil e possível falsificação do produto.  
**EVIDENCE:** propriedades `DOCUMENTED` S-MAT-03; limitações solid-fluid `DOCUMENTED` S-AIV-02/04.  
**DETECTION:** continuidade da fonte ao destino, direção gravitacional, volume, salpico/menisco e fim do fluxo.  
**MITIGATION:** líquido simples e confirmado, câmera estática, recipiente/destino visíveis, rotação progressiva, clip curto; usar alternativa sem líquido se não essencial.  
**RESIDUAL_RISK:** alto.

## FM-10 — Implausible cloth deformation

**CAPABILITY:** Materials / Physical Interaction / Continuity  
**FAILURE:** tecido age como placa, derrete, estica ilimitadamente, troca estampa ou atravessa corpo.  
**TRIGGER:** vestir, duas mãos, contato com cabelo/corpo, material não definido; `INFERRED`.  
**IMPACT:** produto/fit falsos, identidade comprometida.  
**EVIDENCE:** cloth mechanics `DOCUMENTED` S-MAT-04; temporal/physics S-AIV-04.  
**DETECTION:** pontos de pegada, dobras, gravidade, contorno do corpo, textura/estampa e recuperação.  
**MITIGATION:** demonstrar um atributo por clip, ancorar grips, movimento lento/limitado, evitar vestir completo como primeira estratégia.  
**RESIDUAL_RISK:** alto.

## FM-11 — Unnatural motion / AI-looking movement

**CAPABILITY:** Temporal Direction / Cinematography  
**FAILURE:** gesto viscoso, velocidade incoerente, aceleração sem causa, câmera flutuante ou corpo sem peso.  
**TRIGGER:** verbos vagos, múltiplos movimentos, estado final distante; `INFERRED`.  
**IMPACT:** vídeo pode ser fotorrealista por frame e ainda parecer IA.  
**EVIDENCE:** motion smoothness/dynamics `DOCUMENTED` S-AIV-01; percepção social `INFERRED` de S-PHONE/UGC.  
**DETECTION:** playback normal/lento; verificar início, aceleração, contato, settle e balanço corporal.  
**MITIGATION:** trajetória e ritmo claros, amplitude pequena, apoio corporal, câmera simples, fases relativas, split.  
**RESIDUAL_RISK:** médio/alto.

## FM-12 — Over-smoothed skin / AI commercial look

**CAPABILITY:** Visual Style  
**FAILURE:** pele sem textura, luz publicitária perfeita, bokeh extremo e movimento de dolly tornam a peça artificial ao contexto UGC.  
**TRIGGER:** prompts genéricos de “cinematic/beautiful/perfect”, iluminação sem fonte; correlação `INFERRED`.  
**IMPACT:** reduz aparência social-native e confiança.
**EVIDENCE:** comportamento de smartphone `DOCUMENTED` S-PHONE-01..03; diferença de estilo `INFERRED`; padrões UGC S-UGC-01..05.  
**DETECTION:** comparar textura, DOF, altura/distância, estabilidade, fonte de luz e enquadramento com captura plausível.  
**MITIGATION:** remover adjetivos publicitários genéricos, especificar captura phone-like, luz prática e detalhe natural; não adicionar defeitos aleatórios.  
**RESIDUAL_RISK:** médio; preferência da audiência requer teste.

## FM-13 — Focus/exposure/white-balance instability

**CAPABILITY:** Cinematography / Lighting  
**FAILURE:** focus hunting, brightness pumping ou cast muda sem entrada/saída de fonte.
**TRIGGER:** aproximação, rosto/produto competindo, reflexivo, luz mista; comportamento real possível mas excesso é falha.  
**IMPACT:** produto ilegível e aparência amadora/artificial.  
**EVIDENCE:** controles automáticos `DOCUMENTED` S-PHONE-01/02; frequência no gerador `UNKNOWN`.  
**DETECTION:** scopes/inspeção visual ao longo do gesto, legibilidade de rosto/produto.  
**MITIGATION:** prioridade de foco/exposição, distância estável, contraste administrável, WB coerente; lock-like behavior quando a ação exige.  
**RESIDUAL_RISK:** médio.

## FM-14 — Conflicting instructions/input hierarchy

**CAPABILITY:** Generation Specification / Provider Adapter  
**FAILURE:** texto, ingredient, start/end frame ou negative request pedem atributos incompatíveis.
**TRIGGER:** descrição redundante, referências de estilos/identidades diferentes, alterações não priorizadas.  
**IMPACT:** controle ignorado, híbrido ou resultado imprevisível.  
**EVIDENCE:** orientação de não contradição `DOCUMENTED` S-FLOW-01/07; relatos `OBSERVED` S-FLOW-09.  
**DETECTION:** lint semântico pré-geração de atributos/ações conflitantes.  
**MITIGATION:** uma fonte canônica por atributo, referências coerentes, texto centrado na mudança, reduzir inputs.  
**RESIDUAL_RISK:** médio; prioridade interna do provider `UNKNOWN`.

## FM-15 — Exact timing not followed

**CAPABILITY:** Temporal Direction / GoogleFlowAdapter  
**FAILURE:** evento não ocorre no intervalo pedido, sequência muda ou hold final desaparece.  
**TRIGGER:** timestamps literais sem controle oficial, muitas fases, duração curta; `INFERRED`.  
**IMPACT:** sincronização/edição e prova falham.  
**EVIDENCE:** foco em uma cena `DOCUMENTED` S-FLOW-07; garantia de timestamp `UNKNOWN`.  
**DETECTION:** medir eventos no output e comparar ao `TemporalPlan`.  
**MITIGATION:** uma ação, sequência relativa, boundary frames, gerar clips separados e ajustar timing no FFmpeg.  
**RESIDUAL_RISK:** alto até experimento.

## FM-16 — Reference/style copied instead of abstracted

**CAPABILITY:** Reference Analysis / Creative Direction  
**FAILURE:** saída replica identidade, marca, composição distintiva ou sequência específica da referência.
**TRIGGER:** DNA não separa padrão reutilizável de elemento protegido/pessoal.  
**IMPACT:** originalidade, direitos e posicionamento comprometidos.  
**EVIDENCE:** limite deriva da missão/governança; análise por shot S-REF-01/02 apenas ajuda a localizar elementos.  
**DETECTION:** comparação estrutural/visual com referência e revisão de elementos proibidos.  
**MITIGATION:** extrair função/gramática em abstração, trocar cenário/blocking/composição, usar Nina/produto/fatos próprios.  
**RESIDUAL_RISK:** revisão humana necessária.

## FM-17 — Reference or control silently ignored by Flow

**CAPABILITY:** GoogleFlowAdapter / Provider Operation  
**FAILURE:** output não preserva referência ou camera control selecionado.
**TRIGGER:** combinações de modo/modelo/inputs; relação causal `UNKNOWN`.
**IMPACT:** consumo sem atender identidade/produto/câmera.  
**EVIDENCE:** disponibilidade `DOCUMENTED` S-FLOW-01..03; ocorrências relatadas `OBSERVED` S-FLOW-09.  
**DETECTION:** comparar output com invariantes e registrar configuração completa.  
**MITIGATION:** experimento controlado por modo, fallback/redesign, limite de retries; nunca mascarar como sucesso.  
**RESIDUAL_RISK:** desconhecido e `FAST_CHANGING`.

## FM-18 — Shot-boundary/reference analysis error

**CAPABILITY:** Reference Analysis  
**FAILURE:** mudança de luz/movimento vira corte falso, ou transição real não é detectada.
**TRIGGER:** flash, whip pan, dissolve, ação rápida.
**IMPACT:** ritmo, timing e gramática extraídos incorretamente.  
**EVIDENCE:** `DOCUMENTED` S-REF-01/02.  
**DETECTION:** revisão de candidatos com frames anteriores/posteriores e áudio quando útil.  
**MITIGATION:** combinar detecção, sampling e revisão humana; preservar timestamps/original.  
**RESIDUAL_RISK:** médio, administrável.
