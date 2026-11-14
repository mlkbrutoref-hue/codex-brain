**Diagnóstico comparativo do processo manual Shopee Video — 07/10/2026**

O projeto não precisa ser refeito. Ledger, dedup, controles de conta, QA, breaker, logs e proteção contra publicação continuam úteis. O desvio principal é operacional: a implementação começa depois da descoberta/download, não completa de forma reutilizável as transições da mídia e não segue consistentemente o caminho Minhas Curtidas mostrado pelo operador. A demora também vem da condução por comandos e revisões separados, além de leituras redundantes da interface.

Status deste trabalho: **DIAGNOSTIC_COMPLETE / IMPLEMENTATION_CHANGES_PROPOSED**. Sem operação Android, sem consulta autenticada, sem publicação, sem novos jobs, sem resolução de UNKNOWN ou alteração do breaker. Código de produção não foi modificado. Foram criados artefatos locais de análise e instrumentação temporária. Não foi criada arquitetura paralela nem reexecutada auditoria geral.

**Base da análise e limites da evidência**

- Pedido atual integral: attachment 922c7d09-a88b-404d-8448-5a89d28b9bf0/Texto colado.txt.
- Relidos os cinco pedidos históricos anexados: primeira postagem; auditoria de riscos; arquitetura operacional; aceitação; validação assistida. Também consideradas as correções desta conversa: preservação da publicação legada; abandono da Escova; origem do Mousepad; direitos e IA UNKNOWN; liberação apenas de validação de UI; proibição de Postar.
- Brain consultado na ordem README → MISSION → CHIA → CURRENT_STATE → DECISIONS. O escopo específico de teste assistido prevalece sobre orientações antigas mais amplas. A autorização histórica de uma publicação não autoriza publicar nesta análise.
- Vídeo original: [Recording_20261007_153025.mp4](<C:/Users/GAMER/Downloads/Recording_20261007_153025.mp4>), 544,059878 s (9min04,06s), 720×1600, 239.329.531 bytes, um stream de vídeo e nenhum stream de áudio.
- SHA-256 da gravação: cf54089487b28ac4c397a4438f1ff8293a3d7c787fb517a8be6f211e9e6c1165.
- Analisada a linha temporal completa, com decode integral, 262 capturas distribuídas pelo início/meio/fim e amostragem adicional aproximada de 0,5 s nos vínculos de produto e nos dois envios. Não é uma medição exata de cada toque. Timestamps abaixo são posições observadas no vídeo, não tempos presumidos de execução de comandos.
- Os passos fora dos trechos densos têm resolução de aproximadamente 2–2,6 s. Não inferir intenções, licença, uso de IA, IDs comerciais não legíveis ou tempo de rede apenas por imagem.
- Fontes de código e execução: app/mobile/shopee_video.py, ui.py, safety_runtime.py, media_selection.py; scripts de publicação/hashtags; logs das duas sessões assistidas; relatório e provas da rodada anterior.
- A gravação é do operador e mostra dois envios manuais. Eles não são ações executadas pelo agente nesta rodada e não reconciliam automaticamente o UNKNOWN do Mousepad. Não há URL/ID dos posts demonstrados suficiente para essa associação.

**A / WHAT IS ALREADY CORRECT — preservar**

| Componente | Classificação | Evidência e motivo |
|---|---|---|
| Identidade exata da conta | CORRECT | AndroidSafetyRuntime e confirm_account; evidência anterior borgesc542. O vídeo mostra essa conta no Chrome e no perfil Nina / Indica. |
| Ledger central, leases, dedup e tentativa durável | CORRECT para os controles já validados | Protegem concorrência/duplicação; não são a causa da falta do fluxo Chrome. Não precisam de novo desenho. |
| Bloqueio de retry de UNKNOWN e legado | CORRECT | Incidente atual permaneceu preservado; PUBLISHED_LEGACY e dedup permanente não precisam ser reabertos. |
| Separação ASSISTED_VALIDATED / READY_FOR_PUBLISH | CORRECT | Direitos UNKNOWN podem validar UI, mas não autorizam publicação. Manter. |
| Gates finais de direitos, IA, produto e revisão | CORRECT | Não remover para reproduzir os envios manuais. O vídeo não comprova direitos nem declara IA. |
| QA técnico, SHA-256 e inventário | CORRECT | Já existem e foram executados para o Mousepad. Mídia escolhida deve continuar rastreável. |
| Prioridade de seletores e card/botão associados | CORRECT no princípio; cobertura PARTIAL | Não trocar por coordenadas. Ajustar apenas layouts comprovadamente não contemplados. |
| Waits orientados ao estado | CORRECT na base | worker.wait continua assim que o predicado passa; 20 s é teto, não pausa obrigatória. |
| Legenda/hashtags configuráveis e limite UTF-16 | CORRECT | compose_caption respeita o limite observado de 150 e recebe configuração. |
| Probe e parser de hashtags read-only | CORRECT | Preservar capacidade de ler XML sem efeitos. Falta integrá-la ao fluxo de pesquisa assistida. |
| Proteção do clique final e publicação desabilitada | CORRECT | Proibição atual permanece; não reproduzir o Postar mostrado na demonstração. |
| Processo Android persistente durante a sessão | CORRECT na estrutura | IsolatedAndroidDevice cria um processo e conecta uma vez; não reconecta em cada RPC. Reconexões vieram de retomadas/helpers. |

