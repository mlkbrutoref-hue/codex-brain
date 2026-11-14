# Mobile Publisher assistido

Status: **PARTIAL / EXPERIMENTAL**, operação de interface **MANUAL**. Conexão do Phone Link e teste no aparelho adiados pelo usuário para amanhã. Nenhuma publicação ou instalação foi feita.

## Uso local

Na raiz do repositório, com Python 3.11+:

```powershell
python -m app.publishing discover --out output/mobile_publisher/discovery.json
python -m app.publishing prepare --manifest output/e2e_full_content_factory_20260928_0955/manifests/product_stories_manifest.json --brief docs/publishing/example_brief.json --out output/mobile_publisher/session.json
python -m app.publishing inspect --session output/mobile_publisher/session.json
python -m unittest discover -s tests/publishing -v
```

O exemplo usa uma conta explicitamente fictícia e não define horário de postagem. Antes do teste real, preencher conta correta, copy/CTA/disclosure aprovados e horário ISO com offset; criar NOVA sessão. Não editar o JSON de uma sessão preparada, pois isso invalida sua revisão.

Somente `product_story_02` é selecionado no exemplo: tem QA PASS e não contém a personagem. O carrossel completo e o Story 01 permanecem bloqueados pelos respectivos REVIEW. Nenhum QA de origem foi alterado.

## Retomada no celular

1. Usuário instala/configura Phone Link e conecta o aparelho. A conexão, permissões de espelhamento e logins são manuais; não trocar contas.
2. Repetir discovery e observar Apps/Phone screen, sem inferir suporte pela instalação. Confirmar aparelho disponível e abrir Instagram/TikTok somente para verificar acesso e conta.
3. Preparar sessão com conta, mídia, copy, CTA, disclosure e horário reais. Transferência ao aparelho ainda é manual e precisa preservar arquivo/ordem; o runtime não transfere mídia.
4. Operador realiza cada etapa e registra observação por `advance`. A interface do runtime não clica nem verifica pixels automaticamente.
5. Inspecionar a prévia real e registrar os nove checks por `review`. Ausência, erro, REVIEW ou UNKNOWN bloqueia.
6. Avançar para `STOP_BEFORE_FINAL_PUBLISH` e encerrar. **Nunca tocar em Publicar/Compartilhar/Seu story/Enviar.**

`advance --session <json> --evidence <json>` recebe:

```json
{"target":"TIME_RECOMMENDATION","evidence":"Sem histórico; horário escolhido pelo operador com motivo registrado.","observed":{}}
```

Próximos estados exigem observações específicas:

| target | observed |
|---|---|
| OPEN_PHONE_LINK | phone_link_found, phone_connected, apps_available: true após observação |
| OPEN_TARGET_APP | platform e account exatos da sessão |
| SELECT_CONTENT | media_sha256: lista completa dos hashes na ordem selecionada |
| PREPARE_POST | caption, cta, disclosure exatos, incluindo strings vazias quando N/A justificado |
| PRE_PUBLISH_QA | evidência da prévia real |
| STOP_BEFORE_FINAL_PUBLISH | nove checks atuais PASS e horário explícito |

`review --session <json> --evidence <checks.json>` recebe um objeto com **todos** os nomes: CORRECT_ACCOUNT, CORRECT_PLATFORM, CORRECT_MEDIA, CORRECT_ORDER, CORRECT_CAPTION, CORRECT_CTA, CORRECT_DISCLOSURE, CORRECT_TIME, PREVIEW_OK. Cada valor: `{"status":"PASS|REVIEW|FAIL|UNKNOWN","evidence":"observação concreta / referência da captura"}`. Não preencher PASS por ter seguido o roteiro: precisa observar o resultado.

O hash da sessão inclui mídia, ordem, fonte/QA, plataforma, conta, copy e horário. Arquivo, QA, manifest ou payload alterado invalida a sessão. Persistência local atômica; sem banco de posts nem telemetria de publicação fictícia.

## Analytics

A porta `TimeAdvisor` aceita um objeto com `recommend_publish_time(**context)` e envia platform/content_type/category. O contrato concreto do Antigravity ainda precisa ser entregue/revisado; um adapter posterior poderá acrescentar data/timezone e converter o resultado. Falha/ausência preserva `recommended_time=null`, `INSUFFICIENT_DATA`, `samples=0` e explicação.

Recomendação não agenda nem altera o horário escolhido. `record_publication` e `record_metrics` não são chamados nesta v1, porque nenhuma publicação real é executada ou confirmada. Não há merge automático do worktree do Antigravity.

Pesquisa e contrato: [DESIGN.md](DESIGN.md). Evidência reproduzível local: `output/mobile_publisher/local_validation.json`. O fixture de testes não equivale à validação visual no aplicativo.
