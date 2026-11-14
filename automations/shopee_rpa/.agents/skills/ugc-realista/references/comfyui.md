# Aplicação em ComfyUI

Consulte esta referência somente ao montar, explicar ou revisar um workflow técnico solicitado pelo usuário.

O guia de origem propõe modelos Flux e SDXL, LoRAs de fotografia casual, referências de identidade, controle de pose, profundidade, detalhamento de pele e upscale. Trate a combinação como uma proposta a verificar. A imagem aprovada nesta conversa foi feita com o gerador integrado e não validou esses componentes.

## Decisões antes da implementação

- Identifique checkpoint e versão, recursos instalados, referências disponíveis e limitações de hardware. Reaproveite o workflow do usuário quando houver um.
- Consulte documentação oficial, model cards dos autores e repositórios dos nós para conferir compatibilidade. Registre a versão e a origem dos componentes realmente usados.
- Distinga guidance do modelo, CFG do sampler e suporte a negative prompt. Confirme como o workflow implementa cada controle antes de propor valores.
- Verifique base, versão, trigger words e peso recomendado de cada LoRA. Nomes citados no guia servem como pistas de pesquisa, sem pressupor disponibilidade ou adequação.

## Estrutura adaptável

Use uma referência de identidade ou LoRA de personagem quando o pedido exigir repetição consistente. Acrescente condicionamento de pose quando houver uma pose a seguir. Profundidade ou controle de superfície corporal podem ser considerados se o esqueleto sozinho não preservar a composição desejada e existirem componentes compatíveis.

Inspecione os mapas de controle antes da geração. Ajuste enquadramento, resolução e proporções para evitar que uma pose de referência transfira características corporais indesejadas. A folha de personagem deve apresentar proporções coerentes entre vistas.

Introduza componentes conforme uma necessidade observada. A combinação de OpenPose, DensePose e Depth precisa de compatibilidade e teste próprios. A existência de um preprocessador não comprova que o modelo carregado aceite seu resultado como condicionamento.

Após uma imagem base satisfatória, avalie se detalhamento localizado ou upscale é necessário. Compare rosto, silhueta, dedos e textura antes e depois para detectar mudanças de identidade ou anatomia. Entregue um workflow executável somente após conferir os nós e conexões disponíveis. Indique claramente quando a entrega for apenas um esquema proposto.

## Alegações do guia que exigem cuidado

O guia apresenta valores específicos para CFG, LoRAs, steps e treinamento. Use-os apenas como hipóteses a confrontar com a documentação e testes do modelo escolhido. Parâmetros de treinamento dependem também do conjunto de imagens, batch, resolução, otimizador e objetivo.

Não transforme a alegação de faixas fixas de importância dos primeiros 20, 30 ou 80 tokens em uma regra universal. Use uma ordem clara de informações e teste a resposta do modelo. Da mesma forma, termos de óptica e pele descrevem a intenção visual, sem garantir simulação física ou correção anatômica.

Evite transportar sintaxe de pesos, regional prompting, Clip Skip ou trigger words entre modelos e nós sem confirmar suporte. Preserve a configuração efetivamente testada e descreva os limites observados.
