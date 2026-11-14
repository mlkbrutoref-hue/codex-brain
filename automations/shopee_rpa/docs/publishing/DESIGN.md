# Mobile Publisher v1 — EXPERIMENTAL / ASSISTED_MODE

## Pesquisa e decisões anteriores ao protótipo

OBSERVED: o runtime atual usa dataclasses, JSON e unittest. A campanha `e2e_full_content_factory_20260928_0955` contém manifests com assets ordenados, hashes, caminho de QA e status PASS/REVIEW. REVIEW não equivale a mídia pronta. Não existe publicação mobile integrada.

DOCUMENTED: Phone Link oferece Apps/Phone screen somente em aparelhos compatíveis; ter o aplicativo instalado não comprova conexão nem espelhamento. Fontes oficiais consultadas em 28/09/2026:
- https://support.microsoft.com/en-us/windows/apps/phonelink/phone-link-requirements-and-setup
- https://support.microsoft.com/en-us/windows/apps/phonelink/supported-devices-for-phone-link-experiences
- https://support.microsoft.com/en-us/windows/apps/phonelink/setting-up-apps-in-the-phone-link

OBSERVED: neste usuário Windows, consulta via Windows PowerShell 5.1 retornou zero pacotes Microsoft.YourPhone; inventário Computer Use também não encontrou Phone Link. PowerShell 7 não carrega Appx neste host, portanto erro de módulo não deve ser interpretado como ausência. Conexão, Apps, Instagram e TikTok: UNKNOWN/NOT_TESTED.

## Contrato e limites

Protótipo EXPERIMENTAL, implementação PARTIAL; operação de interface MANUAL. Não há promessa de automação validada. A ausência do Phone Link bloqueia a prova real de preparação no celular. Nenhuma instalação, login, alteração de conta, geração de conteúdo ou publicação nesta etapa.

Importador consome manifests existentes sem alterá-los. Seleção explícita de um Story é permitida; carrossel preserva conjunto e ordem completos. Media hash, status do QA e hash do relatório de QA são congelados e revalidados. Copy, conta, plataforma e horário fazem parte do fingerprint. Qualquer edição exige nova sessão/revisão.

Fluxo: CONTENT_READY -> TIME_RECOMMENDATION -> OPEN_PHONE_LINK -> OPEN_TARGET_APP -> SELECT_CONTENT -> PREPARE_POST -> PRE_PUBLISH_QA -> STOP_BEFORE_FINAL_PUBLISH. Estados refletem evidência do operador, nunca cliques simulados. Sem adapter de UI integrado: runtime grava roteiro operacional e só avança mediante observações explícitas. Estado final é uma parada obrigatória; não existe função de publicar nem registro automático de rascunho no analytics.

QA exige os nove checks do usuário, todos PASS, com evidência e fingerprint da sessão: CORRECT_ACCOUNT, CORRECT_PLATFORM, CORRECT_MEDIA, CORRECT_ORDER, CORRECT_CAPTION, CORRECT_CTA, CORRECT_DISCLOSURE, CORRECT_TIME, PREVIEW_OK. Ausente/REVIEW/FAIL bloqueia. Todos começam UNKNOWN. PASS de produção não substitui QA da prévia do app.

Analytics: porta injetável `recommend_publish_time(**context)`; ausência/falha gera recommended_time=null, INSUFFICIENT_DATA e motivo. Não há horário campeão fabricado. A integração concreta e record_publication dependem da entrega revisada do Antigravity e de publicação real futura confirmada; não estão habilitados nesta etapa.

## Critérios de teste

Rejeitar QA pendente, arquivo/hash divergente, seleção parcial de carrossel, ordem errada, timestamp sem timezone, salto de estados, evidência vazia, checklist incompleto, revisão antiga e tentativa de publicar. Verificar persistência/reabertura, mídia real existente, recomendação ausente e disponibilidade mobile desconhecida.