**Fluxo manual reconstruído, incluindo o começo no Chrome**

| Intervalo observado | O que o operador faz |
|---|---|
| 00:00–00:12 | Navega pela tela inicial/lista de apps e abre Chrome. |
| 00:12–00:21 | Splash e carregamento do Chrome; abre uma aba já existente. Espera real visível. |
| 00:21–00:39 | Troca de aba para Shopee web; aparece um anúncio anterior de calçado vermelho. Esse anúncio é contexto de partida, não o produto dos dois envios seguintes. |
| 00:39–01:04 | Vai à home Shopee, espera o conteúdo e chega ao rodapé. A seção Buscas em alta fica visível. |
| 01:04–01:31 | Abre a busca Meia Maluca e espera os resultados. Não há digitação de uma nova query demonstrada nesse trecho; a navegação vem do link da busca. |
| 01:31–01:47 | Inspeciona/rola/ajusta a visualização dos resultados e escolhe o primeiro anúncio de meias usado depois. A página tem aparência de layout desktop; a opção de Chrome Site para computador não é mostrada, portanto essa configuração não é comprovada. |
| 01:47–02:19 | Abre o anúncio Meias Malucas 25 ao 40 dos Desenhos Animados..., assiste ao vídeo do próprio anúncio, abre menu do elemento de vídeo com Baixar o vídeo, conclui download de 3,12 MB e favorita o item. O coração muda de contorno para preenchido. |
| 02:19–02:47 | Volta aos resultados, abre Meia 3D Personagem Divertido Menino - Menina Colorida, inspeciona o vídeo, favorita e conclui outro download de 2,41 MB. Esse vídeo intermediário não é publicado nos dois exemplos mostrados. |
| 02:47–03:31 | Abre Meia 3D Divertida Infantil e Adulto Modelos Coloridos e Criativos Tamanho Único do 25 ao 40, revisa o vídeo, usa Baixar o vídeo, favorita e conclui download de 3,46 MB; volta aos resultados. |
| 03:31–03:43 | Sai do Chrome, abre Shopee e espera o app mostrar o feed. |
| 03:43–03:59 | Vai ao perfil de vídeo da conta Nina / Indica, borgesc542; aguarda o grid do perfil; toca Postar vídeo. |
| 03:59–04:14 | Câmera → Biblioteca → carregamento do grid. Seleciona o vídeo rosa do primeiro anúncio: ele está na terceira célula da primeira linha, não é simplesmente a mídia mais recente. O picker permanece na aba Tudo no exemplo. |
| 04:14–04:18 | Próximo → preview/editing da mídia → Próximo → editor de publicação. Aparece carregamento breve. |
| 04:18–04:25 | Toca a legenda e abre o teclado/menu da área de transferência, mas não preenche conteúdo definitivo. Sai desse foco. |
| 04:25,291–04:33,905 | Adicionar produto → Minhas Curtidas, já selecionada → Mais Recente → escolhe o terceiro card correto → Editar informações do produto → Feito → produto aparece no editor. Não usa a caixa de busca. |
| 04:35–05:54 | Escreve Meias malucas de Desenhos Animados e adiciona hashtags; digitação/correções e espera pelas sugestões ocupam a maior parte do trecho. |
| 05:54–05:57 | Fecha o teclado/edição; desliga Permitir a reutilização do conteúdo. WhatsApp continua selecionado; IA e Salvar no dispositivo continuam desligados. |
| 05:57–06:01 | Faz envio manual; aparece Loading, progresso e Enviado com sucesso. O diálogo Compartilhe no Whatsapp aparece depois. Isso é comportamento observado do operador, sem reproduzi-lo pelo agente. |
| 06:05–06:49 | Vai ao perfil/abre o novo vídeo, confere o produto/legenda e consulta páginas de hashtags, onde aparecem métricas de Visualizações. |
| 06:51–07:18 | Inicia outro vídeo → câmera → Biblioteca → primeiro item da galeria, vídeo do terceiro download → preview → Próximo → editor. Um aviso de baixa resolução aparece perto de 07:02–07:04; o conteúdo exato do limiar não foi usado para alterar o perfil técnico. |
| 07:20,109–07:25,530 | Adicionar produto → Minhas Curtidas/Mais Recente → primeiro card, correspondente ao terceiro anúncio → sheet → Feito → editor com vínculo. Não busca pelo título. |
| 07:26–08:44 | Escreve Meias Divertidas Infantis e hashtags relacionadas. Novamente a edição manual ocupa mais de um minuto. |
| 08:44–08:49 | Desliga reutilização, mantém WhatsApp selecionado, envia manualmente; mostra sucesso e o diálogo de WhatsApp. |
| 08:51–09:04,06 | Perfil → abre o segundo vídeo → legenda/comentários/produto → página de hashtag. A gravação termina nessa inspeção. |

