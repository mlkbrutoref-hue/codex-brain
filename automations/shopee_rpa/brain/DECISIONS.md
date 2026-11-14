# Decisões Arquiteturais

## D-028 — Abandono explícito de preparação assistida com efeito histórico desconhecido

**Status:** aceita para recuperação assistida experimental; produção permanece pausada  
**Data:** 08/10/2026

Após confirmar que o vídeo permanece na galeria e que não existe rascunho do mousepad, o usuário aprovou expressamente registrar a preparação interrompida como abandonada e iniciar outra preparação no mesmo job, parando antes de Postar. Isso autoriza a resolução administrativa PREPARATION_ABANDONED sem afirmar que o Add anterior não executou ou que não houve upload nativo. A declaração explícita do operador de que não houve clique/publicação final é confrontada com configuração e sessão históricas ASSISTED_MODE, log de Add UNKNOWN e timestamp do incidente, ledger sem tentativa/autorização/transição de publicação ou upload explícito.

Uma tabela append-only preserva snapshot do job UNKNOWN, conteúdo e hashes das fontes históricas, autorização e preflight; arquivos originais e evento UNKNOWN permanecem intactos. O efeito do Add e o upload nativo seguem UNKNOWN. Mesmo asset só pode retomar no mesmo job/fingerprint em ASSISTED_MODE; novos jobs equivalentes continuam no dedup. Essa recuperação não permite LIVE_PUBLISH nem reserva de tentativa final, inclusive depois de ASSISTED_VALIDATED. Uma futura habilitação final precisará de decisão e validação próprias; este fluxo não a concede.

Somente o incidente RPC_EFFECT_UNKNOWN de preparação identificado pode ser liberado. Perfil/conta exatos, versão, estado sem editor, hash local/Android, conteúdo assistido, leases, kill switch e integridade são verificados; OPEN → HALF_OPEN → novo preflight somente leitura → CLOSED pelas APIs existentes, com transação para impedir corrida com outro incidente. Falhas mantêm UNKNOWN/OPEN. A conexão Android e o lock podem ser reutilizados pelo worker normal após a resolução, preservando deadlines, budgets, guardas de UI, QA e PublishGate. Legado PUBLISHED_LEGACY não participa desta migração. D-024 a D-027 preservadas, com esta exceção explicitamente aprovada para abandono assistido.

## D-027 — Diagnóstico somente leitura vinculado ao incidente de preparação

**Status:** aceita para diagnóstico experimental; produção permanece pausada  
**Data:** 08/10/2026

Autorizado pelo usuário um diagnóstico específico do UNKNOWN de preparação, sem liberar o breaker. A sessão somente leitura exige ASSISTED_MODE, referência explícita de autorização, identidade central e fingerprint correspondentes, UNKNOWN/RPC_EFFECT_UNKNOWN sem tentativa final ou autorização de publicação e ambas as leases retidas pelo owner original. Cada leitura revalida esse escopo. O lock exclusivo existente do dispositivo, RPC isolado, deadline, kill switch e budgets permanecem ativos. Leases não são transferidas nem removidas. Somente a fronteira de diagnóstico aceita ler sob OPEN; as sessões normais continuam obedecendo ao breaker original.

Essa capacidade não autoriza abrir telas, selecionar mídia, clicar Adicionar/Postar, emitir comandos shell arbitrários, resolver UNKNOWN ou fechar breaker. Conta/título/editor observados são evidências atuais e não provam retrospectivamente ausência de efeito ou de upload nativo. Recuperação continua pela lógica existente, com evidência suficiente; ausência de rascunho e arquivo na galeria não substituem essa prova. D-024, D-025 e D-026 preservadas. Contrato: `docs/publishing/preparation-diagnostic-2026-10-08.md`.

## D-026 — Validação assistida de UI separada da autorização final

**Status:** aceita para o protótipo experimental; produção permanece pausada  
**Data:** 07/10/2026

