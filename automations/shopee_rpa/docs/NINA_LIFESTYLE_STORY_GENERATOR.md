# NINA_LIFESTYLE_STORY_GENERATOR

Gerador isolado para um único Story 9:16 de conexão, rotina ou lifestyle da Nina. Não reutiliza o contrato de produto, carrossel ou vídeo e não transforma cenas cotidianas em anúncios.

## Entradas

- `time_of_day`: `MORNING`, `AFTERNOON` ou `NIGHT`;
- `category`, `story_type` e `text_mode`: `AUTO` ou override compatível;
- `reference_sources`: URLs ou referências fornecidas pelo usuário;
- `reference_notes`: princípios de pose, câmera, luz, ambiente e mood a adaptar;
- `optional_text`: texto curto, apenas quando `LIGHT_TEXT`;
- `product_context`: opcional para Story híbrido ou de produto.

## Identidade

Todo plano declara obrigatoriamente:

- `data/personas/nina_v1/references/persona_master.png` para o rosto;
- `data/personas/nina_v1/references/nina_360_master.png` para corpo, cabelo, ângulos e detalhes físicos.

Referências externas orientam pose, enquadramento, luz, ambiente e comportamento. A pessoa original nunca deve ser copiada.

## Variação e coerência

As bibliotecas de manhã, tarde e noite definem cenas plausíveis para cada período. `data/lifestyle_story/history.json` registra assinatura, categoria, pose, ambiente, roupa, ângulo, mood e texto de cada saída aprovada. O seletor escolhe a assinatura compatível menos usada.

Para um mesmo `day_id`, o operador deve manter ordem temporal `MORNING -> AFTERNOON -> NIGHT`. A biblioteca evita que o tipo `PRODUCT` ou `HYBRID` seja selecionado automaticamente.

## Texto

`NO_TEXT` preserva a fotografia sem overlay. `LIGHT_TEXT` permite uma frase curta e natural, composta localmente com Pillow. O modelo de imagem recebe instrução explícita para não gerar letras.

## Execução

```powershell
python scripts/generate_lifestyle_story.py --input request.json --output creative_plan.json
python scripts/render_lifestyle_story.py --plan creative_plan.json --generated-image generated.png --output-dir output/lifestyle_story --semantic-review semantic_review.json --history data/lifestyle_story/history.json
```

O provider built-in de imagens do Codex gera a fotografia-base. O runtime local normaliza para 1080x1920, aplica o texto opcional, executa QA e grava manifestos. Google Flow não participa desse fluxo.

## QA

O resultado final só recebe `PASS` após revisão explícita de identidade, rosto, cabelo, corpo, mãos, física do celular, iluminação, realismo, artefatos, horário, coerência da cena, espontaneidade, adaptação da referência e anti-monotonia.

## Proporções e recuperação

A versão 1.2 usa a política compartilhada documentada em `docs/nina-proportion-correction.md`. Os sete gates anatômicos exigem revisão vinculada por hash à imagem final e às duas referências. Recortes acima de 5% são bloqueados. Defeitos geram `anatomy_recovery.json`; a execução ocorre pelo agente Codex ou por callbacks de geração/revisão, com uma tentativa e reavaliação obrigatória.
