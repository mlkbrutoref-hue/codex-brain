# Visual Production — Fontes

**RESEARCH_DATE:** 23/09/2026  
**Escopo:** direção de cena para vídeos curtos de produto, cinematografia, luz, interação física, continuidade, falhas de vídeo por IA, linguagem UGC, análise de referência e Google Flow.  
**Estabilidade:** princípios visuais e físicos `STABLE`; práticas de geração `SEMI_STABLE`; Flow e padrões de plataforma `FAST_CHANGING`.

## Método e limites

As fontes abaixo foram consultadas em 23/09/2026. Documentação oficial define recursos declarados, mas não comprova que um recurso funcione com a mesma confiabilidade em toda conta, modelo, região ou cena. Estudos de benchmark indicam classes de falha, mas não medem automaticamente o Flow atual. Conteúdo de plataforma descreve linguagem nativa e, em alguns casos, inclui alegações comerciais do próprio fornecedor. Relatos de comunidade são sinais para teste, nunca autoridade de contrato.

## Google Flow e modelos atuais

### S-FLOW-01 — Create videos in Google Flow

- **Organização / URL:** Google — <https://support.google.com/flow/answer/16353334?hl=en>
- **Tipo / autoridade:** documentação oficial; alta para inputs e workflows declarados.
- **Descoberta:** o Flow aceita combinações atuais de texto, ingredients/referências, frames e, conforme o modo, vídeo. A orientação oficial pede assunto, ação, ambiente, iluminação e estilo. Start/end frames delimitam uma transição; referências limpas e visualmente coerentes ajudam a consistência.
- **Evidência:** `DOCUMENTED`.
- **Decisão influenciada:** separar a especificação visual universal da seleção de modo e inputs feita pelo adapter.

### S-FLOW-02 — Edit videos and build scenes in Flow

- **Organização / URL:** Google — <https://support.google.com/labs/answer/16935718?hl=en>
- **Tipo / autoridade:** documentação oficial; alta para recursos declarados, `FAST_CHANGING`.
- **Descoberta:** histórico, extensão, edição iterativa, salvamento de frames e Scenebuilder existem sob condições que variam por recurso/modelo/região; alguns modos não são compatíveis entre si.
- **Evidência:** `DOCUMENTED`.
- **Decisão influenciada:** não codificar um workflow único como capacidade universal; consultar a UI/documentação corrente no adapter.

### S-FLOW-03 — Flow models and supported features

- **Organização / URL:** Google — <https://support.google.com/flow/answer/16352836?hl=en>
- **Tipo / autoridade:** documentação oficial; alta e `FAST_CHANGING`.
- **Descoberta:** modelos e modos oferecem matrizes diferentes de duração, resolução, aspect ratio, frames, ingredients e controles.
- **Evidência:** `DOCUMENTED`.
- **Decisão influenciada:** duração, modelo e feature matrix não pertencem ao contrato permanente de `SceneDirection`.

### S-FLOW-04 — Flow product page

- **Organização / URL:** Google Labs — <https://labs.google/fx/tools/flow>
- **Tipo / autoridade:** página oficial de produto; alta para disponibilidade anunciada, limitada para alegações de qualidade.
- **Descoberta:** o produto combina modelos Google e anuncia geração/edição com suporte crescente a formatos sociais. Alegações de realismo e física são claims do fornecedor, não benchmark independente.
- **Evidência:** recursos `DOCUMENTED`; eficácia `UNKNOWN` até teste próprio.
- **Decisão influenciada:** Flow é provider atual essencial, mas substituível e sujeito a benchmark.

### S-FLOW-05 — Flow updates, February 2026

- **Organização / URL:** Google — <https://blog.google/innovation-and-ai/models-and-research/google-labs/flow-updates-february-2026/>
- **Tipo / autoridade:** anúncio oficial; alta para recursos anunciados, `FAST_CHANGING`.
- **Descoberta:** workflow unificado de imagem/vídeo, gestão de assets e controles como extensão, add/remove e camera motion evoluem rapidamente.
- **Evidência:** `DOCUMENTED`.
- **Decisão influenciada:** refresh obrigatório quando a matriz de modelos ou UI mudar.

### S-FLOW-06 — Video generation prompt guide