Por correção explícita do usuário, `ASSISTED_MODE` pode validar a interface com `rights=UNKNOWN`, sem fabricar licença ou reclassificar direitos. Proveniência `PLATFORM_PROVIDED / PRODUCT_LISTING_SOURCE`, evidência vinculada ao hash, correspondência mídia/produto, conta e checks da tela continuam obrigatórios; `rights=REJECTED` permanece bloqueado. IA desconhecida permanece null/UNKNOWN. Direitos, originalidade, disclosure e HumanReview completos continuam sujeitos aos gates estritos de publicação final.

`ASSISTED_VALIDATED` indica somente conclusão comprovada do fluxo de UI até o editor final. Não concede token de publicação nem equivale a `READY_FOR_PUBLISH`; o clique final permanece restrito a LIVE_PUBLISH e PublishGate. O estado assistido preserva dedup e uma eventual reentrada do mesmo job sem tentativa passa por novo preflight. UNKNOWN ou tentativa anterior nunca recebe essa exceção.

Motivo: validar tecnicamente mídia de anúncio com proveniência comprovada, sem confundir origem com licença de republicação. O teste real de 07/10 alcançou o editor, mas parou no vínculo do produto em novo RPC_EFFECT_UNKNOWN; a decisão não declara ASSISTED_VALIDATED para essa execução nem libera breaker. D-023, D-024 e D-025 permanecem vigentes. Evidência: `docs/publishing/assisted-validation-2026-10-07.md`.

## D-025 — Publicação legada resolvida administrativamente com lacunas preservadas

**Status:** aceita para o protótipo experimental; produção permanece pausada  
**Data:** 06/10/2026

O pedido explícito do usuário autoriza resolver tentativas anteriores ao PostCandidate/PublishGate como `PUBLISHED_LEGACY`, mediante conta/copy/hashtags públicos correspondentes, mídia histórica consistente, duração compatível e confirmação humana. Não reconstruir fingerprint ou IDs comerciais ausentes. Evidência original permanece intacta; prova nova e lacunas ficam em metadata separada, qualidade LEGACY_PARTIAL, product binding UNKNOWN e fingerprint NOT_AVAILABLE_LEGACY.

Esse estado é terminal, impede retry e mantém dedup permanente sem consumir tentativa diária. Jobs nativos mantêm os gates existentes. A remoção do UNKNOWN não fecha breaker automaticamente: exige avaliação auditada de escopo exclusivo, OPEN → HALF_OPEN, preflight local e do post público em modo read-only, e ausência de outro incidente antes de CLOSED. Outras causas de segurança, conta ou publicação não podem ser descartadas. A auditoria de novas falhas do breaker preserva reason e job em cada ocorrência.

Motivo: primeiro teste histórico real não persistiu o modelo atual e esses campos não são recuperáveis retroativamente; evidências correspondentes permitem encerrar a incerteza de publicação sem fingir validação comercial completa. Contrato: `docs/publishing/legacy-reconciliation.md`. D-023 e D-024 continuam vigentes; a resolução não autoriza publicar nem promove Publishing READY.

## D-024 — Controles operacionais do protótipo Android, isolados da produção

**Status:** aceita para implementação experimental offline; produção não liberada  
**Data:** 06/10/2026

O pedido explícito atual autoriza evoluir o módulo experimental Shopee Video sem executar publicações reais nesta entrega. O limite da fábrica local continua READY_TO_POST; esta exceção de desenvolvimento não habilita auto-publicação em produção e não promove Publishing a READY.

Estado operacional/dedup/budgets/breaker e leases usam um SQLite local compartilhado por usuário/deployment, independente de raiz de job e serial. Reserva de trabalho precede UI; reserva de tentativa final e cobrança são transacionais no PublishGate, com autorização expirada/consumida bloqueada. UNKNOWN não expira nem vira FAILED automaticamente. SQLite não coordena hosts diferentes ou bancos separados; isso permanece uma limitação declarada.

