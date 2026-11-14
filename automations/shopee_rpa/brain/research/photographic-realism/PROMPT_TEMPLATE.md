# Template reutilizável — especificação fotográfica

Este template é um procedimento assistido, não um comando que altera automaticamente código. Recebe três entradas essenciais: **referência inspecionada + sujeito/produto + situação**. Formato/invariantes são informações adicionais que podem vir do contexto. Não exigir que o usuário preencha parâmetros de câmera.

## Entradas e autoridade

```text
REFERENCE: arquivo ou URL + pixels inspecionados + SHA-256
SUBJECT: personagem/pessoa/produto autorizado + fontes canônicas/oficiais
SITUATION: ação, ambiente, intenção de captura
OUTPUT: proporção/dimensões, corte aprovado, camada gráfica se houver
INVARIANTS: o que preservar exatamente (pose, roupa, cenário, texto etc.)
EDIT_SCOPE: nova cena / variação / somente texto e elementos
```

Identidade não vem da pessoa da foto de cena. Para Nina: anexar `data/personas/nina_v1/references/persona_master.png` e `nina_360_master.png`; ler `proportion_rules.txt` e `proportion_negative.txt`. Produto: referência oficial e dados validados. Pinterest: composição/captura/mood. Perfil: DNA e exemplos prioritários. Texto e elementos do post: gerador de imagens conforme orientação vigente do operador.

## As 17 leituras obrigatórias

Cada leitura produz `OBSERVATION`, `EVIDENCE_CLASS`, `CONFIDENCE_REASON`, `UNKNOWN`, `ADAPTATION` e `QA`. Usar confiança descritiva (forte/limitada), não precisão numérica inventada. Ausência de EXIF não impede receita plausível; impede afirmar a receita como configuração histórica.

| Leitura | O que preencher |
|---|---|
| 1 Composição | Sujeito, negativo, crop, horizonte, linhas, camadas; posição relativa no quadro. |
| 2 Câmera | Direta/espelho/terceiro; altura, inclinação, posição e distância proposta; alcançabilidade. |
| 3 Lente | Modelo conhecido ou campo aproximado; física/equivalente claramente separados. |
| 4 Perspectiva | Planos próximos/distantes, escala relativa, convergência, reflexo de espelho. |
| 5 Iluminação | Dominante e secundárias, lado, elevação, tamanho angular, distância, temperatura inferida. |
| 6 Sombras | Bloqueador, receptor, umbra/penumbra, contato, preenchimento/cor. |
| 7 Highlights | Forma/orientação/reflexos por material; fontes fora do quadro possíveis. |
| 8 Exposição | Região prioritária, altas luzes/sombras, clipping se documentado/plausível, curva. |
| 9 DOF | Plano de foco, proximidade, background/foreground e transição; bokeh justificado. |
| 10 Cores | WB/tint, luz mista, cor de objetos, spill e grade separado. |
| 11 Texturas | Escala e resolução; quais materiais pedem detalhe e quais não. |
| 12 Pele | Volume/tonalidade/brilho/detalhe visível, maquiagem, sinais canônicos. |
| 13 Cabelo | Raízes/grupos, orientação, sombra interna, flyaways/contraluz condicionais. |
| 14 Roupa | Material/estrutura/acabamento, peso, tensão, costura, contato corporal. |
| 15 Ambiente | Geometria, rebatedores, suportes, fundo/primeiro plano e uso da cena. |
| 16 Imperfeições | Classe, causa, região, intensidade qualitativa; pode ser nenhuma. |
| 17 Mecanismos | 3–5 relações que mais explicam o aspecto observado; invariantes e riscos. |

## Especificação pronta para o provider

