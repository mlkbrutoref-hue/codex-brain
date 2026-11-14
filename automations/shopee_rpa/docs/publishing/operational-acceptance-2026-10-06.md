# Operational Acceptance — Shopee Video — 06/10/2026

Rodada concluída em 2026-10-06T21:46:41.696045-03:00 (America/Sao_Paulo).

## 1. Executive Summary

**OPERATIONAL STATUS: READY_FOR_DRY_RUN_ONLY.** Rodada offline concluída; o candidato real foi bloqueado pelos gates de conteúdo. Não houve conexão Android, API autenticada, upload, autorização real ou clique em Postar. Não é uma validação do fluxo nativo.

Cinco bugs corrigidos com 15 testes novos. A tentativa antiga foi importada conservadoramente no banco real como UNKNOWN; sua sessão original não foi alterada. Nenhuma arquitetura paralela foi criada.

## 2. Environment

Python: `3.14.7 (tags/v3.14.7:823f032, Aug  5 2026, 10:51:32) [MSC v.1944 64 bit (AMD64)]`. SO: `Windows-10-10.0.19045-SP0`. Dependências instaladas: `{'uiautomator2': '3.7.0', 'Pillow': '12.3.0'}`.

Dispositivo esperado: R9QYA0227VX / SM_A075M / 720x1600 / com.shopee.br. Conexão, tela ligada, versão Android/Shopee e foreground atuais: **NOT EXECUTED / UNKNOWN**. Pré-requisitos impediram avanço à fase Android. `environment.json` distingue valores esperados de observados.

## 3. Baseline

Git status completo salvo antes de alterações; hashes e backup consistente SQLite preservados. Nenhum reset, remoção de ledger ou staging foi executado. Mudanças anteriores fora dos arquivos desta rodada permaneceram iguais aos hashes de entrada.

Baseline: publicação 86/86 em 156.047s; geral 214/214 em 251.379s. Evidências em `baseline-*.txt`, `git-status-before.txt`, `baseline-manifest.json` e `operational-before.sqlite3`.

## 4. Ledger State

Banco real: `C:\Users\GAMER\AppData\Local\AICommerceContentFactory\operational\state.sqlite3`. Integridade SQLite: ok antes/depois. Inicialmente vazio; depois: 1 UNKNOWN, 0 leases, 0 authorizations, counters vazios. Sem RESERVED/PREPARING/READY/UPLOADING/PUBLISHING/PUBLISHED/FAILED/CANCELLED, órfãos ou autorizações expiradas. Leases não têm expiração automática por design; nenhum lease foi removido nesta rodada.

| JOB_ID | ACCOUNT | ASSET | PRODUCT | VARIANT | STATE | PUBLISH_ATTEMPT | UNKNOWN_REASON | LEASE | BREAKER_IMPACT | ACTION_REQUIRED |
|---|---|---|---|---|---|---|---|---|---|---|
| legacy:53926be5d018b6d3b4b5cf0302cd221bb2ba330d54da86f510c377823b253d9f | borgesc542 (namespace esperado histórico) | legacy:c4d7bdea9d2ff771a76444bf3877cfef04887521aa6ce6e7c31ce74912621561 | IDs ausentes; título histórico de mochila | UNKNOWN | UNKNOWN | 1 (histórico) | PUBLICATION_UNCONFIRMED_DO_NOT_REPOST | nenhum; bloqueio pela conta | OPEN crítico | B01: EVIDENCE REQUIRED |

`created` do registro importado é o tempo da migração, não o horário do post. Horários originais constam em `historical-analysis-before.json`. Sem cobrança retroativa fabricada de budgets; o campo attempted registra a tentativa legada, e novos efeitos ficam bloqueados pelo ledger/breaker.

## 5. Historical UNKNOWN

Sessão `shopee_android_usb_20261006_01`: tentativa durável local às 12:07:08, transição PUBLISHING às 12:07:09 e resultado não confirmado às 12:08:18 de 06/10/2026 (America/Sao_Paulo; registros originais em UTC). Retorno ao perfil foi observado, mas não prova o post correto. SHA-256 da sessão continua `065e78a8878f00baf175edbdef4cce00fd9c283493bb63d85e2407673a1b62e8`.