ShopeeUI é a fronteira de efeitos, com RPC em processo terminável, deadline global, budget, breaker e logs sanitizados. Default DRY_RUN. Human review exige fingerprint, reviewer, tempo e evidência; identidade/variante ausentes na UI param em REVIEW ou exigem atestação humana vinculada à observação atual. Confirmação usa reconciler de evidências, não toast/perfil. Helpers não dispõem de ação final. Nenhuma técnica de evasão ou permissão da plataforma é inferida destes controles.

Motivo: achados da auditoria existente e requisitos explícitos do usuário. Fontes, contratos e evidência: `docs/publishing/operational-safety-plan.md`, `operational-safety.md` e `output/operational_safety_20261006/verification.json`. D-023 permanece vigente para produção e demais frentes pausadas.

## D-023 — A fábrica local termina em `READY_TO_POST`; publicação automática fica pausada

**Status:** aceita  
**Data:** 03/10/2026

O escopo operacional atual termina quando uma campanha aprovada possui assets finais, copy, plano de postagem, manifest e resumo de QA em um pacote local `READY_TO_POST`. A publicação é feita manualmente pelo usuário no celular.

`AUTO_PUBLISHING = FUTURE_CAPABILITY / PAUSED`

`PAUSE_REASON = PAUSED_UNTIL_CONTENT_FACTORY_VALIDATED`

AWS, cloud VM, Android virtual, Android Studio Emulator, Phone Link, scrcpy, ADB para publicação, Mobile Publisher, automação de Instagram/TikTok, clique automático em Publicar e APIs de publicação não recebem desenvolvimento enquanto essa pausa estiver vigente. Código, testes, documentação e evidências existentes são preservados; pausa não significa remoção nem invalidação histórica.

Recomendação de horário permanece dentro do pacote como informação conservadora. Sem dados suficientes, o resultado deve declarar incerteza. Métricas posteriores à postagem entram manualmente, com campos indisponíveis em `null`; métricas nunca são inventadas.

O foco ativo é a cadeia local `research-first -> seleção/validação de produto -> pesquisa e mapa visual -> planejamento -> geração -> QA -> recomendação de horário -> READY_TO_POST`. Retomar publicação automática exige nova decisão explícita depois de a fábrica de conteúdo ser validada com resultados reais.

## D-022 — Mobile Publisher assistido e analytics isolado

**Status:** aceita para protótipo experimental, sem promoção a produção  
**Data:** 28/09/2026

Por solicitação explícita, `app/publishing/` prepara sessões locais com mídia/QA/copy vinculados por hashes, nove checks pré-publicação e parada obrigatória `STOP_BEFORE_FINAL_PUBLISH`. Não existe operação de publicação final. `app/mobile/` faz descoberta somente leitura; conexão e operação da interface continuam MANUAL, sem login automático ou troca de contas.

Analytics/time optimization pertence ao Antigravity em worktree separado e diretórios `app/performance/`, `tests/performance/`, `docs/performance/`. Publisher consome uma porta de recomendação injetável; não registra rascunhos como posts reais. A implementação de analytics e sua integração concreta permanecem pendentes de entrega revisada e testes. Sem merge automático. Fonte: `docs/publishing/DESIGN.md` e `docs/handoffs/antigravity_performance_tracker.md`.

## D-001 — Project Brain como fonte principal

**Status:** aceita  
**Data:** 23/09/2026

`brain/` passa a ser a fonte principal de missão, arquitetura, estado e roadmap. Documentos especializados podem continuar canônicos, mas ficam subordinados às decisões registradas aqui.

## D-002 — Ferramentas são substituíveis

**Status:** aceita

A missão e os contratos não incluem marcas ou fornecedores. Shopee, Flow, ElevenLabs, FFmpeg, Canva e serviços futuros são implementações substituíveis.

## D-003 — FFmpeg é o editor primário