Nos dois casos, a ordem efetiva é produto vinculado antes da legenda definitiva. O primeiro toque no campo de legenda foi exploratório; tratá-lo como legenda preenchida inverteria a interpretação.

Favoritar não é toggle cego: o vídeo permite verificar a mudança do coração. A automação futura deve conferir o estado, clicar somente se ainda não estiver favoritado e validar o resultado. Download deve ter confirmação de conclusão e associação ao anúncio antes de entrar no job de preparação.

**B / WHAT IS WRONG — divergências reais**

1. **Execução anterior foi para Todos e pesquisou um título que já estava em Minhas Curtidas.** A gravação mostra inclusive o Mousepad Titorion listado nas curtidas, junto às meias. A instrução original pedia Minhas Curtidas. O worker principal implementa essa aba, mas os helpers da última execução desviaram do caminho. Não é necessário eliminar Todos do aplicativo; é necessário impedir essa troca silenciosa na rota escolhida.
2. **O caminho padrão não completa seleção → preview → editor.** select_media termina deliberadamente com MEDIA_SELECTION_REVIEW_REQUIRED após selecionar. Isso é um checkpoint válido de segurança, mas o código não possui a continuação reutilizável das duas telas Próximo após a revisão. adopt_selection apenas registra CAPTION_READY; não executa essas transições nem comprova por si só que a UI mudou para editor.
3. **A ordem padrão é legenda → produto.** run_prepared chama fill_caption antes de select_product. A demonstração repetida indica produto → legenda definitiva. Não é um defeito universal do aplicativo; é uma diferença em relação ao fluxo solicitado.
4. **select_product exige identidade/atributos no card antes do clique e não consome a revisão atual do card usada pelo helper.** Quando os IDs ficam ocultos, ele para em PRODUCT_CARD_IDS_OR_VARIANT_REVIEW_REQUIRED. O fallback existente product_evidence atende o nó já vinculado, depois da seleção; não resolve a seleção prévia. Não corrigir escolhendo só por título: conectar a prova atual, fonte/IDs, card e botão.
5. **A reconciliação final ainda não tem observador integrado do post correspondente.** publish recebe timeout=60, mas não o utiliza para observar estados pós-envio: após o clique chama reconcile sem evidência, abre UNKNOWN e encerra. É correto não confiar em toast; está faltando a coleta dirigida de evidência. Isso é lacuna para etapa futura de publicação, não trabalho a executar nesta rodada.

**C / WHAT IS PARTIAL**

- Navegação ao perfil: bootstrap/confirmação de conta existem, mas a rota completa home/feed → perfil de vídeo → Postar ainda dependeu do controller no teste. select_media só aceita perfil/picker/câmera previamente reconhecidos.
- Minhas Curtidas existe, porém o worker clica a aba mesmo se já ativa e sempre preenche busca/submete Enter. O vídeo seleciona um card visível sem pesquisa. Melhor: reconhecer aba ativa, verificar a lista atual e buscar somente quando necessário.
- MediaSelectionEvidence é forte, mas mapeamento limitado às primeiras seis posições e unicidade de duração são restrições do protótipo. Na gravação há mais de um vídeo curto com duração de aproximadamente 21 s. Isso exige thumbnail/inventário/hash, não seleção pela duração nem remoção da revisão.
- product_cards já evita cruzar título A com botão B; entretanto exact_title exige igualdade integral. As telas demonstradas exibem títulos cortados e badges COMMSXTRA. Sem XML dessas telas, não é possível afirmar se o texto acessível também está cortado ou se o badge é texto. Registrar cobertura pendente e capturar uma fixture real antes de mudar a regra; não liberar prefixos soltos como identidade.
- O seletor raw_product_add_selector foi corrigido na rodada anterior e passou offline; ainda não houve comprovação real no device. Não tratar esse bug como ainda presente no código corrigido, nem como resolvido ponta a ponta.
- sharing_disabled/ensure_shopee_only existem; XML sem checked exige fallback por pixels e pode gerar screenshots repetidos. Manter a garantia de Shopee-only, usando uma captura por avaliação em vez de uma por ícone.
- Origem de anúncio pode ser registrada, e direitos UNKNOWN já permitem a UI. Falta obter essa evidência no ponto de descoberta/download, em vez de reconstruí-la tarde por scripts.
- Logs de ação existem, mas medem principalmente RPC. Falta duração total de ação/espera e identificação central do job nos spans: atualmente logger recebe job_id da configuração/sessão, diferente do ID do ledger.