32 referências de captura mantêm os hashes; nenhum post ID/URL foi encontrado nas evidências estruturadas/capturas inspecionadas. O hash da configuração atual difere do hash de entrada da sessão histórica; isso não prova adulteração, mas impede herdar sua aprovação/binding. `config_sha256` antigo não é um PostCandidate fingerprint.

## 6. Reconciliation Status

**EVIDENCE REQUIRED.** Ausentes post ID/URL, vínculo verificável conta/asset/copy/produto/variante e fingerprint do candidato legado. Não foi executada promoção a PUBLISHED, cancelamento, FAILED ou retry. O reconciler agora rejeita fingerprint vazio mesmo que ambos os lados estejam vazios. O protocolo atual não oferece migração automática de um legado sem fingerprint; reconstrução auditada requer evidência humana real. Foi solicitada a evidência ao usuário; sua ausência não impediu as demais fases offline.

## 7. DRY_RUN Result

Campanha real existente: `prod_escova_12em1_58261505729_20260910_235725`, produto Escova de Limpeza Elétrica Portátil 12 em 1 com Cabo Epsilon Preto. Fonte take_01 e export Shopee existentes; nenhuma mídia fictícia foi usada para aprovar o candidato. Caption derivada do título persistido e três hashtags já existentes; sem alegação de popularidade, revisão ou proveniência inventada.

QA técnico: PASS; preparado MP4/H.264/AAC, 1080x1920, 30fps, 8s, 5197137 bytes. Probe fonte: 720x1280/24fps/8s. Decode completo do preparado e da fonte executado; fonte confirmada também em `source-decode-qa.json`. Hash fonte `7d2ee879ec6ca62905fc1be7cc8ee6e14f25c11593c5616179747975414b9675`; hash preparado `e998aba453baa92930d1f7dab5a1cc56d8affb5b5dd2ba35f74f59edb524895e`. Sem normalização/reencode nesta rodada; originais preservados.

Resultado do worker: **STOP** / `CONTENT_GATE_FAIL:variant_match:REVIEW,media_product_match:REVIEW,caption_relevance:REVIEW,rights:FAIL,originality:REVIEW,ai_disclosure:FAIL,human_review:REVIEW`. PublishGate em DRY_RUN: `LIVE_PUBLISH_DISABLED_OR_UNAUTHORIZED`. Tripwires para conexão, import de uiautomator2, ADB, transporte HTTP e clique final ficaram em zero. Subprocesses executados foram somente FFprobe/FFmpeg locais. Detalhes: `media-qa.json`, `candidate-source-map.json`, `real-candidate-dry-run.json`, `dry-run-result.json`.

| CHECK | STATUS | EVIDENCE | BLOCKER | ACTION_REQUIRED |
|---|---|---|---|---|
| account | PASS | ContentValidator real | nenhum no escopo local | preservar binding |
| product_identity | PASS | ContentValidator real | nenhum no escopo local | preservar binding |
| variant_match | REVIEW | ContentValidator real | ausência/revisão | evidência humana; não fabricar PASS |
| media_product_match | REVIEW | ContentValidator real | ausência/revisão | evidência humana; não fabricar PASS |
| caption_relevance | REVIEW | ContentValidator real | ausência/revisão | evidência humana; não fabricar PASS |
| media_uniqueness | PASS | ContentValidator real | nenhum no escopo local | preservar binding |
| media_quality | PASS | ContentValidator real | nenhum no escopo local | preservar binding |
| rights | FAIL | ContentValidator real | ausência/revisão | evidência humana; não fabricar PASS |
| originality | REVIEW | ContentValidator real | ausência/revisão | evidência humana; não fabricar PASS |
| ai_disclosure | FAIL | ContentValidator real | ausência/revisão | evidência humana; não fabricar PASS |
| human_review | REVIEW | ContentValidator real | ausência/revisão | evidência humana; não fabricar PASS |

## 8. Validation Gates

A matriz separa o resultado do candidato da verificação offline do controle. PASS_OFFLINE não significa conta ou interface nativa verificadas. Product IDs são cache real de 10/09; disponibilidade, atributos completos e elegibilidade atuais não foram consultados.

