# Biblioteca visual da Nina

- `library.json`: 16 referências inspecionadas, sendo 10 exemplos prioritários do usuário e 6 imagens do Pinterest. Inclui fontes, categorias reutilizáveis, direção, limitações e SHA-256.
- `style_dna.json`: oito dimensões de estilo extraídas dos exemplos do usuário.
- `user/carousel/`: dois exemplos originais de feed preservados. Os demais exemplos são registrados nos caminhos canônicos já existentes.
- `pinterest/beauty/`: espelho, penteadeira e bancada GRWM, indexados também para capa, CTA e cenas de produto.
- `pinterest/morning/`, `afternoon/`, `night/`: referências específicas de rotina.

Selecionadas para direção fotográfica após inspeção dos pixels. Pinterest não autentica autoria, câmera ou ausência de IA. As referências de manhã/tarde são previews stock com watermark preservado; a da noite é diurna e requer adaptação explícita da luz e da câmera conforme exemplos prioritários. Não publicar estas imagens como criações da Nina.

O mapa da campanha atual fica em `output/e2e_content_factory_test_20260927_1505/campaign/reference_map.json`. Consulte `docs/visual-reference-workflow.md` antes de qualquer nova geração. O checkpoint atual está pausado para conferência do usuário.
