# Primeira etapa: continuação do fluxo existente

Implementação limitada ao worker Android existente. Chrome e pesquisa/curadoria de hashtags não foram implementados. A legenda e as tags fornecidas ao candidato continuam sendo usadas sem alteração de estratégia.

## Comportamento

Uma seleção com evidência válida pode continuar pelo seletor nativo `tv_pick_top_next`, pelo preview `edit_compose_view` / `player_container` e por `tv_compress` até o editor com `iv_video_preview`, `et_caption` e `btn_post`. No picker, a identidade do arquivo, o inventário, as durações e a célula marcada são conferidos; a seleção é conferida novamente antes de Próximo. Retomar diretamente um preview exige também `preview_screen_sha256` na evidência existente. Retomar o editor valida o thumbnail contra `preview_pixel_sha256` e não repete Próximo nem a seleção.

O checkpoint de revisão de mídia original foi mantido. Uma seleção nova sem revisão não ganha aprovação automática. Arquivos de prova, fingerprint, conta, hash e validade continuam obrigatórios; fonte e QA não são substituídos pelo nome/duração do vídeo.

No editor, o produto é vinculado antes da legenda definitiva. A aba obrigatória é Minhas Curtidas: se já estiver ativa, o worker não a clica novamente. Um card exato já visível elimina a pesquisa. Ausência do card permite digitar a consulta e submeter Enter dentro de Minhas Curtidas; ambiguidade ou card malformado interrompe a execução para REVIEW. A aba Todos não é usada.

Adicionar continua usando o seletor nativo corrigido, derivado do XPath bruto. O hash da tela observada acompanha o clique e é verificado no guard e no processo Android, prevenindo o uso do mesmo caminho após uma mudança de card. A informação do produto e Feito precisam aparecer; depois, o editor precisa expor exatamente um produto com o título esperado.

Uma revisão explícita de card com IDs ocultos passa a integrar o binding principal durante ASSISTED_MODE. O binding acompanha a sequência card → Adicionar → Editar informações → Feito → produto no editor e é incluído na evidência de conclusão do ledger. Não é usado como evidência final em LIVE_PUBLISH. O caminho anterior de IDs nativos exatos sem variante foi preservado.

Só então a legenda é preenchida. Os checks finais conferem novamente a mídia, o produto, a legenda, os compartilhamentos e os gates existentes. ASSISTED_MODE termina em ASSISTED_VALIDATED, com ready_for_publish=false e sem chamada a publish/final_click. READY_FOR_PUBLISH e PublishGate mantêm seus requisitos de publicação.

As esperas seguem predicates de estado e deadline. Foram eliminadas releituras imediatas no worker ao aproveitar a tela retornada pelo wait e a validação de mídia já feita na continuação. Os guards imediatamente anteriores a mutações foram mantidos. Há uma única conexão Android durante a execução normal; nenhuma reconexão/helper foi acrescentada. Não há benchmark real de ganho nesta rodada.

## Contrato da revisão do card

`product_card_review` aponta para um JSON novo, com revisão efetivamente realizada, contendo:

```text
status = APPROVED_UI_ONLY
reviewer
reviewed_at
candidate_fingerprint
product = identidade comercial e atributos já comprovados do candidato
official_source_url
card = título, XPath bruto e IDs realmente observáveis (null se ocultos)
title_exact = true
button_node_sha256
screen_sha256
screenshot_reference
screenshot_sha256
```

Os hashes de nós usam SHA-256 de JSON com sort_keys=true e ensure_ascii=false. Os hashes de arquivos usam seus bytes. A revisão deve corresponder à tela atual e ficar dentro do approval_ttl; mudanças no arquivo de prova ou no nó vinculado invalidam o binding. Direitos, IA e tamanho UNKNOWN não são promovidos. Os arquivos antigos de revisão não foram alterados nem tiveram timestamps renovados.

## Validação e situação real

Regressões em `tests/publishing/test_posting_flow.py` exercitam o worker e os guards reais com Android fake e SQLite isolado. Cobrem a sequência completa, ordem produto/legenda, card visível sem pesquisa, pesquisa em Curtidas apenas quando ausente, aba inativa, retomadas, seleção/inventário alterados, card duplicado/alterado, revisão inválida, binding modificado, não reutilização do binding assistido na publicação final e bloqueio de UNKNOWN antes de qualquer ação externa.

Resultado final: **171/171 testes de publicação passaram**, incluindo 19 novas regressões, sem falhas, erros ou skips. Compilação dos módulos e whitespace passaram. Consultar `output/posting_flow_stage1_20261007/offline-tests.json` e `offline-tests.log`. Backup dos três módulos, diff e snapshot SQLite anterior estão no mesmo diretório. O relatório de integridade e preflight é `operational-audit.json`; a conferência posterior à suíte é `final-verification.json`.

**A validação assistida real não foi retomada nesta rodada.** Job `a87ba2d7f7f867c58a173b40d5d0755b42e3892ea69ab162cd44c890762c1212` permanece UNKNOWN, attempted=0; breaker borgesc542 permanece OPEN por RPC_EFFECT_UNKNOWN. O banco real foi aberto em modo read-only: integridade ok, sem violações de FK, todas as tabelas iguais ao snapshot e reconciliação legada preservada.

O mecanismo existente `resolve_preparation_unknown` exige provas explícitas de ausência de publicação **e de upload**. A recusa por ausência da segunda prova foi exercitada somente em uma cópia isolada: EXPLICIT_NO_EFFECT_EVIDENCE_REQUIRED. Faltam evidência confiável do efeito do RPC Adicionar anterior e da ausência de upload nativo na preparação. A classe original da exceção não foi persistida; reproduzir offline a incompatibilidade de XPath não reconstrói esse resultado histórico. Zero tentativas/counters finais não prova ausência de upload interno da Shopee.

O preflight do breaker foi exercitado na cópia: CIRCUIT_OPEN também para leitura. Portanto, nenhum telefone foi conectado, nenhum Adicionar repetido, nenhum Postar clicado e nenhum job equivalente criado. UNKNOWN, leases, budgets, autorizações, dedup e o legado não foram editados. Não houve passagem a HALF_OPEN/CLOSED sem resolução suficiente do incidente.

No celular, o editor e o botão Postar foram alcançados **na rodada anterior**, mas o vínculo do produto continua não confirmado. Nesta rodada, a conclusão técnica é comprovada somente offline. A capability permanece EXPERIMENTAL / PARTIAL e produção PAUSED.
