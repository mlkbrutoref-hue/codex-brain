**Relatório operacional — Mousepad Titorion preto — 07/10/2026**

A alteração de escopo foi implementada e o ASSISTED_MODE executou no Android com rights=UNKNOWN. O vídeo correto chegou ao editor que contém o botão Postar, a legenda foi preenchida e o anúncio correspondente foi encontrado. A validação completa parou durante a tentativa de adicionar esse produto. O resultado atual é parcial: ASSISTED_VALIDATED não foi alcançado. O botão Postar não foi clicado e não houve tentativa final de publicação.

Esta atualização do relatório consultou somente arquivos locais e o SQLite em modo read-only. Não retomou a operação do celular. A auditoria local está em [report-ledger-audit.json](<C:/Users/GAMER/Documents/SHOPEE AUTOMATION/ai-commerce-content-factory/output/assisted_mousepad_20261007/report-ledger-audit.json>), com timestamp UTC registrado no próprio arquivo.

| Campo | Resultado comprovado |
|---|---|
| CANDIDATE | Mousepad Titorion preto; asset gallery_mousepad_R9QYA0227VX_410770 |
| ACCOUNT | borgesc542, confirmada na interface nativa |
| ASSISTED_MODE | Executado, fluxo parcial |
| ASSISTED_VALIDATED | NO |
| READY_FOR_PUBLISH | NO |
| PUBLISH BUTTON REACHED | YES, editor observado antes de concluir o vínculo do produto |
| PUBLISH BUTTON CLICKED | NO |
| PUBLISH PERFORMED | NO |
| RIGHTS | UNKNOWN |
| AI GENERATED | UNKNOWN, persistido como null |
| PROVENANCE | PLATFORM_PROVIDED / PRODUCT_LISTING_SOURCE |
| SOURCE MATCH | PASS, declaração do operador e evidência vinculada à mídia/produto |
| PRODUCT MATCH | PASS para a correspondência vídeo/anúncio; vínculo nativo ainda não confirmado |
| PRODUCT | shop_id 473616631; item_id 43050661409 |
| VARIANT | Preto observado/confirmado; variant_id indisponível; tamanho UNKNOWN |
| JOB STATE BEFORE INCIDENT | PREPARING |
| JOB STATE NOW | UNKNOWN, reason RPC_EFFECT_UNKNOWN |
| PUBLIC POST ID / URL DO MOUSEPAD | Não existe resultado de publicação desta rodada |
| FINAL PUBLISH ATTEMPTS | 0 para este job |
| FINAL AUTHORIZATIONS | 0 no banco auditado |
| BREAKER BEFORE | CLOSED |
| BREAKER AFTER | OPEN, crítico, novo incidente RPC_EFFECT_UNKNOWN |
| ACCOUNT AVAILABLE FOR NEW JOBS | NO, bloqueada pelo incidente atual |
| CAPABILITY | EXPERIMENTAL / PARTIAL; produção continua pausada |

JOB_ID: a87ba2d7f7f867c58a173b40d5d0755b42e3892ea69ab162cd44c890762c1212

Fingerprint do candidato atual: adec573b5bf52b7c47d88fe397cbadf7df8380740e8d876347accf96203f462c. Esse fingerprint pertence ao novo candidato, sem reconstruir a identidade ausente da publicação legada.

**Mídia, origem e evidências**

O vídeo veio do anúncio correspondente conforme confirmação explícita do operador. Essa informação foi registrada como proveniência da plataforma; ela não comprova licença comercial separada. RIGHTS permanece UNKNOWN e nenhuma licença foi inventada. O candidato da Escova 12 em 1 foi abandonado para esta validação.

Arquivo no Android: /storage/emulated/0/Download/br-11110105-6v65e-mh2586xh5clgf5.16000081763135246.mp4; MediaStore ID 410770. Duração 39,04 s, 720×1280, 25 fps, H.264/AAC, 3.912.003 bytes. FFprobe e decode completo passaram. A cópia local está em [gallery_410770.mp4](<C:/Users/GAMER/Documents/SHOPEE AUTOMATION/ai-commerce-content-factory/output/gallery_mousepad_review_20261007/media/gallery_410770.mp4>).

SHA-256: 3e53d8c43defcb1ed0731c206533ce7cd0db77084fd3e335ec99aa43cfd727c5. O hash local foi conferido novamente nesta auditoria e coincide com o registrado na seleção/ledger. A revisão anterior confrontou hash remoto/local, ordem e duração na biblioteca e preview visual. O vídeo mostra o mousepad preto; não há prova observável suficiente para afirmar 49×42.

