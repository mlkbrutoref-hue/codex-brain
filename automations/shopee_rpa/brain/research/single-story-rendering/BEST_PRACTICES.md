# Single Story Rendering — Best Practices

1. Gerar a base sem texto promocional e com safe zones explícitas no prompt.
2. Preservar referência oficial, geometria, cor, material, escala e rótulo do produto.
3. Normalizar a base para 1080x1920 antes de compor.
4. Renderizar texto em overlay RGBA independente.
5. Medir cada linha com fonte TrueType real.
6. Quebrar por palavras e respeitar limites de linhas, largura, altura e fonte mínima.
7. Falhar com `TEXT_LAYOUT_FAIL` quando a copy não couber.
8. Exigir contraste de projeto de 4.5:1 para cada texto.
9. Usar caixas e backdrops apenas quando necessários.
10. Registrar safe zones, bounds, fontes, tamanhos e contraste em `layout.json`.
11. Manter QA técnico e revisão semântica separados e rastreáveis.
12. Corrigir primeiro overlay/layout; preservar a base quando ela estiver aprovada.
13. Salvar hashes e origem dos assets no manifest.
