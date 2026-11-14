# Visual Production — Best Practices

Estas regras são acionáveis e provider-independent, exceto quando marcadas `GOOGLE_FLOW_SPECIFIC`. Evidência `INFERRED` exige validação antes de virar política rígida de produção.

## BP-01 — Planejar por estados verificáveis

- **RULE:** declarar estado inicial, mudança principal e estado final de sujeito, produto e props relevantes.
- **SCOPE:** toda cena com ação.
- **EVIDENCE:** `DOCUMENTED`/`INFERRED`; S-FILM-02/03/05, S-FLOW-07.
- **RATIONALE:** remove ambiguidade e oferece pontos de QA.
- **EXCEPTIONS_OR_LIMITS:** atmosfera sem transformação pode usar um estado sustentado.
- **VALIDATION:** primeiro/último frame e evento crítico correspondem aos estados descritos.

## BP-02 — Uma ação dominante por clip

- **RULE:** manter um objetivo físico principal; dividir sequências com múltiplas manipulações dependentes.
- **SCOPE:** vídeos gerados curtos.
- **EVIDENCE:** `DOCUMENTED`; S-FLOW-07.
- **RATIONALE:** reduz ações omitidas, fundidas ou incompletas.
- **EXCEPTIONS_OR_LIMITS:** microações inseparáveis da principal, como segurar enquanto gira, pertencem ao mesmo gesto.
- **VALIDATION:** uma frase identifica sem “e depois” a transformação dominante; se não, considerar split.

## BP-03 — Descrever movimento por entidade

- **RULE:** separar `camera_motion`, `subject_motion`, `product_motion` e `environment_motion`; cada movimento tem agente, trajetória/eixo, limite e resultado.
- **SCOPE:** toda cena com movimento.
- **EVIDENCE:** `DOCUMENTED`/`INFERRED`; S-FLOW-06/07.
- **RATIONALE:** “a cena se move” não define quem muda de posição.
- **EXCEPTIONS_OR_LIMITS:** `none/static` é um valor válido e explícito.
- **VALIDATION:** nenhuma entidade recebe comandos incompatíveis no mesmo beat.

## BP-04 — Priorizar prova visual do produto

- **RULE:** identificar a superfície/mecanismo de prova e mantê-lo visível no contato, atuação e resultado.
- **SCOPE:** demonstrações de produto.
- **EVIDENCE:** `OBSERVED`/`INFERRED`; S-UGC-02/03/04.
- **RATIONALE:** beleza sem compreensão funcional não cumpre social-commerce.
- **EXCEPTIONS_OR_LIMITS:** uma oclusão breve e motivada é aceitável se o antes/depois permanecer inequívoco.
- **VALIDATION:** reviewer consegue explicar o mecanismo sem depender da legenda.

## BP-05 — Usar grip e apoio compatíveis com a tarefa

- **RULE:** declarar mão ativa, mão de suporte, pontos de contato, apoio ambiental e tipo funcional de grip conforme tamanho, peso e precisão.
- **SCOPE:** interação humano-produto.
- **EVIDENCE:** `DOCUMENTED`; S-HAND-01/02/03.
- **RATIONALE:** o gesto plausível depende de estabilidade e affordance.
- **EXCEPTIONS_OR_LIMITS:** propriedade desconhecida do produto permanece `UNKNOWN`; não inventar peso/material.
- **VALIDATION:** objeto não flutua, a mão não atravessa o objeto e a função não depende de dedos impossíveis.

## BP-06 — Decompor manipulação complexa

- **RULE:** modelar `approach -> contact -> grasp -> actuation -> settle/release` e remover fases irrelevantes, sem saltos invisíveis de estado.
- **SCOPE:** tampas, botões, gavetas, ferramentas, vestir, líquido e objetos pequenos.
- **EVIDENCE:** `DOCUMENTED`/`INFERRED`; S-HAND-03, S-AIV-04.
- **RATIONALE:** contatos e permanência são pontos comuns de falha temporal.
- **EXCEPTIONS_OR_LIMITS:** a geração pode começar já em `grasp` quando approach não agrega valor.
- **VALIDATION:** todo estado final tem um evento causal visível.

## BP-07 — Simplificar a câmera quando a física é difícil