**Status:** aceita

`PRIMARY_VIDEO_EDITOR = FFMPEG`

O editor primário deve oferecer montagem automatizada e determinística de:

- cuts e concat;
- áudio, voz e música;
- text overlays, captions e CTA;
- zoom/pan básico e transições;
- normalização de resolução e fps;
- exports por plataforma.

A implementação atual cobre somente parte desse contrato.

## D-004 — Canva fora do caminho crítico

**Status:** aceita

`CANVA = OPTIONAL_POLISH`

Canva pode ser usado para acabamento opcional ou exceções criativas. A integração existente não será removida, mas uma falha no Canva não poderá impedir a produção do master automatizado.

## D-005 — CapCut não é requisito

**Status:** aceita

`CAPCUT = NOT_REQUIRED`

O projeto não depende de CapCut para cumprir a missão ou concluir um job.

## D-006 — Um lifecycle oficial para todos os vídeos

**Status:** aceita

Estoque e pedidos especiais usam o mesmo lifecycle. A prioridade e a origem criativa podem mudar, mas os artefatos, estados e quality gates permanecem iguais.

## D-007 — Dois modos de direção criativa

**Status:** aceita

- `TREND_SELECTED`: pesquisa padrões atuais e seleciona um `Style DNA`.
- `USER_REFERENCE`: analisa uma referência específica e produz um `Reference DNA`.

Ambos alimentam o mesmo Creative Director.

## D-008 — Produção externa não equivale a job concluído

**Status:** aceita

Um vídeo presente apenas no Flow, Canva, Drive ou histórico do chat não é `PACKAGE_READY`. O pacote precisa estar persistido, validado e rastreável pelo `job_id`.

## D-009 — Nenhuma integração nova nesta reorganização

**Status:** aceita

Esta etapa cria somente documentação e baseline. Scheduler, Queue, Workers, Stock Manager e novos providers permanecem planejados.

## D-010 — Nome canônico da etapa de telemetria factual

**Status:** aceita  
**Data:** 23/09/2026

`FACT_EXTRACTION_MS` é o nome canônico. A etapa mede a execução do `FactExtractor`, não o estado ou o artefato genérico `Facts`. O teste já expressava esse contrato e outras verificações de telemetria usavam a mesma nomenclatura. O orquestrador foi alinhado ao contrato; não foi criada uma segunda métrica equivalente.

## D-011 — Score criativo conservador sem prova visual

**Status:** aceita  
**Data:** 23/09/2026

Para a fixture live da escova elétrica sem descrição técnica, mecanismo confirmado ou prova de resultado, o score canônico atual é `70`, com `decision=RESEARCH_REQUIRED`, `recommend_reel=false`, `visual_proof_basis=NONE` e `flow_prompt_ready=false`.

O valor histórico `80` pertencia a uma versão que recomendava o Reel apesar da ausência de prova visual suficiente. A lógica atual representa a decisão de segurança correta; o teste foi atualizado para validar o contrato completo, sem alterar a skill de produção.

## D-012 — Retomadas idempotentes não repetem a consulta de produto

**Status:** aceita  
**Data:** 23/09/2026

Quando os sete checkpoints criativos continuam válidos, uma segunda execução do mesmo `job_id` deve reutilizá-los, registrar sete `resume_skips` e manter apenas uma chamada `SHOPEE_FETCH_MS` no histórico agregado.

O teste anterior esperava duas chamadas ao provider, comportamento incompatível com o cache atual, com a retomada idempotente e com o objetivo de evitar operações externas desnecessárias. O teste foi alinhado ao contrato vigente; o código de cache não foi alterado.

## D-013 — Desenvolvimento global de capabilities é research-first

**Status:** aceita  
**Data:** 23/09/2026

Nenhuma capability importante deve receber design profundo ou implementação de produção sem pesquisa específica anterior. O ciclo obrigatório é:

