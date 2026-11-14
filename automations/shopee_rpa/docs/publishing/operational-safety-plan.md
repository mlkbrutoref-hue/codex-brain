# Fase A — inspeção e contratos (06/10/2026)

1. Arquitetura encontrada: `ShopeeVideoPublisher` mistura UI, validação, captura e tentativa final. Sessões JSON e tentativa exclusiva por serial/hash são locais à raiz; `assisted.py` já prepara pacotes e não publica. `app/validation/media.py`, `app/media/ffmpeg/` e o cliente Affiliate serão reutilizados.
2. Alterações: worker Android, CLI de publicação, probe, pesquisa de hashtags, helper de resume, cliente/provider Affiliate, scripts de pesquisa que continuavam após erro e testes Android.
3. Novos contratos: `app/operational/` (config, deadline, store, budget, modos, breaker), `app/publishing/ledger.py` e `reconciliation.py`, `app/media/identity.py`, `provenance.py`, `normalization.py`, `app/validation/product_media_truth.py`, `publish_gate.py`, `app/mobile/ui.py`, `app/observability/`.
4. Reutilização: FFprobeInspector/TechnicalMediaValidator, FFmpegLocator, sessões e SHA-256, seletores realmente observados, locks de dispositivo e nove checks do preparador assistido. Não criar segundo pipeline de conteúdo.
5. Confirmados por código: C02, C03, C04, C05, C06, C07, C08, C09, C10, C11, C12, C14, C17, C18, C19. Três reproduções sintéticas anteriores e revisão Antigravity preservadas na auditoria.
6. Não reproduzidos: post incorreto real, duplicata real, penalidade, comportamento de nova versão Shopee, IDs/variantes na árvore nativa, confirmação com post ID. Evidência insuficiente deve bloquear em REVIEW; nenhum ID de UI será inventado.
7. Migração: snapshot dos arquivos alterados; SQLite local compartilhado por usuário fora da raiz de jobs; importação conservadora de sessões antigas com tentativa como UNKNOWN; DRY_RUN sem conexão como padrão. Config antiga não autoriza efeitos. Operação assistida exige manifesto novo e aprovações; live exige flag explícita e caminho autorizado. Não apagar tentativa antiga para migrar.
8. Riscos: restrições novas interrompem fluxos permissivos; UI pode não expor identidade forte; hashes de preview são frágeis; morte de RPC não desfaz efeito remoto; SQLite não coordena hosts diferentes. Estes limites são explícitos e falham de forma fechada.

## Contratos e invariantes antes do código

`PostCandidate` contém conta, identidade lógica/hash fonte/hash preparado, produto/variante, copy, proveniência, QA e revisão. Revisão humana vinculada ao fingerprint completo (conta, mídia, produto, variante, copy), revisor e tempo; alterações ou expiração invalidam.

`JobLedger.reserve_job` reserva trabalho antes da UI, sem chamar isso de tentativa de post. `PublishGate` valida novamente e emite capability de uso único registrada na mesma transação da reserva final e orçamento. `reserve_publish_attempt` é durável antes do clique; crash depois disso é UNKNOWN até reconciliação. Nenhuma mensagem genérica muda para PUBLISHED.

OPEN/kill/deadline impedem próxima ação; PAUSED impede leitura externa; RECOVERY permite apenas leitura; nenhum retry automático de efeito incerto. Conta exata e app/versão/tela exigidos. Probe não possui comandos de mutação. Config padrão DRY_RUN; fakes não habilitam LIVE_PUBLISH.

## Testes planejados

Vinte failure modes do pedido: token bucket/deadline/breaker; conta/variante/direitos/QA/revisão/TTL; associação cruzada de card; dedup lógica e reencode; UNKNOWN e corrida transacional; limites diários; versão/seletor; picker ambíguo; confirmação tardia; HTTP 429/Retry-After; helpers sem gate. Mais testes de crash, revogação/uso único de autorização e logger sem segredos. Tudo offline.

## Pesquisa que influencia o design

- DOCUMENTED: [SQLite transactions](https://www.sqlite.org/lang_transaction.html): um escritor por vez e BEGIN IMMEDIATE. Reserva, dedup e contadores devem compartilhar transação; não depender de lock de arquivo por job.
- DOCUMENTED: [Python subprocess](https://docs.python.org/3/library/subprocess.html): timeout mata/aguarda filho em `run`; criação pode ter atraso do SO. UI real será isolada em processo terminável; efeito remoto em voo continua incerto.
- DOCUMENTED/provider-specific: [uiautomator2](https://github.com/openatx/uiautomator2): seletores e RPC podem falhar. Não assumir timeout de espera como deadline global.
- DOCUMENTED: [FFmpeg](https://ffmpeg.org/ffmpeg.html): decodificação e normalização técnica, sem manipulação para evasão. Reusar locator e probe existentes, verificar antes/depois.
- DOCUMENTED: [Retry-After](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Retry-After): segundos ou data HTTP; persistir não-antes e interromper lote, sem retry automático.

Design/implementação EXPERIMENTAL; não promove Publishing a READY nem autoriza produção pela plataforma.