| CONTROL | STATUS | EVIDENCE |
|---|---|---|
| Account Identity | REVIEW | Expected namespace borgesc542 from history; no current login/marker proof |
| Media Identity | PASS_LOCAL | Source and prepared hashes; stable campaign master identity |
| Media QA | PASS | FFprobe + full prepared decode; 1080x1920, H.264/AAC, 30 fps, 8s |
| Media Provenance | REVIEW | Existing generation manifest; license/creator not verified |
| Rights | FAIL_GATE | UNKNOWN is correctly blocked; B02 |
| Originality | REVIEW | No current review; B03 |
| AI Disclosure | FAIL_GATE | AI declared, disclosure absent; B05 |
| Product Identity | PASS_CACHED | shop 1661007426 / item 58261505729; no current catalog availability assertion |
| Variant Match | REVIEW | No variant ID; title color is insufficient; B04 |
| Media/Product Match | REVIEW | No current semantic binding; B03 |
| Caption Match | REVIEW | Local payload consistent; relevance not approved |
| Human Review | REVIEW | Null; no fabricated approval |
| Dedup | PASS_CONTROL | Existing logical/media protections pass; real escova not media duplicate, but account UNKNOWN blocks effects |
| Job Ledger | PASS_CONTROL | SQLite integrity ok; one historical UNKNOWN, no live reservations |
| Action Budget | PASS_CONTROL | Persistent tests pass; current tokens 200 / counters empty; OPEN prevents consume |
| Circuit Breaker | PASS_CONTROL / OPEN | Actual unresolved incident remains critical OPEN; lifecycle regressions fixed |
| Kill Switch | PASS_CONTROL / false | False in real store; isolated active-switch tests block all effects |
| Deadline | PASS_CONTROL | Expired deadline prevents effect; fake hanging RPC terminated |
| PublishGate | BLOCKED_EXPECTED | DRY_RUN rejects before authorization; real content FAIL |
| Authorization Token | PASS_OFFLINE | Binding/expiry/reuse negatives pass; real DB has zero authorization tokens |
| Reconciliation | EVIDENCE_REQUIRED | Legacy has no valid candidate fingerprint; empty binding now refused |
| Logging | PASS | Acceptance event allowlist/schema checked; no forbidden fields/full caption |
| Health | PASS_LOCAL | All requested fields present; local preflight only, no platform inference |
| Read-only Probe | PASS_OFFLINE | Mutation paths refused; no real probe connection |
| Affiliate Error Handling | PASS_OFFLINE | 429/Retry-After and 401/403 stop; no authenticated request |

## 9. Offline Failure Tests

Os 30 cenários foram novamente verificados pelas assertions dos testes referenciados na suíte final. ACTUAL deriva dessas assertions executadas; não de um teste na conta real. Fixtures de autorização/budget permanecem em bancos temporários dos testes, sem LIVE_PUBLISH e sem autorização criada no banco real.