`RESEARCH -> FINDINGS -> CAPABILITY DESIGN -> CONTRACT -> IMPLEMENTATION -> TEST / BENCHMARK -> PRODUCTION -> LEARNINGS`.

A pesquisa deve influenciar decisões concretas e preservar autoridade das fontes, classificação da evidência, incertezas, falhas conhecidas e validações necessárias. Quando a evidência externa não for suficiente, o projeto registra hipótese e experimento em vez de inventar uma conclusão.

`DESIGN_RESEARCHED` é um gate de maturidade do conhecimento e do design, separado de `READY`, que continua exigindo implementação reutilizável, validação e evidência de execução. O padrão completo está em `brain/RESEARCH_FIRST.md`.

## D-014 — Google Flow é o provider de produção visual atual obrigatório

**Status:** aceita  
**Data:** 23/09/2026

`VISUAL_GENERATION = REQUIRED_CAPABILITY`

`GOOGLE_FLOW = REQUIRED_CURRENT_PRODUCTION_PROVIDER`

`CURRENT_INTEGRATION = MANUAL_WITH_PARTIAL_LOCAL_PREPARATION`

`FUTURE_REPLACEABILITY = YES`

Google Flow não é parte permanente da missão nem do contrato universal, mas é essencial para a fábrica produzir visualmente hoje. A operação real continua manual e a preparação local é parcial; não existe geração/ingestão determinística integrada. A classificação anterior `OPTIONAL` confundia substituibilidade futura com necessidade operacional presente.

FFmpeg permanece `REQUIRED PRIMARY VIDEO EDITOR` conforme D-003. Canva permanece `OPTIONAL_POLISH` conforme D-004.

## D-015 — `Realism Prompting` é dividido em direção, especificação e adapter

**Status:** aceita como capability design pesquisado  
**Data:** 23/09/2026

`REALISM_PROMPTING_DECISION = SPLIT`

- `Scene Direction` planeja de forma provider-independent blocking, produto, ação, câmera, luz, interação física, tempo, continuidade e risco.
- `Generation Specification` preserva referências, invariantes, resultados obrigatórios, restrições contextuais e acceptance checks sem sintaxe de provider.
- um futuro `GoogleFlowAdapter` traduz a especificação para os modelos, modos, inputs, prompts e controles atualmente suportados.

As subespecificações de cinematografia, iluminação, interação física, tempo, continuidade e risco permanecem seções de um aggregate, não microserviços. A pesquisa passou o gate `DESIGN_RESEARCHED`; isso não cria implementação nem promove status para `READY`.

A evidência e o desenho detalhado estão em `brain/research/visual-production/`.

## D-016 — Visual risk é contextual e qualitativo até calibração

**Status:** aceita como capability design pesquisado  
**Data:** 23/09/2026

O risk profile usa inicialmente bandas `NONE`, `LOW`, `MEDIUM`, `HIGH` e `CRITICAL` por eixo: mãos, identidade, morph de produto, física, reflexão/refração, líquido, tecido, continuidade, oclusão e texto/logo quando aplicável.

Não há soma linear nem score numérico nesta fase. Cada risco deve ter trigger/evidência, mitigação, checks e fallback; combinações podem elevar a estratégia mesmo sem um eixo isolado crítico. Um perfil crítico pode exigir simplificação, split ou redesign antes da geração, em vez de um negative prompt universal.

Bands, compound risks e políticas de retry precisam de experimentos e Project Learnings antes de automatização.

## D-017 — Story único usa gerador e contrato próprios

**Status:** aceita  
**Data:** 25/09/2026

`NINA_SINGLE_STORY_GENERATOR` vive em `app/single_story/` e não reutiliza o lifecycle de vídeo, roteiro ou storyboard. Sua unidade de trabalho é exatamente uma peça estática 1080x1920, 9:16, autossuficiente, com `artifact_count=1`, `standalone=true` e nenhuma posição em sequência.