- **Organização / URL:** Google Cloud — <https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/video/video-gen-prompt-guide>
- **Tipo / autoridade:** documentação técnica oficial; alta para anatomia de prompt, com limitações declaradas.
- **Descoberta:** prompts úteis explicitam assunto, ação, contexto, câmera, óptica, iluminação, estilo/ambiente e, quando necessário, áudio/temporalidade. Termos avançados de lente/câmera não garantem controle exato.
- **Evidência:** `DOCUMENTED`.
- **Decisão influenciada:** `GenerationSpecification` deve preservar intenção observável e não prometer parâmetros cinematográficos exatos.

### S-FLOW-07 — Video generation best practices

- **Organização / URL:** Google Cloud — <https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/video/best-practice>
- **Tipo / autoridade:** documentação técnica oficial; alta.
- **Descoberta:** cenas curtas funcionam melhor com um momento principal; encadear várias ações pode produzir resultados incompletos. Em image-to-video, o prompt deve priorizar movimento e não contradizer/repetir desnecessariamente a imagem. Câmera, sujeito e ambiente devem ter movimentos distinguíveis.
- **Evidência:** `DOCUMENTED`.
- **Decisão influenciada:** decomposição atômica da ação e separação de movimentos são regras centrais.

### S-FLOW-08 — Export Flow data

- **Organização / URL:** Google — <https://support.google.com/labs/answer/17571126?hl=en>
- **Tipo / autoridade:** documentação oficial; alta.
- **Descoberta:** export pode incluir prompts, modelo, aspect ratio, controles, trims, assets, cenas e histórico.
- **Evidência:** `DOCUMENTED`.
- **Decisão influenciada:** metadados de geração podem futuramente sustentar rastreabilidade e Project Learnings, sem substituir artefatos locais.

### S-FLOW-09 — Relatos de referências/controles ignorados

- **Organização / URLs:** comunidades GoogleFlow/Veo — <https://www.reddit.com/r/GoogleFlow/comments/1wjt0px/google_flow_is_a_mess/>, <https://www.reddit.com/r/GoogleFlow/comments/1uoyyg2/google_flow_omni_model_ignore_refrence_image_in/>, <https://www.reddit.com/r/VEO3/comments/1tk268n/used_to_use_flow_as_a_main_job/>
- **Tipo / autoridade:** relatos de comunidade; baixa e volátil.
- **Descoberta:** usuários relatam referências, câmera ou comportamento mudando/ignorados após atualizações. Não há controle de versão, conta, prompt ou seleção de exemplos.
- **Evidência:** `OBSERVED` somente como relatos; causa e frequência `UNKNOWN`.
- **Decisão influenciada:** criar experimentos de aderência por modo/modelo e nunca tratar ingredient/camera control como garantia.

## Direção de cena, cinematografia e continuidade

### S-FILM-01 — Camera shots and angles

- **Organização / URL:** Adobe — <https://www.adobe.com/creativecloud/video/production/cinematography/camera-shots-and-angles.html>
- **Tipo / autoridade:** guia profissional; média-alta para vocabulário aplicado.
- **Descoberta:** tamanho do plano, ângulo, distância e composição mudam a informação narrativa e a relação sujeito-ambiente.
- **Evidência:** `DOCUMENTED`.
- **Decisão influenciada:** câmera deve ser descrita pela função visual, não por adjetivos soltos.

### S-FILM-02 — Shooting a sequence and continuity

- **Organização / URL:** Adobe — <https://www.adobe.com/creativecloud/video/production/cinematography/camera-shots-and-angles/sequence-shot.html>
- **Tipo / autoridade:** guia profissional; média-alta.
- **Descoberta:** wide/medium/close, storyboard, eixo de ação e match-on-action ajudam a construir continuidade legível.
- **Evidência:** `DOCUMENTED`.
- **Decisão influenciada:** manter screen direction, estado de ação e pontos de match entre takes.

### S-FILM-03 — Blocking actors

- **Organização / URL:** FilmSkills — <https://www.training.filmskills.com/fst/lesson/blocking-actors>
- **Tipo / autoridade:** treinamento profissional; média.
- **Descoberta:** blocking coordena movimento, posição, cenário e câmera; a ação deve parecer motivada e executável no espaço.
- **Evidência:** `DOCUMENTED`.
- **Decisão influenciada:** `SceneDirection` registra posições, orientação corporal, caminho e destino.

