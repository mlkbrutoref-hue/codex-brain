---
name: ugc-realista
description: Gere ou edite fotos casuais de pessoas e personagens virtuais com estética UGC de smartphone, selfies no espelho, luz doméstica e textura natural de pele. Use para pedidos de aparência espontânea de celular e para manter identidade e proporções em séries dessas fotos. Também orienta prompts e workflows ComfyUI quando solicitados nesse contexto.
---

# UGC Realista

Transforme a cena pedida em uma fotografia casual convincente de celular. Preserve a intenção do usuário, com atenção à identidade, pose, iluminação, anatomia e ambiente.

Esta skill adapta o [guia compartilhado pelo usuário](https://share.gemini.google/itu8XB0xxvBS) e incorpora uma imagem de teste aprovada na conversa de origem. A aprovação foi visual e subjetiva. Os parâmetros e componentes técnicos citados no guia não foram testados nesta criação.

## Execução

- Quando o usuário pedir uma imagem, gere a imagem. Quando pedir somente um prompt ou workflow, entregue esse material.
- Para geração e edição, aplique a skill `imagegen`, disponível no ambiente de origem, e use a ferramenta integrada `image_gen`. Se o usuário especificar outra ferramenta, adapte a orientação ao recurso escolhido e às capacidades disponíveis.
- Leia [references/cenas.md](references/cenas.md) para escolher ou adaptar um exemplo. A receita de quarto com luz de janela registra o teste aprovado.
- Use informações e referências já fornecidas. Em um pedido aberto, escolha detalhes cotidianos discretos e uma pessoa adulta. Pergunte somente quando faltar algo indispensável, como uma referência necessária para preservar uma personagem específica.
- Em edições, inspecione a imagem de entrada e explicite quais características devem ser preservadas. Use mecanismos reais de referência da ferramenta.

## Construção da imagem

Organize o prompt em cena e captura, pessoa e ação, luz e materiais, restrições visuais. Prefira descrições concretas a uma sequência extensa de adjetivos de qualidade. Inglês é uma opção prática para os exemplos, mantendo a conversa no idioma do usuário.

**Captura de celular.** Para a estética padrão, descreva uma selfie casual com perspectiva de grande-angular moderada, aproximadamente 24–28 mm equivalente, e fundo reconhecível. Enquadramento levemente imperfeito e assimetria de pose ajudam quando combinam com o pedido. Escolha enquadramento de corpo inteiro, três quartos ou busto conforme a cena. Distância e posição da câmera devem combinar com a perspectiva desejada.

**Pessoa e gesto.** Defina uma ação simples, como olhar para a tela e sorrir discretamente, apoiar o peso em uma perna ou segurar o celular com os ombros relaxados. Preserve proporções plausíveis entre cabeça, pescoço, tronco e membros. Roupas confortáveis e cabelo com alguns fios soltos podem apoiar cenas domésticas, sem virar características obrigatórias.

**Espelho.** Descreva quem segura o celular, a altura aproximada e quanto ele cobre do rosto. Peça pegada plausível, dedos anatomicamente coerentes e reflexo consistente. Confira continuidade dos braços, posição das câmeras, orientação dos objetos e eventuais duplicações. A palavra “selfie” sozinha pode deixar a geometria ambígua.

**Luz.** Escolha uma situação principal que explique as sombras e os brilhos. As opções incluem luz lateral de janela, lâmpadas de penteadeira, flash refletido no espelho, quarto com pouca luz ou iluminação fria de banheiro. Acrescente uma segunda fonte apenas quando ela fizer sentido na cena. Preserve contraste e exposição plausíveis.

**Pele e materiais.** Descreva variação natural de tom, pequenas imperfeições, brilho discreto e poros proporcionais à distância da câmera. Tecidos devem apresentar dobras plausíveis. Termos como `natural skin texture`, `subtle skin imperfections` e `natural skin sheen` podem expressar a intenção. Poros exagerados, nitidez agressiva e ruído pesado prejudicam a aparência casual.

**Ambiente.** Acrescente poucos sinais de uso compatíveis com o lugar, como cama levemente desarrumada, roupa sobre uma cadeira ou cosméticos na bancada. Ajuste a quantidade à cena pedida. Bagunça, maquiagem, marcas, etnia ou um padrão corporal específico não são requisitos universais.

**Imperfeições de captura.** Quando pertinentes, use granulação discreta nas sombras, leve compressão e exposição um pouco desigual. Mantenha detalhes importantes legíveis. Evite aplicar todos os artefatos ao mesmo tempo.

## Consistência entre imagens

Quando houver uma personagem definida, registre suas características observáveis e use as referências fornecidas a cada geração ou edição. Preserve rosto, cabelo, faixa etária aparente, silhueta, proporções e marcas distintivas, respeitando mudanças solicitadas.

Diferencie no prompt a referência de identidade da referência de pose ou estilo. Uma pose de outra pessoa pode orientar a ação sem substituir o corpo da personagem. Para séries extensas, uma folha de referência em vários ângulos pode ajudar, quando necessária ao trabalho pedido.

Uma descrição como “mesma pessoa da referência” depende de a imagem realmente acompanhar a chamada. Uma seed fixa isolada não deve ser apresentada como garantia de identidade. Avalie o resultado visual e corrija desvios relevantes com uma edição focalizada.

## Restrições e revisão

Para a estética natural padrão, peça que sejam evitados pele encerada, retoque excessivo, iluminação de estúdio, bokeh intenso, proporções exageradas e aparência de renderização. Adapte essas restrições quando o usuário pedir um efeito específico, como flash estourado ou fundo desfocado.

Use um campo de negative prompt apenas se a ferramenta ou workflow realmente o suportar. Em ferramentas de linguagem natural, expresse as restrições no próprio pedido. Tokens de LoRA como `s3lfi3` só devem ser usados quando o recurso correspondente estiver ativo e documentado.

Inspecione o resultado disponível antes de entregar. Confira correspondência com o pedido, pose, mãos, espelho, proporções, textura na escala correta, luz e identidade quando aplicável. Corrija defeitos salientes com a menor alteração necessária. Não prometa anatomia perfeita ou realismo garantido por palavras do prompt.

## Quando o usuário pedir ComfyUI

Leia [references/comfyui.md](references/comfyui.md). Verifique componentes e compatibilidade antes de fornecer parâmetros executáveis. A orientação visual desta skill pode ser aplicada diretamente no gerador integrado, sem afirmar que LoRAs, ControlNets ou nós externos foram usados.
