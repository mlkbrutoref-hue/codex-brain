# Visual Production — Estudos de caso

Estes casos validam a expressividade do design. São especificações conceituais, não prompts finais nem instruções para gerar mídia. Produtos são arquétipos; qualquer job real deve substituir suposições por `ProductFacts` confirmados.

## Caso A — Cozinha: dispenser transparente despejando líquido

### Preconditions / fatos necessários

- confirmar material, formato, tampa/bico e se o produto é adequado ao líquido mostrado;
- não assumir vedação, capacidade, “anti-gotejamento” ou benefício não documentado;
- para o exercício, usa-se água limpa como líquido visual e um copo medidor como destino; isso ainda precisaria de aprovação factual/creative.

### Creative goal

Mostrar, em linguagem de celular, como segurar e inclinar o dispenser para produzir um fluxo controlado e visível, sem alegar desempenho além do que aparece.

### Scene direction

- **Environment:** bancada de cozinha real, fundo organizado mas habitado; dispenser e copo medidor já presentes.
- **Initial state:** Nina em 3/4 diante da bancada; dispenser vertical à direita do copo; mão direita envolve o corpo na zona não crítica, mão esquerda livre próxima à base; líquido e bico visíveis.
- **Blocking:** antebraços apoiados/estáveis; corpo ligeiramente voltado para a bancada; Nina olha primeiro para o bico/destino, não para a câmera.
- **Primary action:** Nina estabiliza o dispenser, inclina-o de forma progressiva sobre o centro do copo; um fluxo contínuo sai apenas do bico; ela reduz a inclinação, encerra o fluxo e retorna o recipiente à vertical.
- **Final state:** dispenser vertical, ainda na mão; copo contém volume visualmente maior; sem gotejamento adicional salvo se factual/esperado; hold curto do resultado.
- **Proof moment:** origem, arco curto do fluxo e chegada ao copo aparecem simultaneamente.

### Camera / `CinematographySpec`

- vertical 9:16 intent; medium-close de bancada incluindo torso inferior, duas mãos, dispenser e copo;
- câmera na altura ligeiramente acima da bancada, distância de braço/celular, perspectiva moderadamente ampla sem deformar mãos;
- estática ou micro-handheld estabilizado; sem push-in durante o fluxo;
- foco prioriza bico/mãos/copo, com Nina ainda reconhecível; DOF moderada, não macro rasa;
- exposição preserva transparência e highlights sem clip.

### Lighting / `LightingSpec`

- janela lateral esquerda como key ampla e suave;
- teto difuso fraco como fill ambiente;
- sem backlight de estúdio invisível;
- highlights longos e coerentes nas bordas transparentes; sombra suave para a direita; líquido/fundo vistos por refração plausível;
- pele e contorno do recipiente preservam detalhe; WB neutra levemente quente de cozinha.

### Interaction / `PhysicalInteractionSpec`

- **active hand:** direita, power/intermediate grip no corpo;
- **support:** esquerda pode estabilizar parte inferior se o peso/volume confirmados justificarem; não tocar no bico/fluxo;
- **anchor/axis:** rotação controlada pelo punho/cotovelo sobre eixo lateral; copo permanece apoiado;
- **material response:** recipiente rígido; conteúdo conserva volume e responde à gravidade/viscosidade; reflexos mudam com orientação;
- **occlusion budget:** dedos podem cobrir uma área lateral, nunca bico, fluxo ou marca funcional necessária.

### Temporal sequence / `TemporalPlan`

1. `INITIAL_HOLD`: produto vertical, destino vazio/estado inicial visível.
2. `MOTION_START`: inclinação lenta, bico cruza sobre o copo.
3. `FLOW`: fluxo começa no bico e permanece contínuo até o destino.
4. `MOTION_END`: fluxo reduz e cessa antes do retorno total.
5. `RESULT_HOLD`: vertical, copo com resultado visível.

Beat windows podem orientar edição; o adapter não deve prometer segundos exatos antes de E-02.

### Continuity / `ContinuitySpec`

- Nina, cabelo, roupa, mão ativa e posição à direita do copo invariáveis;
- contorno, tampa, bico, nível/cor do líquido e escala do dispenser invariáveis;
- copo e bancada fixos; nenhum prop aparece/desaparece;
- janela permanece à esquerda e highlights/reflexos acompanham apenas a rotação.

### Risk profile

| Eixo | Band | Motivo / resposta |
|---|---|---|
| HAND_INTERACTION | `HIGH` | grip + inclinação; simplificar para uma mão ativa e apoio opcional |
| IDENTITY | `MEDIUM` | rosto não é o centro; evitar oclusão/rotação facial |
| PRODUCT_MORPH | `HIGH` | transparente e em rotação; usar ref limpa e ângulo limitado |
| PHYSICS | `HIGH` | rotação, gravidade e conservação |
| REFLECTION | `HIGH` | material transparente/glossy |
| LIQUID | `CRITICAL` | fluxo, volume e recipiente |
| CLOTH | `LOW` | roupa quase estática |
| CONTINUITY | `HIGH` | nível do líquido e estado do copo mudam causalmente |
| OCCLUSION | `MEDIUM` | dedos podem esconder contorno |