### S-FILM-04 — Script supervisor job profile

- **Organização / URL:** ScreenSkills — <https://www.screenskills.com/media/7610/final-jd-script-supervisor-110523.pdf>
- **Tipo / autoridade:** descrição profissional de continuidade; alta para responsabilidades da função.
- **Descoberta:** continuidade exige registrar blocking, ensaio, movimentos/composição de câmera, screen direction e eyelines.
- **Evidência:** `DOCUMENTED`.
- **Decisão influenciada:** continuidade vira estado explícito, não apenas “same character”.

### S-FILM-05 — Prose Storyboard Language

- **Autores / URL:** Ye e Baldwin — <https://arxiv.org/abs/1508.07593>
- **Tipo / autoridade:** pesquisa técnica; média-alta.
- **Descoberta:** um vocabulário limitado e estruturado pode representar storyboards plano a plano de forma humana e computacionalmente legível.
- **Evidência:** `DOCUMENTED`.
- **Decisão influenciada:** contrato pequeno e estruturado é preferível a prosa longa sem hierarquia.

### S-CAMERA-01 — Focal length, aperture and depth of field

- **Organização / URL:** Adobe — <https://www.adobe.com/creativecloud/photography/hub/guides/relationship-aperture-and-focal-length.html>
- **Tipo / autoridade:** guia técnico profissional; média.
- **Descoberta:** profundidade de campo depende de abertura, distância e focal; “fundo desfocado” não é um controle isolado.
- **Evidência:** `DOCUMENTED`.
- **Decisão influenciada:** UGC padrão usa profundidade moderada/alta; DOF extrema exige intenção específica.

### S-CAMERA-02 — Facial perspective and camera distance

- **Autores / URL:** Cooper et al., *Perception* — <https://pubmed.ncbi.nlm.nih.gov/22637709/>
- **Tipo / autoridade:** artigo científico; alta para o efeito perceptual estudado.
- **Descoberta:** distância de câmera e perspectiva alteram a aparência facial; “look de lente” envolve posicionamento, não apenas focal nominal.
- **Evidência:** `DOCUMENTED`.
- **Decisão influenciada:** evitar close extremo e perspectiva facial distorcida em demonstrações da Nina.

## Smartphone, luz e materiais

### S-PHONE-01 — Final Cut Camera settings

- **Organização / URL:** Apple — <https://support.apple.com/guide/final-cut-camera/change-camera-settings-dev0eb85c508/2.3/ios/18.6>
- **Tipo / autoridade:** documentação oficial de dispositivo/software; alta.
- **Descoberta:** smartphones operam autofocus, exposição, white balance, troca de lentes/zoom e estabilização, com possibilidade de lock.
- **Evidência:** `DOCUMENTED`.
- **Decisão influenciada:** look social plausível admite pequenas transições motivadas, mas nunca defeitos aleatórios que escondam o produto.

### S-PHONE-02 — iPhone focus/exposure and stabilization

- **Organização / URLs:** Apple — <https://support.apple.com/en-ie/guide/iphone/iph3dc593597/ios>, <https://support.apple.com/en-lk/guide/iphone/iphc1827d32f/ios>
- **Tipo / autoridade:** documentação oficial; alta.
- **Descoberta:** foco/exposição podem ajustar automaticamente ou ser bloqueados; estabilização pode recortar a imagem.
- **Evidência:** `DOCUMENTED`.
- **Decisão influenciada:** microcorreções são plausíveis; pulsação repetida de foco/exposição é falha, não “autenticidade”.

### S-PHONE-03 — Smartphone video stabilization

- **Autores / URL:** Karpenko et al., Stanford — <https://www.graphics.stanford.edu/papers/stabilization/>
- **Tipo / autoridade:** pesquisa técnica; alta.
- **Descoberta:** vídeo móvel sofre shake e rolling-shutter; estabilização usa sensores/movimento e tem limites.
- **Evidência:** `DOCUMENTED`.
- **Decisão influenciada:** handheld UGC significa deriva pequena e coerente, não tremor caótico.

### S-LIGHT-01 — Basic lighting for footage

- **Organização / URL:** Adobe — <https://stock.adobe.com/pages/artisthub/learn/how-to/basic-lighting-tips-for-amazing-stock-footage>
- **Tipo / autoridade:** guia profissional; média.
- **Descoberta:** key/fill/back, direção, intensidade relativa e difusão determinam volume e separação.
- **Evidência:** `DOCUMENTED`.
- **Decisão influenciada:** `LightingSpec` descreve fontes motivadas, dominância, direção e qualidade.