**D / WHAT IS MISSING — Chrome e integração**

CHROME FLOW STATUS: **MISSING no RPA Android reutilizável; fontes/proveniência PARTIAL no domínio existente**.

Não foi encontrado worker de Chrome Android para Buscas em alta → lista → anúncio → player → download → favoritar → confirmação de arquivo. app/mobile/discovery.py descobre ambiente, não produtos web. A Affiliate API existe e continua útil para identidade comercial, mas não implementa os passos visuais do Chrome. Não confundir um provider de produto READY para API com descoberta Chrome implementada.

A automação começa tarde demais: exige local_media_path/candidate prontos, quando o processo completo mostrado começa na escolha do assunto/produto. O primeiro teste antigo tinha escopo deliberadamente menor, com vídeo na galeria e item curtido; preservar esse entrypoint de postagem isolada. A nova integração deve alimentar o mesmo candidato/ledger, não criar outro pipeline.

Persistir no ponto do anúncio: termo de origem, URL, shop/item observáveis, título, variações realmente demonstradas, player/source, favorito antes/depois, confirmação do download, arquivo MediaStore e hash. Não inventar IDs de meias a partir de títulos ou thumbnails. A gravação não mostra o endereço completo com todos os IDs de forma confiável.

Seleção e pesquisa de hashtags: existe parser de sugestões visíveis, mas não fluxo integrado para observar sugestões pertinentes e escolher tags. A métrica vista é **Visualizações**, não quantidade de posts/usos. A pesquisa nativa deve registrar nome, métrica, unidade, timestamp e fonte; a popularidade não pode ser fabricada.

| Hashtag | Rótulo observado na gravação | Posição de evidência |
|---|---|---|
| #meia | 115,6mi Visualizações | 06:15,155 |
| #meiainfantil | 17,1mi Visualizações | 05:13,289 / 06:19,205 |
| #meias | 101,2mi Visualizações | 05:33,882 |
| #meiamalucas | 2,1mi Visualizações | 06:29,242 |
| #MeiasDeDesenho | 2,3mil Visualizações | 05:38,209 |
| #infantil | 837,3mi Visualizações | 06:41,307 |
| #modainfantil | 163,8mi Visualizações | 06:47,349 |

Esses valores são snapshots históricos da gravação, não consulta atual nem ranking de eficácia. #MeiasDeDesenho apresenta escala muito menor que as outras; não dizer que todas têm muitos usos. A página #undefined aparece na navegação e é um resultado anômalo a tratar, sem inferir que o texto #undefined estava na legenda.

Permitir reutilização: o operador desliga antes dos dois envios, mas o worker não tem essa etapa/validação. É uma pequena lacuna concreta de configuração de UI, separada de direitos legais. A sequência com WhatsApp selecionado não altera automaticamente o requisito Shopee-only existente: a demonstração mostra o prompt indesejado que a proteção atual evita.

**E/F / BIGGEST TIME BOTTLENECKS e suas causas**

Medidas retrospectivas reais dos logs, sem Android:

| Sessão | Tempo entre primeiro/último evento | Soma de RPCs registrados | Ações / leituras |
|---|---:|---:|---:|
| assisted_mousepad_20261007 | 2.233,458 s = 37min13,458s | 89,798 s | 142 / 132 |
| assisted_mousepad_editor_resume_20261007 | 897,660 s = 14min57,660s | 50,556 s | 82 / 75 |
| Soma dos dois intervalos | 3.131,118 s = 52min11,118s | 140,354 s = 2min20,354s | 224 / 207 |

Os intervalos pertencem a sessões/logs com interrupções e retomadas; não equivalem a um benchmark contínuo de UI. 140,354 s representam 4,48% da soma dos intervalos, mas não atribuir os 95,52% restantes apenas a sleeps. Eles incluem análise, tool calls, comandos externos, revisões, inicialização, I/O e recuperação não medidos pelo logger. Há ainda um intervalo entre as sessões; a soma não é o tempo total global do trabalho.

| Categoria registrada | Quantidade | Soma |
|---|---:|---:|
| XML/hierarchy | 105 | 59,978 s |
| foreground | 82 | 35,565 s |
| app_version | 10 | 6,229 s |
| screenshots | 6 | 6,573 s |
| read_shell | 4 | 11,228 s |
| product_card com falha | 1 | 10,595 s |

