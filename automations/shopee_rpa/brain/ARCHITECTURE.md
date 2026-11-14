# Arquitetura Oficial

## 1. Visão de alto nível

```text
                   +-------------------+
TREND_SELECTED --->|                   |
                   | Creative Director |---> Creative Direction
USER_REFERENCE --->|                   |
                   +-------------------+
                            |
                            v
Product -> Facts -> Script -> Storyboard -> Scene Direction
                                                |
                                                v
                                  Generation Specification
                                                |
                                                v
                              Provider Adapter -> Visual Generation
                                                |
                                                v
                                        Media + Visual QA
                                                |
                                                v
Voice -> FFmpeg Editor -> Final QA -> Package -> READY_TO_POST
```

`READY_TO_POST` é o terminal operacional atual. O handoff seguinte é manual: o usuário abre o pacote no celular e publica. Publicação automática e infraestrutura dedicada de publicação são uma capability futura pausada; não fazem parte do caminho crítico da fábrica local.

O pipeline deve funcionar sem depender do chat que iniciou a execução. O chat pode criar, supervisionar, aprovar ou corrigir um job, mas o estado pertence ao job.

## 2. Entradas criativas

### TREND_SELECTED

1. Pesquisa sinais atuais do nicho.
2. Registra fontes e evidências.
3. Extrai padrões reutilizáveis de hook, ritmo, enquadramento, texto e CTA.
4. Produz um `Style DNA` selecionado.
5. Envia o DNA ao Creative Director.

### USER_REFERENCE

1. Recebe vídeo, imagens ou URL escolhida pelo usuário.
2. Analisa estrutura e linguagem sem copiar literalmente.
3. Registra elementos reutilizáveis e elementos proibidos.
4. Produz um `Reference DNA`.
5. Cria um `PRIORITY JOB` para o mesmo Creative Director.

## 3. Production Pipeline

Fluxo conceitual oficial:

```text
Product
  -> Facts
  -> Creative Direction
  -> Script
  -> Storyboard
  -> Scene Direction
  -> Generation Specification
  -> Visual Generation
  -> Visual QA
  -> Voice
  -> Editing
  -> Final QA
  -> Package
```

Cada etapa recebe artefatos versionados e produz saídas explícitas. Uma etapa não deve depender apenas de texto perdido em conversa.

## 4. Lifecycle oficial

| Estado | Condição mínima |
|---|---|
| `CREATED` | Job identificado, origem e objetivo registrados. |
| `PRODUCT_READY` | Produto e fonte comercial persistidos. |
| `FACTS_READY` | Fatos classificados e rastreáveis. |
| `CREATIVE_DIRECTION_READY` | Modo criativo, DNA, formato e tese aprovados. |
| `SCRIPT_READY` | Roteiro validado factual e narrativamente. |
| `STORYBOARD_READY` | Cenas, timings, ações e referências definidos. |
| `GENERATION_READY` | `GenerationSpecification`, referências, request do provider, orçamento e autorização prontos. |
| `MEDIA_READY` | Todos os takes esperados estão armazenados e identificados. |
| `VOICE_READY` | Voz final persistida e vinculada ao roteiro aprovado. |
| `EDITING` | Montagem determinística em andamento. |
| `QA` | Master submetido aos gates técnico, visual e factual finais. |
| `PACKAGE_READY` | Master, variantes, copy, manifest e relatórios completos. |
| `REVIEW_REQUIRED` | Decisão humana necessária antes de avançar. |
| `FAILED` | Falha terminal registrada com causa e estágio. |

### Regras de transição

- Nenhuma etapa pode marcar a seguinte apenas porque uma operação externa foi solicitada.
- `MEDIA_READY` exige arquivos locais válidos, não somente thumbnails em um serviço.
- `VOICE_READY` exige arquivo final e metadados de geração.
- `QA` deve distinguir QA técnico de QA visual.
- `PACKAGE_READY` exige evidência local completa e manifest atualizado.
- Regenerações voltam para o estado apropriado e registram motivo e custo conhecido.

## 5. Estrutura conceitual de um job

```text
output/<job_id>/
  manifest.json
  product.json
  facts.json
  creative_direction.json
  script.json
  storyboard.json
  prompts/
  generated/
  audio/
  subtitles/
  master/
  platforms/
  content/
  qa/
```