### S-LIGHT-02 — White balance

- **Organização / URL:** Adobe — <https://www.adobe.com/creativecloud/video/discover/white-balance.html>
- **Tipo / autoridade:** guia técnico profissional; média.
- **Descoberta:** fontes com temperaturas distintas criam casts diferentes e dificultam balanço global.
- **Evidência:** `DOCUMENTED`.
- **Decisão influenciada:** luz mista deve ser intencional, espacialmente coerente e verificada em pele, produto e fundo.

### S-MAT-01 — Reflection and refraction

- **Organização / URLs:** OpenStax — <https://openstax.org/books/physics/pages/16-1-reflection>, <https://openstax.org/books/physics/pages/16-2-refraction>
- **Tipo / autoridade:** livro-texto técnico; alta para princípios ópticos.
- **Descoberta:** superfícies lisas tendem a reflexão especular; superfícies rugosas espalham; materiais transparentes refletem e refratam conforme interfaces e índices.
- **Evidência:** `DOCUMENTED`.
- **Decisão influenciada:** highlights, reflexos e distorção do fundo devem responder à orientação/material, não flutuar independentemente.

### S-MAT-02 — Conductor reflection model

- **Organização / URL:** *Physically Based Rendering* — <https://www.pbr-book.org/4ed/Reflection_Models/Conductor_BRDF>
- **Tipo / autoridade:** referência técnica de computação gráfica; alta.
- **Descoberta:** metais/conductors têm resposta especular dependente do material e da microgeometria.
- **Evidência:** `DOCUMENTED`.
- **Decisão influenciada:** risco de reflexão aumenta com metal polido e movimento; QA deve comparar highlight com orientação e ambiente.

### S-MAT-03 — Liquid viscosity and surface tension

- **Organização / URLs:** OpenStax — <https://openstax.org/books/chemistry-atoms-first/pages/10-2-properties-of-liquids>, <https://openstax.org/books/college-physics-2e/pages/11-8-cohesion-and-adhesion-in-liquids-surface-tension-and-capillary-action>
- **Tipo / autoridade:** livros-texto; alta para princípios físicos.
- **Descoberta:** viscosidade governa resistência ao escoamento; coesão/adesão e tensão superficial afetam gotas, menisco e contato com recipientes.
- **Evidência:** `DOCUMENTED`.
- **Decisão influenciada:** “despejar líquido” precisa de origem, fluxo contínuo, recipiente de destino, gravidade e aparência compatível com viscosidade.

### S-MAT-04 — Large Steps in Cloth Simulation

- **Autores / URL:** Baraff e Witkin, SIGGRAPH 1998 — <https://doi.org/10.1145/280814.280821>
- **Tipo / autoridade:** pesquisa primária seminal; alta para propriedades simuladas de cloth.
- **Descoberta:** tecido é deformável, anisotrópico, sujeito a forças internas, damping e constraints; não se move como corpo rígido.
- **Evidência:** `DOCUMENTED`.
- **Decisão influenciada:** interação com roupa deve ancorar pontos de pegada e permitir dobras/deformação propagada por gravidade e movimento.

## Interação humano-produto e física em vídeo por IA

### S-HAND-01 — The GRASP Taxonomy of Human Grasp Types

- **Autores / URLs:** Feix et al. — <https://doi.org/10.1109/THMS.2015.2470657>, <https://is.mpg.de/uploads/publication_attachment/attachment/256/grasp_taxonomy.pdf>
- **Tipo / autoridade:** pesquisa primária; alta.
- **Descoberta:** grasps podem ser classificados por power/precision/intermediate, posição do polegar e oposição; tamanho e tarefa mudam o tipo adequado.
- **Evidência:** `DOCUMENTED`.
- **Decisão influenciada:** o contrato descreve mão ativa/de suporte, tipo funcional de grip e pontos de contato, não apenas “holding product”.

### S-HAND-02 — Anticipatory control of grip force

