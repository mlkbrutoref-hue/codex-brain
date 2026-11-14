# CreativePackage schema

## Entrada mínima

```json
{
  "product": "nome do produto",
  "confirmed_facts": {"fact_key": "valor confirmado"},
  "platform": "Instagram Reels",
  "content_goal": "objetivo principal"
}
```

Não converta campos ausentes em fatos. Registre-os em `unknown_facts`.

## Campos obrigatórios de saída

```text
product
product_provider
product_score
reliability_status
decision
recommend_reel
profile_coherence_status
visual_proof_basis
flow_prompt_ready
research_required
selected_format
format_reasoning
video_duration_target
flow_take_duration_target
scene_count
multi_take_justification
hook_type
hook
script_structure
script_word_count
final_script
scene_plan
on_screen_text_start
on_screen_text_end
cta
caption
hashtags
cover_concept
flow_prompt
negative_prompt
confirmed_facts
facts_used
fact_ledger
unknown_facts
fact_safety
nina_safety
posts_manual
carousels_manual
reels_creative_skill_ready
reels_pipeline_integrated
flow_integrated_with_skill
flow_generations
```

## Score

Cada componente contém `score`, `max` e `reason`. Chaves: `visual_proof`, `problem_clarity`, `curiosity`, `audience_breadth`, `compressibility`, `originality` e `reliability`. Inclua `total`.

## Scene plan

Cada cena contém `scene`, `timing`, `narrative_role`, `action`, `framing`, `environment_light`, `audio_speech`, `flow_prompt` e `fact_keys`.

## Cover concept

Use `cover_title`, `cover_subtitle`, `product_position` e `nina_position`.

## Fact ledger

Cada item contém `claim`, `source_key` e `used_in`. `source_key` precisa existir em `confirmed_facts`.

## Regras de consistência

- Os máximos do score são fixos e totalizam 100.
- `facts_used` e `scene_plan[].fact_keys` devem existir em `confirmed_facts`.
- `video_duration_target` aceita `30–45 s`, `45–60 s` ou `60–90 s`.
- `flow_take_duration_target` fica entre 5 e 10 segundos.
- `scene_count` deve ser igual ao número de cenas e respeitar a faixa: 4–6, 6–8 ou 8–12 takes, respectivamente.
- Todo pacote exige justificativa da decomposição em múltiplos takes.
- `script_structure` contém pelo menos cinco beats e demonstra começo, meio e fim.
- `script_word_count` deve coincidir com `final_script` e ser compatível com fala natural: 65–120, 95–160 ou 130–230 palavras, respectivamente.
- Total abaixo de 70 ou confiabilidade falha impede recomendação.
- `decision` aceita `RECOMMEND_REEL`, `RESEARCH_REQUIRED` ou `REJECT`.
- `recommend_reel = true` exige `profile_coherence_status = PASS` e `flow_prompt_ready = true`.
- `visual_proof_basis` aceita `CONFIRMED_OPERATION`, `CONFIRMED_RESULT`, `APPEARANCE_LED_REVEAL` ou `NONE`.
- Produto funcional sem operação ou resultado confirmado usa `visual_proof_basis = NONE`, `decision = RESEARCH_REQUIRED` e não pode ser recomendado.
- `flow_prompt_ready = false` permite `flow_prompt` vazio e exige listar a lacuna em `research_required`.
- O prompt do Flow não pode delegar verificação factual ao gerador nem conter instruções condicionais sobre fatos desconhecidos.
- `reliability` mede procedência, atualidade e cobertura da evidência. Fixture não pode receber mais de 5; uma única resposta LIVE não pode receber mais de 8.
- A saída não contém formatos de post ou carrossel.
- `reels_automated` não é permitido antes da integração autorizada com o Flow.
- `reels_creative_skill_ready` é verdadeiro; `reels_pipeline_integrated` registra o estado real da integração.
- `flow_integrated_with_skill` permanece falso nesta etapa.
- `flow_generations` continua zero até autorização separada.
