# Single Story Rendering — Design Decisions

## SSR-D01 — Provider e renderer são separados

O provider nativo do Codex cria a base. `RealSingleStoryPipeline` ingere esse arquivo e o Pillow gera overlay/final. Google Flow não participa.

## SSR-D02 — Pillow é o engine tipográfico atual

Pillow oferece medição, fontes TrueType, alpha compositing e formas vetoriais com poucas dependências. HTML/browser adicionaria runtime e diferenças de captura desnecessárias para esta prova.

## SSR-D03 — Layout é dado rastreável

Safe zones, componentes, fonte, tamanho, linhas, bbox, overflow e contraste são persistidos em `layout.json`. O resultado pode ser reproduzido sem regenerar a foto.

## SSR-D04 — Auto-fit tem limite mínimo

O algoritmo reduz por passos e nunca ultrapassa número de linhas, largura ou altura. Abaixo do mínimo, lança `TEXT_LAYOUT_FAIL` e registra falha.

## SSR-D05 — QA semântico é explícito

Sem revisão visual, fidelidade, física, realismo e artefatos ficam `REVIEW`. O primeiro teste recebeu revisão visual registrada e foi promovido a `PASS`.

## SSR-D06 — Variação vem do StoryDirector

Componentes são reutilizáveis, mas o diretor escolhe layout e subconjunto por tipo de Story. Isso mantém consistência de marca sem congelar todas as peças no mesmo template.

## SSR-D07 — Correção preserva base aprovada

Erro tipográfico ou de posição rerenderiza overlay/final. Edição localizada vem antes de regeneração completa.
