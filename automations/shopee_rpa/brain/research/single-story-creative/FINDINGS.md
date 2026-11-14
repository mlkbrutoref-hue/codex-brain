# Single Story Creative — Findings

## 1. A unidade correta é uma peça independente

O pedido define uma imagem vertical autossuficiente. A peça não herda posição, cliffhanger, continuidade ou dependência de outra tela. O contrato registra `artifact_count=1`, `standalone=true` e `sequence_position=null`.

## 2. O produto precisa de uma referência oficial

Descrição textual não preserva embalagem, geometria, escala, material ou rótulo. O módulo pode montar direção e copy sem imagem, mas mantém `final_image_prompt_ready=false` até receber ao menos uma referência do produto.

## 3. A copy objetiva vem dos fatos confirmados

Headline pode enquadrar curiosidade sem alegação objetiva. Supporting e benefit text são copiados literalmente de `confirmed_facts`. Isso cria uma fronteira verificável entre linguagem criativa e claim comercial.

## 4. Tipos criativos são funções, não templates fixos

- `PRODUCT_HIGHLIGHT`: reconhecimento e descoberta.
- `BENEFIT`: torna um benefício confirmado legível.
- `USE_LIFESTYLE`: mostra uma ação sustentada por evidência visual.
- `AESTHETIC_EMOTIONAL`: valoriza forma, material, cor e atmosfera.
- `LIGHT_CTA`: prioriza uma ação discreta e factual.

A seleção automática é heurística de adequação, não previsão de alcance ou conversão. Override explícito sempre vence.

## 5. Tendência útil vira princípio abstrato

O sinal de 2026 favorece realidade, utilidade e justificativa de compra. O gerador aplica esses princípios a produto e marca. Referências externas entram como notas de estilo abstratas; composição, texto e assinatura alheios não são copiados.

## 6. Texto e imagem precisam de estratégias separáveis

O prompt especifica o texto exato, mas o pacote alerta que geradores visuais podem errar grafia. A saída pode orientar uma geração completa ou uma geração de base visual seguida de composição tipográfica determinística.

## 7. Realismo é verificável

Os checks principais são fidelidade do produto, material, rótulo, escala, luz, sombra, reflexo, textura, anatomia e identidade da Nina. “Fotorealista” isoladamente não cobre essas dimensões.

## Gate

**GATE RESULT:** `PASS / DESIGN_RESEARCHED` para o pacote criativo provider-independent.  
**IMPLEMENTATION RESULT:** `READY` para geração local do pacote e prompt.  
**MEDIA GENERATION:** continua `MANUAL / OUT_OF_SCOPE` deste módulo.
