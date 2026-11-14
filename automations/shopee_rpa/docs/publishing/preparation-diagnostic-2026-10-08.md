# Diagnóstico do UNKNOWN de preparação — 08/10/2026

Correção limitada à observação do incidente. A sessão `preparation_diagnostic` consegue ler sob OPEN, emprestando o escopo das leases retidas sem transferi-las, sob o lock exclusivo existente. Não oferece navegação, seletores, texto, Add, publicação, resolução de UNKNOWN ou liberação de breaker. Cada RPC revalida identidade/fingerprint, UNKNOWN/RPC_EFFECT_UNKNOWN, attempted=0, ausência de autorização final, kill switch e owner das duas leases. Deadline, processo RPC terminável e budgets existentes continuam obrigatórios. Leituras consomem orçamento; não consomem uploads nem tentativas de publicação.

Arquivos novos: `app/mobile/preparation_diagnostic.py`, `scripts/diagnose_shopee_preparation.py` e `tests/publishing/test_preparation_diagnostic.py`. Ledger, dedup, breaker global, modes globais, budgets, PublishGate, reconciliação legada, QA e worker de postagem existente não foram alterados. A identificação diagnóstica aceita também o prefixo nativo exato `Nome de usuário:`, usando o parser de perfil Video já existente, com marcador de perfil. Isso não substitui o preflight operacional antes de mutações.

## Evidência real

Telefone R9QYA0227VX, Shopee em foreground. Primeira inspeção: home, sem editor. Segunda: perfil Video com `Nome de usuário: borgesc542`, confirmado visualmente na captura com SHA-256 `d8e135cb143c5e5a6df96a081eab55ecdd8fdd8c94a850059f65162b58dae1d7`. O parser estrito da segunda execução ainda retornou UNKNOWN para conta por causa do prefixo nativo; o relatório original foi preservado e a interpretação visual é registrada separadamente. O parser de diagnóstico foi corrigido posteriormente e coberto por regressão offline, sem alterar o guard de conta operacional.

O perfil mostrava `Rascunhos: 3`. Após conferir manualmente essa lista, o operador informou que nenhum é o mousepad. O vídeo permanece na galeria segundo o operador. Essa declaração não comprova ausência de upload nativo anterior nem o efeito histórico do Adicionar. Não foi renovado artificialmente o timestamp da revisão anterior da mídia; ela está expirada para retomada operacional.

## Resultado

| Campo | Resultado |
|---|---|
| UNKNOWN resolvido | NÃO |
| JOB_ID | a87ba2d7f7f867c58a173b40d5d0755b42e3892ea69ab162cd44c890762c1212 |
| Estado | UNKNOWN, attempted=0 |
| Produto já vinculado / efeito histórico do Add | UNKNOWN |
| Add executado novamente | NÃO |
| Produto confirmado no editor nesta rodada | NÃO |
| ASSISTED_VALIDATED | NO |
| READY_FOR_PUBLISH | NO |
| Postar alcançado nesta rodada | NO; alcançado na rodada histórica |
| Postar clicado / publicação realizada | NO / NO |
| Breaker | OPEN → OPEN |
| Novos jobs | ZERO |

**Bloqueio exato:** não há editor/rascunho recuperável do candidato para comprovar o vínculo anterior ou sua ausência; o efeito do Add histórico continua UNKNOWN. O resolvedor existente também exige evidência explícita de ausência de upload e de publicação; a confirmação de que o arquivo está na galeria ou que o rascunho não foi salvo não comprova ausência de upload nativo. Sem essa prova, cancelar a preparação e liberar o breaker violaria os controles existentes. Nenhum preflight de fechamento foi executado porque a resolução não se tornou elegível. Nenhuma nova condição administrativa de liberação foi introduzida.

## Verificação

Suíte completa: 185/185 PASS, incluindo os 171 testes anteriores e 14 regressões carregadas no início da execução. Depois da última correção de leitura do username, o módulo final de diagnóstico passou 16/16, cobrindo duas regressões adicionais: 187 casos distintos verificados, sem falhas/erros/skips. O resultado não é apresentado como uma execução única de 187 casos. Compilação e whitespace passaram.

Resultados e logs: `output/preparation_recovery_20261008/offline-tests.json`, `offline-tests.log`, `diagnostic-tests.json` e `final-verification.json`. Dezesseis regressões específicas cobrem leitura com OPEN, bloqueio de mutações e dispatcher privado, shell restrito, kill switch, deadline, orçamento, autorização prévia, leases incompatíveis, mudança durável durante a sessão, foreground e identidade exata/prefixada. O teste de editor sem produto não permite inferir ausência histórica de efeito/upload.

Auditoria SQLite somente leitura em `operational-audit.json`: jobs, leases, ledger events, authorizations, job details, legacy publications e demais tabelas imutáveis preservadas; integridade `ok`, sem violações de FK. Únicas mudanças permitidas: counters de ações de diagnóstico, tokens da conta e início dessas sessões. Histórico PUBLISHED_LEGACY preservado. Backup anterior em `ledger-before.sqlite3`; capturas em `android-diagnostic-01/` e `android-diagnostic-02/`; respostas do operador em `operator-confirmation.json`.

Capability EXPERIMENTAL / PARTIAL; produção PAUSED. Chrome, pesquisa de hashtags e contas Google não são necessários nesta correção. D-027 documenta exclusivamente a capacidade de diagnóstico.