1. **Maior gargalo percebido: fluxo operado por conversa/helpers.** Faltam continuações reutilizáveis, então simples transições viram novos comandos, capturas, revisões e sessões. Instrumentar e integrar o caminho normal é mais relevante que diminuir um timeout de 20 para 5.
2. **Amplificação de leituras comprovada offline.** tap_id faz observe; ShopeeUI.click resolve o seletor; _execute resolve novamente, captura XML para guard e consulta foreground; wait observa outra vez. Com um fake do código real, uma transição faz quatro XMLs + dois foregrounds antes do clique e mais um XML + um foreground após o clique. Prova em offline-read-amplification.json.
3. **RPC com falha Adicionar: 10,595 s.** Não é espera de segurança deliberada. O diagnóstico anterior encontrou incompatibilidade XPath/SDK. Corrigir seleção e preservar o estágio/classe de erro resolve a causa; timeout menor só falharia mais cedo.
4. **Retomadas reiniciam a conexão e o preflight.** O processo é persistente dentro da sessão, mas helpers como submit_search iniciam outro IsolatedAndroidDevice. A sequência sem interrupções deve usar um só owner/processo.
5. **Repetição de QA e revisões locais na retomada.** local_preflight executa hash e inspect novamente. Não remover QA; reutilizar prova hash-bound apenas quando mídia/perfil não mudaram, conferindo a integridade relevante. O custo de FFmpeg nessa execução não foi separado nos logs.
6. **Screenshots de diagnóstico e pixel fallback.** As seis capturas registradas somaram 6,573 s; não explicam sozinhas os 52 minutos. Há potencial de repetição maior em ensure_shopee_only e liked_tab_active quando o XML não expõe estado.
7. **I/O persistente e subprocesso.** Budget/breaker/SQLite/guard acontecem antes de start=time.monotonic no logger de ação; esse custo não aparece em latency_ms. O mecanismo protege invariantes e deve permanecer; medir antes de otimizar.
8. **RPC máximo de 60 s é teto ampliado no teste.** Não significa que cada chamada espere 60 s. Ajustar por operação e medição futura, sem reduzir o limite de bootstrap com base em suposição.

**UNNECESSARY WAITS**

Não encontrei sleep(8) nem jitter no caminho principal. O polling usa pausas de até 0,25 s depois de uma observação sem sucesso. O período real entre amostras soma XML + foreground + guard/I/O + até 0,25 s, portanto não é polling de quatro observações por segundo. Ao encontrar o estado, o loop retorna imediatamente.

Evitar:
- clicar Minhas Curtidas se já ativa;
- pesquisar título/submeter Enter se card correto já visível e comprovado;
- repetir _resolve_click sobre vários XMLs sem transição;
- executar observe logo depois de wait já devolver a tela validada;
- capturar uma screenshot por ícone quando uma serve para todos;
- encerrar/reabrir conexão entre ações normais;
- obrigar retomada completa depois de checkpoint sem efeito pendente.

Preservar: foreground/package imediatamente antes de mutação, guards de segurança, breaker/kill/deadline/budget persistentes, confirmação objetiva depois de cada efeito e revisão quando há ambiguidade real. Um snapshot pode ser reutilizado apenas no mesmo contexto com validade explícita; após ação/transição/intervenção externa deve ser invalidado. Não propor cache indiscriminado da conta/tela.

**Tabela comparativa de tempo por etapa**

| STEP | CURRENT TIME comprovado | Comportamento manual observado | Problema |
|---|---|---|---|
| Descoberta Chrome | Sem etapa implementada/medida | ~00:12–03:31 inclui abertura, busca, curadoria, três downloads e favoritos | Pipeline só recebe mídia/candidato prontos |
| Splash do Chrome | Não medido na automação | Logo visível de ~00:12 a ~00:19; página até ~00:21 | Espera de inicialização real, não usar tempo fixo |
| Home/resultados web | Não medido na automação | Carregamento visível ~00:41–00:56 e ~01:04–01:18 | Não confundir network load com delay artificial |
| Download 1/2/3 | Não implementado | Conclusões visíveis ~02:11, ~02:38 e ~03:16 | Não há início/ACK precisos para cronometrar duração de cada transferência |
| Perfil/picker | Não separado por etapa nos logs | ~03:43–04:14, com carregamento de perfil e grid | Caminho parcial exige controller |
| Picker → preview → editor | Sem continuação reutilizável | ~04:12–04:18 no primeiro; ~07:06–07:18 no segundo, incluindo inspeção | Falta driver de continuação, não segurança extra |
| Abrir produtos 1 | Sem span completo | Editor antes em 265,291s; lista em 268,364s | Transição delimitada entre amostras, não toque exato |
| Adicionar + Feito 1 | RPC Adicionar anterior falhou em 10.595,190ms; span total ausente | Sheet em 271,143s; editor vinculado em 273,905s | Seletor/integração de prova; manual não procura novamente |
| Fluxo de vínculo 1 completo | Não medido como span | 265,291 → 273,905 = intervalo amostrado 8,614s | Inclui decisão e render; não atribuir tudo à rede |
| Fluxo de vínculo 2 completo | Não medido como span | 440,109 → 445,530 = intervalo amostrado 5,421s | Menos navegação; mesmo caminho Curtidas |
| Legenda/hashtags | Duas RPCs text_field: soma 904,590ms na retomada; não é duração total de edição | ~04:35–05:54 e ~07:26–08:44, com digitação e sugestões | O RPA pode preencher texto em bloco; pesquisa pertinente ainda falta |
| Clique/envio manual 1 | Proibido nesta rodada | Loading 357,921s; sucesso 360,023s (2,102s entre estados amostrados) | Não é prova cronométrica do clique nem ID público |
| Clique/envio manual 2 | Proibido nesta rodada | Loading 526,666s; sucesso 528,988s (2,322s entre estados amostrados) | Não extrapolar velocidade de upload para outros vídeos |