```text
TASK: [escopo da edição ou criação].
REFERENCE ROLES: [arquivo → identidade / corpo / produto / cena / gráfico].
PRESERVE: [invariantes; dados/sinais canônicos; não copiar identidade da cena].

COMPOSITION: [posição, gesto, cortes, negativo, linhas e camadas].
CAMERA: [modo; altura; direção; distância aproximada PROPOSTA; alcançabilidade].
OPTICS: [campo equivalente; sensor/classe se pertinente; abertura conhecida ou
  aparência de foco desejada; não inventar EXIF; distorção discreta só se plausível].
PERSPECTIVE: [relações de escala, planos e lógica do espelho se houver].
FOCUS: [distância/plano; quem permanece definido; blur gradual; bokeh condicionado].
EXPOSURE: [prioridade; relação entre janelas/pele/sombra; processamento moderado].

KEY LIGHT: [origem, lado, elevação, angular size; distância proposta se útil].
FILL: [parede/céu/rebatedor, menor/igual intensidade relativa com motivo].
AMBIENT / SECONDARY: [fontes mistas; temperatura relativa; sem fonte imaginária].
SHADOWS: [bloqueador→receptor, contato, largura/continuidade e cor residual].
REFLECTIONS: [por superfície; forma das fontes; curva/espelho/refração].

MATERIALS: [acabamentos específicos e fidelidade oficial do produto].
SKIN: [identidade/tonalidade, brilho e textura na escala disponível].
HAIR: [grupos, direção, sombras, continuidade e foco].
FABRICS: [estrutura, gravidade, pontos de tensão, costuras e limites].
BACKGROUND / FOREGROUND: [distâncias/camadas/oclusões; sem props arbitrários].
COLOR: [WB, tint, spill, saturação, curva; gráfico separado de fotografia].
PLAUSIBLE IMPERFECTIONS: [causa→região→efeito; excluir se sem causa].
AVOID: [somente falhas relevantes para esta cena].
TYPOGRAPHY / GRAPHICS: [se solicitado; texto exato e DNA do perfil;
  manter fotografia aprovada; não tratar overlay como objeto físico].

[PHOTOREALISM ENGINE]
```

Parâmetros detalhados são direção desejada, não garantia de física pelo modelo. Não encher prompt com 30 proibições irrelevantes: selecionar riscos realmente presentes e relações observáveis. Se especificação contradiz invariantes, corrigir especificação antes de gerar.

## Exemplo preenchido: nova selfie direta de Nina em rotina

Hipótese ilustrativa, não geração executada nem EXIF de uma referência real:

“Nina adulta conforme duas canônicas e direção corporal slim-to-average existente; selfie vertical do peito para cima em quarto. Câmera frontal na mão estendida, aproximadamente 0,6–0,8 m do rosto como distância proposta alcançável; lente perto da altura dos olhos, sem ultra-wide exagerado. Campo amplo típico de celular, ambiente legível e plano de foco no rosto; não pedir bokeh de full frame f/1.2. Braço pode entrar no canto e ficar um pouco ampliado pela proximidade, sem dominar quadro nem comprimir torso. Telefone capturando fica fora do quadro; não inserir sua traseira como numa selfie de espelho. Janela grande à esquerda e ligeiramente acima, parede clara preenche à direita com intensidade menor. Sombra do nariz/cabelo acompanha a janela; volume e brilho locais na pele. Roupa esportiva fosca com costuras e tensão coerentes, cabelo canônico em mechas; fundo com cama parcialmente cortada. Exposição prioriza rosto, janela mais clara, cavidades menos legíveis. WB plausível de dia, sem laranja geral; sem grain/flare/clipping obrigatórios.”

QA planejado: cabeça/braço/ombros, distância alcançável, identidade, foco gradual, textura e origem da luz. As distâncias são sugestões adaptáveis ao usuário, não regras anatômicas rígidas.

## Exemplo preenchido: edição apenas gráfica da capa aprovada

“Editar a fotografia fornecida preservando pessoa, pose, anatomia, proporções, roupa, telefone, relógio, tatuagem, cabelo, ambiente, iluminação, enquadramento e orientação. Adicionar apenas o texto exato solicitado e elementos do DNA visual do perfil, conforme exemplos gráficos anexados. Não usar o PHOTOREALISM ENGINE para reluminar, refazer o rosto ou reposicionar o corpo. A fotografia já é o conteúdo aprovado; o escopo é a camada gráfica. Verificar ortografia, hierarquia, contraste e preservação visual após a edição.”

Preservação visual não significa pixels idênticos quando o provider regenera raster. Não declarar identidade de bytes sem comparação. O QA precisa revisar o arquivo efetivamente entregue.
