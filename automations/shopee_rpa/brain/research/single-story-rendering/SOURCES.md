# Single Story Rendering — Fontes

**RESEARCH_DATE:** 25/09/2026  
**Escopo:** geração real de imagem-base, composição tipográfica determinística, auto-fit, contraste, QA e artefatos de Story estático.

## Fontes internas

### S-INT-01 — Single Story Creative

- **Arquivos:** `brain/research/single-story-creative/` e `app/single_story/`.
- **Autoridade:** canônica para contrato criativo, factualidade, formato 9:16 e referência do produto.
- **Decisão:** a renderização consome o pacote aprovado; não reescreve fatos nem escolhe outro conceito.

### S-INT-02 — Visual Production

- **Arquivos:** `brain/research/visual-production/`.
- **Autoridade:** `DESIGN_RESEARCHED` para realismo, produto, materiais, luz, física e QA visual.
- **Decisão:** os mesmos invariantes de produto e realismo são aplicados à imagem estática.

### S-INT-03 — Imagegen skill

- **Arquivo:** `C:/Users/GAMER/.codex/skills/.system/imagegen/SKILL.md`.
- **Autoridade:** operacional para o provider nativo do ambiente.
- **Decisão:** usar o provider built-in, persistir o resultado no workspace e manter o renderer local separado.

## Fontes externas

### S-RENDER-01 — Pillow ImageDraw

- **Organização / URL:** Pillow — <https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html>
- **Tipo / autoridade:** documentação oficial da biblioteca.
- **Descoberta:** `textbbox`, `textlength`, fontes TrueType, multiline text, stroke e desenho RGBA permitem medir e compor texto deterministicamente.
- **Decisão:** usar Pillow para wrap, auto-fit, componentes gráficos e overlay transparente.

### S-RENDER-02 — WCAG 2.2 Contrast Minimum

- **Organização / URL:** W3C WAI — <https://www.w3.org/WAI/WCAG22/quickref/#contrast-minimum>
- **Tipo / autoridade:** padrão técnico oficial; usado como referência conservadora de legibilidade.
- **Descoberta:** 4.5:1 para texto normal e 3:1 para texto grande.
- **Decisão:** o QA exige alvo mínimo de 4.5:1 para todos os componentes textuais deste renderer.

### S-PLAT-01 — Vertical creative e safe zones

- **Organização / URL:** Meta — <https://www.facebook.com/business/ads/facebook-instagram-reels-ads>
- **Tipo / autoridade:** orientação oficial para formato imersivo vertical.
- **Descoberta:** 9:16 e elementos-chave em safe zones são princípios centrais.
- **Decisão:** canvas 1080x1920, margem externa e zonas nomeadas; validar o preview final na plataforma.

## Limites

- O provider built-in é operado pelo Codex e não expõe neste repositório uma API Python estável; o pipeline ingere o arquivo gerado e registra sua origem.
- Métricas locais verificam dimensão, bounds, exatidão da fonte de texto e contraste planejado; fidelidade semântica e artefatos visuais ainda exigem inspeção explícita.
- As fontes Windows são dependência do perfil atual; portabilidade futura pede font assets licenciados dentro do projeto.
