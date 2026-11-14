# Imagens de Referência — Nina (v1.0)

Este diretório armazena o conjunto canônico de imagens de referência visual para a persona **Nina** (`persona_main_v1`).

> **IMPORTANTE:** Nenhuma imagem deve ser gerada automaticamente ou buscada aleatoriamente. Quando fornecidas, as imagens oficiais da Nina devem ser alocadas nesta pasta com os nomes padronizados abaixo.

---

## Inventário Atual

1. `persona_master.png` — imagem principal e autoridade máxima sobre a identidade facial e estética da Nina; nunca sobrescrever automaticamente.
2. `nina_360_master.png` — referência 360 obrigatória fornecida pelo usuário em 25/09/2026; autoridade sobre corpo, proporções, cabelo, ângulos, perfis, costas, expressões e detalhes físicos.
3. `nina.png` — referência secundária existente.
4. `ChatGPT Image 9 de set. de 2026, 09_32_57.png` — referência complementar adicionada pelo usuário.

Referências futuras de rosto, corpo, cenário ou interação podem ser acrescentadas, mas não substituem automaticamente `persona_master.png`.

---

## Hierarquia de Autoridade Visual

Em caso de divergência ou ambiguidade durante prompts ou modelos generativos, adota-se rigorosamente a seguinte hierarquia de autoridade:

```
persona_master.png  (Autoridade Absoluta sobre Identidade Facial)
nina_360_master.png (Autoridade Canônica sobre Corpo, Ângulos e Detalhes)
       ↓
user-provided secondary references (contexto, pose e enquadramento)
```

---

## Diretrizes de Uso

- **Preservação de Identidade:** Todos os prompts visuais devem carregar `persona_master.png` e `nina_360_master.png` quando a ferramenta aceitar ambas.
- **Uso obrigatório do 360:** Posts anteriores não substituem `nina_360_master.png` como referência da personagem.
- **Não Alterar:** Traços faciais, cabelo longo castanho levemente ondulado, tom de pele e idade aparente (22–24 anos).
- **Detalhes físicos:** Preservar proporções corporais, textura natural da pele, tatuagem, unhas, cabelo visto de frente, perfil e costas conforme o 360.
- **Consistência:** As referências secundárias servem para ancorar iluminação, ângulos e composições de cena sem degradar a fisionomia original.
