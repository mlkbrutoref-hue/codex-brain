# Pesquisa aprofundada: fotografia plausível

Data: 12/10/2026. Pedido: reduzir aparência artificial por coerência física, não por embelezamento. Escopo: fotografia estática, com aplicação a retratos, selfies, lifestyle e produtos da Nina. Este relatório consolida pesquisa técnica, análise visual e hipóteses de direção. Consulte [fontes](SOURCES.md), [atlas inspecionado](REFERENCE_ATLAS.md) e [taxonomia detalhada](AI_TELLS.md).

Convenção: **D = DOCUMENTED**, **O = OBSERVED**, **I = INFERRED**, **U = UNKNOWN**. D sustenta um mecanismo; não comprova que uma frase de prompt o fará funcionar. As instruções de geração são aplicações propostas, a validar no provider. Não estamos certificando autoria de imagens por aparência.

## 1. Resumo executivo

A fotografia plausível depende de uma cadeia comum: **geometria da cena → iluminação → resposta dos materiais → projeção/foco → exposição/processamento → apresentação**. Um erro numa etapa pode contradizer as demais. Poros não corrigem reflexo impossível; ruído não corrige braço gigante; fundo desfocado não corrige uma pessoa iluminada por outra cena.

A principal conclusão aplicada é dirigir as relações antes dos efeitos: de onde vem a luz, o que bloqueia essa luz, o que a reflete, onde está a câmera e o que ela consegue resolver. Só depois decidir textura, cor e imperfeições. Fotografias limpas e retocadas também são reais; a oposição entre “perfeito” e “real” é insuficiente. O estudo de [percepção de gloss](https://pubmed.ncbi.nlm.nih.gov/30508429/) mostra que luz, contexto e tone mapping mudam a leitura do material; extrapolar isso para uma checklist universal de detecção de IA seria incorreto. **D/I**

Resultado prático: [template completo](PROMPT_TEMPLATE.md), [módulo PHOTOREALISM ENGINE](PHOTOREALISM_ENGINE.txt), [REALISM CHECK](REALISM_CHECK.md) e [protocolos A/B](AB_PROTOCOLS.md). Prioridade de correção: anatomia/identidade e geometria; depois luz/inserção; materiais/foco; por último tratamento. Não foi necessário gerar novas imagens para realizar esta pesquisa.

## 2. Principais características que denunciam aparência artificial

Três famílias ajudam a diagnosticar problemas: **contradição estrutural** (dedos, perspectiva, apoios, espelhos); **contradição física** (sombra, reflexão, gravidade, comportamento dos materiais); **tratamento excessivo** (nitidez, textura, saturação, blur). A taxonomia tem 33 problemas com reconhecimento, motivo perceptivo, comportamento esperado, correção e frase operacional.

Um sinal isolado não prova IA. Iluminação uniforme pode ser um estúdio real; pele lisa pode resultar de maquiagem, retouch ou distância; acessórios repetidos podem ser peças fabricadas iguais. A suspeita útil é uma contradição verificável: por exemplo, vários dedos unidos a uma mesma falange, colar atravessando tecido sem oclusão, curva de copo incompatível com a refração. **I**, apoiada por princípios físicos e casos observados, não estudo clínico do cérebro.

Pergunta de revisão: “qual relação específica deixou de fechar?” Trocar “parece fake” por “o pé toca o chão, mas o ponto de apoio não tem mudança de iluminação/oclusão compatível” permite uma correção localizada. Se a região não está visível, marcar REVIEW, não inventar aprovação ou defeito.

## 3. Como fotografias reais se diferenciam

Fotografar impõe restrições simultâneas. Uma única posição de câmera organiza os tamanhos relativos; luz encontra os mesmos objetos que aparecem nas ocultações; materiais respondem a essa luz com brilho, absorção e transmissão diferentes; foco/exposição afetam o conjunto de maneira explicável. O JPEG pode depois receber ajustes locais; isso não apaga a necessidade de geometria coerente. **D/I**

Não existe uma aparência única: sol direto pode revelar relevo; luz ampla pode escondê-lo; flash pode achatar sombras; catálogo pode ter fundo branco uniforme. No corpus há cenas limpas e cenas ruidosas, forte e fraco contraste. A diferença útil é uma explicação causal compatível com o propósito da captura, não uma lista fixa de defeitos. Veja o [atlas](REFERENCE_ATLAS.md). **O**

Transferir uma referência significa manter relações: razão de preenchimento, altura de câmera, proximidade, plano de foco, posição de highlights. Copiar o rosto, a roupa ou uma marca não é necessário para transferir a lógica fotográfica.

## 4. Física da iluminação

### Direção e leitura do volume

| Direção | Comportamento plausível | Decisão concreta / limite |
|---|---|---|
| Frontal | Sombras projetadas ficam atrás; contraste facial pode ser baixo | Descrever fonte perto do eixo, não remover toda sombra em pálpebras, cabelo e roupa. |
| Lateral | Gradiente entre lados; nariz/objetos bloqueiam luz | Preservar lado em sombra e preenchimento do ambiente; não desenhar brilho igual nos dois lados. |
| Cerca de 45° | Modelagem entre frontal e lateral | Informar lado e elevação; “45°” sem convenção é ambíguo. |
| Contraluz | Separação de borda, transmissão em partes finas e frente potencialmente escura | Exigir fonte atrás; não contornar todo sujeito igualmente, inclusive partes ocultas. |
| Superior | Sombra sob sobrancelhas, nariz, queixo; superfícies voltadas para cima recebem mais | Fonte grande pode suavizar; luz superior não implica olhos pretos obrigatórios. |
| Inferior | Sombra sobe e volumes ficam incomuns | Plausível perto de tela/chão/refletor; não usar como luz cotidiana sem justificativa. |
| Ambiente | Contribuições de céu, paredes, portas e luminárias | “Ambiental” não significa campo uniforme, nem fonte independente sem origem. |
| Múltiplas | Sombras/reflexos podem ter mais de uma direção | Identificar dominante e secundárias; algumas sombras ficam preenchidas por outra fonte. |

Essas são inferências geométricas para direção, não promessas de um padrão obrigatório em cada rosto. O modelo de [transporte de luz](https://www.pbr-book.org/4ed/Light_Transport_I_Surface_Reflection/The_Light_Transport_Equation) sustenta a dependência entre geometria, incidência e resposta do material. **D/I**

### Tamanho aparente

O tamanho **angular visto pelo sujeito** importa: uma janela grande próxima pode ocupar muito do campo; uma janela igualmente grande distante pode ocupar pouco. Para uma fonte plana centrada e frontal de largura `w` a distância `d`, estimativa geométrica: `α ≈ 2 arctan(w / (2d))`. Uma largura de 1 m a 1 m dá aproximadamente 53°; a 4 m, 14°. É um cálculo ilustrativo, não reconstrução de referência.

Uma fonte extensa distribui direções incidentes: o bloqueio tende a produzir penumbra mais ampla; a pequena favorece transições mais firmes. Superfície rugosa também espalha reflexo, portanto highlight largo **não identifica sozinho** uma fonte grande. Fonte e material precisam ser separados. [Area Lights](https://pbr-book.org/4ed/Light_Sources/Area_Lights), [Microfacet Theory](https://www.pbr-book.org/4ed/Reflection_Models/Roughness_Using_Microfacet_Theory). **D/I**

Na pele, a luz rasante pode salientar relevo; luz frontal ampla e baixa resolução podem ocultá-lo. Não exigir sombra dura para demonstrar poros. Em plástico/metal, a forma aparente da fonte contribui para o highlight; em superfície áspera, a forma fica menos definida.

### Distância e queda de intensidade

Para fonte pontual isotrópica em espaço livre, o fluxo se distribui por áreas crescentes: contribuição ao plano depende de `1/r²` e do ângulo de incidência. Dobrar distância reduz a contribuição para 1/4, cerca de dois stops, **mantidas potência e geometria pertinente**. [PBRT: Point Lights](https://www.pbr-book.org/4ed/Light_Sources/Point_Lights). **D**

Não aplicar essa conta cegamente a janela próxima, softbox finito, teto emissor, luz rebatida ou sol. Uma fonte extensa exige integrar contribuições; o sol não perde visivelmente dois stops entre rosto e fundo a poucos metros. Fonte próxima pode gerar gradiente importante entre pontos próximos/distantes; fonte afastada tende a produzir distribuição mais uniforme em um sujeito pequeno. Mover fonte altera também tamanho angular e direção: não é um teste isolado de intensidade sem controles. **I**

### Rebatedores e color spill

Uma parede bege iluminada pode devolver contribuição quente às superfícies orientadas para ela; não pinta toda a pessoa de bege. Roupa rosa pode contribuir sutilmente sob o queixo; piso pode clarear parte inferior; superfícies escuras reduzem preenchimento. Intensidade depende de reflectância, área visível, distância e ângulo. Vidro pode redistribuir luz concentrada, mas não é obrigatório desenhar caustics em toda cena. **D/I**, [transporte de luz](https://www.pbr-book.org/4ed/Light_Transport_I_Surface_Reflection/The_Light_Transport_Equation).

Instrução aplicada: “janela à esquerda e acima; lado direito recebe preenchimento fraco das paredes claras; piso de madeira contribui discretamente para superfícies voltadas para baixo; nada de rim light sem fonte”. As relações são mais úteis que “perfect lighting”.

## 5. Sombras

**Sombra própria** ocorre onde a superfície deixa de receber a fonte por orientação ou bloqueio local. **Projetada** depende do objeto que bloqueia e da superfície receptora. **Umbra** corresponde ao bloqueio completo de uma fonte; **penumbra**, ao parcial. Luz de outras origens pode continuar chegando: sombra de uma fonte não é ausência de toda luz.

Em configuração simples de fonte extensa, o afastamento entre bloqueador e superfície costuma alargar penumbra; perto do apoio, a transição tende a ser mais estreita. Chão irregular, difusão, várias fontes ou objeto translúcido modificam essa expectativa. A direção no quadro não precisa ser idêntica em planos diferentes: projetar o mesmo raio num chão e numa parede produz trajetórias aparentes distintas. **I**, geometria aplicada a [fontes extensas](https://pbr-book.org/4ed/Light_Sources/Area_Lights).

**Contato:** conferir pé/chão, frasco/bancada, mão/objeto e roupa/pele. A proximidade reduz direções de luz disponíveis, criando escurecimento localizado em muitas situações. Não fabricar um contorno preto universal. Um apoio em superfície branca muito preenchida pode ter sombra pouco visível; objeto transparente pode ter sombra transmissiva/colorida.

**Ambient occlusion:** é uma aproximação de visibilidade ambiental, não uma “tinta preta” adicionada à borda e nem solução para toda iluminação indireta. O que importa fotograficamente é se luz consegue chegar à cavidade. A cor residual depende das fontes/rebatedores, não de um parâmetro universal de sombra cinza.

Reconstrução de shadow map manual: marcar fonte dominante; listar bloqueadores; identificar superfícies receptoras; comparar penumbra perto/longe; procurar preenchimento. Só declarar FAIL quando a configuração proposta não consegue explicar o resultado. Sombra sob um olho não deve ser corrigida como olheira sem separar luz de pigmentação.

## 6. Pele humana

A pele tem resposta superficial e contribuição abaixo da superfície; ambas variam espacialmente. [Debevec et al.](https://www.pauldebevec.com/Research/LS/) medem esse comportamento, que não é equivalente a sobrepor uma textura. Brilho localizado de oleosidade e reflexão da fonte precisam coexistir com cor e relevo. **D**

Para geração, tratar três escalas. **Grande:** volume, anatomia e gradação de luz. **Média:** tonalidade regional, pequenas marcas da identidade, maquiagem, vermelhidão plausível. **Pequena:** poros, pelos e linhas resolvidos apenas onde foco, distância e resolução permitem. Não prescrever poros com igual contraste em testa, pálpebra, lábio e braço. Essa adaptação por região é direção anatômica/fotográfica **I**, não diagnóstico dermatológico.

Lábios podem apresentar sulcos finos e brilho que acompanha curvatura; bordas não são um adesivo perfeito. Sobrancelhas têm raiz/direção e densidade variável; cílios fazem oclusão e não surgem como arcos sólidos; pelos finos só aparecem quando contraste e escala resolvem. Barba deve seguir implantação do sujeito, não textura facial genérica. Olheiras e manchas não devem ser acrescentadas para “ficar humano” se mudam identidade ou idade aparente.

**Translucidez/SSS:** partes finas sob luz atrás podem apresentar transmissão avermelhada; diffusion altera transição em escala apropriada. Não aplicar luz vermelha em todos os contornos, inclusive os que não recebem contraluz. [Jensen et al.](https://graphics.stanford.edu/papers/bssrdf/) sustentam transporte subsuperficial, não glow decorativo. **D/I**

Rosto pequeno no quadro pode ter pele lisa sem ser artificial. Redução de ruído, compressão, lente, movimento, foco e retoque mudam o detalhe publicado. Uma ampliação interpolada não revela poros que a captura não registrou. Para Nina, preservar sinais das canônicas e silhueta aprovada; não adicionar sardas de outra modelo, mudar textura para envelhecer ou afinar progressivamente o corpo.

Instrução: “volume e tonalidade coerentes com a luz; brilho discreto nas regiões orientadas para a fonte; detalhes cutâneos apenas na escala visível; sem alisamento plástico nem poros gravados com igual contraste em toda a pele”.

## 7. Cabelo

Fibras refletem/transmitem luz de maneira direcional; a aparência inclui componentes distintos de highlight. [Marschner et al.](https://www.cs.cornell.edu/~srm/publications/SG03-hair.pdf) fundamentam a resposta de fibras, não apenas “milhares de fios ultra detalhados”. **D**

Aplicação **I**: modelar massa e mechas primeiro, sombras internas depois, fios individuais por último. Grupos acompanham raízes, curvatura, gravidade e penteado. O brilho pode formar faixa atravessando mechas; cada fio não precisa ter sua própria faixa branca. Bordas com fios soltos devem permitir fundo entre eles; em contraluz, alguns podem ficar claros, enquanto outros continuam escuros por oclusão. Fios à frente do rosto deixam pequenas sombras se a fonte favorece isso.

Erros de aparência: mechas fundidas à orelha/roupa, fios sem origem, bandas de brilho idênticas, contorno sólido sem transição, todos os fios nítidos apesar do foco. Correção: recuperar continuidade, agrupamento e profundidade; não transformar Nina em outra cor de cabelo para obter brilho.

Instrução: “cabelo castanho-escuro canônico em mechas com espessuras variadas; brilho seguindo orientação e curvatura, sombras entre grupos e poucos fios soltos compatíveis com o penteado; fios fora do plano de foco discretamente menos definidos”.

## 8. Tecidos e roupas

A aparência depende de fibra, trama, acabamento e ângulo, não só nome do material. [Irawan/Marschner](https://www.cs.cornell.edu/~srm/publications/TOG12-cloth.html) medem tecidos naturais/sintéticos e suas diferenças de reflexão. **D**. A matriz abaixo é uma direção **I**, condicionada a estrutura/espessura/acabamento reais; não um classificador universal.

| Material / estrutura | Forma e luz plausíveis | Erro a evitar |
|---|---|---|
| Algodão tecido comum | Dobras médias, reflexão difusa relativamente ampla, fios só em escala suficiente | Brilho espelhado de plástico em peça fosca. |
| Linho | Trama/irregularidade possível, vincos marcados quando usado | Distribuir rugas aleatórias sem costura/apoio. |
| Jeans | Rigidez relativa, dobras mais largas, espessura em bainha/costura, desgaste contextual | Caimento de seda ou fibras gigantes de longe. |
| Poliéster | Pode ser fosco ou brilhante; depende de filamento e acabamento | Tratar toda peça sintética como vinil. |
| Seda / cetim | Reflexão direcional, highlight atravessa dobras; caimento depende de espessura | Pintar degradê luminoso uniforme sem relação com dobra. |
| Couro | Folha com espessura, vincos/compressão, brilho conforme acabamento | Escamas/riscos genéricos, costura que some, elasticidade excessiva. |
| Malha / roupa esportiva | Estrutura de laços e elasticidade; tensão ao redor de articulações e apoios | Ondas soltas em peça esticada, compressão mudando anatomia. |

**Gravidade e tensão:** parte pendurada tende a cair; tecido tracionado organiza pregas entre pontos de ancoragem; compressão cria dobras perto de articulação/sentado. Costura muda tensão e espessura; dobra tem lado iluminado, cavidade e oclusão. Não inventar muitas rugas onde malha está lisa por tensão. Roupa colada não deve virar pele pintada: gola, cava, bainha e costura ainda têm limites físicos.

Para o macaquinho preto: preservar forma real do produto, costuras, opacidade e acabamento conforme referência oficial. Não clarear todo preto até cinza; sombras podem ocultar detalhe. Ao girar pose, tecido e apoios precisam se adaptar, mantendo corpo canônico. Selecionar análise específica da roupa se o produto exigir propriedades não cobertas aqui.

## 9. Materiais e objetos

Rugosidade modifica distribuição de reflexo; interfaces dielétricas e condutores têm respostas distintas. [Microfacet Theory](https://www.pbr-book.org/4ed/Reflection_Models/Roughness_Using_Microfacet_Theory), [Dielectric BSDF](https://www.pbr-book.org/4ed/Reflection_Models/Dielectric_BSDF), [Conductor BRDF](https://www.pbr-book.org/4ed/Reflection_Models/Conductor_BRDF). **D**. Estas regras de direção por objeto são síntese **I**; o acabamento e a referência oficial prevalecem.

| Material | Relação a preservar | Imperfeição contextual |
|---|---|---|
| Vidro | Transmissão/refração, espessura em bordas, reflexo angular, conteúdo visto através | Impressão digital em objeto manuseado; nenhuma obrigatória em produto preparado. |
| Metal | Reflexos do ambiente, curvatura e rugosidade/acabamento; peças escovadas podem ser direcionais | Microarranhões concentrados por uso, apenas se resolvidos. |
| Plástico | Opacidade/translucidez e acabamento específico; molde e juntas coerentes | Marca de uso em região tocada; não “pele” granular em plástico liso. |
| Madeira | Veios contínuos e orientação física; verniz altera brilho | Desgaste em bordas/contato, não padrões de corte impossíveis. |
| Pedra | Granulação/veios conforme tipo; polida pode refletir, fosca dispersar | Lascas ou marcas apenas compatíveis com estado do objeto. |
| Cerâmica | Esmalte brilhante sobre forma consistente ou superfície fosca | Craquelado não obrigatório; não confundir com porcelana translúcida em todo caso. |
| Papel | Espessura fina, dobra/curvatura, reflexão geralmente difusa; revestido pode brilhar | Vinco ligado ao manuseio; impressão acompanha plano/deformação. |
| Tecido | Fibras/trama e dobras em escalas separadas | Desgaste perto de uso/atrito, não ruído uniforme. |
| Água | Superfície/menisco, reflexão/transmissão e movimento; recipiente redefine geometria | Ondulação após gesto, gotas quando há motivo; não onda num copo parado sempre. |

O highlight é uma imagem/modulação do campo de luz pela superfície, não uma tinta branca fixa. Pode vir de janela **fora do quadro**. Antes de chamar “reflexo impossível”, tentar explicar superfície, câmera e ambiente. A foto de produto [Profoto](https://www.fimeko.fi/pdf/Creating_long_and_even_highlights_with_softboxes.pdf) ilustra controle real; o atlas distingue informações fornecidas e deduções.

## 10. Câmera e lente

**Perspectiva:** numa aproximação pinhole, tamanho projetado é proporcional a `f·tamanho/distância`. Mantida a posição, mudar focal altera framing, não a razão de tamanho entre partes. A “compressão de tele” normalmente vem de afastar a câmera para recompor. [Telephoto Lenses](https://www.cambridgeincolour.com/tutorials/telephoto-lenses.htm). **D**

Exemplo geométrico **I**: se um nariz fica a 0,30 m e a região do rosto de comparação a 0,40 m, a ampliação relativa é 0,40/0,30 ≈ 1,33; a 1,50 e 1,60 m, ≈ 1,07. Não é medição anatômica nem prescrição fixa: mostra por que distância importa. Em braço estendido, antebraço próximo pode crescer um pouco; não tornar todos os planos do corpo iguais para “corrigir” perspectiva. Escolher posição que reduza diferença excessiva, mantendo selfie possível.

**Selfie direta:** telefone que está capturando normalmente fica fora do quadro; pode haver braço visível. **Espelho:** a traseira do telefone pode aparecer e o caminho óptico inclui espelho; foco/perspectiva respondem à imagem virtual. Não atribuir a câmera aos olhos da modelo. Para preservar pose aprovada, editar só o necessário e manter posição/altura/distância lógica.

**Focal equivalente versus física:** declarar qual convenção. “26 mm equivalente” descreve campo, não implica lente física de 26 mm num celular. Abertura f/1.8 num sensor pequeno não produz automaticamente o desfoque de full frame f/1.8. Campo, tamanho de sensor, distância e modo de processamento precisam fechar juntos. [Projective Camera Models](https://www.pbr-book.org/4ed/Cameras_and_Film/Projective_Camera_Models), [Depth of Field](https://www.cambridgeincolour.com/tutorials/depth-of-field.htm). **D/I**

**Tempo:** motion blur depende de movimento relativo e duração; estabilização pode compensar câmera, não parar mãos/cabelo. **ISO:** altera ganho/resposta/pipeline; não aumenta fótons coletados. Pouca exposição e amplificação tornam ruído mais aparente, mas denoise e merge modificam o JPEG. [Camera Exposure](https://cdn.cambridgeincolour.com/tutorials/camera-exposure.htm), [Noise](https://www.cambridgeincolour.com/tutorials/image-noise-2.htm). **D**

| Efeito | Condição que justifica | Regra aplicada |
|---|---|---|
| Aberração cromática | Lente/cena podem produzir franja, frequentemente mais visível em bordas de alto contraste | Não colocar arco-íris em todo contorno; correções ópticas podem removê-lo. |
| Vinheta | Geometria óptica/abertura/processamento | Não escurecer bordas por padrão; verificar referência. |
| Flare | Fonte intensa atingindo lente, até fora do quadro | Posição e resposta óptica coerentes; ausência não é defeito. |
| Bloom / halation | Espalhamento/captura/processamento ou filme apropriado | Não cercar pele/cabelo com glow universal. |
| Difração | Apertura suficientemente pequena frente ao comprimento de onda e amostragem | Não exigir detalhes ilimitados ao fechar diafragma; não simular blur pesado só para “parecer câmera”. |
| Distorção de lente | Curvatura de linhas por modelo óptico | Diferenciar de convergência por inclinação/perspectiva. |
| Rolling shutter | Leitura temporal com movimento de câmera/objeto | Só relevante com movimento e leitura apropriados; não deformar selfie parada. |

Fontes: [Flare](https://www.cambridgeincolour.com/tutorials/lens-flare.htm), [Lens Corrections](https://www.cambridgeincolour.com/tutorials/lens-corrections.htm), [Diffraction](https://www.cambridgeincolour.com/tutorials/diffraction-photography.htm), [Sony electronic shutter](https://helpguide.sony.net/ilc/2440/v1/en/contents/0414L_electronic_shutter.html). **D/I**. Estas condições não significam que tais defeitos devem ser adicionados.

## 11. Profundidade de campo

Foco nítido não vira desfoco num degrau sem motivo; transição depende da distância ao plano focado, abertura e projeção. O circle of confusion é um critério de blur tolerável, dependente da ampliação/exibição. Bokeh descreve qualidade do desfocado, não a extensão da zona aceitavelmente nítida. [Depth of Field](https://www.cambridgeincolour.com/tutorials/depth-of-field.htm). **D**

Aplicação **I**: identificar três planos e o foco. Uma mão mais perto que os olhos pode ser menos nítida; um objeto do fundo à mesma distância de outro tende a ter blur compatível, salvo diferenças locais de contraste/movimento. Fios de cabelo transparentes não devem parecer máscara de recorte rígida. Se houver modo retrato computacional, pequenos erros de segmentação são possíveis, mas não obrigatórios nem uma desculpa para cabelo impossível.

Bokeh circular/poligonal depende da abertura/lente; próximo às bordas pode mudar forma. Não espalhar bolas luminosas se não há fontes/pontos claros no fundo. Nem todo fundo deve desaparecer: celular, cena ampla e distâncias grandes ao foco podem manter ambiente legível. O teste fotografado R07 mostra transição coerente, não prova qual prompt funcionará.

## 12. Exposição e faixa dinâmica

Separar luminância física, sinal capturado e brilho publicado. A faixa da cena pode exceder a câmera; a curva de apresentação reorganiza os valores. Clipping elimina diferença em uma região/canal; não é apenas uma área visualmente clara. Highlight roll-off percebido pode vir de resposta/curva/compressão tonal; não se deduz RAW do JPEG. [Dynamic Range](https://www.cambridgeincolour.com/tutorials/dynamic-range.htm). **D/I**

Selecionar prioridade de exposição: rosto numa selfie, rótulo no produto, ambiente no interior. Manter diferenças de luminosidade; aceitar sombra com menos detalhe e brilho pontual saturado **quando o contexto pede**, sem fabricar janela branca em foto HDR bem capturada. Em roupa preta, cavidades podem ficar pouco legíveis; não recuperar costura em todos os pontos ao mesmo nível.

O [HDR+](https://research.google/pubs/burst-photography-for-high-dynamic-range-and-low-light-imaging-on-mobile-cameras/) demonstra fotografia real com maior faixa dinâmica e menos ruído usando múltiplos frames. “Tudo está relativamente legível” não prova geração; o problema é luminância achatada ou gradientes que contradizem a luz pretendida. **D/O/I**

Instrução: “exposição prioriza o rosto; janela permanece mais clara que parede e lado em sombra; detalhe reduzido nas cavidades, sem levantar o ambiente inteiro até o nível da pele; processamento de celular moderado, sem halos”. Não exigir clipping, não proibir HDR técnico. Latitude varia por sensor/pipeline; não inventar número de stops sem modelo/medição.

## 13. Color science

White balance adapta a cor a uma referência; Kelvin descreve tendência de fonte/WB e tint lida com eixo verde–magenta. Fontes de mesma temperatura correlacionada podem ter espectros diferentes. Com luz mista, um único WB pode deixar regiões diferentes. Não recuperar temperatura exata da foto apenas pela cor da pele. [White Balance](https://www.cambridgeincolour.com/tutorials/white-balance.htm). **D**

Aplicação **I**: distinguir **cor do objeto**, **cor da luz**, **reflexão ambiental** e **tratamento**. Uma bolsa rosa não obriga rosa no branco de toda a imagem. Luz de janela mais fria com luminária quente pode coexistir; explicar onde cada uma incide. Preservar nuance da pele e branco do ambiente sem tornar todos os tons neutros artificialmente.

Color grading cinematográfico é escolha válida quando a intenção é cinema; não padrão para selfie doméstica. Teal & orange, dourado e contraste local excessivos podem trocar o material e cenário percebidos. Em Nina, a paleta rosa/creme pertence também à camada gráfica; não se deve contaminar sua pele para “combinar”. Curva tonal deve respeitar gradação; highlight claro não precisa ganhar amarelo saturado. Saturação excessiva em sombras pode indicar amplificação/tratamento, não necessariamente objeto realmente saturado.

Instrução: “WB doméstico plausível, brancos levemente influenciados pelas fontes; tons de pele canônicos, sem filtro laranja geral; rosa vem dos objetos/elementos da marca; curva moderada e contraste local discreto”.

## 14. Imperfeições naturais e composição

Não maximizar quantidade de imperfeições. Escolher zero, uma ou poucas, com causa e região. Esta classificação é procedimento editorial **I**, não receita empiricamente provada de aumentar realismo.

| Classe | Exemplos | Quando usar / quando não usar |
|---|---|---|
| FÍSICAS | Dobra, arranhão de uso, borda irregular | Estado real do objeto e interação sustentam; não estragar produto novo. |
| ÓPTICAS | Desfoco, flare, distorção, franja | Apenas captura/lente/luz permitem; excluir se ausência é plausível. |
| HUMANAS | Assimetria discreta, mecha solta, expressão incompleta | Preservar sujeito, gesto e identidade; não adicionar idade/doença/manchas. |
| AMBIENTAIS | Objeto parcialmente oculto, cabide, luz rebatida irregular | Cena justifica; não bagunçar catálogo limpo nem inventar decoração genérica. |
| DE CÂMERA | Ruído, pequeno tremor, exposição limitada, compressão | Pipeline e condições explicam; não aplicar grain forte a foto clara limpa. |

**Composição natural:** pode ser central ou assimétrica; não declarar centralização um erro. Considerar motivo do enquadramento: selfie alcançável, produto lido, negativo para headline, gesto espontâneo. Horizonte/verticais respondem à altura/inclinação; linhas de fuga devem permanecer consistentes. Um foreground cortado cria camada se pertence ao espaço; não inserir objeto aleatório para dar profundidade.

Partes fora de quadro não exigem anatomia inventada. Deixar cotovelo cortado pode ser plausível; cortar dedo no ponto errado não deve fundi-lo com telefone. Preservar foto aprovada em edição de post: textos, swashes e doodles são gráficos sobrepostos, não objetos que devem receber sombras da cena. Composição gráfica do perfil permanece a autoridade do usuário.

## 15. Integração sujeito/cenário

Pessoa e produto precisam compartilhar **campo de luz, perspectiva, escala, apoio, oclusão, foco e processamento**. Não basta igualar temperatura global. Uma pessoa pode receber janela lateral e parede de fundo luz difusa, mas diferenças precisam ser explicáveis pela posição. **D/I**, [transporte de luz](https://www.pbr-book.org/4ed/Light_Transport_I_Surface_Reflection/The_Light_Transport_Equation).

Mapa de integração: onde toca? o que está à frente? que fonte vê? qual superfície reflete? a que distância está do foco? Em espelho, revisar continuidade da pessoa/telefone e paridade da cena; não inverter tatuagem só porque “selfie é espelhada” sem rastrear a transformação. Relógio/colares pertencem ao corpo, com encaixe, peso e ocultação; não mudar a dimensão de um produto por estética.

A atmosfera em distâncias grandes pode reduzir contraste; em quarto pequeno, haze uniforme geralmente não tem justificativa. Mesma nitidez não é obrigatória, mesmo processo de captura é. Blur por profundidade, ruído por exposição e correções locais podem coexistir. Borda demasiado nítida contra cenário com suavização cria aparência de recorte; corrigir transição e foco antes de adicionar sujeira.

## 16. Padrões descobertos nas referências

O [atlas](REFERENCE_ATLAS.md) cobre nove casos com proveniência documentada e dois pins reinspecionados de autenticidade não verificada. As comparações de uma mesma cena não contam como amostras independentes. **O**

Padrões repetidos: detalhe depende do plano/contraste; highlights diferem por material; áreas ocultas e fora do quadro são comuns; fontes podem estar fora da composição; a exposição/processamento altera legibilidade sem mudar objetos. Não apareceu uma exigência universal de poros fortes, grão, flare ou clipping. **O**

Exceções importam: retrato retocado tem aparência muito limpa; produto preparado tem reflexos controlados; foto computacional pode conservar altas luzes e melhorar sombra. Logo, nossas regras devem exigir coerência causal e preservar escolhas reais, não punir limpeza/controle. **I**

Limites: amostra intencional, não representativa; sem testes perceptivos próprios; sem RAW; cobertura reduzida de tecidos/materiais específicos e variedade de tons de pele. A análise técnica amplia mecanismos, mas não autoriza dizer que todas as hipóteses visuais foram verificadas em cada categoria.

## 17. Técnicas de maior impacto

Ordem recomendada **I**, baseada no custo das contradições, ainda sem ranking experimental no provider:

1. Fixar identidade, geometria e posição de câmera antes de detalhe.
2. Definir fonte dominante, bloqueadores e preenchimento concreto.
3. Reproduzir apoio/oclusão/reflexos da interação.
4. Diferenciar material e acabamento; preservar referência oficial do produto.
5. Definir plano de foco e exposição, mantendo relações de luminosidade.
6. Limitar detalhe à escala realmente visível.
7. Preservar tratamento moderado e imperfeições causais.
8. Revisar o arquivo final, com evidência e correção focalizada.

Os princípios têm respaldo técnico; **a ordem de eficácia e as frases de prompt são hipóteses aplicadas**, não melhoria percentual medida. “85 mm”, “poros” e “natural lighting” isolados não fecham uma cena. Referências anexadas + instruções de relação + QA reduzem ambiguidades, mas não garantem fidelidade automática.

## 18. Técnicas que podem deixar a imagem mais artificial

“8K/masterpiece/ultra detailed/hyperrealistic/cinematic/perfect lighting” não especificam causa física. Podem funcionar como preferência estilística em um provider, porém não são garantia de fotografia. Não afirmar que cada palavra sempre piora resultado; isso depende do modelo e requer comparação.

Evitar: poros iguais em todas as regiões; grain como véu uniforme; brilho branco em toda borda; flare sem fonte; desfoque por recorte sem profundidade; saturação dourada universal; cada fio perfeitamente nítido; arranhões aleatórios; textura ampliada em objetos distantes; “imperfeição” que muda rosto/idade/corpo; sombra preta de contorno para fingir contato.

Sharpening excessivo pode produzir bordas/texture unnatural; denoise pode apagar informação. [Adobe Camera Raw](https://helpx.adobe.com/ca/camera-raw/desktop/using/sharpening-noise-reduction-camera-raw.html) documenta ajustes de borda e ruído, sustentando revisão em 100%, não um preset obrigatório. **D/I**

Em edição da foto aprovada, regenerar toda a cena para “adicionar realismo” é uma mudança de escopo que pode perder pose e produto. Pedir preservação fotográfica e adicionar apenas design via gerador atende melhor à tarefa do usuário.

## 19. Checklist anti-IA

O [REALISM CHECK](REALISM_CHECK.md) separa anatomia, mãos, olhos, dentes, cabelo, pele, roupa, gravidade, perspectiva, escala, iluminação, sombras, contato, reflexos, materiais, DOF, bokeh, exposição, textura, fundo, integração e artefatos; acrescenta identidade, espelhos, texto e efeitos ópticos contextuais.

Cada item recebe PASS / REVIEW / FAIL / N/A; registrar região e justificativa. PASS vale somente para o que é visível e foi inspecionado. Não usar nota numérica inventada. Um defeito constatado é FAIL; falta de evidência é REVIEW; N/A exige motivo real. Vincular a imagem final e referências por SHA-256. Uma imagem intermediária aprovada não aprova automaticamente o novo arquivo editado.

Correção: registrar problema original, trecho físico a corrigir, invariantes, tentativa e novo resultado. Para Nina, seguir as regras existentes de recuperação, duas canônicas e no máximo uma correção por tentativa. Não regenerar em loop. A checklist manual complementa QA existente, sem novo gate automático.

## 20. Sistema final para reprodução

**Input:** referência visual inspecionada, sujeito/produto autorizado, situação desejada, formato e invariantes. **Output:** especificação fotográfica e prompt executável, com campos desconhecidos honestos e QA planejado.

**Procedimento de 17 leituras:** composição; câmera; lente estimada; perspectiva; iluminação; sombras; highlights; exposição; DOF; cores; texturas; pele; cabelo; roupa; ambiente; imperfeições; mecanismos de realismo. O [template](PROMPT_TEMPLATE.md) define evidência, adaptação e verificação para cada leitura.

**Conversão:** escrever primeiro a configuração espacial e a captura, depois materiais/identidade, depois exposição/tratamento. Trocar descrições vagas por relações: “luz ampla à esquerda, sombra direita com fill fraco”, “foco no rosto; mão próxima ligeiramente menos definida”, “metal polido reflete fontes fora do quadro”. Selecionar somente efeitos justificáveis. Não preencher todo UNKNOWN com falso EXIF.

**Geração:** anexar referências com papéis distintos. Para Nina, rosto/corpo vêm das canônicas; produto da fonte oficial; cena do Pinterest aprovado/usuário; elementos gráficos do DNA do perfil. O módulo compacto reforça essas relações, sem substituir mapa/brief. Geração visual e elementos de post permanecem no gerador de imagens por orientação do usuário.

**Revisão/aprendizado:** inspecionar resultado em tamanho de publicação e 100%; aplicar checklist; corrigir apenas falha observada e revalidar hash. Protocolos [A/B](AB_PROTOCOLS.md) isolam variável quando possível. Sem seed/controlabilidade do provider, manter resultado como comparação qualitativa, não causalidade provada. O conhecimento agora está salvo; eficácia generativa sistemática permanece pendente de execução.
