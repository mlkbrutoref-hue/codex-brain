# Single Story Creative — Fontes

**RESEARCH_DATE:** 25/09/2026  
**Escopo:** peça estática vertical 9:16, independente, orientada a produto, com copy curta, legibilidade, realismo e segurança factual.  
**Estabilidade:** composição e legibilidade `STABLE`; linguagem de plataforma `FAST_CHANGING`.

## Fontes internas

### S-INT-01 — Missão, arquitetura e segurança factual

- **Arquivos:** `brain/MISSION.md`, `brain/ARCHITECTURE.md`, `brain/CHIA.md`.
- **Autoridade:** canônica para o projeto.
- **Descoberta:** originalidade, rastreabilidade, fidelidade à Nina e fatos confirmados têm precedência sobre pressão comercial.
- **Decisão:** o gerador aceita fatos confirmados, preserva sua redação na copy de apoio e bloqueia prompt final sem referência oficial do produto.

### S-INT-02 — Persona Nina

- **Arquivos:** `docs/persona.md`, `data/personas/nina_v1/persona.json`, referências canônicas.
- **Autoridade:** canônica para identidade.
- **Descoberta:** Nina deve parecer pessoa real; `persona_master.png` e `nina_360_master.png` são referências complementares obrigatórias quando Nina aparece.
- **Decisão:** as duas referências entram juntas no prompt e o validador rejeita apenas uma referência.

### S-INT-03 — Visual Production / Scene Direction

- **Arquivos:** `brain/research/visual-production/`.
- **Autoridade:** `DESIGN_RESEARCHED`.
- **Descoberta:** realismo exige produto, materiais, luz, sombra, física e riscos observáveis; prompt não substitui direção nem QA.
- **Decisão:** o pacote explicita cena, composição, realismo, negativos e blockers; geração continua fora deste módulo.

## Fontes externas

### S-PLAT-01 — Reels ads creative guidance

- **Organização / URL:** Meta — <https://www.facebook.com/business/ads/facebook-instagram-reels-ads>
- **Tipo / autoridade:** orientação oficial de plataforma; alta para formato, limitada para claims de performance.
- **Descoberta:** a Meta recomenda criação vertical 9:16 e elementos-chave em safe zones para inventário imersivo.
- **Evidência:** `DOCUMENTED`.
- **Decisão:** 1080x1920, 9:16, conteúdo-chave afastado de overlays e verificação no preview da plataforma.
- **Limite:** a página não publica neste contexto uma medida numérica estável da safe zone para Story estático; o projeto não inventa margens em pixels.

### S-TREND-01 — TikTok Next 2026

- **Organização / URL:** TikTok for Business — <https://ads.tiktok.com/business/en/next>
- **Tipo / autoridade:** relatório oficial de tendências da plataforma; alta para sinais declarados, baixa para prever performance da conta Nina.
- **Descoberta:** realidade e processo humano ganham espaço sobre perfeição artificial; compra mais intencional exige explicar o “porquê comprar”.
- **Evidência:** `DOCUMENTED` como sinal de plataforma.
- **Decisão:** traduzir tendências em realismo editorial, utilidade e prova factual; nunca copiar layout, slogan ou identidade de terceiro.

### S-A11Y-01 — WCAG 2.2, contraste mínimo

- **Organização / URL:** W3C WAI — <https://www.w3.org/WAI/WCAG22/quickref/#contrast-minimum>
- **Tipo / autoridade:** padrão técnico oficial para acessibilidade web; alta para contraste, usado aqui como referência conservadora de legibilidade visual.
- **Descoberta:** texto normal usa referência de 4.5:1 e texto grande de 3:1.
- **Evidência:** `DOCUMENTED`.
- **Decisão:** exigir alto contraste e validar a composição final; a regra não é alegada como requisito formal do Instagram.

## Lacunas

- Não há evidência de performance da conta Nina para comparar os cinco tipos de Story.
- Não há medida oficial estável e pública, recuperada nesta pesquisa, para safe zone de Story orgânico estático.
- Texto renderizado por geradores de imagem pode falhar; grafia exata precisa de composição posterior quando necessário.
- Tendências mudam por nicho, região e conta; devem ser atualizadas antes de campanhas relevantes.
