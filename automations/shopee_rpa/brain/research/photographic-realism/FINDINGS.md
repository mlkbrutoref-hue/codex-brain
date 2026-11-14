# Findings

## WHAT WE KNOW

- `DOCUMENTED` — perspectiva depende da posição; campo/focal e blur são relações diferentes (S07/S13/S14). Direcionar câmera antes de corrigir proporções pela lente.
- `DOCUMENTED` — luz refletida, geometria e material participam da aparência (S01–S06). Contato/reflexos não se corrigem com grain.
- `DOCUMENTED` — pele e cabelo têm respostas espaciais/direcionais que não equivalem a textura sobreposta (S08–S10).
- `DOCUMENTED` — trama e acabamento afetam tecidos; nome de fibra não determina sozinho brilho/caimento (S11).
- `DOCUMENTED` — fotografia computacional pode reduzir ruído e preservar faixa dinâmica (S12); efeitos de captura/processamento são condicionais (S15–S21/S23).
- `OBSERVED` — corpus contém limpeza, retoque, ruído, blur e forte contraste em casos distintos. Nenhum “defeito fotográfico” é requisito universal; ver atlas.
- `OBSERVED` — R02 tem conflito descrição–EXIF; admitir desconhecimento é necessário, não uma lacuna a preencher com parâmetros inventados.

## WHAT SEEMS TO WORK

- `INFERRED` — escrever relações de câmera/luz/apoio antes de textura reduz ambiguidade de direção.
- `INFERRED` — separar identidade, produto, cena e gráfico protege invariantes da Nina.
- `INFERRED` — correção localizada e evidência por hash evitam aprovação indevida de arquivo novo.
- `INFERRED` — detectar contradição concreta é mais acionável que rotular tudo como “muito perfeito”.

## WHAT IS UNCERTAIN

- `UNKNOWN` — efeito quantitativo deste template por modelo/provider e estabilidade entre gerações.
- `UNKNOWN` — captura, autenticidade e EXIF dos dois exemplos Pinterest; tratados somente como direção visual.
- `UNKNOWN` — configurações exatas das fotos sem metadados/bastidores; receitas estimadas não são reconstrução única.
- `UNKNOWN` — ranking de impacto perceptivo entre pele, luz, foco e materiais neste público/perfil.
- `UNKNOWN` — generalização para roupas/fibras, tons de pele e ambientes não representados pelo corpus visual.

## WHAT NEEDS TESTING

AB01–AB08, [protocolos](AB_PROTOCOLS.md): instrução causal de luz, textura por escala, distância de selfie, apoio, blur, grain, acabamento e cor. Sem resultados próprios, não declarar EXPERIMENTAL/PASS de provider ou capability READY. A pesquisa está concluída como material de direção; o benchmark generativo permanece pendente.
