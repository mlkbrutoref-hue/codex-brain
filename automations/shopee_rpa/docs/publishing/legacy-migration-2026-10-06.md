# Migração administrativa da tentativa histórica Shopee Video

A tentativa original foi encerrada como PUBLISHED_LEGACY, sem fabricar fingerprint ou identidade comercial, sem repost e sem novo job real. O bloqueio administrativo da conta borgesc542 foi removido após preflight de escopo restrito.

| Campo | Resultado |
|---|---|
| OLD STATE | UNKNOWN |
| NEW STATE | PUBLISHED_LEGACY |
| PUBLIC POST ID | oOIfmsEhCgDfE7kkAAAAAA== |
| RECONCILIATION QUALITY | LEGACY_PARTIAL |
| MEDIA MATCH | PASS — confirmação humana + hash histórico + duração compatível |
| CAPTION MATCH | PASS — caption e hashtags exatos |
| PRODUCT BINDING | UNKNOWN |
| ORIGINAL FINGERPRINT | NOT_AVAILABLE_LEGACY — campo original continua vazio |
| RETRY ALLOWED | NO |
| DEDUP PRESERVED | YES — permanente |
| BREAKER BEFORE | OPEN |
| BREAKER AFTER | CLOSED, passando por HALF_OPEN |
| ACCOUNT AVAILABLE FOR NEW JOBS | YES — independentes e sujeitos aos gates atuais |

## Identidade e prova

Job central: `legacy:53926be5d018b6d3b4b5cf0302cd221bb2ba330d54da86f510c377823b253d9f`. Job original: `shopee_android_usb_20261006_01`. URL: https://br.shp.ee/zjhibtop?fromSource=copy_link&smtt=0.0.9

A estrutura LegacyPublicationEvidence valida username e XML histórico do perfil, caption/hashtags no READY_TO_PUBLISH, sessão e seus hashes, mídia local, duração FFprobe, snapshot público HTML/JSON e confirmação manual explícita. Duração local 15.022993 s; pública 15.022 s. A identidade do vídeo público é confirmada pelo operador; não houve comparação de pixels ou hash do export remoto. O token público é opaco, preservado como exposto pela Shopee.

## Preservação e lacunas

A linha do job real mudou somente state; fingerprint vazio, attempted=1, created, owner, hashes e evidence original permanecem idênticos. A sessão e o MP4 conservam SHA-256. Nenhum shop_id/item_id/variant_id foi criado. Metadata separada enumera campos comprovados e UNKNOWN, registra URL/token/reviewer/timestamp e hashes das referências. O status expõe product_binding_status UNKNOWN, candidate_fingerprint_status NOT_AVAILABLE_LEGACY e reconciliation_quality LEGACY_PARTIAL. Não é PUBLISHED comum.

O estado é terminal; mark_unknown por worker antigo não o reabre. Retry, transição a READY/PUBLISHING e autorização final são bloqueados. Dedup por logical/source/prepared é permanente, além da janela e com reencode que preserve a identidade lógica. A reconciliação normal segue exigindo fingerprint e binding completos para candidatos nativos.

## Escopo do breaker e preflight

A avaliação retrospectiva está em breaker-scope-review.json. O baseline era vazio; primeira causa foi o único histórico UNKNOWN. A segunda falha foi CONTENT_GATE_FAIL de DRY_RUN local, sem efeitos Android/API, que sobrescreveu a causa crítica herdada por um bug já corrigido; o conteúdo desse candidato continua bloqueado. A terceira ocorrência registrou novamente o mesmo UNKNOWN. Esses fatos foram auditados nos snapshots e harness preservados; não foi inventado um histórico antigo por ocorrência.

Novas ocorrências ficam em breaker_events, com reason e job por evento. A recuperação exige avaliação explícita, snapshot exato e recente, nenhum outro incidente conhecido, nenhum job/lease/autorização pendente da conta e kill switch desativado. Em HALF_OPEN, um GET público atual confirmou novamente conta, post ID, caption/hashtags e duração. A transação final verificou que nenhum incidente concorrente apareceu. Resultado PASS; OPEN → HALF_OPEN → CLOSED. Prova em breaker-preflight.json e no evento/snapshot persistente. Outros breakers permaneceram idênticos.

Preflight com escopo LEGACY_LEDGER_AND_PUBLIC_POST_READ_ONLY: não validou login, versão ou tela Android atual. Essa recuperação apenas remove PUBLICATION_UNKNOWN legado. Não autoriza efeitos futuros e não pode resolver CAPTCHA/LOGIN/SECURITY_ALERT. Default DRY_RUN, produção pausada e todos os gates normais continuam ativos. Nenhum celular foi conectado ou operação de publicação executada.

## Verificação sobre o estado real

Integridade SQLite OK; um único job real antes/depois. Counters e authorizations reais inalterados. Todos os campos originais, exceto state, preservados. Backups antes/depois e snapshots estão nesta pasta.

Os exercícios de retry, dedup além da janela/reencode, impossibilidade de READY/PUBLISHING/UNKNOWN e reserva independente foram executados numa cópia isolada do banco real. A reserva utilizou o candidato já existente da campanha da escova, não um job equivalente real. Product binding UNKNOWN continua visível. Nenhum candidato foi inserido no ledger de deployment para esse teste.

## Testes e implementação

21 novos testes legados cobrem evidência falsa/divergente, tampering, idempotência, estado terminal, dedup permanente, conta liberada, lacunas visíveis, falhas/concorrência do breaker, kill switch, incidentes sem escopo e preflight alterado/indisponível. Suíte geral final: 250/250, zero falhas/erros/skips, incluindo 122 testes de publicação e os 21 novos legados. Compilação e whitespace dos nove arquivos Python alterados passaram.

A primeira rodada específica teve um erro no tratamento controlado de NaN; a implementação foi corrigida, o teste foi reexecutado e toda a suíte final passou. Logs anteriores permanecem preservados, sem ocultar a falha.

Rotina: app/publishing/legacy_reconciliation.py; ledger e armazenamento estendidos sem reescrever registros originais; auditoria de breaker em app/operational/circuit_breaker.py. CLI: reconcile-legacy e preflight-legacy-breaker. Três chamadas de falha da UI/runtime agora registram o job causador. Contrato em docs/publishing/legacy-reconciliation.md e decisão D-025. Nenhuma promotion Publishing READY.