O módulo recebe produto, fatos confirmados, referências e direção opcional; seleciona ou aceita override de `PRODUCT_HIGHLIGHT`, `BENEFIT`, `USE_LIFESTYLE`, `AESTHETIC_EMOTIONAL` e `LIGHT_CTA`; e produz um `SingleStoryCreativePackage` provider-independent. Supporting e benefit text são fatos confirmados literais. O prompt final fica bloqueado sem referência resolvível do produto. Se Nina aparecer, as referências canônicas de rosto e 360 são usadas juntas.

Geração de imagem, operação de provider, QA final e publicação ficam fora deste módulo. A pesquisa e as decisões específicas estão em `brain/research/single-story-creative/`.

## D-018 — Story final separa geração visual e composição determinística

**Status:** aceita  
**Data:** 25/09/2026

`NINA_REAL_SINGLE_STORY_PIPELINE` usa o provider built-in de imagens do Codex para criar a fotografia-base e Pillow para tipografia, gráficos, auto-fit e composição final. Google Flow permanece exclusivo do fluxo de vídeo e não participa de Stories estáticos.

O contrato persiste `base_image.png`, `text_overlay.png`, `story_final.png`, `creative_package.json`, `layout.json`, `qa.json`, `manifest.json`, `prompt.txt` e `asset_manifest.json`. Zonas seguras e bounds tipográficos são dados do layout, não instruções implícitas. Copy que não caiba acima do mínimo legível causa `TEXT_LAYOUT_FAIL`.

QA técnico valida dimensão, camada, texto-fonte, overflow, contraste e safe zones. Fidelidade, física, realismo, artefatos, composição e marca ficam `REVIEW` até revisão visual explícita. Correções de texto/layout preservam a imagem-base; regeneração completa é último recurso.

A evidência e o desenho estão em `brain/research/single-story-rendering/`.


## D-019 — Política compartilhada de proporção e QA com evidência

**Status:** aceita  
**Data:** 26/09/2026

Regras de corpo/câmera da Nina ficam em `data/personas/nina_v1/proportion_rules.txt` e `proportion_negative.txt`, consumidas por PromptBuilder, Story de produto e lifestyle através de `app/creative/proportion_policy.py`. A identidade facial não transfere a perspectiva de close para o corpo; o 360 define a silhueta, respeitando a direção corporal mais recente do usuário.

Os pipelines estáticos e VisualQAResult exigem sete checks anatômicos. Aprovação requer revisão explícita vinculada ao hash do arquivo e das referências. Isso é um gate determinístico sobre revisão visual, não um detector automático de anatomia. Correções preservam a tentativa anterior, têm limite de uma geração por execução e passam novamente pelo QA. Providers e revisores podem ser injetados; o built-in imagegen continua operado pelo agente.

A nova implementação foi validada com testes de falha/ausência de evidência/recuperação e três imagens reais. Não promove geração visual ou QA semântico a automação ponta a ponta. Evidência: `output/nina_proportion_validation/` e `docs/nina-proportion-correction.md`.


## D-020 — Carrossel 3:4 reutiliza o compositor estático existente

**Status:** aceita  
**Data:** 27/09/2026

`NINA_CAROUSEL_PIPELINE` é uma camada fina de sequência e integração. Ela formaliza slides `COVER`, `PRODUCT` e `CTA`, usa canvas 1080x1440, prepara pedidos provider-independent, reutiliza `StoryTypographyRenderer`, executa QA por slide e persiste um manifesto agregado.

O carrossel não cria outro motor tipográfico, provider de imagem ou cópia do pipeline de Story. Os presets 3:4 vivem em `app/carousel/`, enquanto os contratos `LayoutPlan`, `SafeZone` e `LayoutComponent` e o renderer Pillow continuam compartilhados com `app/single_story/`. A geração de imagens e o QA visual semântico permanecem assistidos; o runtime apenas prepara, ingere, compõe, valida checks determinísticos e registra a revisão explícita. A correção é limitada a uma tentativa por slide.


