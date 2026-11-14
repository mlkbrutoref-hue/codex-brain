# Gerador de Story Único

`NINA_SINGLE_STORY_GENERATOR` cria o pacote criativo de **uma peça estática, vertical 9:16 e independente**. Ele não cria carrossel, sequência narrativa, storyboard, vídeo, publicação ou geração no Flow.

## Entrada

Arquivo JSON com:

- `product_name` e `confirmed_facts` obrigatórios;
- `product_reference_paths` para liberar o prompt final;
- `story_type=AUTO` ou override;
- contexto opcional: categoria, objetivo, Nina, paleta, evidências visuais, sinais de tendência e notas de referências externas;
- CTA opcional, sem urgência ou escassez inventada.

Tipos aceitos:

- `PRODUCT_HIGHLIGHT`
- `BENEFIT`
- `USE_LIFESTYLE`
- `AESTHETIC_EMOTIONAL`
- `LIGHT_CTA`

## Saída

O `SingleStoryCreativePackage` inclui conceito, cena, composição, papel do produto, hierarquia, copies, elementos, mood, cor, realismo, negative prompt, prompt final, variantes, legenda, hashtags, rationale e blockers.

`final_image_prompt_ready=true` significa que o pacote passou pelo validador e possui referência do produto. Isso não significa que uma imagem foi gerada ou aprovada em QA.

## Execução isolada

```powershell
python scripts/generate_single_story.py `
  --input data/examples/single_story_request.json `
  --output output/single_story_dry_run/creative_package.json
```

O comando não usa API, não abre navegador e não consome créditos.

O código também oferece `SingleStoryGenerator.generate_from_product(product, facts)`, uma ponte direta para os contratos `Product` e `ProductFacts` já existentes, sem acoplar o módulo ao lifecycle de vídeo.

## Regras de segurança

- Supporting e benefit text vêm literalmente dos fatos confirmados.
- O prompt final fica bloqueado sem referência oficial do produto.
- Nina usa as referências canônicas de rosto e 360 juntas.
- A peça mantém `artifact_count=1`, `standalone=true` e nenhuma posição de sequência.
- Texto exato deve ser composto depois quando o gerador visual não renderizar português corretamente.

## Pesquisa e limites

O design e as fontes estão em `brain/research/single-story-creative/`. A seleção automática é uma heurística explicável de adequação criativa; ainda precisa de benchmark e resultados reais para qualquer afirmação de performance.

A continuação que gera a imagem real, compõe tipografia e executa QA está documentada em [`real-single-story-pipeline.md`](real-single-story-pipeline.md).
