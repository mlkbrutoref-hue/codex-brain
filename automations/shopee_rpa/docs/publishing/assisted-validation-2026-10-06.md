# Validação assistida Shopee Video — rodada solicitada em 06/10/2026

Checkpoint registrado em 07/10/2026, America/Sao_Paulo. Caminho/data da rodada preservados conforme pedido. **BLOCKED_AWAITING_OPERATOR**, antes da sessão assistida. Não declarar ASSISTED_VALIDATED.

Evidências: `output/assisted_validation_20261006/`. Fonte do pedido: attachment `9ca1991c-8f53-40b2-89c3-c128b538dfeb/Texto colado.txt`. O pedido de desligamento recebido durante a execução permanece pendente até a conclusão da validação; não foi executado durante este checkpoint bloqueado.

## Resultado operacional

| Campo | Resultado comprovado |
|---|---|
| OPERATIONAL STATUS | BLOCKED_AWAITING_OPERATOR; EXPERIMENTAL / PARTIAL |
| DEVICE | Único device elegível observado: R9QYA0227VX; ADB model SM_A075M, getprop SM-A075M; 720x1600; Android 16; com.shopee.br instalado, versão 3.83.36 |
| ACCOUNT | Esperada borgesc542; namespace local PASS. Conta Android atual NÃO verificada |
| CANDIDATE | prod_escova_12em1_58261505729_20260910_235725; configuração local, sem reserva de novo job |
| CONTENT GATES | FAIL: 4 PASS, 5 REVIEW, 2 FAIL; detalhes abaixo |
| MEDIA QA | PASS: FFprobe, hashes, decode completo de fonte e preparada; sem reencode |
| RIGHTS | UNKNOWN; geração interna declarada no manifest não comprova licença comercial/referências/áudio |
| ORIGINALITY | REVIEW; sem aprovação humana atual |
| AI DISCLOSURE | FAIL; ai_generated=true e ai_disclosure=false. Proposta de rótulo nativo aguardando revisão e verificação na UI |
| HUMAN REVIEW | Ausente; nenhuma aprovação antiga reutilizada |
| PRODUCT BINDING | IDs locais reais shop 1661007426 / item 58261505729; vínculo comercial na UI NÃO testado |
| VARIANT | variant_id ausente; atributo Preto derivado apenas do título, sem confirmação |
| DRY RUN | FINAL NÃO EXECUTADO: bloqueios prévios. Executado ContentValidator local real; não confundir com runtime final PASS |
| ANDROID DRY_RUN CONNECTIONS | ZERO; consultas ADB realizadas fora de qualquer DRY_RUN |
| ASSISTED MODE | NOT_STARTED; zero conexões uiautomator2 e zero mutações Android |
| MEDIA PICKER | NOT_TESTED; sem MediaSelectionEvidence nem seleção arbitrária |
| EDITOR | NOT_TESTED |
| PRODUCT SELECTION | NOT_TESTED |
| FINAL PREVIEW | NOT_TESTED |
| PUBLISH BUTTON REACHED | NO |
| PUBLISH BUTTON CLICKED | NO |
| PUBLISH PERFORMED | NO |
| PUBLISH ATTEMPT CREATED | NO; delta zero |
| UNKNOWN CREATED | NO; delta zero |
| BREAKER STATE | CLOSED antes e depois, sem alterações; kill switch false |
| TESTS | 122/122 de publicação nesta rodada, antes do ADB; 225.248 s. Nenhuma sessão assistida ocorreu, portanto não há suíte pós-sessão |
| BUGS FOUND | Artefato de entrada histórico contém mojibake; não é bug novo do runtime. Nenhum bug de implementação reproduzido nesta rodada |
| BUGS FIXED | 0 no runtime; candidato novo foi reconstruído com leitura UTF-8 da fonte canônica, sem modificar a evidência histórica |
| OPEN BLOCKERS | Foreground diferente; direitos não comprovados; variante e correspondência vídeo-produto; originalidade/copy; disclosure; HumanReview atual |
| NEXT STEP | Receber respostas agrupadas, confirmar foreground/conta em preflight novo, consolidar provas e fingerprint, obter HumanReview exata, executar DRY_RUN final e somente então ASSISTED_MODE |