- **RULE:** preferir câmera estática ou handheld leve quando a cena combina mãos, oclusão, líquido, transparência, tecido ou mecanismo fino.
- **SCOPE:** cenas de risco médio/alto.
- **EVIDENCE:** `INFERRED` a partir de S-AIV-01..04; precisa benchmark do Flow.
- **RATIONALE:** reduz movimentos concorrentes e melhora inspeção.
- **EXCEPTIONS_OR_LIMITS:** movimento de câmera pode ser essencial ao conceito e deve então ser testado isoladamente.
- **VALIDATION:** comparar variante simples e móvel; escolher por aderência/QA, não por preferência abstrata.

## BP-08 — Descrever look de smartphone por comportamento plausível

- **RULE:** usar altura/distância humanas, perspectiva moderadamente ampla, DOF moderada/alta, microderiva estabilizada e autoajuste apenas quando motivado.
- **SCOPE:** `BELIEVABLE_SOCIAL_VIDEO`.
- **EVIDENCE:** `DOCUMENTED`/`INFERRED`; S-PHONE-01/02/03.
- **RATIONALE:** imita condições de captura, não um filtro de “imperfeição”.
- **EXCEPTIONS_OR_LIMITS:** tripé, macro, slow motion ou estética comercial são válidos quando deliberados.
- **VALIDATION:** produto continua legível; não há shake caótico, focus hunting ou exposição pulsante.

## BP-09 — Tratar cinematografia como intenção observável

- **RULE:** combinar vocabulário técnico com efeito pretendido: o que aparece, em qual relação espacial e por quê.
- **SCOPE:** câmera, lente, DOF e composição.
- **EVIDENCE:** `DOCUMENTED`; S-FILM-01, S-CAMERA-01/02, S-FLOW-06.
- **RATIONALE:** termos ou números isolados não garantem reprodução pelo provider.
- **EXCEPTIONS_OR_LIMITS:** parâmetros exatos podem ser usados quando a ferramenta realmente os expõe e o adapter os valida.
- **VALIDATION:** acceptance check descreve o resultado visível, não apenas o termo solicitado.

## BP-10 — Motivar cada fonte de luz

- **RULE:** declarar fonte dominante e secondary/practicals, direção, qualidade, família de cor e efeito em pele/produto/sombra/reflexo.
- **SCOPE:** todas as cenas, inclusive “natural light”.
- **EVIDENCE:** `DOCUMENTED`; S-LIGHT-01/02, S-MAT-01/02.
- **RATIONALE:** “bem iluminado” não define uma cena fisicamente coerente.
- **EXCEPTIONS_OR_LIMITS:** em exterior difuso, céu/nuvens podem funcionar como fonte ampla sem sombra dura.
- **VALIDATION:** sombras e highlights apontam para fontes plausíveis; produto e pele preservam detalhe.

## BP-11 — Fazer material governar aparência e movimento

- **RULE:** vincular reflexão/refração, rigidez/deformação e fluxo ao material confirmado e à ação.
- **SCOPE:** plástico, vidro, metal, tecido, líquido, madeira, borracha, matte/glossy.
- **EVIDENCE:** `DOCUMENTED`/`INFERRED`; S-MAT-01..04.
- **RATIONALE:** consistência material é parte da identidade do produto e da física percebida.
- **EXCEPTIONS_OR_LIMITS:** composição/material não confirmado não pode ser deduzido da imagem.
- **VALIDATION:** geometria, highlight, deformação e comportamento temporal permanecem compatíveis com `ProductFacts`.

## BP-12 — Registrar continuidade como ledger

- **RULE:** fixar atributos imutáveis e handoff de estado: Nina, produto, roupa/cabelo, mão/grip, lado/direção, props, luz e ambiente.
- **SCOPE:** take único e sequência multi-clip.
- **EVIDENCE:** `DOCUMENTED`; S-FILM-02/04, S-AIV-01.
- **RATIONALE:** “same character/product” não cobre os elementos que podem derivar.
- **EXCEPTIONS_OR_LIMITS:** transformação deliberada precisa de evento ou corte registrado.
- **VALIDATION:** comparação entre keyframes e com o take anterior não encontra mudança causalmente inexplicada.