O manifest deve registrar origem, modo criativo, versões dos artefatos, estados, timestamps, regenerações, consumo conhecido, falhas e caminhos das entregas.

## 6. Editor de vídeo

`PRIMARY_VIDEO_EDITOR = FFMPEG`

O compositor FFmpeg será responsável pelo master reproduzível. O contrato-alvo inclui cuts, concat, voz, música, mixagem, overlays, captions, CTA, zoom/pan, transições, normalização e exports.

`CANVA = OPTIONAL_POLISH`

O Canva pode receber um master ou assets para refinamento opcional. Seu uso não altera o estado canônico até que o resultado volte ao diretório do job e seja validado.

`CAPCUT = NOT_REQUIRED`

## 7. Automação de estoque

```text
Scheduler -> Queue -> Job Worker -> Stock Manager -> Production Pipeline -> READY_TO_POST
```

- Scheduler cria demanda conforme regras futuras.
- Queue ordena jobs normais e prioritários.
- Job Worker executa etapas idempotentes.
- Stock Manager acompanha quantidade, validade, diversidade e consumo do estoque.
- Production Pipeline aplica o lifecycle oficial.

Esses componentes são arquitetura desejada e ainda não estão implementados.

## 8. Pedidos especiais

```text
USER_REFERENCE -> PRIORITY JOB -> Production Pipeline
```

O pedido especial pode exigir aprovação adicional, mas não pode ignorar facts, persistência, QA ou packaging.

## 9. Research-First Capability Development

Toda capability importante deve seguir o ciclo:

```text
RESEARCH
  -> FINDINGS
  -> CAPABILITY DESIGN
  -> CONTRACT
  -> IMPLEMENTATION
  -> TEST / BENCHMARK
  -> PRODUCTION
  -> LEARNINGS
```

A pesquisa deve influenciar concretamente o design, o contrato e os testes. Inferências não podem ser promovidas a fatos documentados, e lacunas de evidência devem gerar incerteza explícita ou experimentos controlados.

O padrão completo, incluindo hierarquia de fontes, classificação de evidência, estrutura dos registros, experimentação, Project Learnings e gate `DESIGN_RESEARCHED`, está em `brain/RESEARCH_FIRST.md`.

Esse gate é independente do status de implementação. `DESIGN_RESEARCHED` não significa `READY`, e documentação sem evidência suficiente não satisfaz nenhum dos dois estados.

## 10. Limite operacional de publicação

```text
Local Content Factory -> READY_TO_POST -> MANUAL MOBILE PUBLISHING
                                      -> manual performance entry
                                      -> future learning
```

O pacote pode incluir `RECOMMENDED_PUBLISH_TIME`, sempre acompanhado da evidência ou da incerteza que o sustenta. A publicação externa, o clique final e qualquer automação móvel ficam fora do runtime ativo. AWS, cloud VM, Android virtual/emulador, Phone Link, scrcpy, ADB de publicação e APIs de Instagram/TikTok são `FUTURE_CAPABILITY / PAUSED_UNTIL_CONTENT_FACTORY_VALIDATED`.

## 11. Visual Production capability design

A pesquisa canônica de 23/09/2026 decidiu substituir a responsabilidade conceitual ampla `Realism Prompting` por três limites:

```text
Storyboard + Facts + Nina + Style/Reference DNA
                  |
                  v
           Scene Direction
  (blocking, camera, light, interaction,
   time, continuity, physical/material risk)
                  |
                  v
      Generation Specification
  (references, invariants, required outcomes,
   contextual restrictions, acceptance checks)
                  |
                  v
          Provider Adapter
  (current model/mode/inputs/prompt/settings)
                  |
                  v
          Visual Generation
```

`SceneDirection` e `GenerationSpecification` são provider-independent. Modelo, modo, ingredients, frames, controles e sintaxe pertencem ao adapter. O provider atual é Google Flow: essencial para a produção presente, `MANUAL` na operação e `PARTIAL` na preparação local, mas substituível no futuro.

O aggregate de `SceneDirection` inclui seções conceituais de cinematografia, iluminação, interação física, direção temporal, continuidade e risco. Elas não são serviços independentes nesta fase. O risk profile é contextual, usa bandas qualitativas e deve mudar a estratégia da cena; não existe score numérico calibrado.

A especificação detalhada, evidência, unknowns e experimentos pendentes ficam em `brain/research/visual-production/`. Nenhum contrato de runtime foi implementado por essa decisão.