**Compound risk:** `hands + transparent container + liquid + rotation`. Se o teste falhar, dividir em insert do pour sem rosto ou substituir por demonstração estática do mecanismo.

### Generation specification

- **must_preserve:** Nina/roupa; geometria, bico e transparência; um dispenser e um copo; luz esquerda.
- **must_show:** origem e destino do fluxo; contato plausível; fluxo contínuo; retorno e resultado.
- **must_avoid:** recipiente deformando; líquido nascendo fora do bico; mãos fundidas; mudança de volume impossível; reflexo flutuante; copo movendo sozinho.
- **preferred inputs:** referência limpa do produto e da Nina; boundary states desejáveis se o modo atual os suportar.
- **acceptance checks:** anatomia, landmarks do produto, trajetória/volume, sombra/refração, contagem e final state.
- **provider note:** o `GoogleFlowAdapter` futuro decide ingredients/frames/mode; nada aqui contém sintaxe Flow.

## Caso B — Organização/casa: gaveta organizadora deslizante

### Preconditions / fatos necessários

- confirmar montagem, direção/curso do trilho, capacidade e se a unidade precisa estar fixada;
- não demonstrar peso/carga ou facilidade de instalação sem evidência.

### Creative goal

Provar o acesso visual e o movimento de abrir/fechar de uma gaveta organizadora sob prateleira, com mudança espacial fácil de entender.

### Scene direction

- **Environment:** armário/prateleira doméstica; poucos itens reconhecíveis e estáveis.
- **Initial state:** gaveta fechada e alinhada sob a prateleira; Nina ao lado, não bloqueando o trilho; mão direita próxima ao puxador.
- **Primary action:** dedos fecham no puxador; estrutura superior permanece fixa; Nina puxa a gaveta em linha reta até o limite visível, pausa para revelar conteúdo e empurra de volta até alinhamento.
- **Final state:** gaveta fechada no mesmo alinhamento inicial; mão liberada; estrutura e conteúdo preservados.
- **Proof moment:** lateral/trilho, puxador, translação e conteúdo aparecem no mesmo plano.

### Camera

- medium-close lateral em 3/4, câmera à altura da gaveta, distância que mostra estrutura fixa e curso inteiro;
- perspectiva normal/moderadamente ampla; linhas verticais/horizontais estáveis;
- câmera estática; nenhum pan concorrente;
- DOF moderada/alta para prateleira, trilho, mão e conteúdo.

### Lighting

- janela frontal-lateral suave ou luz ambiente de quarto/dispensa; uma fonte dominante;
- fill natural do cômodo; interior da prateleira não deve ficar preto, mas também não receber luz sem fonte;
- sombra da gaveta se desloca coerentemente sobre a superfície inferior.

### Interaction

- mão direita em power/precision híbrido no puxador; polegar oposto aos dedos;
- braço aplica força paralela ao trilho; ombro/cotovelo recuam de modo pequeno;
- gabinete/prateleira é anchor imóvel; conteúdo acompanha a gaveta sem deslizar sozinho;
- função/trilho não são ocultados pela mão.

### Temporal sequence

1. fechada/alinhada;
2. contact + grip no puxador;
3. translação para fora em eixo único;
4. pause/reveal;
5. retorno pelo mesmo eixo;
6. release/alinhada.

Se abrir e fechar for instável no mesmo clip, manter apenas abrir + result hold; o fechamento vira outro take ou é omitido.

### Continuity

- mão ativa, lado de Nina, conteúdo e ordem dos itens invariáveis;
- estrutura superior, trilho e puxador não mudam geometria;
- direção de tela do movimento permanece consistente;
- luz e shadow anchor permanecem constantes.

### Risk profile

| Eixo | Band | Motivo / resposta |
|---|---|---|
| HAND_INTERACTION | `MEDIUM` | grip simples, uma mão |
| IDENTITY | `LOW` | rosto secundário/parcial |
| PRODUCT_MORPH | `HIGH` | trilho/encaixe/volume devem permanecer |
| PHYSICS | `HIGH` | parte fixa vs. móvel, colisão e limite |
| REFLECTION | `LOW/MEDIUM` | depende do acabamento confirmado |
| LIQUID | `NONE` | não presente |
| CLOTH | `LOW` | roupa estática |
| CONTINUITY | `HIGH` | conteúdo e alinhamento durante a translação |
| OCCLUSION | `MEDIUM` | mão/puxador/trilho |

