# Reconciliação administrativa de publicações legadas

Contrato experimental autorizado pelo usuário para tentativas anteriores a PostCandidate/PublishGate. A resolução `PUBLISHED_LEGACY` confirma uma publicação por evidência parcial forte. Não equivale a `PUBLISHED` comum, não cria autorização de publicação e não promove Publishing a READY.

## Evidência e validação

`LegacyPublicationEvidence` exige username, URL e token público, caption base, hashtags ordenadas, SHA-256 esperado da mídia histórica, duração esperada em segundos, confirmação humana booleana explícita, reviewer, reviewed_at Unix e referência da confirmação. Também aponta mídia local, XML histórico da conta e snapshot JSON/HTML público.

O reconciliador compara esses dados com o job importado, SHA-256 original da sessão, arquivos referenciados pela seleção histórica e XML READY_TO_PUBLISH. Exige tentativa durável, owner/id legados, fingerprint vazio, hash local consistente com sessão/seleção/ledger, duração FFprobe e duração pública dentro de 0,1 s, username público e caption/hashtags exatos, e token extraído de `__NEXT_DATA__.query.postId` correspondente à URL oficial resolvida. O HTML e seu JSON têm hashes e conteúdo concordantes. A confirmação humana estabelece a identidade do vídeo; não se alega igualdade byte a byte com o export público com watermark.

Evidência discordante, inválida, alterada ou sem confirmação não resolve. Jobs nativos não podem usar essa exceção; o reconciliador normal continua rejeitando fingerprints vazios. URLs aceitas são HTTPS nos hosts Shopee definidos, sem credenciais. FFprobe tem timeout e a validação não opera Android nem a UI de publicação.

## Persistência e invariantes

Uma transação muda somente `jobs.state` para `PUBLISHED_LEGACY`, acrescenta auditoria e armazena a evidência e metadata em `legacy_publications`, uma tabela separada. A evidência original, o fingerprint vazio, hashes, owner, created e attempted são preservados. Nenhum shop_id/item_id/variant_id é fabricado; todos ficam null com product_binding_status UNKNOWN, candidate_fingerprint_status NOT_AVAILABLE_LEGACY e reconciliation_quality LEGACY_PARTIAL. Campos comprovados e desconhecidos são enumerados. Metadados incluem URL/token, reviewer, timestamp e hashes das referências.

A resolução é idempotente apenas com a mesma evidência. Ela não cobra tentativa diária nem cria publish attempt. Autorizações antigas desse job são revogadas. Leases de conta/device pertencentes ao legado podem ser liberados quando não há outro resultado incerto na conta; leases de outros owners são preservados.

`PUBLISHED_LEGACY` é terminal: não retorna a READY/PUBLISHING/UNKNOWN, não aceita autorização final e o worker antigo não pode reabri-lo. Dedup de logical/source/prepared é permanente, inclusive além de dedup_window e quando um novo produto é indicado. Outros jobs independentes deixam de ser bloqueados pelo antigo UNKNOWN, mas conservam integralmente os gates normais e qualquer outro bloqueio da conta.

## Recuperação do breaker

A migração não fecha breaker. `LegacyBreakerAssessment` exige avaliação explícita e recente de que apenas esse incidente legado causava o OPEN, snapshot exato do breaker, reviewer e referência ao histórico auditado. Contador ou último reason isolado não provam essa condição. Para controles anteriores à auditoria, o operador/agente precisa registrar a análise dos artefatos originais; não se fabrica um histórico antigo de incidentes.

Novas falhas e releases ficam em `breaker_events`. A recuperação verifica toda a época após o último CLOSED explícito: falha diferente, sem job conhecido ou referente a outro job impede liberação, mesmo quando o último reason voltou a PUBLICATION_UNKNOWN. Uma mudança do snapshot após a avaliação também impede a liberação.

O preflight autorizado tem escopo **LEGACY_LEDGER_AND_PUBLIC_POST_READ_ONLY**. Verifica integridade SQLite, kill switch, ausência de jobs/leases/autorizações pendentes da conta e confirmação pública atual do mesmo post por GET HTTPS com timeout e limite de resposta. Executa OPEN → HALF_OPEN → CLOSED apenas se essas verificações passarem e nenhum incidente concorrente aparecer. Prova do preflight é persistida no snapshot/evento do breaker e no relatório. Falha de leitura mantém HALF_OPEN; novo incidente pode reabrir OPEN e é preservado. Não há retry automático.

Este preflight resolve a causa administrativa PUBLICATION_UNKNOWN. Não valida login, versão ou tela Android atual e não pode fechar CAPTCHA/LOGIN/SECURITY_ALERT ou outros incidentes. Os checks atuais de conta, app, mídia, produto, direitos, review, versão, modo e PublishGate continuam obrigatórios antes de efeitos futuros. O modo padrão segue DRY_RUN e produção continua pausada.

## CLI

```powershell
python scripts/operational_control.py reconcile-legacy --job LEGACY_JOB_ID --evidence legacy-evidence.json
python scripts/operational_control.py preflight-legacy-breaker --job LEGACY_JOB_ID --evidence breaker-assessment.json --output preflight.json
python scripts/operational_control.py status
```

O status expõe metadata legada separadamente de job_details e da evidência original. A CLI nunca publica. STOP ou falha de preflight retorna exit code 1. A execução e seus backups ficam em `output/legacy_reconciliation_20261006/`; testes em `tests/publishing/test_legacy_reconciliation.py` usam somente fixtures isoladas.