## Baseline e parada de dispositivo

Documentos de segurança, aceitação, migração, configuração e Brain consultados. CLI de status, backup SQLite e inspeção de integridade confirmaram CLOSED, kill switch false, zero leases, zero authorizations, nenhum UNKNOWN/UPLOADING/PUBLISHING pendente. O único job continua PUBLISHED_LEGACY. Baseline em `baseline-check.json`, `baseline.sqlite3`, `ledger-before.json` e `operational-status-before.json`.

Após 122 testes aprovados, consultas ADB somente leitura confirmaram conexão/serial, modelo, resolução, Android e package/version. `mCurrentFocus` e `mFocusedApp` apontaram **com.sec.android.app.launcher**. A inspeção foi interrompida conforme a instrução PACKAGE DIFERENTE. Nenhum app foi aberto, nenhum tap executado e uiautomator2 não foi iniciado. Tela awake foi observada; desbloqueio completo, conta, login/challenge/restrições na Shopee continuam não verificados. Evidência minimizada: `device-adb-preflight.json`.

## Candidato real e mídia

| Campo | Valor |
|---|---|
| CANDIDATE | prod_escova_12em1_58261505729_20260910_235725 |
| ASSET | prod_escova_12em1_58261505729_20260910_235725:master |
| SOURCE MEDIA | output/prod_escova_12em1_58261505729_20260910_235725/generated/take_01.mp4 |
| PREPARED MEDIA | output/prod_escova_12em1_58261505729_20260910_235725/platforms/shopee.mp4 |
| SHOP_ID / ITEM_ID | 1661007426 / 58261505729 |
| VARIANT_ID | null; não fabricado |
| PRODUCT TITLE | Escova de Limpeza Elétrica Portátil 12 em 1 com Cabo Epsilon Preto |
| CAPTION proposta | Escova de Limpeza Elétrica Portátil 12 em 1 com Cabo Epsilon Preto |
| HASHTAGS existentes | #achadinhos #shopeebrasil #escovaeletrica |
| AI GENERATED | true, conforme manifest existente do Flow |
| RIGHTS STATUS | UNKNOWN |
| DEDUP STATUS | PASS_NOT_DUPLICATE, antes e depois pelo JobLedger real |
| CURRENT FINGERPRINT | 76e13dc046ad8328f263587bf8719a40b5e85e496e65c7200c4b06544b9ae5e3 |

Produto: https://shopee.com.br/product/1661007426/58261505729. IDs e título vêm do cache local real; disponibilidade/preço/variante atuais do anúncio não foram verificados. A versão anterior da entrada de aceitação tinha texto mojibake. O candidato novo usa UTF-8 e conserva a evidência anterior intacta. A copy longa original excedia o limite observado no teste histórico; o título com as três hashtags é uma proposta que ainda exige revisão. Nenhuma copy foi enviada ao celular.

Fonte: 720x1280, 24 fps, 8 s, H.264/AAC, 3.070.512 bytes; SHA-256 `7d2ee879ec6ca62905fc1be7cc8ee6e14f25c11593c5616179747975414b9675`.

Preparada: 1080x1920, 30 fps, 8 s, H.264/AAC, 5.197.137 bytes; SHA-256 `e998aba453baa92930d1f7dab5a1cc56d8affb5b5dd2ba35f74f59edb524895e`. FFprobe e decode completo passaram para ambos, sem regeneração/reencode. Fonte e preparada continuam com os mesmos hashes. Evidência em `media-qa.json`.

## ContentValidator e revisão