**G / MINIMAL FIXES — propostas em ordem, sem arquitetura paralela**

1. No worker existente, adicionar continuação após a revisão da seleção: observar a tela atual; picker Próximo → preview; confirmar mídia; preview Próximo → editor; cada ação passa pela mesma ShopeeUI e pelo mesmo owner. Revisão válida deve continuar o job, sem abrir outro equivalente. UNKNOWN nunca se beneficia dessa retomada.
2. Em select_product: reconhecer Minhas Curtidas/Mais Recente ativos, verificar card visível primeiro, buscar só se ausente e nunca trocar para Todos sem escolha explícita de rota. Confirmar que o estado da aba é observado, não presumido.
3. Integrar a revisão pré-clique do card ao caminho principal, usando fonte/IDs/hash/fingerprint/TTL/card/botão. Reusar product_evidence após Feito; não inventar variante nem considerar título identidade.
4. Ajustar run_prepared para produto → legenda definitiva, apoiado pelos dois exemplos e pela validação final; não mudar o núcleo de legenda.
5. Consolidar a resolução/guard do clique em uma captura imediatamente anterior à mutação, e reutilizar a tela retornada por wait. Manter checks mutáveis de breaker/kill/budget/deadline e foreground recente. Mudança exige regressões de tela alterada e selector ambíguo.
6. Confirmar sharing com uma screenshot quando necessário; implementar opção de reutilização desabilitada, observada antes da conclusão. Não alterar AI para False por causa do toggle desligado no vídeo.
7. Registrar erro sanitizado e estágio do RPC: falha comprovadamente antes do despacho não é efeito UNKNOWN; resposta perdida depois do despacho continua UNKNOWN. Alteração futura deve testar ambos os casos. O UNKNOWN atual não pode ser apagado nem reclassificado só pelo diagnóstico.
8. Planejar o adapter Chrome como entrada para o candidato existente, com limites e controles atuais. Esta é mudança maior: diagnóstico entregue primeiro, implementação ainda não iniciada.
9. Integrar observação de hashtags e preservar unidade Visualizações. Esse fluxo não transforma o parser read-only em ferramenta de digitação; ações de pesquisa devem continuar pela camada autorizada.
10. Em etapa futura de publicação autorizada, adicionar observação/reconciliação por post correspondente, mantendo UNKNOWN em incerteza. Nada de publicar para provar essa capacidade agora.

**H / PREVIOUS REQUIREMENTS NOT IMPLEMENTED CORRECTLY — mapa pedido**

| MINHAS INSTRUÇÕES | IMPLEMENTAÇÃO ATUAL | DIVERGÊNCIA | CORREÇÃO PROPOSTA |
|---|---|---|---|
| Produto já curtido → Minhas Curtidas | Worker usa Curtidas, helpers da rodada usaram Todos | Execução divergiu do requisito | Rota Curtidas consistente; sem troca silenciosa |
| Chrome faz parte do processo | Só entrada de mídia/configuração pronta; provider API separado | Descoberta/download ausentes | Adapter de entrada ligado ao mesmo candidato |
| Identificar mídia exata | Hash/inventário/thumbnail + primeiras seis/duração única | Proteção boa, mapeamento limitado e checkpoint sem continuação | Completar transições e ampliar evidência somente quando comprovado |
| Ação → aguardar estado → continuar | wait funciona; há várias leituras iguais e helper por etapa | Excesso de captura/orquestração | Snapshot único por ação e continuação no mesmo worker |
| Não voltar ao começo sem necessidade | start pede conta e worker reconhece poucos estados | Resumes dependem de arquivos/scripts/adopção | Retomada bound ao estado observado, sem efeito pendente |
| Card A nunca pega botão B | ProductCard estrutural existe | Correto; cobertura de layout e revisão pré-clique incompleta | Preservar C02 e conectar prova, não título solto |
| Rights UNKNOWN permite UI, bloqueia final | validate_assisted separado de validate final | Corrigido na rodada anterior | Preservar; não reabrir essa discussão sem evidência nova |
| Hashtags relacionadas com evidência de popularidade | Parser read-only existe; copy atual usa três tags sem métricas | Pesquisa não integrada | Registrar sugestões/métrica/unidade antes da revisão final |
| Confirmar publicação correspondente | publish chama reconcile sem evidência logo após clicar | Segurança conservadora, confirmação ausente | Observador/reconciler em escopo futuro autorizado |
| Logs de duração/estado | latency_ms somente RPC; transições separadas | Falta span de ação completa e wait | Instrumentação temporária preparada nesta rodada |
| Sem evasão/humanização e concurrency=1 | Nada disso foi introduzido | Coerente | Manter |
| Preserve legado/UNKNOWN e não reposte | Sem mudanças de estado nesta análise | Coerente | Manter enquanto prepara correções offline |