| SCENARIO | EXPECTED | ACTUAL | STATUS | TEST |
|---|---|---|---|---|
| 1. rights UNKNOWN | rights FAIL | rights FAIL | PASS | test_unknown_rights_block |
| 2. rights REJECTED | rights FAIL | rights FAIL | PASS | test_rejected_rights_never_pass |
| 3. QA FAIL | ContentValidator FAIL | ContentValidator FAIL | PASS | test_quality_fail_or_wrong_hash_block |
| 4. account mismatch | ACCOUNT_MISMATCH | ACCOUNT_MISMATCH | PASS | test_account_requires_exact_match |
| 5. stable marker missing | account preflight STOP | account preflight STOP | PASS | test_missing_stable_marker_blocks |
| 6. shop_id mismatch | product_identity FAIL | product_identity FAIL | PASS | test_each_commercial_id_mismatch_blocks |
| 7. item_id mismatch | product_identity FAIL | product_identity FAIL | PASS | test_each_commercial_id_mismatch_blocks |
| 8. variant mismatch | content FAIL / review invalidated | content FAIL / review invalidated | PASS | test_variant_change_invalidates_review |
| 9. title A + button B | card association refused | card association refused | PASS | test_c02_one_foreign_add_button_refused |
| 10. stale review fingerprint | human_review REVIEW | human_review REVIEW | PASS | test_all_reviewed_components_invalidate_review |
| 11. expired review | human_review REVIEW | human_review REVIEW | PASS | test_expired_or_future_approval_block |
| 12. caption changed | human_review REVIEW | human_review REVIEW | PASS | test_all_reviewed_components_invalidate_review |
| 13. media changed | human_review REVIEW | human_review REVIEW | PASS | test_all_reviewed_components_invalidate_review |
| 14. duplicate logical asset | DUPLICATE_MEDIA | DUPLICATE_MEDIA | PASS | test_reencode_same_logical_asset_duplicate |
| 15. reencode same logical ID | DUPLICATE_MEDIA | DUPLICATE_MEDIA | PASS | test_reencode_same_logical_asset_duplicate |
| 16. previous UNKNOWN | retry blocked / UNKNOWN retained | retry blocked / UNKNOWN retained | PASS | test_unknown_blocks_repost_across_root_and_device |
| 17. breaker OPEN | no UI effect | no UI effect | PASS | test_open_kill_and_deadline_block_ui_before_any_effect |
| 18. kill switch | no UI effect | no UI effect | PASS | test_open_kill_and_deadline_block_ui_before_any_effect |
| 19. budget exhausted | BUDGET_EXCEEDED | BUDGET_EXCEEDED | PASS | test_persistent_daily_budget_not_reset_by_session |
| 20. deadline expired | no UI effect | no UI effect | PASS | test_open_kill_and_deadline_block_ui_before_any_effect |
| 21. authorization reused | INVALID_OR_USED_PUBLISH_AUTHORIZATION | INVALID_OR_USED_PUBLISH_AUTHORIZATION | PASS | test_final_reservation_is_durable_one_use_and_charged |
| 22. token for another job | INVALID_OR_USED_PUBLISH_AUTHORIZATION | INVALID_OR_USED_PUBLISH_AUTHORIZATION | PASS | test_authorization_is_bound_to_its_job |
| 23. token expired | INVALID_OR_USED_PUBLISH_AUTHORIZATION | INVALID_OR_USED_PUBLISH_AUTHORIZATION | PASS | test_expired_authorization_blocks |
| 24. two workers | one reserved / one blocked | one reserved / one blocked | PASS | test_two_workers_cannot_reserve_same_job |
| 25. probe mutation | READ_ONLY_ACTION_BLOCKED | READ_ONLY_ACTION_BLOCKED | PASS | test_read_only_probe_has_no_mutation_paths |
| 26. Affiliate 429 | RATE_LIMITED / shared breaker / no next call | RATE_LIMITED / shared breaker / no next call | PASS | test_429_stops_other_workers_and_preserves_retry_after |
| 27. Affiliate 401/403 | AUTH_OR_ACCESS / no continuation | AUTH_OR_ACCESS / no continuation | PASS | test_401_blocks_following_api_request, test_403_is_access_not_rate_limit |
| 28. hanging RPC | RPC_TIMEOUT / child terminated | RPC_TIMEOUT / child terminated | PASS | test_hanging_rpc_is_terminated_with_global_deadline |
| 29. ambiguous picker | selection evidence refused | selection evidence refused | PASS | test_ambiguous_picker_even_equal_duration_requires_review |
| 30. missing selector | no click | no click | PASS | test_missing_selector_blocks_click |

## 10. Assisted Mode Result

**BLOCKED / NOT EXECUTED.** Conta com UNKNOWN real e breaker crítico OPEN, gates de conteúdo FAIL/REVIEW, stable marker ausente, app allowlist vazia e autorização de interface ausente. Nenhum desses controles foi liberado para alcançar Android/READY. Não se reivindica ASSISTED_VALIDATED. Não houve navegação, seleção, preview, editor ou upload na conta real.

## 11. UI Failure Tests

Dez cenários de UI foram verificados offline com fakes e assertions de ausência de mutação. Nenhum desafio/login foi provocado no celular. Remoção de selector entre duas inspeções é detectada; permanece a janela física entre última observação e RPC. Controle exclusivo do aparelho continua necessário; não há atomicidade com a UI externa.