| Check real | Status | Limite da evidência |
|---|---|---|
| account | PASS | Apenas identificação local; não comprova conta da UI |
| product_identity | PASS | IDs válidos persistidos; não comprova card comercial atual |
| variant_match | REVIEW | Cor no título sem variant_id ou evidência aprovada |
| media_product_match | REVIEW | Sem revisão específica do SKU/variante |
| caption_relevance | REVIEW | Revisão editorial pendente |
| media_uniqueness | PASS | JobLedger não encontrou duplicata |
| media_quality | PASS | QA vinculada ao hash preparado |
| rights | FAIL | Rights UNKNOWN e licença ausente |
| originality | REVIEW | Sem aprovação atual |
| ai_disclosure | FAIL | Disclosure ainda false |
| human_review | REVIEW | Nenhuma aprovação vinculada ao fingerprint atual |

`candidate-summary.json` e `content-validation.json` registram resultados do ContentValidator real. Logs pelo OperationLogger preservam somente categorias/check/status e contexto técnico; nenhuma hierarquia ou screenshot Android foi capturada.

Frames de 0,5 / 3,5 / 7,0 s foram extraídos e inspecionados. A revisão usou as duas referências canônicas da Nina, regras de proporção e a skill visual-qa. Cada frame tem SHA-256 e os hashes das duas referências em `visual-review.json`, com os sete checks anatômicos. Nina ausente no primeiro frame: checks não aplicáveis. Nos dois frames de tronco/rosto, a visão parcial não permite aprovação completa de anatomia/proporções: REVIEW, sem inventar defeito ou nota numérica.

A ferramenta mostrada tem corpo branco/preto e cabo preto; isso não identifica sozinho a variante esperada. Nenhuma imagem oficial do produto foi inspecionada nesta rodada; correspondência segue REVIEW. Há sinais/acentos soltos no lettering gerado que exigem revisão do clipe inteiro. O QA histórico genérico permaneceu intacto e não foi convertido em aprovação atual.

Proposta de disclosure: ativar o rótulo nativo de conteúdo gerado por IA, se disponível e comprovado na UI, preservando a caption proposta. Nada foi ativado; nenhuma aprovação ou licença foi inferida. Mudanças de variante, provenance, copy ou disclosure exigem recalcular fingerprint antes da HumanReview final. O campo HumanReview não será preenchido com uma aprovação genérica deste checkpoint.

## Verificação de integridade e retomada

`finalize_blocked_review.py` é um verificador local desta rodada, sem conexão Android ou escrita no ledger. Comparou **todas as tabelas** da cópia de baseline com o banco real em conexão SQLite mode=ro: nenhuma diferença; integrity_check=ok. Também verificou hashes dos arquivos operacionais originais, da sessão/mídia legada e das duas mídias do candidato: todos preservados. O JobLedger real confirmou dedup do candidato inalterado. Resultados em `ledger-after.json` e `verification.json`.

Zero novos jobs, publish attempts, PUBLISHED, UNKNOWN, tokens ou leases. Registro legado, metadata, attempted, evidência, breaker, counters e eventos permaneceram iguais ao baseline. A suíte geral 250/250 é evidência **da rodada anterior de migração**, não resultado novo desta rodada. Nenhuma correção de runtime exigiu regressão adicional; não foram repetidos testes após uma sessão que não aconteceu.

Perguntas agrupadas enviadas ao operador:

1. Abrir manualmente a Shopee na conta borgesc542 e avisar quando estiver pronta; nova inspeção será necessária.
2. Informar produtor e licença/termos para uso comercial do vídeo, referências e áudio, com referência documental verificável.
3. Confirmar variante exata do anúncio, com ID se existir ou atributos observáveis comprovados. Título sozinho é insuficiente.
4. Revisar o clipe inteiro, correspondência com o produto, originalidade, textos sobrepostos, caption e hashtags propostas.
5. Aprovar ou ajustar disclosure de IA; depois registrar provas, recalcular fingerprint e obter HumanReview exata.

Após as respostas, os gates operacionais de autorização aplicável, versão permitida, identidade de conta, mídia e produto também continuam obrigatórios. Este relatório não cria autorização final, não habilita LIVE_PUBLISH e não remove nenhum controle. O próximo estágio permitido permanece condicionado a todas as evidências e gates exigidos.
