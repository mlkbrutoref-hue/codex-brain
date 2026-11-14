# Instruções para agentes

## Fotografia plausível — pesquisa e procedimento persistentes

Por solicitação do operador em 12/10/2026, antes de dirigir novas cenas fotográficas, consultar `brain/research/photographic-realism/README.md` e `PROMPT_TEMPLATE.md`; usar `PHOTOREALISM_ENGINE.txt` como reforço apenas após especificar a cena. Depois do provider, aplicar `REALISM_CHECK.md` ao arquivo final, com evidências e hashes, complementando o QA existente.

Prioridade: fotografia fisicamente plausível acima de embelezamento. Resolver câmera/geometria, luz/integração, materiais/foco e então tratamento. Não adicionar automaticamente poros, grain, sujeira, flare, aberração, bloom ou clipping; cada efeito exige causa na captura. Distinguir observação, dado documentado, estimativa e desconhecido; não inventar EXIF nem usar aparência como detector de autoria por IA.

As referências canônicas da Nina, direção corporal aprovada, imagem oficial do produto, Pinterest e DNA do perfil mantêm seus papéis existentes. Em edição somente gráfica de uma foto aprovada, preservar foto/pose/formato e alterar apenas texto/elementos pelo gerador de imagens, conforme instrução do operador. Não reluminar ou recriar a pessoa para aplicar o módulo. Esta pesquisa não altera arquitetura, implementa gate automático ou promove capability para READY; testes A/B generativos permanecem propostos até execução real.

Para trabalhos grandes neste repositório, antes de planejar ou alterar código, leia nesta ordem:

1. `brain/README.md`
2. `brain/MISSION.md`
3. `brain/CHIA.md`
4. `brain/CURRENT_STATE.md`
5. `brain/DECISIONS.md`

Depois do trabalho:

- atualize `brain/CURRENT_STATE.md` somente se o estado real do projeto mudou;
- atualize `brain/DECISIONS.md` somente se uma nova decisão arquitetural foi tomada;
- não altere o Brain desnecessariamente em toda execução;
- preserve a hierarquia e a classificação de status definidas pelo Brain.

## Referência visual obrigatória da Nina

Sempre que o trabalho envolver criar, editar ou revisar imagens ou vídeos com a personagem Nina:

- use obrigatoriamente `data/personas/nina_v1/references/persona_master.png` para identidade facial;
- use obrigatoriamente `data/personas/nina_v1/references/nina_360_master.png` para corpo, proporções, cabelo, ângulos, perfil, costas, expressões e detalhes físicos;
- trate essas duas imagens como referências canônicas complementares e de maior autoridade que referências de pose, cenário, roupa ou tendência;
- não use posts gerados anteriormente como autoridade primária sobre a aparência da Nina;
- preserve textura natural da pele, cabelo castanho-escuro longo e volumoso, olhos castanhos, proporções corporais, tatuagem e demais sinais visuais mostrados no 360;
- se uma ferramenta aceitar apenas uma imagem de personagem, priorize `nina_360_master.png` quando a cena mostrar corpo ou ângulos variados e `persona_master.png` quando for um close facial; registre essa limitação no QA.

## Referência visual obrigatória dos Stories da Nina

Sempre que o trabalho envolver criar, editar ou revisar um Story estático de produto da Nina:

- use `data/brands/nina_v1/references/story_style_master.png` como referência canônica de direção visual;
- siga `data/brands/nina_v1/references/README.md` para composição, tipografia, paleta e elementos gráficos;
- ignore o selo `da série...` mostrado no topo da referência; ele não faz parte do padrão;
- extraia o sistema visual, sem copiar o produto ou o texto da peça de referência.

Para Stories de rotina/lifestyle da Nina, separados dos Stories estáticos de produto:

- consulte `data/brands/nina_lifestyle_v1/references/README.md` e use a referência de cena mais compatível;
- combine a referência de cena com `persona_master.png` e `nina_360_master.png`;
- preserve apenas pose, enquadramento, câmera, ambiente, luz, espontaneidade e lógica de texto curto da referência;
- nunca copie a identidade da pessoa retratada na referência.
- aplique a direção corporal mais recente do usuário: silhueta um pouco mais magra, cintura mais definida e menos volume visual em braços, coxas e quadris, sem emagrecimento extremo e sem perder a anatomia natural da Nina.

## QA obrigatório de proporções

Toda criação da Nina usa `data/personas/nina_v1/proportion_rules.txt` e `proportion_negative.txt`, compartilhados por `app/creative/proportion_policy.py`. A foto facial não define perspectiva corporal. O corpo deve seguir o 360 com a direção slim-to-average aprovada, sem emagrecimento progressivo a cada geração.

Revise os sete checks anatômicos e vincule a revisão ao SHA-256 da imagem final e das referências. Sem evidência, mantenha REVIEW; defeito constatado é FAIL. Quando `anatomy_recovery.json` indicar REGENERATION_REQUIRED, execute a correção com as duas referências canônicas e revise o novo arquivo; limite uma correção por tentativa, sem loops ilimitados. A execução do provider é pelo agente Codex ou callback integrado, não pelo pipeline local sozinho.


## Pesquisa visual Pinterest obrigatória antes de gerar

Siga `docs/visual-reference-workflow.md`. Analise primeiro os exemplos do usuário e seu DNA; depois pesquise/selecione fotografias Pinterest, inspecione pixels e registre metadados em `references/library.json`. Mapeie cada asset para referência, requisitos e adaptação antes do provider. Capa, CTA fotográfico e cada Story manhã/tarde/noite exigem seleção explícita. Internos podem reutilizar cenas adequadas, sem composição idêntica. Referência oficial Shopee define produto; Pinterest define cena; as duas canônicas definem Nina.

Pinterest não substitui pesquisa recente de tendências/posts verificáveis. Não chamar referências visuais de virais sem evidência. Sem referência inspecionada e REFERENCE_ANALYSIS completo, bloquear geração assistida. Esta regra operacional não é um gate automático novo no runtime.

Campanha `output/e2e_content_factory_test_20260927_1505/` está PAUSED_AWAITING_USER_REFERENCE_CHECKPOINT. Não gerar novas imagens antes de o usuário conferir esse checkpoint. Preservar as três imagens anteriores como PRE_REFERENCE_GENERATION. Carrossel: CAROUSEL_INTEGRATION_GAP; consultar a investigação da campanha, sem criar compositor paralelo.