- **URL:** PubMed Central — <https://pmc.ncbi.nlm.nih.gov/articles/PMC5451044/>
- **Tipo / autoridade:** revisão/pesquisa científica; alta.
- **Descoberta:** força e posicionamento dos dedos se ajustam às propriedades/dinâmica esperadas do objeto para manter estabilidade.
- **Evidência:** `DOCUMENTED`.
- **Decisão influenciada:** peso, tamanho, torque e operação determinam uma ou duas mãos e o apoio necessário.

### S-HAND-03 — Manipulation task decomposition

- **URL:** PubMed Central — <https://pmc.ncbi.nlm.nih.gov/articles/PMC6377750/>
- **Tipo / autoridade:** pesquisa científica; alta.
- **Descoberta:** manipulação pode ser descrita por componentes centrados no objeto, ambiente e mão.
- **Evidência:** `DOCUMENTED`.
- **Decisão influenciada:** decompor approach → contact → grasp → actuation → release/final state.

### S-AIV-01 — VBench

- **Autores / URL:** Huang et al., CVPR 2024 — <https://openaccess.thecvf.com/content/CVPR2024/papers/Huang_VBench_Comprehensive_Benchmark_Suite_for_Video_Generative_Models_CVPR_2024_paper.pdf>
- **Tipo / autoridade:** benchmark científico revisado; alta para taxonomia de avaliação.
- **Descoberta:** consistência de sujeito/fundo, flicker, suavidade/dinâmica, qualidade, múltiplos objetos, ações, cor, relação espacial, cena e estilo são dimensões distintas.
- **Evidência:** `DOCUMENTED`.
- **Decisão influenciada:** QA não pode reduzir qualidade a uma impressão única nem a um frame.

### S-AIV-02 — VideoPhy

- **Autores / URL:** Bansal et al. — <https://arxiv.org/abs/2406.03520>
- **Tipo / autoridade:** benchmark científico; alta para categorias avaliadas, temporalmente limitado aos modelos testados.
- **Descoberta:** física de interações solid-solid, solid-fluid e fluid-fluid é uma fraqueza mensurável em geradores avaliados.
- **Evidência:** `DOCUMENTED` para o benchmark; desempenho do Flow atual `UNKNOWN`.
- **Decisão influenciada:** material e interação física entram no risk profile.

### S-AIV-03 — WorldModelBench

- **Autores / URL:** NeurIPS 2025 — <https://proceedings.neurips.cc/paper_files/paper/2025/hash/4ec03ed08a3fcb59e1c815b5598beff1-Abstract-Datasets_and_Benchmarks_Track.html>
- **Tipo / autoridade:** benchmark científico revisado; alta.
- **Descoberta:** adherence e plausibilidade física precisam ser avaliadas separadamente; mudanças sutis de tamanho/estado podem violar conservação e continuidade.
- **Evidência:** `DOCUMENTED`.
- **Decisão influenciada:** checar contagem, tamanho, massa aparente, contato e permanência ao longo do take.

### S-AIV-04 — VLIPP

- **Autores / URL:** Yang et al., ICCV 2025 — <https://openaccess.thecvf.com/content/ICCV2025/papers/Yang_VLIPP_Towards_Physically_Plausible_Video_Generation_ICCV_2025_paper.pdf>
- **Tipo / autoridade:** pesquisa revisada; alta.
- **Descoberta:** colisão, continuidade/permanência de objetos, oclusão e fluidos exigem avaliação temporal explícita.
- **Evidência:** `DOCUMENTED`.
- **Decisão influenciada:** QA amostra frames críticos e eventos, não apenas início/fim.

## Referências e linguagem social-commerce

### S-REF-01 — Video Intelligence shot change detection

- **Organização / URLs:** Google Cloud — <https://cloud.google.com/video-intelligence/docs/feature-shot-change>, <https://docs.cloud.google.com/video-intelligence/docs>
- **Tipo / autoridade:** documentação oficial; alta para o serviço e unidades de anotação.
- **Descoberta:** análise pode operar por vídeo, segmento, shot e frame; shot-boundary detection fornece candidatos de corte, não interpretação criativa completa.
- **Evidência:** `DOCUMENTED`.
- **Decisão influenciada:** `ReferenceDNA` preserva timestamps/frames e revisão humana dos limites.

### S-REF-02 — Survey of shot-boundary detection