A ordem produto → legenda é uma correção explicitada pela gravação; a especificação inicial sugeria legenda → produto. O novo vídeo corrige a ordem sem invalidar os gates antigos. Favorito precisa acontecer na descoberta, antes da seleção via Curtidas.

**I / FLUXO IDEAL baseado no vídeo e nos requisitos ativos**

Chrome → home Shopee / Buscas em alta → termo escolhido → resultados → anúncio específico → registrar identidade/fonte → inspecionar vídeo/variante observável → Baixar o vídeo e conferir/favoritar somente se necessário → confirmar conclusão real do download → correlacionar arquivo MediaStore/hash com anúncio → candidato/QA/proveniência/dedup no modelo existente. A gravação mostra favorito e download próximos entre si, inclusive favorito antes da notificação de conclusão em um anúncio; não impor espera fixa nem exigir aguardar a transferência para favoritar se a ação já for segura no estado atual. A transferência assíncrona não exige um segundo worker Android.

Depois: reserva central/preflight seguro → Shopee → conta correta/perfil de vídeos → Postar vídeo → Biblioteca → selecionar mídia EXATA (não necessariamente a primeira) → revisão/evidência necessária → Próximo → preview → Próximo → editor → Adicionar produto → Minhas Curtidas → Mais Recente/lista atual → card correto com binding → Adicionar → Editar informações → Feito → editor com produto → legenda/hashtags pertinentes e verificadas → fechar overlay → desabilitar reutilização e compartilhamentos externos conforme configuração → checks finais → ASSISTED_VALIDATED → STOP antes de Postar.

A origem registrada não comprova direitos. Direitos e IA UNKNOWN continuam visíveis. READY_FOR_PUBLISH e autorização final só existem quando os gates finais necessários forem satisfeitos em escopo explicitamente autorizado.

**J / ESTIMATIVA de aceleração sem reduzir confiabilidade**

| Otimização | Estimativa e limite |
|---|---|
| 4 XMLs pré-clique → 1 XML imediatamente pré-clique | Até ~75% menos XML nessa parte do caminho; a transição completa pode passar de 5 para 2. Potencial, ainda não implementação/benchmark. |
| Leituras evitadas por clique | Medianas observadas XML ~412–625ms e foreground ~366–382ms sugerem cerca de 1,6–2,3s por clique quando forem removidos três XMLs e um foreground redundantes. Não extrapolar a todos os cliques. |
| Evitar busca quando card está visível | Elimina digitação/Enter/resultados e possibilidade de selecionar anúncio parecido. Ganho em segundos ainda não medido. |
| Sessão persistente sem helper/revisão repetida | Provavelmente maior ganho de tempo percebido, mas nenhuma porcentagem confiável pode ser calculada pelos logs atuais. |
| Caption em bloco | A RPC set_text já fica em centenas de ms no caso registrado, versus dezenas de segundos de digitação humana. Não inclui curadoria das hashtags/revisão. |
| Esperas de rede/player/download | Ganho não garantido; apenas continuar imediatamente quando o estado aparecer. Não reduzir precisão por meta arbitrária de tempo. |
| Provas locais reutilizadas | Evita FFprobe/decode repetidos sem mudança de arquivo/perfil, depois de provar invalidação correta. Custo atual por etapa ainda não medido. |
| Shopee-only pixels | Uma captura por verificação reduz chamadas sem remover a confirmação. Atual mediana screenshot ~1s; não é o principal gargalo. |

Não há estimativa responsável de “fluxo todo em X segundos” nem garantia de operação 20–30/dia. A gravação inclui curadoria de três itens e dois envios; não comparar seus 9min04s diretamente com um job assistido interrompido do Mousepad.

**Instrumentação temporária entregue e validada**

Criados no diretório de evidências, sem editar classes de produção:

