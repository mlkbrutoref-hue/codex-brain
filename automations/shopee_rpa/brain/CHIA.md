# CHIA — Contexto, Habilidades, Integrações e Automação

## C — Contexto

O projeto é uma fábrica de conteúdo original para afiliados. A Nina é a persona visual e narrativa principal. A Shopee é a fonte comercial atual, enquanto Instagram, TikTok e Shopee Video são destinos e referências de linguagem.

Existem dois objetivos operacionais:

1. **Estoque automático:** manter uma reserva de vídeos aprovados e prontos para publicação.
2. **Pedidos especiais:** produzir conteúdo prioritário a partir de produtos, referências ou instruções selecionadas pelo usuário.

Vídeos de referência servem como direção criativa. Eles não autorizam cópia literal nem substituem a verificação factual do produto.

## H — Habilidades

Status permitidos:

- `READY`: implementado, reutilizável e validado.
- `PARTIAL`: existe implementação útil, mas o contrato não está completo.
- `MANUAL`: depende de operação humana ou operação conversacional por interface.
- `PLANNED`: ainda não implementado.
- `BLOCKED`: existe intenção ou estrutura, mas há bloqueio externo conhecido.
- `PAUSED`: capability futura preservada, mas explicitamente fora do foco ativo até nova decisão.

Esses status medem implementação. A maturidade de pesquisa é uma dimensão independente: uma capability somente pode ser chamada de `DESIGN_RESEARCHED` depois de satisfazer o gate de expertise de `brain/RESEARCH_FIRST.md`. Nenhuma habilidade abaixo recebe esse selo apenas por já possuir código, documentação ou status `READY`.

| Habilidade | Input | Responsibility | Output | Current status |
|---|---|---|---|---|
| Product Discovery | Termos, categoria, filtros comerciais | Encontrar produtos reais e elegíveis sem inventar dados | Lista de candidatos com IDs, métricas, links e imagens oficiais | `READY` para o catálogo exposto pela Shopee Affiliate API |
| Product Facts | Produto e resposta oficial | Separar fatos confirmados, contexto inferido e desconhecido | `ProductFacts` rastreável | `PARTIAL`; a API não fornece descrição longa e todos os atributos |
| Trend Research | Nicho, plataforma, período | Identificar padrões atuais de hooks, estrutura, estética e CTA | Evidências e candidatos a `Style DNA` | `MANUAL` |
| Reference Analysis | Vídeo, imagens ou URL escolhida | Extrair estrutura, ritmo, cenas, texto, estética e limites reutilizáveis | `Reference DNA` | `MANUAL` |
| Creative Direction | Produto, fatos, objetivo e DNA criativo | Escolher formato, tese, progressão narrativa e prova visual | `Creative Direction` aprovada | `PARTIAL`; módulos e skills existem, mas não há contrato único persistido |
| Script Writing | Direção criativa e fatos | Escrever fala, hook, progressão e CTA com segurança factual | Roteiro temporizado | `PARTIAL`; existe geração, mas produções recentes foram corrigidas manualmente no chat |
| Storyboard | Roteiro e direção criativa | Dividir o vídeo em cenas filmáveis/geráveis | Storyboard com timing, ação e enquadramento | `PARTIAL` |
| Scene Direction | Storyboard, fatos, Nina e DNA aprovado | Especificar blocking, produto, ação, câmera, luz, interação física, tempo, continuidade e risco sem depender de provider | `SceneDirection` verificável | `PARTIAL`; a pesquisa passou o gate `DESIGN_RESEARCHED`, mas o runtime atual cobre apenas partes dispersas |
| Generation Specification | `SceneDirection`, referências aprovadas e risk profile | Consolidar invariantes, resultados, restrições contextuais e checks de geração sem sintaxe de provider | `GenerationSpecification` provider-independent | `PLANNED`; capability design `DESIGN_RESEARCHED`, ainda sem contrato de runtime |
| Visual Generation | Especificação, referências e orçamento | Gerar takes e preservar identidade/produto | Mídias por cena | `MANUAL`; há preparação local `PARTIAL`, mas geração/ingestão não são integradas |
| Voice Generation | Roteiro aprovado e direção de voz | Gerar narração natural, versionada e reutilizável | Arquivo de voz e metadados | `MANUAL`; não existe provider de voz integrado |
| Video Editing | Takes, voz, música e especificação | Montar vídeo determinístico e sincronizado | Master vertical | `PARTIAL`; FFmpeg concatena e normaliza, mas o compositor completo ainda não existe |
| Caption/Subtitles | Voz ou roteiro temporizado | Criar legendas sincronizadas e textos na tela | SRT/ASS e/ou overlays renderizados | `MANUAL`; feito principalmente no Canva nas produções recentes |
| Technical QA | Arquivos de mídia e requisitos | Validar integridade, codec, resolução, fps, áudio e duração | Relatório técnico | `READY` para os checks implementados com FFprobe |
| Visual QA | Takes, Nina, produto e intenção da cena | Avaliar identidade, anatomia, fidelidade, realismo e continuidade | Decisão `PASS`, `REVIEW_REQUIRED` ou `FAILED` com evidências | `MANUAL`; há contrato estruturado, mas não um revisor automático integrado |
| Packaging | Master, metadados, copy e destinos | Organizar artefatos finais por plataforma | Pacote do job | `PARTIAL`; existe em piloto, mas as variantes atuais podem ser apenas cópias do mesmo master |
| Ready-to-Post Finalization | Manifests, assets, QA, copy e aprovação explícita | Aplicar gates, preservar hashes e montar o handoff local canônico | `ready_to_post/campaign_<id>/` | `READY`; reutilizável, testado e executado contra campanha real, que bloqueou corretamente por copy ausente e quatro reviews não aprovados |
| Stock Management | Pacotes aprovados e regras de estoque | Controlar disponibilidade, prioridade, validade e consumo | Catálogo `READY_TO_POST` | `PLANNED` |
| Special Requests | Pedido do usuário e referências | Criar job prioritário sem quebrar o pipeline comum | `PRIORITY JOB` rastreável | `MANUAL` |
| Publishing | Pacote `READY_TO_POST` aprovado | Publicar em plataformas externas | Post publicado e identificador externo | `PAUSED`; `FUTURE_CAPABILITY`, publicação atual é manual no celular |
| Performance Tracking | Métricas reais informadas após publicação manual | Persistir resultados sem preencher ausências e aprender padrões | Histórico factual de performance | `PLANNED`; entrada manual e recomendação conservadora são o próximo contrato, sem analytics implementado |

