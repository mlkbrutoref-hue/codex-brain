# Integração com Google Flow

> **OUTDATED:** preservado como desenho histórico da integração. Google Flow é um provider opcional e atualmente manual; o estado canônico está em [`../brain/CHIA.md`](../brain/CHIA.md) e [`../brain/CURRENT_STATE.md`](../brain/CURRENT_STATE.md).

## Arquitetura preparada

```text
PipelineOrchestrator
  -> VisualGenerationProvider
       -> ManualFlowProvider
       -> AntigravityFlowProvider (desabilitado por padrão)
  -> output/<job_id>/generated/
  -> VisualQAResult
  -> FFmpegAssembler
```

O sistema não presume uma API pública do Google Flow. A futura operação automatizada é modelada como navegador controlado pelo Antigravity, mas continua sem comprovação live nesta retomada.

## Contrato de operação

Cada `SceneGenerationRequest` inclui:

- referência canônica da Nina: `data/personas/nina_v1/references/persona_master.png`;
- primeira imagem oficial disponível do produto na Shopee;
- prompt da cena;
- caminho esperado do take;
- `generation_authorized=False` por padrão.

`prepare_generation(job_id)` grava `flow_operation.json` e avança o job de `PROMPTS_READY` para `WAITING_FOR_GENERATION`. Essa ação não abre o Flow e não gera mídia. `record_generation_started(..., operator_confirmation=True)` apenas registra uma geração iniciada externamente; não clica em Generate.

## ManualFlowProvider

Permanece o fallback operacional. Ele cria `prompts/scene_XX.txt`, `prompts/INSTRUCTIONS_FLOW.md` e a pasta `generated/`. O operador deposita `take_XX.mp4` ou imagens equivalentes. Quando todas as cenas têm arquivos não vazios, `refresh_media_status()` pode avançar o job para `MEDIA_READY`.

## AntigravityFlowProvider

Está preparado para a cadeia Python -> Antigravity -> Browser Agent -> Google Flow. Enquanto a cota não estiver disponível, retorna `REVIEW_REQUIRED` com `BLOCKED_BY_ANTIGRAVITY_QUOTA`. Mesmo com cota, rejeita cenas sem autorização explícita.

Uma execução futura deve inspecionar a UI real, usar apenas a sessão autenticada aprovada, nunca extrair cookies e devolver um resultado estruturado com estados `READY`, `LOGIN_REQUIRED`, `GENERATING`, `SUCCESS`, `FAILED` ou `REVIEW_REQUIRED`.

## Limites atuais

- `FLOW_GENERATIONS=0`.
- Nenhum clique Generate foi realizado.
- Visual QA está implementado, mas ainda não foi exercitado sobre mídia real.
- O binário FFmpeg não está disponível no `PATH`; somente o builder e testes mock foram validados.