### Generation specification

- **must_preserve:** uma gaveta, um trilho/estrutura fixa, conteúdo e alinhamento.
- **must_show:** mão no puxador, eixo linear, estrutura parada, reveal.
- **must_avoid:** prateleira movendo, gaveta atravessando estrutura, conteúdo duplicando/caindo, eixo mudando.
- **preferred inputs:** ref do produto montado e, se possível, frame inicial lateral que revele mecanismo.
- **acceptance checks:** landmarks da estrutura, trajetória, contagem de itens, anatomia/grip, estado aberto final.

## Caso C — Beleza: conta-gotas depositando sérum na mão

### Preconditions / fatos necessários

- confirmar embalagem/conta-gotas, aparência/viscosidade do produto e uso permitido;
- não mostrar efeito clínico, transformação de pele ou aplicação facial se não sustentado;
- demonstração de textura não prova eficácia.

### Creative goal

Mostrar embalagem, abertura e uma única gota/textura sobre o dorso da mão de forma natural e factual, sem before/after artificial.

### Scene direction

- **Environment:** bancada de banheiro/quarto, espelho fora do eixo para não multiplicar identidades; frasco central.
- **Initial state:** frasco apoiado e aberto somente se abertura for outro take; conta-gotas na mão direita acima do dorso da esquerda, ponta sem contato com pele.
- **Primary action:** Nina estabiliza a mão esquerda, comprime/solta conforme o mecanismo confirmado e permite que uma gota se forme na ponta, caia e assente no dorso.
- **Final state:** conta-gotas permanece acima sem tocar; uma gota/textura visível; hold curto.
- **Proof moment:** ponta, gota no ar/contato e textura final, sem esconder a mão.

### Camera

- close funcional do torso/mãos; celular ligeiramente acima e a 30–45° da bancada;
- perspectiva natural, sem macro extremo que distorça dedos;
- câmera estática/micro-handheld quase imperceptível;
- foco no plano da ponta e dorso; DOF suficiente para manter ambos legíveis.

### Lighting

- janela frontal-lateral suave como key; practical do espelho/teto fraco e compatível;
- pele sem clipping/alisamento; vidro e líquido com small highlights coerentes;
- WB neutra; evitar casts que alterem cor factual do produto.

### Interaction

- mão direita usa precision grip na tampa/conta-gotas; mão esquerda relaxada e apoiada;
- ponta nunca atravessa ou gruda na pele;
- gota responde à gravidade e à viscosidade confirmada; frasco não flutua fora de cena;
- nenhuma alegação visual de absorção instantânea se não factual.

### Temporal sequence

1. conta-gotas estável acima da mão;
2. gota se forma na ponta;
3. separa e cai em trajetória curta;
4. contato e settle no dorso;
5. hold da textura, sem transformação inventada.

### Continuity

- tom/textura de pele, unhas, joias permitidas, número/posição dos dedos e mão ativa invariáveis;
- conta-gotas, tampa, rótulo/cor e quantidade de produto invariáveis;
- mesma direção de key/highlight e mesma posição de bancada.

### Risk profile

| Eixo | Band | Motivo / resposta |
|---|---|---|
| HAND_INTERACTION | `HIGH` | duas mãos e precision grip |
| IDENTITY | `LOW/MEDIUM` | rosto não precisa dominar; pele deve ser consistente |
| PRODUCT_MORPH | `HIGH` | vidro, conta-gotas e rótulo fino |
| PHYSICS | `HIGH` | gota e contato |
| REFLECTION | `HIGH` | vidro/líquido/glossy |
| LIQUID | `CRITICAL` | formação/separação/queda/settle |
| CLOTH | `LOW` | secundário |
| CONTINUITY | `HIGH` | gota e anatomia ao longo do evento |
| OCCLUSION | `MEDIUM` | dedos podem esconder mecanismo |

**Fallback:** take estático da textura já depositada + insert separado do frasco, se a queda não for confiável.

### Generation specification

- **must_preserve:** um conta-gotas, uma gota, anatomia, embalagem e cor confirmada.
- **must_show:** espaço entre ponta e pele, formação/queda causal, textura final sem claim.
- **must_avoid:** dedos extras/fundidos, múltiplas gotas, ponta atravessando pele, líquido sólido/teleporte, pele plasticizada, rótulo falso.
- **preferred inputs:** produto em fundo limpo, Nina/mãos aprovadas; start/end boundaries conforme modo testado.
- **acceptance checks:** anatomy/contact frames, origem/trajetória/contagem da gota, highlights/refração e invariantes do produto.

## Caso D — Roupa/acessório: touca de tecido mostrada e colocada parcialmente

### Preconditions / fatos necessários

- confirmar material, elasticidade, reversibilidade, tamanho e modo de uso;
- não prometer proteção/resultado capilar; não representar stretch além do documentado.

