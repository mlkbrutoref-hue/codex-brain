# Roadmap Controlado

O roadmap evita reescrita ampla e separa organização, estabilização e novas integrações.

## Fase 0 — Fonte de verdade

**Status:** concluída nesta etapa

- criar o Project Brain;
- registrar missão e CHIA;
- definir lifecycle único;
- definir FFmpeg como editor primário;
- classificar documentação antiga;
- registrar baseline sem esconder falhas.

## Fase 1 — Consolidar a baseline

**Próximo passo recomendado**

- revisar o working tree sem descartar alterações válidas;
- corrigir somente as duas divergências atuais da suíte;
- alinhar `README.md` e `docs/` com o Brain;
- decidir quais arquivos históricos serão arquivados;
- criar um commit de baseline revisável.

Critério de saída: suíte verde e documentação sem contradições materiais.

## Trilha transversal — Pesquisa antes do desenvolvimento

Antes do design profundo de qualquer capability importante, aplicar o padrão de `brain/RESEARCH_FIRST.md`. Essa trilha não pesquisa todas as capabilities antecipadamente; ela é ativada somente quando uma capability entra em desenvolvimento.

Primeira pesquisa profunda concluída em 23/09/2026: **Visual Production / Scene Direction**, com cinematografia, iluminação, materiais, interação física, direção temporal, continuidade, realismo em vídeo por IA, referência/UGC e prompting do Google Flow como conhecimento provider-specific.

O gate `DESIGN_RESEARCHED` foi aprovado com evidência rastreável em `brain/research/visual-production/`. Esse gate não substitui implementação, testes ou o status `READY`.

O framework dos experimentos E-01 a E-05 foi desenhado em 23/09/2026, sem operar o Flow. Ele define golden scenes, rubric, hard failures, blind comparison, repetitions, early-stop, budget, storage e knowledge promotion.

O primeiro pre-flight do E-01 parou corretamente no gate de produto. A aquisição posterior avaliou cinco produtos reais e selecionou o SKU `58267960935`, shop `1234187269`, cuja bandeja inferior corrediça passou pelos gates factual e visual. O repeat pre-flight foi concluído em 24/09/2026, com variante preta, originais/hashes, variáveis, prompts, configuração/custo atual do Flow, quatro runs cegos e pacote de avaliação congelados. Próximo passo dessa trilha: obter autorização humana explícita para gastar até 80 créditos e executar o screening de quatro outputs exatamente conforme `experiments/visual-production/E-01/preflight/`. Depois, avaliar às cegas e promover resultados apenas pelo fluxo de Project Learning. Contrato de runtime para `SceneDirection`, `GenerationSpecification` e `GoogleFlowAdapter` continua posterior aos experimentos.

O screening foi autorizado em 24/09/2026. Após o bloqueio inicial de Flow/reCAPTCHA, uma nova tentativa passou o recheck de 20 créditos, mas duas solicitações autorizadas de `E01-R01` falharam na geração de áudio; o Flow confirmou ausência de cobrança e nenhum output foi criado. Próximo passo: resolver o controle oficial de vídeo silencioso fora do run ou repetir formalmente o pre-flight com configuração/prompt revisado. Não editar silenciosamente o prompt congelado, trocar de modelo, iniciar `E01-R02..R04` nem promover learning enquanto não houver dados.

## Fase 2 — Contrato único de job

- alinhar os enums atuais ao lifecycle oficial;
- garantir um manifest único e idempotente;
- migrar o piloto existente sem quebrar artefatos;
- persistir Creative Direction, DNA, voz e relatórios de QA;
- criar comandos de retomada por `job_id`.

Critério de saída: qualquer job pode ser inspecionado e retomado sem depender do chat.

## Fase 3 — Editor FFmpeg completo

- cuts e concat determinísticos;
- mixagem de voz, áudio e música;
- legendas e overlays;
- CTA e textos temporizados;
- zoom/pan e transições básicas;
- variantes reais por plataforma;
- QA do master e das variantes.

Critério de saída: um conjunto de mídias aprovadas vira pacote final sem Canva.

## Fase 4 — Providers externos

- contrato real de visual generation;
- download e ingestão automática de takes;
- provider de voz;
- análise de referência persistida;
- pesquisa de tendências com evidências;
- Canva preservado como polimento opcional.

Critério de saída: integrações substituíveis e sem estado preso ao navegador.

## Fase 5 — Estoque e prioridade

- implementar Queue e Job Worker;
- implementar Stock Manager;
- suportar `PRIORITY JOB`;
- políticas de quantidade, diversidade e validade;
- catálogo `READY_TO_POST`.

Critério de saída: estoque controlado e pedidos especiais compartilhando o mesmo pipeline.

## Fase 6 — Scheduler, execução remota e publicação automática

**Status:** `FUTURE_CAPABILITY / PAUSED_UNTIL_CONTENT_FACTORY_VALIDATED`

- scheduler configurável;
- futura VM/cloud worker;
- observabilidade, limites de custo e recuperação;
- futura publicação automática somente em etapa separada e explicitamente reativada;
- Mobile Publisher, Phone Link, scrcpy, ADB, Android virtual/emulador e APIs de publicação permanecem preservados e pausados.

Critério para retomar esta fase: fábrica local validada, estoque `READY_TO_POST` funcionando e resultados reais suficientes para uma nova decisão explícita.

## Fora do escopo imediato

- gerar vídeos;
- operar Flow ou Canva;
- adicionar integrações;
- implementar Scheduler, Queue ou VM;
- reescrever o projeto inteiro.
