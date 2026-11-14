# Single Story Rendering — Findings

## 1. Imagem e tipografia precisam de lifecycles separados

O provider visual cria produto, cenário, luz e áreas vazias. O renderer escreve somente depois. Isso permite corrigir texto, posição ou cor sem consumir nova geração e sem degradar a imagem-base.

## 2. Safe zones devem existir antes da geração

Zonas nomeadas (`TOP_PILL_ZONE`, `HEADLINE_ZONE`, `SUPPORT_TEXT_ZONE`, `BOTTOM_BENEFIT_ZONE`, `CTA_ZONE`) orientam o prompt e o layout. O provider pode desobedecer parcialmente; por isso o resultado ainda precisa de QA e ajuste de layout.

## 3. Auto-fit precisa falhar de forma fechada

O renderer tenta quebras por palavras e reduz fonte apenas até o mínimo legível. Token indivisível, excesso de linhas ou altura impossível gera `TEXT_LAYOUT_FAIL`; o sistema não corta nem esconde copy.

## 4. Contraste é uma decisão local

O fundo varia dentro da fotografia. O renderer mede a região, escolhe texto claro/escuro e adiciona caixa ou backdrop quando o alvo não é atingido. O QA registra ratio e estratégia por componente.

## 5. QA técnico não substitui inspeção visual

Dimensões, overflow, source text e safe zones são determinísticos. Fidelidade ao produto, física, realismo, artefatos e identidade continuam `REVIEW` até receberem avaliação explícita.

## 6. Correção seletiva preserva custo e qualidade

Texto e layout podem ser rerenderizados mantendo o hash da base. Edição localizada é preferida para problema visual pontual. Regeneração completa permanece último recurso.

## Gate

**GATE RESULT:** `PASS / DESIGN_RESEARCHED`.  
**IMPLEMENTATION RESULT:** `READY` para ingestão de imagem do provider built-in, render local, QA e pacote final.  
**PUBLICATION:** fora do escopo.
