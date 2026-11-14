# Pipeline de Story Final

O `NINA_REAL_SINGLE_STORY_PIPELINE` transforma um `creative_package.json` aprovado e uma imagem gerada pelo provider nativo do Codex em um Story estático pronto para revisão/publicação.

```text
single_story_request
  -> creative_package
  -> Codex built-in imagegen
  -> base_image.png
  -> StoryDirector + Pillow renderer
  -> text_overlay.png + story_final.png
  -> QA técnico + revisão visual
  -> manifest.json
```

Google Flow não participa deste pipeline.

## Execução local

O runtime precisa de Pillow. No Codex desktop, use o Python informado por `load_workspace_dependencies`; em outro ambiente, instale `requirements-dev.txt`.

```powershell
python scripts/render_single_story.py `
  --creative-package output/single_story_dry_run/creative_package.json `
  --generated-image caminho/da/imagem-gerada.png `
  --output-dir output/single_story_real_test `
  --prompt data/examples/single_story_base_prompt.txt
```

Sem revisão semântica, o resultado correto é `REVIEW`. Depois da inspeção:

```powershell
python scripts/render_single_story.py `
  --output-dir output/single_story_real_test `
  --semantic-review output/single_story_real_test/manual_visual_review.json `
  --refresh-qa
```

## Saídas

- `base_image.png`: fotografia normalizada para 1080x1920;
- `text_overlay.png`: camada RGBA determinística;
- `story_final.png`: composição final;
- `creative_package.json`: copy e direção de origem;
- `layout.json`: safe zones, fontes, linhas, bounds e contraste;
- `qa.json`: checks técnicos e semânticos;
- `manifest.json`: status, provider, hashes e arquivos;
- `asset_manifest.json`: referências, fonte gerada e fontes tipográficas;
- `prompt.txt`: prompt realmente usado para a base.

## Correção seletiva

Texto, posição, tamanho ou cor exigem apenas novo overlay/final. Problema visual localizado deve usar edição localizada quando possível. Regeneração completa da base é o último recurso.