## D-021 — Carrossel usa geração integral por IA como padrão

**Status:** aceita; substitui D-020 como padrão visual do carrossel  
**Data:** 27/09/2026

`NINA_CAROUSEL_PIPELINE` usa `FULL_AI_CREATIVE` por padrão. Fotografia, copy, tipografia, pills, caixas, annotations e decoração são dirigidas e geradas como uma única peça visual. Pinterest controla cena, câmera, luz e mood; referências editoriais da Nina controlam hierarquia, tipografia e decoração; referências canônicas controlam a personagem; assets oficiais controlam produtos.

Python permanece responsável por plano, dimensões, arquivos, metadata, manifesto e QA, mas não desenha o slide final por padrão. O compositor Pillow anterior fica disponível apenas pelo modo explícito `DETERMINISTIC_COMPOSITOR` e os seis slides já produzidos permanecem classificados como `DETERMINISTIC_COMPOSITOR_BASELINE`.

O QA do modo integral verifica presença e exatidão do texto, ortografia, acentos, keyword, legibilidade, coesão e aparência de template, além dos checks visuais existentes. Erro localizado de texto ou decoração usa no máximo uma edição localizada por IA; se continuar após a tentativa, termina em `TEXT_RENDER_REVIEW_REQUIRED`, sem fallback automático para design Pillow.

## D-030 — Reutilização de anúncio sob aceitação finita do operador

**Status:** aceita para lote supervisionado experimental, sem promover produção autônoma
**Data:** 10/10/2026

O operador autorizou cinco posts de vídeos dos próprios anúncios, incluindo mídia horizontal e escopo de produto base/todas as cores do anúncio. Uma revisão explícita vinculada a hashes de fonte, preparado, conta, produto e legenda, com expiração, pode registrar OPERATOR_ACCEPTED para direitos/originalidade/IA desconhecidos. Isso não altera UNKNOWN para VERIFIED, não comprova licença, autorização da Shopee ou atributos/IDs de variante ausentes; REJECTED e demais bloqueios não são dispensados. PublishGate, tentativas, budgets, ledger e dedup permanecem ativos. Mídia horizontal pode ser preparada preservando aspecto, conteúdo e original; qualidade técnica continua obrigatória.

Colisão de duração na galeria exige revisão visual atual vinculada à mídia e aos pixels selecionados antes de Próximo. O editor sem prova de capa termina em EDITOR_MEDIA_REVIEW e requer revisão explícita antes do produto. Reconciliação administrativa de um Próximo já observado mantém job/asset/owner, histórico e upload UNKNOWN; não repete ação nem cria tentativa de publicação. Recuperação do breaker continua limitada aos incidentes comprovados do escopo, com preflight somente leitura. Evidências e testes direcionados: `output/posting_batch_20261010/`.

## D-029 — Reconciliação de Add observado sem repetição

**Status:** aceita para ASSISTED_MODE experimental
**Data:** 08/10/2026

Um UNKNOWN de EXPECTED_STATE_TIMEOUT após clique Add comprovadamente SUCCESS pode voltar a PREPARING no mesmo job/owner somente por reconciliação auditada do efeito observado. Exige revisão vinculada ao candidato/card, folha nativa do produto correto, hashes local/Android, ausência de tentativa/autorização final e de outro incidente impeditivo. OPEN → HALF_OPEN → preflight somente leitura → CLOSED. Snapshot UNKNOWN e evidência permanecem no ledger; upload nativo continua UNKNOWN. Não concede autorização para publicação. O operador autorizou explicitamente continuar em Feito; nenhum Add é repetido.

O digest usado para manter a identidade do produto já vinculado ignora geometria e foco transitórios. Texto, pacote, classe, resource-id e demais atributos semânticos permanecem verificados. O hash integral de tela imediatamente antes de Adicionar permanece obrigatório.