| SCENARIO | OFFLINE | REAL ANDROID | TEST |
|---|---|---|---|
| selector missing | PASS_OFFLINE | NOT_EXECUTED | test_missing_selector_blocks_click |
| unexpected/security screen | PASS_OFFLINE | NOT_EXECUTED | test_enter_cannot_activate_post_or_security_screen |
| foreground changed | PASS_OFFLINE | NOT_EXECUTED | test_foreground_change_blocks_next_mutation |
| account marker missing | PASS_OFFLINE | NOT_EXECUTED | test_missing_stable_marker_blocks |
| expected product missing/wrong | PASS_OFFLINE | NOT_EXECUTED | test_wrong_linked_product_blocks_ui_before_mutation |
| ambiguous media | PASS_OFFLINE | NOT_EXECUTED | test_ambiguous_picker_even_equal_duration_requires_review |
| breaker OPEN | PASS_OFFLINE | NOT_EXECUTED | test_open_kill_and_deadline_block_ui_before_any_effect |
| kill switch | PASS_OFFLINE | NOT_EXECUTED | test_open_kill_and_deadline_block_ui_before_any_effect |
| deadline | PASS_OFFLINE | NOT_EXECUTED | test_open_kill_and_deadline_block_ui_before_any_effect |
| operator removes selector between checks | PASS_OFFLINE | NOT_EXECUTED | test_operator_removes_selector_between_check_and_action |

## 12. Observability

25 eventos estruturados da rodada inspecionados: schema dos eventos de ação completo, zero campos proibidos ou caption completa. XML/screenshot históricos ficam preservados como evidência antiga; não foram copiados para JSONL novo.

Health executado: `{'actions_total': 1, 'success_rate': 0.0, 'error_rate': 1.0, 'avg_latency_ms': 442.676600003324, 'p95_latency_ms': 442.676600003324, 'consecutive_failures': 1, 'unknown_results': 0, 'session_duration': 15.448588499995822, 'budget_remaining': {'tokens': 200, 'counters': {'account:borgesc542:2026-10-06': {}, 'session:borgesc542:acceptance_dry_escova_20261006': {}, 'worker:borgesc542:acceptance-local': {}, 'session_duration': 0.00041294097900390625}}, 'circuit_breaker_state': 'OPEN', 'current_mode': 'PAUSED'}`. A única ação é uma avaliação **local** do preflight, bloqueada por conteúdo; error_rate=1 não representa erro de Shopee ou punição. unknown_results=0 refere-se a esse recorte de eventos, enquanto o ledger tem um UNKNOWN histórico. Nenhuma inferência de shadowban/chance de ban/risk score foi feita.

## 13. Bugs Found

F01: fingerprint vazio do legado podia confirmar PUBLISHED com evidência igualmente vazia. F02: XPath Adicionar não exigia pacote Shopee. F03: erro de caption no construtor escapava do STOP JSON da CLI. F04: critical permanecia após close humano e alterava o threshold de futuras falhas recuperáveis. F05: falha recuperável sobrescrevia causa crítica OPEN. Reproduções anteriores preservadas: `bugs-before-fix-tests.txt` (2 failures, 1 error) e `breaker-before-fix-tests.txt` (2 failures).

## 14. Bugs Fixed

Cinco correções pontuais: SHA-256 válido obrigatório na reconciliação; pacote exato no wrapper e dispatcher XPath; construtor incluído no try da CLI; critical removido somente após close humano completo; causa crítica mantida contra erro recuperável. Não foram desativados gates, alterados limites, liberado breaker real ou criado fluxo paralelo.

Arquivos de runtime alterados: `app/publishing/reconciliation.py`, `app/mobile/ui.py`, `scripts/publish_shopee_android.py`, `app/operational/circuit_breaker.py`. Novo `tests/publishing/test_operational_acceptance.py`: 15 testes. Documentação desta rodada e `brain/CURRENT_STATE.md` registram o estado; DECISIONS não muda por ausência de nova decisão arquitetural. Backup pré-fix em `pre-fix/`.

O primeiro DRY_RUN revelou também a substituição de causa no breaker real; a ocorrência foi preservada no snapshot e a tentativa histórica verdadeira foi registrada novamente como PUBLICATION_UNKNOWN após a correção. O estado sempre permaneceu OPEN/crítico; não houve liberação. `breaker-incident-preservation.json` registra essa manutenção.

## 15. Remaining Blockers

Sete grupos de blocker; ausências de evidência são requisitos de revisão, não bugs automaticamente.