### Creative goal

Mostrar textura, abertura e modo básico de posicionamento da touca preservando rosto/cabelo da Nina e comportamento de tecido; priorizar credibilidade sobre uma colocação completa arriscada.

### Scene direction

- **Environment:** quarto/banheiro doméstico, fundo simples; Nina em frente à câmera sem espelho visível.
- **Initial state:** Nina segura a touca à altura do peito com duas mãos separadas nas bordas; abertura e interior visíveis; cabelo/roupa canônicos.
- **Primary action:** ela abre suavemente a borda apenas dentro do stretch factual, eleva a touca até a linha posterior/superior da cabeça e posiciona a borda frontal sem esconder olhos/rosto. Para reduzir risco, a cena termina no posicionamento inicial, não em tuck completo de todo o cabelo.
- **Final state:** touca apoiada de modo plausível, mãos ainda estabilizando a borda; rosto/cabelo visível onde esperado; hold.
- **Proof moment:** borda, abertura, textura/dobra e primeiro contato com a cabeça.

### Camera

- medium chest-up, eye-level ou ligeiramente acima, distância típica de front camera/tripod de celular;
- câmera estática; composição central levemente casual, headroom suficiente para elevar o acessório;
- perspectiva natural sem ultra-wide facial; DOF moderada/alta para mãos, touca e rosto.

### Lighting

- janela suave em 45° como key e bounce ambiente do cômodo;
- tecido mantém highlights/dobras compatíveis com acabamento; pele não é excessivamente suavizada;
- sombra da touca acompanha aproximação da cabeça; fundo não muda.

### Interaction

- duas mãos em pontos opostos da borda, grip simétrico mas não rígido; polegares internos/dedos externos apenas se compatível com a abertura;
- extensão limitada e progressiva; centro do tecido cede à gravidade;
- mãos e borda seguem trajetórias claras ao redor da cabeça, sem atravessar cabelo/orelhas;
- tecido forma dobras nos pontos de compressão e se adapta parcialmente à cabeça.

### Temporal sequence

1. apresentação da abertura/textura;
2. stretch leve;
3. elevação alinhada à cabeça;
4. contato posterior/superior;
5. ajuste curto da borda frontal;
6. result hold.

**Split recomendado:** se a geração misturar fases, clip 1 = textura/stretch; clip 2 = start frame já próximo à cabeça e posicionamento curto.

### Continuity

- rosto, cabelo, cor/volume, roupa e acessórios da Nina invariáveis;
- cor, costura, acabamento, abertura e lado interno/externo da touca invariáveis;
- mão esquerda/direita mantêm seus pontos de contato; direção do movimento sempre para cima/atrás;
- luz, fundo, posição de ombros e eyeline preservados.

### Risk profile

| Eixo | Band | Motivo / resposta |
|---|---|---|
| HAND_INTERACTION | `CRITICAL` | duas mãos, cabeça, borda e cabelo |
| IDENTITY | `CRITICAL` | rosto/cabelo parcialmente ocluídos e deformação próxima |
| PRODUCT_MORPH | `HIGH` | forma flexível pode trocar geometria/costura |
| PHYSICS | `HIGH` | contato, stretch e adaptação |
| REFLECTION | `MEDIUM/HIGH` | depende de satin/gloss confirmado |
| LIQUID | `NONE` | ausente |
| CLOTH | `CRITICAL` | deformação e dobras são a ação |
| CONTINUITY | `CRITICAL` | cabelo, roupa, mãos e tecido |
| OCCLUSION | `CRITICAL` | rosto/cabelo/mãos se cruzam |

**Compound risk:** `two hands + cloth deformation + face/hair occlusion`. A especificação recomenda split/redesign; um único take completo só depois de experimento bem-sucedido.

### Generation specification

- **must_preserve:** identidade/rosto/cabelo, mãos, cor/costura/material confirmado e uma única touca.
- **must_show:** abertura, pontos de grip, stretch limitado, dobras e contato progressivo.
- **must_avoid:** tecido rígido/derretido, mãos atravessando, cabelo desaparecendo, rosto mudando, touca duplicando, estampa/costura migrando.
- **preferred inputs:** referências limpas e coerentes da Nina e do acessório; dois clips/boundary states em vez de uma sequência longa.
- **acceptance checks:** anatomia, identity keyframes, pontos de grip, deformação/gravidade, oclusão, textura/costura e final state.

## Resultado do walkthrough

Os quatro casos podem ser expressos com um único `SceneDirection` agregado e uma `GenerationSpecification`, sem transformar cada subespecificação em serviço. O exercício também mostra que risk profile precisa mudar o próprio desenho: A/C pedem fallback para líquido; B pede eixo/anchor; D pede split antes de tentar um take completo. Essa influência concreta é a razão para o risco existir antes do prompt.
