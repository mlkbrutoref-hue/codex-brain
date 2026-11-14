# Direção visual antes da geração

Norma operacional do fluxo assistido, subordinada ao Brain e às instruções atuais do usuário. Não constitui implementação de um orquestrador automático.

## Ordem obrigatória

Project Brain → pesquisa recente de tendências → oportunidade → descoberta de produtos → validação Shopee → seleção → estratégia/copy → análise dos exemplos do usuário → pesquisa visual Pinterest → seleção → mapa referência/asset → direção da cena → geração → tipografia determinística → QA → pacote final.

Pesquisa de tendências e pesquisa de fotografia são etapas distintas. Pinterest não prova viralidade. Uma data de atualização de agregador não comprova a data de um post. Registrar fontes primárias e métricas observadas; desconhecido continua UNKNOWN.

## Autoridades

- Identidade: `persona_master.png` e `nina_360_master.png`, mais política compartilhada de proporções. Posts anteriores não redefinem a Nina.
- Estilo: exemplos do usuário em primeiro lugar; consultar `references/style_dna.json` e referências canônicas de marca.
- Produto: imagem oficial e fatos validados da Shopee; nunca produto parecido encontrado no Pinterest.
- Cena: fotografia Pinterest inspecionada e selecionada a partir do DNA do usuário. Não copiar rosto, corpo, texto, marca ou composição exata.

## Gate obrigatório antes do provider

1. Analisar VISUAL_DNA, COMPOSITION_DNA, LIGHTING_DNA, CAMERA_DNA, POSE_DNA, ENVIRONMENT_DNA, TEXT_PLACEMENT_DNA e LIFESTYLE_DNA.
2. Consultar `references/library.json`. Reusar referência compatível ou pesquisar nova; título de Pin sozinho não basta.
3. Inspecionar o arquivo e registrar URL, data, SHA-256, categoria, câmera, luz, composição, pose, ambiente, motivo e limitações. Não assumir autenticidade documental apenas pela aparência fotográfica.
4. Mapear cada asset para requisitos, melhor referência e adaptação. Capa e CTA fotográfico precisam de referência Pinterest; manhã, tarde e noite precisam de seleção individual. Internos podem reutilizar cena compatível, com composição distinta. Uma demonstração específica exige referência apropriada à ação.
5. Registrar WHAT_TO_KEEP, WHAT_TO_ADAPT, WHAT_NOT_TO_COPY, NINA_INTEGRATION, PRODUCT_INTEGRATION, CAMERA_DIRECTION, LIGHTING_DIRECTION e COMPOSITION_DIRECTION.
6. Entregar ao provider a referência visual de cena, as duas canônicas da Nina quando ela aparecer, o produto oficial quando aparecer, direção, realismo e regras corporais/câmera. Não substituir referências disponíveis por descrição abstrata.
7. Ausência de referência, inspeção ou análise bloqueia geração assistida. Não há validador novo de runtime implementado nesta correção. Se houver checkpoint solicitado pelo usuário, aguardar a conferência antes de gerar, mesmo com mapa completo.

A composição tipográfica e o QA existentes continuam obrigatórios. Sem evidência visual vinculada a hashes, manter REVIEW. Defeitos constatados são FAIL. No máximo uma correção por tentativa; preservar original e registrar falha, correção e resultado.

## Biblioteca e campanha atual

`references/library.json` indexa arquivos por categorias reutilizáveis; os exemplos já canônicos são registrados por caminho, sem duplicação. Os dois exemplos adicionais de feed estão preservados em `references/user/carousel/`. As fotografias Pinterest estão em `references/pinterest/`; previews com watermark ficam intactos e servem apenas à direção interna.

Campanha: `output/e2e_content_factory_test_20260927_1505/`. Mapa: `campaign/reference_map.json`. Três imagens antigas são PRE_REFERENCE_GENERATION, não aceitas, sem exclusão. A pesquisa anterior, candidatos e produtos validados permanecem preservados.

Não criar compositor paralelo: consultar `campaign/carousel_investigation.md`. O trabalho anterior de pesquisa/copy existe; renderizador integrado de carrossel não foi localizado. Registrar CAROUSEL_INTEGRATION_GAP até resolução explícita.