## BP-13 — Preservar referência e texto sem contradição

- **RULE:** referências devem ser limpas, autorizadas e coerentes; em I2V, o texto enfatiza movimento/mudança e não redescreve de forma incompatível o frame.
- **SCOPE:** `GOOGLE_FLOW_SPECIFIC` no formato, universal no princípio de não contradição.
- **EVIDENCE:** `DOCUMENTED`; S-FLOW-01/07.
- **RATIONALE:** inputs conflitantes tornam prioridade e identidade ambíguas.
- **EXCEPTIONS_OR_LIMITS:** edição deliberada pode solicitar mudança explícita, com atributo-alvo definido.
- **VALIDATION:** revisão pré-geração não encontra duas descrições diferentes para o mesmo atributo.

## BP-14 — Usar tempo relativo como contrato; timestamp como hipótese

- **RULE:** `TemporalPlan` usa fases e beat windows internamente; o adapter não promete aderência a segundos exatos sem teste atual.
- **SCOPE:** temporal direction e tradução para providers.
- **EVIDENCE:** fases `INFERRED`; falta de garantia oficial `UNKNOWN`; S-FLOW-06/07.
- **RATIONALE:** timing é necessário para edição/QA, mas sintaxe de prompt não equivale a controle temporal comprovado.
- **EXCEPTIONS_OR_LIMITS:** ferramenta com timeline/control explícito pode receber tempos exatos por adapter.
- **VALIDATION:** experimento mede início/fim de eventos antes de aprovar sintaxe temporal.

## BP-15 — Tornar risco contextual, não um negative prompt universal

- **RULE:** ativar restrições/mitigações somente para eixos presentes na cena; a combinação de riscos governa estratégia.
- **SCOPE:** preparação de geração e QA.
- **EVIDENCE:** `INFERRED` a partir de S-AIV-01..04.
- **RATIONALE:** listas enormes diluem a intenção e não distinguem cena simples de manipulação crítica.
- **EXCEPTIONS_OR_LIMITS:** invariantes globais de identidade/factualidade continuam em toda cena.
- **VALIDATION:** cada restrição aponta para trigger, risco e check; nenhuma frase defensiva órfã.

## BP-16 — Inspecionar o evento, não o thumbnail

- **RULE:** revisar início, meio, fim e frames imediatamente antes/durante/depois de contatos, oclusões e transformações.
- **SCOPE:** Visual QA.
- **EVIDENCE:** `DOCUMENTED`; S-AIV-01..04.
- **RATIONALE:** falhas temporais podem desaparecer em um still selecionado.
- **EXCEPTIONS_OR_LIMITS:** checks automáticos são auxiliares e não substituem inspeção de alto risco.
- **VALIDATION:** checklist cobre identidade, contagem, geometria, contato, movimento, material, luz e estado final.

## BP-17 — Extrair Reference DNA sem copiar identidade

- **RULE:** segmentar por shots/keyframes, separar movimentos e extrair gramáticas/padrões; excluir identidade, marca e composição distintiva não autorizada.
- **SCOPE:** `USER_REFERENCE` e pesquisa de exemplos.
- **EVIDENCE:** `DOCUMENTED`/`INFERRED`; S-REF-01/02, S-FILM-05.
- **RATIONALE:** referência deve orientar estrutura e linguagem, não produzir réplica.
- **EXCEPTIONS_OR_LIMITS:** uso de assets próprios/autorizados segue os direitos registrados.
- **VALIDATION:** cada atributo do DNA é classificado como reutilizável/proibido e ligado a timestamp/frame.

## BP-18 — Atualizar conhecimento rápido antes de operar

- **RULE:** conferir documentação/model matrix/UI atual do Flow e pesquisa recente da plataforma antes de decisão de produção relevante.
- **SCOPE:** Flow e padrões UGC `FAST_CHANGING`.
- **EVIDENCE:** `DOCUMENTED`; S-FLOW-02/03/05, S-UGC-01..05.
- **RATIONALE:** feature, modelo, região, custo e linguagem social mudam.
- **EXCEPTIONS_OR_LIMITS:** princípios físicos/cinematográficos estáveis não precisam de refresh por job.
- **VALIDATION:** metadata futura registra research date e configuração corrente.
