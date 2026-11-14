# Segurança operacional do publicador assistido

Implementação de 06/10/2026. Classificação: **EXPERIMENTAL / PARTIAL**, validada offline. Default **DRY_RUN**. Não habilita produção nem concede permissão da Shopee; exposição contratual do método permanece conforme a auditoria. Nada foi publicado durante esta implementação.

## 1. Resumo executivo

O worker existente passa a depender de controles transacionais e de uma fronteira única de UI. Conta, candidato, proveniência, QA real, identidade lógica, IDs comerciais, variante, copy e revisão são obrigatórios. Configs antigas param antes de conectar. Seleção nova para em revisão antes de avançar ao editor/upload. Uma tentativa reservada ou incerta nunca é repetida automaticamente.

Preparação e publicação têm reservas distintas. A primeira impede dois workers de manipular a mesma conta/dispositivo/asset; a segunda é durável e emite token de uso único via PublishGate. Mensagem de sucesso/retorno ao perfil deixa de confirmar publicação. Confirmação exige evidência correspondente ao candidato e post ID/URL; ausência fica UNKNOWN.

## 2. Arquitetura final e integração

```text
config + candidato + aprovações
  -> validação local / FFprobe / decode / hashes
  -> DRY_RUN: relatório local, zero conexão
  -> interface autorizada + reserva central de trabalho
  -> processo Android limitado por deadline
  -> identidade da conta + app/versão
  -> ShopeeUI (modo/breaker/budget/deadline/log)
  -> mídia e produto inequívocos + revisão atual
  -> READY
  -> PublishGate: valida + orçamento + reserva final na mesma transação
  -> autorização consumida uma vez + clique final
  -> UNKNOWN
  -> PublicationReconciler + evidência explícita
  -> PUBLISHED ou UNKNOWN
```

Reutilizados: `Screen`, composição de legenda/limite observado de UTF-16, nove checks do preparador assistido, hashes, sessões JSON, lock de dispositivo, `FFprobeInspector`, `FFmpegLocator`, protocolo de assinatura Affiliate e contratos Product existentes. Não foi criado segundo pipeline de conteúdo.