### Capability não é Provider

Uma **capability** descreve o que o sistema precisa ser capaz de fazer. Um **provider** é uma tecnologia atual e substituível que pode executar toda ou parte dessa capability. A necessidade arquitetural da capability não transforma o provider atual em obrigatório nem em `READY`.

| Capability | Necessidade | Provider atual | Papel do provider | Provider status |
|---|---|---|---|---|
| Visual Generation | `REQUIRED` para produzir mídia original | Google Flow | `REQUIRED_CURRENT_PRODUCTION_PROVIDER`; essencial à fábrica atual e arquiteturalmente substituível | Operação `MANUAL`; preparação local `PARTIAL` |
| Voice Generation | `REQUIRED` para conteúdo narrado | ElevenLabs por operação de interface | Provider atual não integrado ao runtime | `MANUAL` |
| Video Editing | `REQUIRED` | FFmpeg; Canva como apoio | FFmpeg é primário; Canva é polimento opcional | FFmpeg `PARTIAL`; Canva `MANUAL` |
| Storage | `REQUIRED` | Filesystem local; Google Drive como apoio | Persistência canônica local; Drive é handoff opcional | Local `READY` para artefatos existentes; Drive `MANUAL` |
| Trend Research | `REQUIRED` no modo `TREND_SELECTED` | TikTok/Instagram e pesquisa web | Fontes atuais, substituíveis | `MANUAL` |

## I — Integrações

A classificação expressa o papel arquitetural, não o nível atual de implementação.

| Integração | Classificação | Estado atual e limite |
|---|---|---|
| Shopee Affiliate API | `REQUIRED` | Integração live existente e comprovada para os campos expostos pela API. |
| TikTok/Instagram research | `REQUIRED` para `TREND_SELECTED` | Pesquisa e análise ainda manuais; acesso por navegador é instável. |
| Google Flow | `REQUIRED_CURRENT_PRODUCTION_PROVIDER` | Essencial à produção visual atual, mas substituível no futuro. Operação real é `MANUAL`; preparação de prompts/handoff é `PARTIAL` e ainda não integra geração ou ingestão ao runtime determinístico. |
| Voice provider | `REQUIRED` para conteúdo narrado | ElevenLabs foi operado manualmente; provider abstrato/integrado ainda não existe. |
| FFmpeg/FFprobe | `REQUIRED` | Base do editor primário e do QA técnico; concatenação e normalização já existem. |
| Canva | `OPTIONAL` | Ferramenta de polimento; integrações e navegador foram instáveis. Fica fora do caminho crítico. |
| Google Drive | `OPTIONAL` | Usado como handoff manual de assets em alguns fluxos; sem contrato integrado. |
| GitHub | `OPTIONAL` | Pode hospedar revisão e colaboração futura; o repositório local Git é a base atual. |
| Future cloud VM | `PLANNED` | Não provisionada; possível destino futuro para workers e mídia. |
| Auto publishing / mobile automation | `FUTURE_CAPABILITY` | `PAUSED_UNTIL_CONTENT_FACTORY_VALIDATED`; preservar protótipos existentes, sem desenvolvimento de Mobile Publisher, Phone Link, scrcpy, ADB, emulador ou APIs de publicação. |

### Maturidade da pesquisa visual

Em 23/09/2026, **Visual Production / Scene Direction** passou o gate `DESIGN_RESEARCHED` de `brain/RESEARCH_FIRST.md`. A pesquisa canônica está em `brain/research/visual-production/` e decidiu dividir a responsabilidade histórica `Realism Prompting` entre `Scene Direction`, `Generation Specification` e um futuro adapter provider-specific.

Esse selo mede conhecimento e capability design. Não altera automaticamente os status de implementação acima, não cria schemas de runtime e não torna Google Flow integrado. As táticas específicas do Flow permanecem `FAST_CHANGING` e algumas exigem experimentos controlados.

## A — Automação

Arquitetura desejada para estoque:

```text
Scheduler
  -> Queue
  -> Job Worker
  -> Stock Manager
  -> Production Pipeline
  -> READY_TO_POST
```

Arquitetura desejada para pedidos especiais:

```text
USER_REFERENCE
  -> PRIORITY JOB
  -> Production Pipeline
  -> READY_TO_POST
```

Os dois caminhos compartilham lifecycle, artefatos, quality gates e empacotamento. `PRIORITY JOB` altera prioridade e origem criativa, não cria um segundo pipeline.

O Scheduler, a Queue, os Workers e o Stock Manager ainda não são implementados nesta etapa.

O terminal operacional atual é `READY_TO_POST`. Recomendação de horário integra o pacote; a publicação é manual e métricas reais são registradas posteriormente por entrada manual. Publicação automática e infraestrutura remota permanecem pausadas conforme D-023.