| ID | SEVERITY | COMPONENT | CAUSE | EVIDENCE | ACTION REQUIRED | OWNER |
|---|---|---|---|---|---|---|
| B01 | HIGH | Historical UNKNOWN | No post ID/URL, strong product binding or candidate fingerprint; current config hash differs from historical session hash | historical-unknown.json; historical-evidence-inventory.json | Provide matched post evidence and audit legacy binding; keep UNKNOWN | User + maintainer |
| B02 | HIGH | Rights / provenance | Generation metadata is not a verified license | real-candidate-dry-run.json | Provide source ownership/license and evidence; no inferred VERIFIED | User / rights holder |
| B03 | HIGH | Semantic QA / HumanReview | No current media-product, originality or caption review bound to this candidate | dry-run-result.json | Review actual asset/product/copy and submit fingerprint-bound evidence | Human reviewer |
| B04 | HIGH | Variant | Cached product has no variant ID; Preto in title does not prove the depicted selected variant | candidate-source-map.json | Provide exact variant and observed attribute correspondence | User / product reviewer |
| B05 | MEDIUM | AI Disclosure | Existing campaign declares Flow generation; candidate contains no disclosure | dry-run-result.json | Approve applicable disclosure and re-review changed copy | User / content reviewer |
| B06 | HIGH | Account / native UI evidence | Current stable marker, app version allowlist and fresh selection/preview evidence are absent | environment.json; real-candidate-dry-run.json | Supply exact account marker, reviewed configuration and fresh native evidence when gates permit | User + operator |
| B07 | HIGH | External interface authorization | No applicable platform_authorization reference in the candidate configuration | dry-run-result.json | Provide applicable interface authorization; do not bypass the existing gate | User / platform |

## 16. Tests

| RUN | PASSED/TOTAL | FAILED | ERRORS | SKIPPED | SECONDS |
|---|---|---|---|---|---|
| baseline-tests.txt | 86/86 | 0 | 0 | 0 | 156.047 |
| baseline-general-tests.txt | 214/214 | 0 | 0 | 0 | 251.379 |
| bugs-before-fix-tests.txt | 8/11 | 2 | 1 | 0 | 17.39 |
| bugs-after-fix-tests.txt | 11/11 | 0 | 0 | 0 | 14.221 |
| breaker-before-fix-tests.txt | 0/2 | 2 | 0 | 0 | 6.776 |
| acceptance-regressions-final.txt | 13/13 | 0 | 0 | 0 | 25.527 |
| ui-negative-extra-tests.txt | 2/2 | 0 | 0 | 0 | 8.818 |
| publishing-tests.txt | 97/97 | 0 | 0 | 0 | 174.232 |
| general-tests.txt | 225/225 | 0 | 0 | 0 | 277.368 |
| final-publishing-tests.txt | 101/101 | 0 | 0 | 0 | 182.244 |
| final-general-tests.txt | 229/229 | 0 | 0 | 0 | 273.141 |

As suítes de publicação estão incluídas na geral; não somar contagens como testes únicos. Compilação e diff check dos arquivos alterados passaram. Suítes intermediárias começaram antes dos dois ajustes de breaker/testes finais; evidência de aceite do código final são `final-publishing-tests.txt` e `final-general-tests.txt`.

## 17. Operational Status

**READY_FOR_DRY_RUN_ONLY.** Historical UNKNOWN: EVIDENCE REQUIRED / bloqueio preservado. DRY_RUN: executado e bloqueado corretamente. ASSISTED_MODE: não executado por pré-requisitos. PUBLISH PERFORMED: NO. Não foi configurado LIVE_PUBLISH ou executado --publish.

## 18. Recommendation

Prioridade: obter evidência correspondente ao post histórico, avaliar seu binding legado sem apagar/burlar UNKNOWN, comprovar licença/semântica/variante/disclosure e realizar revisão humana vinculada ao fingerprint. Só depois, com autorização de interface e account/app/selection preflight verificáveis, reavaliar uma sessão ASSISTED_MODE que pare antes da publicação. Até lá, continuar com produção/QA/empacotamento local e publicação manual. Não fabricar permissões, reviews ou token para completar a demonstração.

Artefatos canônicos da rodada: `output/operational_acceptance_20261006/`; matriz, blockers, snapshots, logs, hashes e `acceptance-verification.json` permitem reproduzir o resultado sem operar a conta.
