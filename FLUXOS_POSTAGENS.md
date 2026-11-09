# Fluxos de produção de postagens e vídeos

## Princípio central
A **referência de identidade** determina quem aparece. O **vídeo de origem** determina o que acontece. Os dois papéis não devem ser confundidos.

## Fluxo A — Substituição de personagem em vídeo (Flow / Higgsfield)
1. Receber o **vídeo original de cada take** e a **imagem de referência correta de Nina** para aquele take.
2. Identificar, quando houver mais de uma pessoa, **qual pessoa deve ser substituída**. Preservar as demais sem alterações.
3. Vídeo original controla: sequência, movimentos, gestos, ritmo, expressão, câmera, duração, cenário, iluminação, roupa, objetos e transições.
4. Referência de personagem controla: rosto, cabelo e outras características de identidade/visual de Nina. Não copiar os traços faciais da pessoa do vídeo original.
5. Criar **um prompt final claro e conciso**, de preferência em inglês para a ferramenta, com `@` das referências quando aplicável. Mapeamento direto entre TARGET e REFERENCE.
6. Não acrescentar falas, ações, novos objetos, closes, zooms, movimentos de câmera ou mudanças de aparência que não foram pedidos.
7. Inspecionar consistência quadro a quadro: rosto, corpo, cabelo, roupa, mãos, proporções, duplicações e geometria da cena.
8. Em cada iteração, voltar às referências originais quando possível, evitando degradação por cadeias de versões geradas.

### Modelo mental
- **SOURCE VIDEO = performance + movimento + timing + câmera + cena.**
- **REFERENCE IMAGE = identidade + aparência desejada.**
- **OUTPUT = vídeo original com a substituição do alvo, sem recriar o restante.**

### Qualidade de celular
- Manter ruído, compressão, leve desfoque, limitações de exposição e luz que façam parte do vídeo original.
- Não 'melhorar' automaticamente para estética de estúdio, nitidez excessiva ou imagem cinematográfica.
- Quando o pedido mencionar vídeo de sono, preservar o aspecto casual, iluminação e qualidade de celular, sem adicionar movimentos incompatíveis.

## Fluxo B — Foto realista para postagem
1. Ler o pedido e as referências; distinguir identidade, pose, roupa, cenário e estilo.
2. Manter a identidade facial de Nina ao substituir a pessoa em uma foto.
3. Ajustar câmera, iluminação, perspectiva e proporções para integração natural.
4. Em cena com câmera fixa/tripé, **não colocar celular na mão** da personagem.
5. Respeitar ângulos solicitados (ex.: 3/4, 1/4 do rosto), enquadramento e proporção (frequentemente 9:16).
6. Resultado deve parecer foto de celular real, eventualmente um pouco imperfeita, sem 'cara de IA'.
7. Conferir rosto e anatomia antes de considerar concluído. Corrigir desvio de identidade, sem modificar o que já foi aprovado.

## Fluxo C — Vídeo curto de produto / edição de takes
- A ordem, duração e corte devem seguir exatamente as instruções do usuário.
- Quando for pedido vídeo sem áudio, exportar silencioso, sem criar narração ou trilha.
- Não repetir ações já mostradas sem solicitação; frequentemente o último quadro deve enfatizar o produto.
- Não aplicar esse padrão automaticamente a toda postagem: seguir a especificação de cada trabalho.

## Problema conhecido: Flow com áudio
- Em algumas edições relatadas, vídeos com música/voz acionaram erro semelhante a `Unable to edit the speech`.
- Para esses casos, preparar MP4 realmente sem áudio e testar projeto/sessão limpa.
- Não afirmar que isso resolve todas as falhas, nem alterar a fala quando o pedido exigir áudio.

## Padrões de aprovação
- Respeita os materiais de entrada?
- Nina mantém a mesma identidade visível do início ao fim?
- Não há novas pessoas, clones, deformações ou mudanças gratuitas?
- O visual preserva o caráter de captura por celular?
- O arquivo final tem resolução, proporção, duração e áudio especificados?
- Houve verificação real ou somente geração de prompt? Declarar a diferença.

## A documentar futuramente
Plataformas de postagem, legendas, hashtags, horários, frequência, chamadas de ação e métricas de conteúdo **não foram definidos de maneira suficiente**. Confirmar somente quando necessário para uma tarefa concreta.