- analyze_timings.py / current-timings.json: medidas reais retrospectivas de RPCs e intervalos. START derivado de END menos latency é identificado como estimado. STATE OBSERVED e WAIT_REASON antigos permanecem NOT_CAPTURED, sem fabricação.
- temporary_profiler.py: hooks por instância, opt-in, restaurados ao sair; gera ACTION, START, STATE_OBSERVED, END, DURATION_MS, WAIT_REASON, STATUS, ERROR_TYPE e DEPTH. Mede método completo/wait; preserva métodos originais, exceções, budgets e guards. Não cria sessão/conexão, não clica por conta própria e rejeita LIVE_PUBLISH. Arquivo exclusivo evita sobrescrever provas.
- test_temporary_profiler.py: cinco testes PASS, cobrindo retorno/restauração, erro original, ausência de dados privados, preservação do arquivo e rejeição de modo/rótulos inadequados.
- trace_click_offline.py / offline-read-amplification.json: reprodução de tap_id com fake e DB isolado; comprova 4 XMLs + 2 foregrounds pré-clique, 5 + 3 no total; exatamente um clique fake; pending_effect limpo só depois de wait válido.
- offline-instrumentation-example.jsonl: exemplo real da instrumentação com ambiente fake. Seus tempos não são latências de Android, não devem ser apresentados como benchmark do celular.
- runtime-code-hashes.json: hashes dos módulos relevantes usados na reprodução; production_code_unchanged=true no resultado.

A instrumentação está preparada e exercitada offline. Não foi anexada a uma sessão Android real nesta análise, porque não foi necessário operar o telefone para o diagnóstico e o incidente anterior continua pendente. A próxima validação autorizada deve medir o caminho corrigido com esses spans. Spans aninhados não devem ser somados como custos independentes.

Exemplo de integração temporária dentro de uma sessão já criada e autorizada, após anexar a ShopeeUI ao worker:

    with profile_methods(worker_bindings(worker), caminho_novo,
                         mode=worker.safety.config.mode):
        # Somente as ações de validação já autorizadas da sessão.
        ...

Isso é uma instrução de uso futuro, não comando executado no telefone nem autorização de retomada.

**FILES THAT NEED CHANGES — somente correções direcionadas**

| Arquivo existente | Mudança proposta |
|---|---|
| app/mobile/shopee_video.py | Continuação da mídia, rota Curtidas sem busca compulsória, revisão do card integrada, ordem produto/legenda, reutilização configurável, reaproveitamento de tela/captura. |
| app/mobile/ui.py | Unificar resolução/guard da ação; preservar estágio/classe de RPC; nenhuma liberação automática do UNKNOWN. |
| app/mobile/safety_runtime.py | Conectar prova atual de card/retomada ao estado; invalidar evidências em transições e mudanças relevantes. |
| app/observability/operation_logger.py | Se a medição temporária confirmar utilidade, incorporar spans sanitizados e central_job_id, preservando allowlist. |
| scripts/publish_shopee_android.py | Somente se necessário expor a continuação/rota já implementada no worker; manter default DRY_RUN. |
| tests/publishing/ | Fixtures e regressões das transições alteradas, card/IDs ocultos, aba ativa, mudança de tela e zero finalclick. |
| app/mobile/entrada Chrome a definir | Planejamento posterior dentro do módulo existente; não criado agora. |

**FILES THAT SHOULD NOT BE TOUCHED nesta correção de fluxo**

Preservar a lógica de app/publishing/ledger.py, reconciliation.py, legacy_reconciliation.py; app/operational/store.py, action_budget.py, circuit_breaker.py, deadlines.py e modes.py; app/validation/publish_gate.py; contratos e QA de mídia. Não alterar hashes/arquivos antigos, o SQLite real, sessões originais ou evidências do legado. Só mudar interfaces nesses componentes se uma necessidade específica for demonstrada depois, com regressão.

Preservar seletores já comprovados, ContentValidator final estrito, testes válidos e o parser read-only de hashtags. Não refatorar factory criativa, Nina/Stories/carrosséis, providers de imagem, Antigravity ou analytics por causa deste fluxo Android. Nenhuma delegação ao Antigravity foi realizada nesta análise.

**RECOMMENDED NEXT STEP**

Primeiro corrigir offline o trecho de postagem existente: continuidade picker/preview/editor, revisão pré-clique do card e Minhas Curtidas, mesma sessão e produto antes da legenda. Adicionar fixtures dos estados correspondentes e medir o custo com instrumentação temporária. Depois resolver o incidente atual pelo mecanismo apropriado com evidência suficiente e preflight, antes de uma nova operação real.

O fluxo Chrome é a próxima integração maior, já descrita aqui para revisão. Deve registrar a origem no começo e entregar o mesmo PostCandidate. Não é necessário reescrever ledger, breaker ou gates para fazer isso.

A análise está concluída. A adaptação operacional ainda não foi aplicada e o projeto não é declarado ASSISTED_VALIDATED nem pronto para publicação.