SQLite usa `BEGIN IMMEDIATE`, `synchronous=FULL` e transações conjuntas para dedup, leases, counters e tentativa final. [Contrato de transações SQLite](https://www.sqlite.org/lang_transaction.html). Host único/filesystem local; múltiplos hosts precisam de armazenamento transacional compartilhado diferente. SQLite em pasta de rede/cloud sync não é solução distribuída.

## 3. Arquivos e classes

```text
app/operational/                       NOVO
  config.py                            OperationalConfig, OperationalLimits, MediaProfile,
                                       FeatureMode, ActionType
  store.py                             OperationalStore
  deadlines.py                         ExecutionDeadline / Deadline
  action_budget.py                     ActionBudget, AccountBudget
  circuit_breaker.py                    OperationCircuitBreaker, CircuitState
  modes.py                             OperationModeEngine, OperationMode
  http_transport.py                    BoundedHTTPTransport
app/media/                             ESTENDIDO
  identity.py                          MediaIdentity
  provenance.py                        MediaProvenance, RightsStatus
  normalization.py                     MediaProcessor, PreparedMedia
app/validation/                        ESTENDIDO
  media.py                             FFprobeInspector: inclui formato do container
  product_media_truth.py                PostCandidate, ProductIdentity, ExpectedAccount,
                                       HumanReview, ContentValidator, ValidationReport
  publish_gate.py                       PublishGate, PublishAuthorization
app/publishing/                        ESTENDIDO
  ledger.py                            JobLedger, JobState
  reconciliation.py                    PublicationReconciler, PublicationEvidence
app/mobile/                            ESTENDIDO
  ui.py                                ShopeeUI, IsolatedAndroidDevice
  safety_runtime.py                    AndroidSafetyRuntime
  media_selection.py                   MediaSelectionEvidence
  read_only.py                         ReadOnlyShopeeUI, read_only_session
  shopee_video.py                       worker refatorado, ProductCard
app/observability/                     NOVO
  operation_logger.py                  OperationLogger
  health.py                            health_report
app/providers/shopee/{client,live}.py   ALTERADOS
scripts/
  publish_shopee_android.py             ALTERADO: conexão somente após preflight/reserva
  probe_shopee_android.py               ALTERADO: apenas captura de estrutura/hashes
  research_shopee_hashtags.py           ALTERADO: apenas sugestões já visíveis/XML offline
  prepare_shopee_android_resume.py      ALTERADO: aprovação automática antiga desabilitada
  execute_kbeauty_research.py           ALTERADO: interrompe lote após erro
  research_bolsas_shopee.py             ALTERADO: interrompe lote após erro
  operational_control.py               NOVO: controle local, sem Android
tests/publishing/
  test_shopee_android.py                reserva antiga migrada para ledger + rejeição direta
  test_operational_safety.py            NOVO: contratos e corridas
  test_operational_integration.py       NOVO: integrações offline
docs/publishing/
  operational-safety-plan.md            inspeção/contratos anteriores ao código
  operational-config.example.json      exemplo intencionalmente sem aprovações
  operational-safety.md                 este documento
brain/{CURRENT_STATE,DECISIONS}.md      atualização de escopo/arquitetura, sem promoção READY
```

## 4. Estados e invariantes

Estados de domínio: CREATED, PREPARING, READY, RESERVED, UPLOADING, PUBLISHING, PUBLISHED, UNKNOWN, FAILED, CANCELLED. O caminho implementado reserva em RESERVED, avança PREPARING/READY e só o gate inicia PUBLISHING. UPLOADING é reservado para efeitos de upload integrados; a seleção nova atual para antes deles. Não declarar upload só porque o arquivo foi selecionado.

1. UNKNOWN nunca muda automaticamente para FAILED, não expira com a janela de dedup e bloqueia nova tentativa da conta.
2. O caminho final do worker exige PublishAuthorization emitida pelo gate e registrada no ledger; JSON `publish_authorized=true` sozinho não basta.
3. Owner, fingerprint, expiração e uso do token são verificados transacionalmente. Um token consumido não permite segundo clique.
4. Conta, mídia/hash fonte/hash preparado, produto, variante, copy, QA ou proveniência alterados invalidam HumanReview.
5. FAIL, REVIEW e UNKNOWN nunca passam o ContentValidator/PublishGate.
6. Conta exata é obrigatória; substring antiga não comprova identidade.
7. OPEN e kill switch impedem a próxima ação externa; HALF_OPEN só permite leitura.
8. Deadline/cancelamento impedem a próxima ação e limitam processo/RPC/subprocess.
9. Probe não contém clique, preenchimento, tecla, upload ou input shell; flags antigas de ação são rejeitadas pelo parser.
10. Não há retry automático de efeitos. Morte do processo não desfaz pedido remoto já enviado: persistir UNKNOWN.

Depois de uma ação, a fronteira de UI bloqueia outra mutação até observar o estado esperado. Se o wait/deadline falhar antes dessa validação, até uma preparação sem clique final fica UNKNOWN e mantém leases; não é convertida automaticamente em FAILED.

A fronteira também revalida foreground e telas de segurança antes de cada mutação. Enter só é permitido no contexto de busca de produtos observado, sem botão Postar; chamadas diretas ao dispatcher não podem enviar outras teclas. A reserva local não torna a inspeção e o efeito remoto atômicos.

Modos NORMAL/CAUTIOUS permitem preparação controlada; RECOVERY somente leitura; PAUSED nenhuma ação externa. Modos não simulam comportamento humano.

## 5. Gates de conteúdo e evidência

`PostCandidate` vincula conta, `MediaIdentity`, `ProductIdentity`, título, caption/hashtags, proveniência, QA, correspondência mídia-produto, originalidade, disclosure, keywords/aliases e revisão. O fingerprint é SHA-256 do candidato completo, excluindo a própria revisão.

Direitos exigem VERIFIED, tipo de licença e referência de evidência. Originalidade/caption review/media-product match exigem PASS de revisão explícita; não existe detector semântico automático ou score inventado. IA exige disclosure quando gerada por IA ou requerido. QA informado é vinculado ao hash e rechecado sobre o arquivo local com FFprobe e decode real antes de UI.

HumanReview exige APPROVED, fingerprint atual, timestamp Unix UTC não futuro, reviewer e evidence_reference; TTL configurável. Não preencher como PASS por conveniência. URLs/referências não substituem a análise humana da licença ou aparência.

ProductIdentity compara shop_id + item_id + variante e atributos. URL comercial observada no MESMO card é uma fonte possível de IDs; sem ela, a seleção automática para antes de clicar Adicionar. Produto já vinculado pode ser aprovado por evidência humana explícita: `product_binding_review` com produto completo, URL oficial, fingerprint do candidato, hash do nó vinculado ATUAL, reviewer, timestamp e referência. Título sozinho não passa. Variante não observável sem prova humana permanece REVIEW.

Identidade da conta usa username e stable_profile_marker exatos na tela atual. Ao retomar no editor, `account_preflight_review` pode atestar a sessão atual: conta/username exatos, hash da tela ATUAL, reviewer, timestamp, status APPROVED e referência. Sessão antiga ou flag booleana não basta. Lease local não impede um humano de tocar o aparelho: operação exige controle exclusivo e parada se houver mudança de tela.

MediaSelectionEvidence inclui hash esperado, thumbnail com hash/arquivo e vínculo ao asset, duração, inventário e célula selecionada. Durações iguais/próximas, inventário inconsistente ou thumbnail sem prova param em REVIEW. Retomada exige `candidate_fingerprint`, reviewer, reviewed_at, arquivos íntegros, conta e `visual_preview_reviewed=true`. O preview atual também precisa corresponder ao recorte revisado; pixel hash é corroboração adicional, não identificação autônoma do vídeo.

Não há um revisor automático de produto/variante/thumbnail. O worker não fabrica essas evidências. Seleção nova salva evidência incompleta e interrompe ANTES de editor/upload; a continuação exige operador e uma retomada com prova fresca do preview final. Só preflight/manifesto local válido não prova a célula nativa.

## 6. Budgets, breaker e deadline

Custos internos configuráveis: READ_STATE=.25, CLICK=1, SCROLL=2, NAVIGATION=3, PRODUCT_LOOKUP=3, MEDIA_SELECT=5, UPLOAD_START=10, PUBLISH_ATTEMPT=20. Token bucket persistente por conta: capacidade 200, refill 1/s por padrão. `can_consume` simula a transação sem cobrança; espera respeita deadline/cancel/breaker e não consome indefinidamente. Nova sessão preserva saldo, orçamento diário e contadores de worker.

Defaults conservadores internos: 1 tentativa/dia e sessão; 1 upload/dia e sessão; 5 produtos/sessão; 30 Affiliate/dia e 10/sessão; 500 ações/worker. Dia usa America/Sao_Paulo (fallback explícito UTC-3 quando tzdata não disponível). Estes valores NÃO são limites oficiais ou faixa segura de automação da Shopee. Ajustar em configuração explícita, não espalhar constantes.

Tentativas UNKNOWN continuam consumidas. Não descontar porque o resultado ficou incerto. Worker usa serial/worker_id estável para contagem, além de owner único para reserva. API usa conta de serviço identificada por hash do app_id, ou account_id injetado, com contadores globais entre clientes.

CAPTCHA/login/SMS/segurança/conta restrita, identidade divergente ou resultado UNKNOWN abrem breaker imediatamente. Erros recuperáveis: threshold padrão 2, cooldown interno 900s. Crítico exige release humano, evidência e preflight somente leitura; não fecha por tempo. 429 respeita Retry-After (segundos/data HTTP), abre e interrompe lote; 401/403 são AUTH_OR_ACCESS, sem retry ou escolha alternativa de produto. Headers/resposta não entram em logs.

Deadline padrão 900s por execução, RPC 15s. Processo Android e HTTP são termináveis; FFmpeg/FFprobe usam subprocess sem shell com timeout limitado pelo restante. [Python subprocess](https://docs.python.org/3/library/subprocess.html) documenta que inicialização do processo pode ter atraso do SO; nenhuma continuação fica autorizada após expirar. Em voo, o Android pode concluir um efeito mesmo após matar cliente: não é exatamente-once remoto.

## 7. Ledger, dedup e reconciliação

Banco default: `%LOCALAPPDATA%\AICommerceContentFactory\operational\state.sqlite3`, comum às raízes/jobs/devices do usuário. `COMMERCE_OPERATIONAL_DB` pode fixar outro caminho absoluto no deployment; JSON de job não pode trocar o banco. Todos os workers/helpers devem apontar ao mesmo arquivo; perfis Windows/hosts diferentes não se coordenam automaticamente.

Identidade: platform + account + logical_asset_id + shop_id + item_id + variant_id. Dedup também compara hash fonte/preparado cruzados dentro da conta. Reencode com mesma identidade lógica continua duplicata. Janela padrão 30 dias só aplica histórico PUBLISHED; UNKNOWN/tentativas não confirmadas/reservas em andamento não expiram automaticamente. Perceptual hash/embeddings têm campos de extensão, **não detector implementado**; reencode com IDs e hashes fonte falsos não é detectável pelo sistema atual. Nunca alterar mídia para escapar de dedup.

Reserve job antes de conectar; leases por conta e dispositivo. Reserve tentativa durável só após todos os gates, imediatamente antes do clique. Estados e owner são registrados em `ledger_events`; preparação falha sem tentativa pode ir FAILED/liberar leases; tentativa/upload incerto retém bloqueio. READY interrompido retém reserva até cancelamento explícito, impedindo concorrência silenciosa.

`PublicationReconciler` consome evidência manual/somente leitura: conta, fingerprint, post ID/URL, timestamp, reviewer, referência e PASS de mídia/copy/produto. UI toast não é evidência suficiente. Não existe API oficial de confirmação integrada; o worker fica UNKNOWN após clique até evidência correspondente. O reconciler não clica nem reenvia e não fecha breaker crítico automaticamente.

Sessões antigas com publish_attempted são importadas conservadoramente como UNKNOWN antes de UI (raiz atual e raiz canônica); o JSON original não é reescrito. Evidência histórica insuficiente não será promovida a PUBLISHED só pelo relato anterior. Nunca apagar ledger/banco para liberar retry. Por autorização posterior explícita, registros anteriores ao PostCandidate sem fingerprint podem usar a resolução administrativa separada `PUBLISHED_LEGACY`, com confirmação humana e corroboração dos campos históricos disponíveis, preservando fingerprint ausente e product binding UNKNOWN. Esse estado é terminal e mantém dedup permanente; não enfraquece a reconciliação normal. Contrato, auditoria e preflight limitado ao incidente PUBLICATION_UNKNOWN em `docs/publishing/legacy-reconciliation.md`.

## 8. Logging e saúde

JSONL local: timestamp, session_id, job_id, account_id, modo, action_type, categoria de selector/elemento, token_cost, latency_ms, status. Eventos de transição, validação, erro, tentativa e reconciliação. A UI registra custo e latência; ledger e sessão preservam identidade do asset/produto e se houve reserva final.

Allowlist de campos; texto da legenda, seletor por texto, XML integral, screenshot integral, resposta HTTP, senha, OTP, cookie, token e credenciais não são registrados. Probe persiste apenas estrutura sem textos e hashes. Arquivos de revisão/thumbnail fornecidos pelo operador ficam em área de evidência controlada; preservá-los sem credenciais e com acesso restrito. Evidências históricas não são apagadas retroativamente.

`OperationLogger.get_health_report()` lê últimos N eventos do job/conta, inclusive após reabertura: actions_total, success/error rate, média/p95 de latência, falhas consecutivas e unknown results. Pode receber budget_remaining, circuit_breaker_state, current_mode e session_duration; são dados locais, nunca prova de shadowban. `operational_control.py status` mostra estados/counters/controles persistentes, produto/variante, hash de caption e reviewer por versão do candidato, sem tokens de autorização. Eventos do ledger vinculam o fingerprint da versão observada. A duração da sessão também limita novas instâncias que reutilizem a mesma session_id.

## 9. Configuração e exemplo de integração

Exemplo: `docs/publishing/operational-config.example.json`. Ele é DRY_RUN e intencionalmente bloqueia por direitos/QA/revisão ausentes. Não contém autorização, conta real ou aprovação fictícia.

Requisitos locais: Python, FFmpeg/FFprobe resolvidos por FFmpegLocator; Pillow no runtime quando houver preview. Para operação externa futura, uiautomator2/ADB em `requirements-android.txt`, app/versão explicitamente permitidos e evidência de autorização aplicável. Flags: DRY_RUN não conecta; ASSISTED_MODE prepara sem post; LIVE_PUBLISH exige config explícita, `--publish`, consentimento local e autorização aplicável. Testes nunca usam LIVE_PUBLISH.

```python
import json
from pathlib import Path
from app.mobile.shopee_video import ShopeeVideoPublisher

config = json.loads(Path('docs/publishing/operational-config.example.json').read_text())
# Preencher evidências reais e aprovação humana; não mudar statuses para simular validação.
worker = ShopeeVideoPublisher(None, config)
result = worker.run_prepared(publish=False)  # padrão local DRY_RUN; gate bloqueia ausências
```

Entrypoints disponíveis para uso futuro (não executados live nesta entrega):

```powershell
python scripts/publish_shopee_android.py --config seu_manifesto.json
python scripts/operational_control.py status
python scripts/operational_control.py fingerprint --config seu_manifesto.json
python scripts/operational_control.py kill --enabled true --reviewer operador --reason STOP
python scripts/operational_control.py cancel-preparation --job ID --reviewer operador --reason cancelado --evidence revisao.json
python scripts/operational_control.py reconcile --job ID --evidence post_confirmado.json
```

`release-breaker` exige account/reviewer/reason/evidence; primeiro HALF_OPEN, depois preflight read-only e `--close` explícito. Nunca liberar só para ignorar UNKNOWN. O controlador local não muda direito/licença, não confirma post por conta própria e não conecta ao Android.

## 10. Correções e pendências

| Achado | Controle entregue | Limite restante |
|---|---|---|
| C02 | ProductCard limitado, recusa ancestral cruzado; XPath absoluto do botão observado | Cards novos exigem fixture real; implementação conservadora pode recusar UI válida |
| C03/C18 | IDs exatos no provider e gate; variante/atributos vinculados | UI sem IDs exige operação/evidência humana; get_product não aceita keyword |
| C04/C11 | revisão obrigatória fresca + MediaSelectionEvidence; ambiguidades bloqueadas | revisão visual manual; seleção nova pausa antes de upload |
| C05/C06 | reserva central pré-UI, dedup lógica/fonte/preparado e leases | coordenação local, não entre hosts/bancos diferentes |
| C07 | toast/perfil insuficientes; reconciler sem repost | confirmação automática por ID de post não implementada |
| C08/C09 | budgets/breaker/kill persistentes, deadline global e processo terminável | efeito remoto já recebido não é desfeito |
| C10 | conta exata obrigatória/preflight atual | atestação humana no editor; operador precisa manter exclusividade |
| C12 | estado nativo checkable/checked prioritário; flags false genéricas não provam desativação; pixels opcionais e recorte branco/uniforme não passa | alguns controles nativos não expõem estado; REVIEW |
| C14/C15/C16 | probes sem ações; hashtag só leitura; helper antigo não fabrica aprovação | pesquisa interativa automática removida deliberadamente |
| C17 | erros tipados, Retry-After persistente, lote interrompido | quotas oficiais continuam desconhecidas |
| C19 | QA/decode, direitos, originalidade e IA integrados ao gate | avaliações semânticas/licença dependem de evidência humana |

Não houve evasão, spoofing, randomização para humanização, CAPTCHA/login bypass ou reencode para ocultar duplicação. O normalizador padroniza codec/resolução e preserva a identidade lógica.

## 11. Testes e failure modes

`test_operational_safety.py` e `test_operational_integration.py` acrescentam 57 testes offline, cobrindo os vinte cenários solicitados: bucket, deadline/cancel, breaker, conta, card cruzado, variante, direitos, QA, fingerprint/TTL, dedup e reencode lógico, UNKNOWN, concorrência, budget diário, versão/seletor, picker, confirmação tardia, 429 e helper sem gate. Adicionais: kill, token falso/usado/expirado/ligado ao job, redaction e reabertura de logs, contexto comercial auditável, duração persistente, flags genéricas de compartilhamento, preparação incerta, recuperação explícita sem efeitos, bloqueio da próxima ação até confirmar o estado, teclado e tela de segurança, 403, Retry-After HTTP date, erros GraphQL, migração e limites de modos/dispatcher.

Uma RPC fake travada roda em processo real e é terminada por deadline de 0,2s. O bootstrap Windows ganhou prazo separado no teste após falha inicial; o prazo da RPC continua 0,2s, sem relaxar produção. Normalização foi testada com MP4 sintético local real, probe antes/depois, decode e hashes/proveniência. Nenhuma suíte publica live; nenhuma chamada autenticada Shopee foi feita.

Resultados finais e checks de integridade: `output/operational_safety_20261006/verification.json`. A primeira suíte completa preserva a falha de bootstrap em `full-tests.txt`; não foi silenciada. Rodadas intermediárias ficam em `final-tests.txt`, `release-tests.txt`, `accepted-publishing-tests.txt` e `final-acceptance-tests.txt`. A suíte geral fica em `final-project-tests.txt`; a suíte `final-ui-tests.txt` cobre também o reforço de teclado/security acrescentado depois de iniciar a rodada geral.

Resultado: **213 testes gerais aprovados em 187,698s**, seguidos de **86 testes de publicação aprovados em 85,658s** sobre a fronteira final de UI. Zero falhas/erros nas duas rodadas. Compilação de 36 arquivos Python e JSON de exemplo passaram; `git diff --check` passou nos arquivos preexistentes alterados nesta entrega. Os 13 backups conferem com o manifesto, e SHA-256 da sessão de tentativa antiga e do MP4 original continuam iguais aos registrados na auditoria.

## 12. Recovery e rollback

Segurança/conta/divergência: interromper, resolver pelo titular, registrar evidência, HALF_OPEN de leitura, validar e fechar explicitamente. Não guardar OTP, senha ou cookies. READY/preparação abandonada sem tentativa: cancelamento humano auditado; após liberação, novo preflight. UPLOADING/PUBLISHING/UNKNOWN: não reexecutar job, não apagar reserva, reconciliar evidência do resultado. Conta inteira permanece parada se houver UNKNOWN. Crash antes de tentativa não é automaticamente uma tentativa de publicação.

Exceção de recuperação explícita: UNKNOWN durante preparação, sem tentativa final durável, pode ir CANCELLED somente após revisão humana com evidência de que não houve upload nem publicação. `resolve-preparation-unknown --job ID --reviewer operador --reason revisado --evidence revisao.json --verified-no-publish --verified-no-upload` exige ambas as constatações. Não promove o job a FAILED, não libera tentativa final reservada, não fecha o breaker e não executa retry. Evidência insuficiente mantém UNKNOWN. Uma tentativa de publicação reservada continua exigindo reconciliação do post.

Rollback: ativar kill switch compartilhado; preservar banco SQLite, sessões, logs e evidências; copiar baseline de `output/operational_safety_20261006/baseline/` somente sobre arquivos desta mudança, após verificar hashes em `manifest.json`. Não usar `git reset --hard` num working tree com mudanças anteriores. Módulos novos podem permanecer sem uso; restaurar o worker antigo nunca significa autorização para retomar live e remove estes gates, portanto manter publicação desabilitada. Backup do banco deve ser feito com SQLite backup ou com todos os workers parados, não copiando durante escrita.

Antigravity: tentativa pelo Bridge terminou por timeout; a resposta pelo CLI oficial foi recuperada e está em `output/operational_safety_20261006/antigravity-implementation-review.md`, com recibo e hash. Ele confirmou reserva/dedup, retenção de UNKNOWN e uso único nos trechos recebidos; destacou a janela entre gate/driver e inspeção/clique, que não é atômica com a UI. Leases/UNKNOWN mitigam repetição, sem prometer desfazer efeito remoto. A implementação também registra versões comerciais/eventos e reforça o dispatcher. Escopo limitado aos trechos daquele snapshot, sem certificação do conjunto ou dos ajustes posteriores, e sem economia de créditos medida. O problema de captura do Bridge não foi corrigido nesta tarefa.
