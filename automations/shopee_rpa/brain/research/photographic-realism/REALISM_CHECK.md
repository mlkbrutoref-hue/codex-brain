# REALISM CHECK

Inspeção manual complementar ao QA existente. Não é detector de IA nem validador automático. Avaliar **tamanho de publicação + 100%**; distinguir detalhes resolvidos de regiões sem evidência. Para Nina, carregar as duas canônicas e políticas de proporção; aplicar também os sete checks anatômicos já existentes.

Os checks preservados de `app/creative/proportion_policy.py` são: `HEAD_BODY_RATIO_FAIL`, `TORSO_WIDTH_FAIL`, `WAIST_SHAPE_FAIL`, `LIMB_PROPORTION_FAIL`, `MIRROR_PERSPECTIVE_FAIL`, `BODY_IDENTITY_DRIFT` e `OVERWEIGHT_INTERPRETATION_FAIL`. Os itens abaixo complementam esses nomes; não os renomeiam nem substituem suas regras de evidência/recuperação.

## Evidência da revisão

```text
JOB / ASSET:
FINAL_FILE / SHA256 / DIMENSIONS:
REFERENCE_FILES / SHA256 / ROLES:
PROMPT_VERSION / PROVIDER / CAPTURE_INTENT:
REVIEWER / DATE / INSPECTION_SCALES:
RESULT: PASS / REVIEW / FAIL
OBSERVED_DEFECTS:
UNKNOWN_OR_NOT_VISIBLE:
CORRECTION_PLAN:
```

**PASS**: região relevante visível, inspecionada e compatível. **REVIEW**: ocultação, escala insuficiente, interpretação conflitante ou referência ausente. **FAIL**: contradição constatada e descrita. **N/A**: item não pertence à cena, com justificativa; boca fechada torna dentes N/A, não “dentes aprovados”.

| Check | Verificação concreta | Correção se houver defeito |
|---|---|---|
| [ ] Anatomia | Continuidade de membros/articulações, cabeça/torso, cintura/ombros | Reconstruir região contra canônicas e política corporal; não afinar globalmente. |
| [ ] Mãos | Quantidade/topologia visível, articulação, pega, dedo oculto | Corrigir pega/local, mantendo gesto e telefone. |
| [ ] Olhos | Alinhamento do olhar, pálpebras/cílios, íris/reflexos | Preservar identidade; corrigir olhar/reflexo específico. |
| [ ] Dentes | Visibilidade, limite com lábio e oclusão | Corrigir apenas área visível; não abrir boca para testar. |
| [ ] Cabelo | Raízes, grupos, separação, brilho, foco | Remover fusão/fio sem origem; restaurar mecha. |
| [ ] Pele | Volume, tonalidade canônica, brilho/escala de textura | Corrigir plastificação/localização do detalhe; sem manchas aleatórias. |
| [ ] Roupa | Estrutura/acabamento, costuras, espessura e tensão | Reorientar dobra ou costura, preservar produto. |
| [ ] Gravidade | Apoios, pendentes, cabelos/tecido segundo gesto | Corrigir queda/ancoragem; manter ação. |
| [ ] Perspectiva | Uma posição de câmera explica planos e linhas | Corrigir câmera ou região; registrar se muda enquadramento aprovado. |
| [ ] Escala | Telefone, produto, cabeça, braço, mobiliário | Restabelecer relação sem mudar dimensões do produto por estética. |
| [ ] Iluminação | Origens/dominante/fill explicam sujeito e ambiente | Remover luz sem origem ou readequar região. |
| [ ] Direção das sombras | Fonte/bloqueador/receptor; planos diferentes considerados | Corrigir trajetória, não uniformizar vetores no quadro. |
| [ ] Sombras de contato | Apoio/oclusão, densidade e penumbra plausíveis | Corrigir ponto de apoio; evitar contorno preto automático. |
| [ ] Reflexos | Curvatura, materiais, ambiente fora do quadro | Restaurar fonte/forma; não apagar reflexo válido apenas porque fonte não aparece. |
| [ ] Materiais | Diferenciar vidro/metal/plástico/tecido, refração/acabamento | Alterar resposta material específica, não adicionar grain a tudo. |
| [ ] Profundidade de campo | Plano de foco/transição por distância | Corrigir blur no plano afetado, sem máscara semântica uniforme. |
| [ ] Bokeh | Pontos luminosos e forma/contexto óptico | Remover bolas inventadas ou corrigir origem/escala. |
| [ ] Exposição | Hierarquia de luz, sombra e prioridade | Corrigir achatamento/halo; não forçar clipping ou ruído. |
| [ ] Textura | Escala, foco, resolução e região compatíveis | Reduzir detalhe inventado ou recuperar variação realmente necessária. |
| [ ] Fundo | Geometria contínua, repetição contextual, função | Corrigir prop/linha local, não substituir cenário inteiro. |
| [ ] Integração sujeito/cenário | Luz, apoio, oclusão, spill, foco/processamento | Resolver relação específica antes de tratamento global. |
| [ ] Artefatos típicos | Fusões, clonagens, pseudo-letras, bordas desenhadas | Corrigir elemento e revalidar restante do arquivo. |
| [ ] Identidade Nina | Canônicas, sinais físicos, idade, corpo aprovado | Restaurar identidade; não copiar pessoa da referência de cena. |
| [ ] Espelho/captura | Telefone, mão, paridade, trajeto e foco | Corrigir geometria virtual; manter tatuagem rastreável. |
| [ ] Texto/logotipo | Copy exata, legibilidade, logo oficial | Corrigir letras/layout no gerador visual, preservar foto. |
| [ ] Efeitos ópticos/câmera | Ruído, flare, bloom, distorção têm causa | Remover efeito arbitrário; manter efeitos legítimos. |
| [ ] Cor/processamento | WB/mistos, pele, contraste, halos, denoise | Ajuste focalizado sem trocar paleta gráfica do perfil. |

## Registro por problema

```text
CHECK / STATUS:
REGION: coordenada normalizada ou descrição recuperável
EVIDENCE: o que foi realmente observado
EXPECTED_PHYSICAL_RELATION:
ORIGINAL_FAILURE:
CORRECTION_APPLIED: mudança mínima; tentativa 0 ou 1
INVARIANTS_PRESERVED:
CORRECTED_FILE / SHA256:
FINAL_RESULT / RESIDUAL_ISSUE:
```

Não contar ausência de imagem/referência como anatomia PASS. Não reaproveitar QA de arquivo anterior após editar. No resultado global: defeito relevante constatado → FAIL; nenhuma falha, mas requisito relevante sem evidência → REVIEW; todos os requisitos aplicáveis efetivamente sustentados → PASS. Um efeito pouco perceptível sem contradição concreta não basta para FAIL.

Máximo uma correção por tentativa, respeitando recuperação existente da Nina. Se persistir, registrar resultado e parar essa tentativa. Não usar loop, não conceder PASS por esgotamento do limite, não executar provider local fictício.
