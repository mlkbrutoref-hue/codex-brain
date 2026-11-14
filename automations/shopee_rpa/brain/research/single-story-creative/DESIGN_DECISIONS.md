# Single Story Creative — Design Decisions

## SS-D01 — Segundo gerador isolado

**DECISÃO:** `app/single_story/` é um módulo separado do pipeline de Reels, scripts e storyboards. Recebe `SingleStoryRequest` e produz `SingleStoryCreativePackage`.

**POR QUÊ:** a unidade, o ritmo, a copy e o lifecycle são diferentes. Reuso prematuro do gerador de vídeo introduziria cenas, duração e continuidade que não pertencem a uma peça estática.

## SS-D02 — Seleção automática explicável com override

**DECISÃO:** a seleção usa sinais nos fatos/evidências e expõe rationale. O usuário pode fixar qualquer tipo.

**POR QUÊ:** permite comportamento consistente sem fingir previsão de performance. O score interno nunca aparece como nota de qualidade comercial.

## SS-D03 — Prompt final exige referência do produto

**DECISÃO:** sem `product_reference_paths`, o pacote é válido para planejamento, porém `final_image_prompt_ready=false` e inclui `MISSING_PRODUCT_REFERENCE`.

**POR QUÊ:** realismo e consistência do produto não podem ser inferidos com segurança apenas do nome.

## SS-D04 — Copy de apoio é factual por construção

**DECISÃO:** supporting e benefit text são fatos confirmados copiados literalmente. Headline e CTA usam molduras neutras.

**POR QUÊ:** reduz transformação semântica e facilita auditoria.

## SS-D05 — Nina é opcional, referências duplas são obrigatórias

**DECISÃO:** o padrão é produto sem personagem. Quando `use_nina=true`, entram `persona_master.png` e `nina_360_master.png`.

**POR QUÊ:** uma peça de produto nem sempre precisa de pessoa, mas identidade parcial não é aceitável quando Nina aparece.

## SS-D06 — Geração de mídia fica fora do módulo

**DECISÃO:** o gerador termina em JSON e prompt provider-independent. Não abre Flow, não consome créditos e não publica.

**POR QUÊ:** preserva separação de responsabilidade, rastreabilidade e controle de custo.

## SS-D07 — Texto exato admite composição posterior

**DECISÃO:** o prompt lista texto exato, porém as notas recomendam composição tipográfica posterior quando o modelo visual não respeitar grafia.

**POR QUÊ:** legibilidade e correção ortográfica são requisitos do artefato, não capacidades presumidas do provider.

## Validação futura

- Executar benchmark com os cinco tipos usando produtos de categorias diferentes.
- Medir concordância humana sobre clareza, identidade, produto e originalidade.
- Registrar performance real apenas após publicação, sem transformar poucos posts em regra universal.