- **URL:** Springer — <https://link.springer.com/article/10.1007/s10462-024-10742-1>
- **Tipo / autoridade:** revisão científica; alta.
- **Descoberta:** iluminação súbita, movimento e transições graduais podem confundir detecção de cortes.
- **Evidência:** `DOCUMENTED`.
- **Decisão influenciada:** não assumir que cada pico visual é uma nova cena.

### S-UGC-01 — TikTok Creative Codes

- **Organização / URL:** TikTok for Business — <https://ads.tiktok.com/business/en/creative-codes>
- **Tipo / autoridade:** guia oficial de plataforma; alta para convenções declaradas, limitada para universalizar performance.
- **Descoberta:** formato vertical, safe zone, hook/body/close, som e estímulos visuais são convenções recomendadas.
- **Evidência:** `DOCUMENTED`.
- **Decisão influenciada:** primeira leitura visual, produto e ação precisam sobreviver a interface mobile.

### S-UGC-02 — Product and niche creative tips

- **Organização / URLs:** TikTok Creative Center — <https://ads.tiktok.com/business/creativecenter/quicktok/online/tiktok_creative_accelerator/pc/en>, <https://ads.tiktok.com/business/creativecenter/quicktok/online/creative-tips-for-home-and-lifestyle/pc/en>, <https://ads.tiktok.com/business/creativecenter/quicktok/online/creative-tips-for-beauty-personal-care/pc/en>, <https://ads.tiktok.com/business/creativecenter/quicktok/online/creative-tips-fashion-apparel/pc/en>
- **Tipo / autoridade:** análise/guia oficial de plataforma; média-alta, com viés comercial.
- **Descoberta:** demos, show-and-tell, tutoriais, uso real, textura, resultado, try-on e múltiplos ângulos aparecem repetidamente; casa pede situação/problema, beleza pede aplicação/textura, moda pede fit/styling.
- **Evidência:** padrões `OBSERVED` nas análises da plataforma; causalidade universal `UNKNOWN`.
- **Decisão influenciada:** quatro casos de estudo usam prova visual específica do nicho, sem copiar criadores.

### S-UGC-03 — Top Ads Spotlight and Creative Center Help

- **Organização / URLs:** TikTok — <https://ads.tiktok.com/business/creativecenter/tiktok-topads-spotlight/pc/en>, <https://ads.tiktok.com/resources/help/article/creative-center>
- **Tipo / autoridade:** curadoria oficial de exemplos; média para padrões observáveis.
- **Descoberta:** problem/solution, comparação em tempo real, aplicação e demonstração da função aparecem em criativos selecionados.
- **Evidência:** `OBSERVED`; seleção não representa todo o universo.
- **Decisão influenciada:** analisar padrões repetidos e momentos de atenção, não replicar um anúncio.

### S-UGC-04 — YouTube Shopping Shorts tips

- **Organização / URL:** YouTube — <https://support.google.com/youtube/answer/15814303>
- **Tipo / autoridade:** documentação oficial de plataforma; alta para orientação declarada.
- **Descoberta:** storytelling orgânico, hook, close-up, demonstração, before/after e try-on são formatos sugeridos, com disclosure comercial.
- **Evidência:** `DOCUMENTED`.
- **Decisão influenciada:** prova visual e transparência comercial têm prioridade sobre acabamento publicitário genérico.

### S-UGC-05 — Reels ads creative guidance

- **Organização / URL:** Meta — <https://www.facebook.com/business/ads/facebook-instagram-reels-ads>
- **Tipo / autoridade:** orientação oficial de plataforma; alta para formato, limitada para claims de performance.
- **Descoberta:** 9:16, áudio e safe zones são centrais ao inventário de Reels.
- **Evidência:** `DOCUMENTED`.
- **Decisão influenciada:** composição deve reservar espaço funcional sem comprometer a demonstração.

## Lacunas de fonte

- Não existe documentação oficial encontrada que garanta aderência a timestamps exatos em prompts do Flow; essa tática permanece `UNKNOWN`/experimental.
- Não existe taxa pública e atual de falhas do Flow por categoria de cena/material; benchmarks gerais não substituem teste do provider.
- Padrões de UGC mudam rapidamente e variam por conta, região, categoria e audiência; devem ser atualizados antes de campanhas relevantes.
- Nenhuma fonte permite deduzir a causa interna de morphing, dedos extras ou referência ignorada; o projeto registra apenas gatilhos correlacionados e mitigação observável.