Produto de origem: [anúncio Shopee](https://shopee.com.br/product/473616631/43050661409). A consulta oficial por shop/item retornou o título “Mousepad Gamer APEX Control Mouse pad Grande 49x42 Mouse Pad Branco Preto Blade Red Girl Titorion”. O tamanho mencionado no título não foi promovido a atributo verificado do vídeo. display_model_id 275052030708 no link fornecido permanece uma indicação, sem confirmação automática de variant_id.

Legenda preenchida, com 95/150 caracteres:

> Mousepad Titorion preto para o setup. Veja o produto vinculado. #Mousepad #SetupGamer #Titorion

As três hashtags são descritivas. Esta rodada não pesquisou buscas em alta nem verificou quantidades de usos dessas hashtags. Não há comprovação de popularidade para informar.

**O que funcionou no Android**

1. Conexão ao dispositivo R9QYA0227VX, SM-A075M, Android 16, Shopee 3.83.36.
2. Navegação para Eu e confirmação exata da conta borgesc542.
3. Abertura de Live e Vídeo, perfil de vídeos e entrada Postar vídeo.
4. Abertura da biblioteca, seleção da mídia 410770 e revisão de thumbnail/preview.
5. Chegada ao editor de publicação com Postar visível.
6. Preenchimento da legenda e hashtags.
7. Abertura de Adicionar produto, aba Todos e busca “Mousepad Gamer APEX”.
8. Identificação do segundo card com título exato e thumbnail compatível, distinguindo os anúncios similares.

O card nativo não expôs shop_id/item_id. Os IDs esperados vieram da confirmação do operador e da fonte oficial, e essa limitação está explicitamente registrada. A revisão do card foi APPROVED_UI_ONLY, sem virar aprovação de direitos ou autorização de publicação.

Evidências principais: [editor com Postar](<C:/Users/GAMER/Documents/SHOPEE AUTOMATION/ai-commerce-content-factory/output/assisted_mousepad_20261007/editor-after-transition.png>), [preview do vídeo](<C:/Users/GAMER/Documents/SHOPEE AUTOMATION/ai-commerce-content-factory/output/assisted_mousepad_20261007/mousepad-video-preview.png>), [busca do produto](<C:/Users/GAMER/Documents/SHOPEE AUTOMATION/ai-commerce-content-factory/output/assisted_mousepad_20261007/exact-product-search.png>) e [revisão do card](<C:/Users/GAMER/Documents/SHOPEE AUTOMATION/ai-commerce-content-factory/output/assisted_mousepad_20261007/native-card-review.json>). A captura do editor foi feita antes do preenchimento da legenda; o preenchimento posterior está registrado na sessão CAPTION_FILLED e nos logs.

**Onde parou e diagnóstico**

Houve uma tentativa controlada de clicar em Adicionar no card revisado. O RPC falhou após aproximadamente 10,6 segundos. O log de 11:35:59 no horário de São Paulo registra CLICK/product_card com status UNKNOWN. O sistema interrompeu o fluxo, manteve o job e as reservas de conta/dispositivo e abriu o breaker.

Não foi confirmado que o produto entrou no editor. A etapa Feito, o retorno ao editor com produto vinculado e os checks finais não foram concluídos. Não existe completion.json desta rodada.

A inspeção posterior read-only identificou incompatibilidade entre o XPath do XML bruto (/hierarchy/node[...]) e a transformação de tags usada pelo SDK uiautomator2. O XPath correspondia ao XML bruto, mas retornava zero correspondências pelo mecanismo do SDK. Isso sustenta o diagnóstico do seletor; a classe exata da exceção remota original não ficou persistida, portanto não é apresentada como comprovada.

O driver foi corrigido para resolver o caminho no XML bruto e usar o seletor nativo do botão Adicionar, restrito a package/classe/instância, com validação de texto e enabled. As proteções rejeitam Postar, pacote diferente e alvo alterado. A correção passou nos testes locais, mas não foi reexecutada no celular. Corrigir o driver não resolve retroativamente o UNKNOWN nem autoriza fechar o breaker.

Ocorreram dificuldades anteriores de runtime/timeout, nome da aba Eu e continuidade da conta ao entrar no editor. As preparações encerradas foram registradas com evidências e seus eventos preservados. As sessões de continuação pertencem ao mesmo JOB_ID central; não foi criado um segundo job equivalente.

**Implementação entregue**

- Proveniência explícita PRODUCT_LISTING_SOURCE e AI desconhecido representável como null.
- Validação assistida separada da validação final: rights UNKNOWN pode passar pela UI; direitos, IA, originalidade e revisão final ficam para o PublishGate. Rights REJECTED continua bloqueado.
- Binding de mídia/produto e evidência de origem vinculada ao hash continuam obrigatórios no modo assistido.
- Estado ASSISTED_VALIDATED no ledger, distinto da prontidão final, com conclusão condicionada aos checks reais da tela, conta, mídia e produto.
- ASSISTED_VALIDATED não concede autorização final e permanece no dedup. Uma nova avaliação do mesmo job sem tentativa exige novo preflight.
- Clique final exige LIVE_PUBLISH e PublishGate; os caminhos assistidos bloqueiam a ação final.
- Adaptação à aba Eu e ao texto nativo “Nome de usuário”, mantendo comparação exata da conta.
- Reconhecimento dos rótulos de comissão/vendidos sem perder o vínculo do botão ao card correto.
- Correção do seletor de Adicionar descrita acima.

Arquivos centrais: app/media/provenance.py, app/validation/product_media_truth.py, app/publishing/ledger.py, app/mobile/safety_runtime.py, app/mobile/ui.py e app/mobile/shopee_video.py. Regressões novas estão em [test_assisted_scope.py](<C:/Users/GAMER/Documents/SHOPEE AUTOMATION/ai-commerce-content-factory/tests/publishing/test_assisted_scope.py>).

O gate final real do candidato retorna FAIL por direitos, com variante, originalidade, disclosure de IA e HumanReview em REVIEW. A liberação da validação assistida não remove esses requisitos de publicação.

**Testes e integridade**

| Verificação | Resultado |
|---|---|
| Suíte de publicação antes da última correção do driver | 151/151 PASS, 216,517 s |
| Suíte específica depois da correção do driver | 30/30 PASS, 43,228 s |
| Suíte completa depois da última correção | Não reexecutada |
| SQLite integrity_check | ok |
| SQLite foreign_key_check | Sem violações |
| Job atual | UNKNOWN, attempted=0 |
| Autorizações finais | 0 antes e depois |
| Cobranças de posts/uploads nos counters | Nenhuma registrada |
| Jobs no banco auditado | Um legado e um candidato mousepad |
| Job e metadata legados versus backup | Idênticos |
| Hash da sessão original legada | Coincide com a evidência original |

As regressões cobrem rights UNKNOWN chegando a ASSISTED_VALIDATED em ambiente isolado, bloqueio de autorização final com UNKNOWN, rejeição de rights REJECTED, bloqueio do clique final assistido, preservação da proveniência, exigência de binding, falhas de evidência/hash, conta não comprovada, dedup/reentrada e seletor nativo.

A suíte usa testes locais/fakes; isso não comprova a conclusão ponta a ponta no Android. Resultados: [151 testes](<C:/Users/GAMER/Documents/SHOPEE AUTOMATION/ai-commerce-content-factory/output/assisted_mousepad_20261007/publishing-regressions-complete.txt>) e [30 testes após a correção](<C:/Users/GAMER/Documents/SHOPEE AUTOMATION/ai-commerce-content-factory/output/assisted_mousepad_20261007/driver-card-regressions.txt>).

O ledger registra 226 ações do worker, incluindo leituras, uma visualização de produto e uma consulta oficial Affiliate nesta rodada. Ausência de contador de upload/publicação não comprova ausência de tráfego ou preparação/upload interno de rascunho pelo aplicativo. O que se comprova é ausência de tentativa final registrada e de clique final.

A publicação histórica permanece PUBLISHED_LEGACY, post oOIfmsEhCgDfE7kkAAAAAA==, qualidade LEGACY_PARTIAL, product binding UNKNOWN e fingerprint NOT_AVAILABLE_LEGACY. Retry continua proibido e dedup permanente. O novo breaker OPEN decorre do incidente atual, e não desfaz a resolução legada. Campos antigos de recuperação legada permanecem no registro do breaker; não são um preflight válido para este incidente novo.

**Pendências concretas**

1. Revisar e resolver administrativamente o novo UNKNOWN com evidência suficiente sobre o efeito da ação, preservando o histórico. A rotina [resolve_preparation_unknown](<C:/Users/GAMER/Documents/SHOPEE AUTOMATION/ai-commerce-content-factory/app/publishing/ledger.py:178>) exige cancelamento humano explícito, reviewer, motivo, evidência e comprovação de ausência de publicação e upload. Esses campos não foram inventados nem enviados como verdade. Se a ausência de upload não puder ser demonstrada, essa rotina ainda não pode ser usada.
2. Após resolução válida, avaliar todos os incidentes e executar o preflight seguro do breaker. Não foi feita passagem para HALF_OPEN/CLOSED nesta rodada.
3. Com a conta liberada e evidências renovadas, confirmar o vínculo nativo do produto e retornar ao editor. A correção do seletor precisa de validação real.
4. Desativar o compartilhamento automático WhatsApp: estava selecionado na captura do editor. Nenhum compartilhamento externo foi executado.
5. Concluir os checks finais e registrar ASSISTED_VALIDATED, mantendo READY_FOR_PUBLISH=false e parando antes de Postar.
6. Uma eventual publicação futura ainda depende dos gates finais: direitos, IA/disclosure, variante, originalidade e revisão humana vinculada ao candidato.

Não houve nova delegação ao Antigravity nesta rodada. O notebook não foi desligado porque a validação não terminou e o usuário solicitou este relatório.

