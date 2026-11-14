# Auditoria de risco — RPA Android para Shopee Video

Data: 06/10/2026, America/Sao_Paulo. Escopo: revisão de código e evidências locais, pesquisa pública e reproduções offline. Nenhuma conexão ao Android, login, curtida, upload, publicação ou consulta autenticada à API foi executada nesta auditoria. Runtime, configuração operacional e registros de postagem foram preservados.

## 1. Executive Summary

**RISCO ATUAL: HIGH.** Classificação de exposição contratual e prontidão operacional; **não** significa alta probabilidade demonstrada de banimento. A chance de detecção, aplicação de sanção e prazo são **DESCONHECIDOS**. Não há evidência de punição aplicada à conta nesta revisão.

**DOCUMENTADO:** os termos específicos do Shopee Video, item 4.1(g), proíbem scripts automatizados para coletar informações ou interagir com o serviço. Isso é mais específico que a regra geral sobre bots não autorizados. **INFERÊNCIA:** o publicador Python/uiautomator2 se enquadra na interação por script; celular físico, revisão humana e baixo volume não estabelecem uma exceção. [Termos específicos, 4.1(g)](https://help.shopee.com.br/portal/4/article/150523), [termos gerais, 6.2(k)](https://help.shopee.com.br/portal/4/article/77113).

**20–30 POSTS/DIA: NOT SUPPORTED BY OFFICIAL EVIDENCE.** Não foi encontrada, nas fontes consultadas, aprovação desse volume para este RPA. Limite diário permitido, limite técnico por conta e frequência que evitaria restrições: **UNKNOWN**. Essa ausência não comprova que toda publicação manual nesse volume seja proibida.

O núcleo já oferece waits por estado, persistência, identificação por hash, interrupção diante de erros e reserva durável anterior ao clique final. Entretanto, não integra autorização da plataforma, direitos de mídia, QA técnico, identidade comercial por ID/variante, disponibilidade atual, orçamento por conta ou circuit breaker persistente. Três lacunas adicionais foram reproduzidas offline na seção 7.

**Recomendação:** automatizar produção e empacotamento local; usar a Affiliate API somente dentro do acesso e escopo concedidos; fazer a operação de postagem manualmente. Evolução de RPA que interaja com Shopee Video deve depender de exceção/autorização formal aplicável ao método ou de interface oficial explicitamente habilitada para esse uso. Hardening reduz falhas; não concede permissão.

O usuário informou que o teste anterior deu certo. O registro automático continua `ERROR / PUBLICATION_UNCONFIRMED_DO_NOT_REPOST`, com `publish_attempted=true` e sem identificador externo. Não foi reinterpretado como falha de publicação nem promovido a confirmação independente. Primeiro passo operacional futuro: reconciliar o post existente, sem repetir o envio. [Evidência local](</C:/Users/GAMER/Documents/SHOPEE AUTOMATION/ai-commerce-content-factory/docs/publishing/audit/offline-evidence-2026-10-06.json>).

### Critério de evidência

- **DOCUMENTADO:** fonte oficial pública ou código/artefato inspecionado. Quando for código, descreve comportamento local, não comportamento interno da Shopee.
- **INFERÊNCIA:** avaliação de engenharia ou recomendação proposta, sem confirmação da plataforma.
- **DESCONHECIDO / UNKNOWN:** evidência insuficiente. Não substituído por uma porcentagem inventada.

LOW: impacto limitado; MEDIUM: degradação recuperável; HIGH: exposição material da conta/receita ou erro relevante de publicação; CRITICAL: comprometimento ou dano extremo demonstrado que exige resposta imediata. Nenhum achado recebeu CRITICAL. Severidade não equivale à probabilidade.

## 2. Políticas públicas encontradas

Todas as fontes abaixo foram consultadas em 06/10/2026. Os documentos podem mudar. A análise usa fontes primárias, sem relatos de fóruns como prova de funcionamento interno.

| Fonte oficial | Evidência DOCUMENTADA relevante | Aplicação à auditoria |
|---|---|---|
| [Termos gerais](https://help.shopee.com.br/portal/4/article/77113), 6.2(k), 5.3 | Restrição a equipamentos/aplicações não autorizados, incluindo bots/emuladores; suspensão e encerramento entre as medidas previstas. | Dispositivo real não constitui autorização de automação. |
| [Termos do Shopee Video](https://help.shopee.com.br/portal/4/article/150523), 4.1(g), 3.4 | Vedação de scripts de coleta/interação; possibilidade de desativar, suspender ou terminar acesso. | Inclui automação de preparação dentro do serviço; não depende apenas do clique final. |
| [Afiliados](https://help.shopee.com.br/portal/10/article/124094), 4.2–4.3, 5.2, 7.2, 14.4 | Programa exige cumprimento das políticas, restringe extração automatizada, prevê retenção de comissão/rescisão e proíbe envio de vídeos estáticos. | Acesso a ofertas não autoriza extração irrestrita nem operação de publicação por bot. Não se presume sanção financeira automática por qualquer incidente. |
| [Diretrizes do Video](https://help.shopee.com.br/portal/10/article/165433), 2, 7.3, 9.5, 13 | Correspondência ao produto; restrições a conteúdo copiado, watermark concorrente persistente, baixa qualidade e falso engajamento; conteúdo não original pode ser inelegível para recomendação. | Moderação e elegibilidade para distribuição são eixos distintos de permissão de RPA. |
| [Originalidade com IA](https://help.shopee.com.br/portal/10/article/224502) | IA é permitida como recurso criativo; autoria e transformação significativa importam. Publicação massiva de peças quase idênticas pode indicar falta de originalidade. | Persona recorrente ou formato consistente não são, sozinhos, prova de falta de originalidade. |
| [Termos de IA](https://help.shopee.com.br/portal/4/article/167605), 3.3 | Conteúdo gerado por IA de terceiros exige direitos necessários e rotulagem como gerado por IA. | Gate separado para origem, direitos e indicação de IA; não autoriza bot de publicação. |
| [Privacidade Brasil](https://help.shopee.com.br/portal/4/article/77068), 4.1–4.3, 6.1 | Descreve dados como IP, dispositivo/SO, navegador, páginas/conteúdos e horários, associação à conta e usos de segurança/antifraude. | Não confirma detecção de ADB, uiautomator2, depuração USB, coordenadas ou intervalos de cliques. |
| [Explorer Affiliate](https://open-api.affiliate.shopee.com.br/explorer) | Endpoint público oficial identificado; página depende de aplicação web e não forneceu documentação legível nesta pesquisa. | Escopo de credenciais, quotas e publicação de Video não foram comprovados pela página. |
| [Android ADB](https://developer.android.com/tools/adb), [uiautomator2](https://github.com/openatx/uiautomator2) | Ferramentas de operação/teste Android, seleção de dispositivo e automação de UI. | Documentação técnica não estabelece consentimento da Shopee. |

### Separação dos mecanismos

| Eixo | O que avaliar | O que não concluir automaticamente |
|---|---|---|
| Anti-abuso | Avisos, desafios, conta limitada e uso autorizado. | Uma regra pública não revela o classificador interno. |
| Rate limiting | Limitação de frequência ou 429 quando efetivamente observado. | Timeout/RPC desconectada não comprovam rate limit. |
| Conteúdo | Produto, claims, qualidade, autoria, IA e direitos. | Arquivo tecnicamente válido não garante aprovação. |
| Afiliados | Elegibilidade, links, regras do programa e comissão. | Upload concluído não garante comissão. |
| Recomendação | Elegibilidade e métricas reais do post. | Poucas views não provam shadowban ou punição da conta. |
| Conta | Suspensão, funcionalidade restrita e comunicados oficiais. | Mudança de tela ou falha de upload não provam banimento. |

**DESCONHECIDO:** parâmetros de recomendação, thresholds anti-abuso, correlação entre repetição e sanção, prazo de análise e limites específicos de posts. As regras de penalidade por produto irrelevante não foram extrapoladas para automação. [Política de produto relevante](https://help.shopee.com.br/portal/10/article/165433).

## 3. Arquitetura atual

### Fluxos efetivamente encontrados

```text
Produção local / QA / Campaign Finalizer -> pacote READY_TO_POST

ShopeeAffiliateClient -> Affiliate GraphQL -> produtos com itemId/shopId
                                         (sem ligação ao gate do RPA)

CLI publish_shopee_android
  -> Python -> uiautomator2 -> ADB -> Android físico -> app Shopee
  -> perfil/câmera/galeria -> seleção/editor -> legenda
  -> Minhas Curtidas -> produto por título -> validações
  -> reserva local -> um chamado de clique final -> observação de confirmação

probe_shopee_android / research_shopee_hashtags
  -> ações e capturas separadas, sem os controles globais do núcleo
```

**DOCUMENTADO no checkout:** `app/mobile/shopee_video.py` implementa o publicador experimental. `app/publishing/assisted.py` é outro contrato, para Instagram/TikTok, com parada anterior à publicação; não é o gate do Shopee RPA. `app/mobile/discovery.py` apenas descobre Phone Link. `app/platforms/shopee_video/exporter.py` copia/hardlinka o master; não valida nem transcodifica para o app.

A descoberta comercial reutilizável usa `app/providers/shopee/` e inclui IDs, URLs e campos de oferta. No publicador Android inspecionado, não foi encontrado crawler de produtos, rotina de curtir produtos ou navegação infinita. A aba Minhas Curtidas consome uma seleção existente. As atividades futuras declaradas pelo usuário não foram tratadas como já implementadas.

Na pesquisa anterior de sete hashtags, o app expôs **Visualizações**, não número de publicações/usos. `scripts/research_shopee_hashtags.py` preserva esse significado. Métrica alta não demonstra adequação à legenda, entrega garantida ou frequência permitida. Evidência anterior: `debug/shopee_android/hashtags/research.json`; não foi consultada novamente no aparelho nesta auditoria.

**Chrome Android:** informado pelo usuário, mas não foi localizado adapter/fluxo Chrome em `app/` ou `scripts/`, nem nos demais Python pesquisados fora de artefatos e ferramentas. Sua implementação, navegação, cookies, login e tratamento de erros permanecem **DESCONHECIDOS**. Usar Chrome não cria exceção à política. A auditoria não abriu o navegador nem inspecionou contas nele.

**Dispositivo físico versus emulador versus API — INFERÊNCIA:** hardware físico reduz diferenças técnicas de ambiente, mas não altera a natureza de script de UI. Emulador adiciona outra categoria expressamente citada nos termos gerais. API com acesso concedido permite apenas operações do escopo concedido; consulta de ofertas não demonstra permissão para publicar. Nenhuma API de publicação Shopee Video aplicável à conta foi confirmada. [Regra geral](https://help.shopee.com.br/portal/4/article/77113), [Explorer](https://open-api.affiliate.shopee.com.br/explorer).

### Controles já presentes

**DOCUMENTADO no núcleo:** lock por serial/raiz local; waits finitos por condição; IDs dinâmicos por sufixo; validação da legenda completa e limite UTF-16 observado de 150; erro em produto ambíguo; SHA-256 do arquivo fonte e recorte de preview; sessão JSON com replace/fsync; eventos JSONL; reserva exclusiva por serial/hash anterior ao clique; retorno sem nova execução quando sessão já está PUBLISHED; parada por marcadores de autenticação/erro. Compartilhamento automático externo é conferido por pixels.

Os controles são úteis, mas não equivalem a transação distribuída nem a garantia formal de exactly-once. O núcleo faz um chamado final de clique; duplicatas em outra raiz/dispositivo ou por operação manual ficam fora dessa proteção. [Código, `reserve_attempt` e `publish`](</C:/Users/GAMER/Documents/SHOPEE AUTOMATION/ai-commerce-content-factory/app/mobile/shopee_video.py:515>).

### Estado e limite da evidência

O teste teve oito validações verdadeiras antes da tentativa. O arquivo de sessão registra retorno ao perfil, timeout e nenhuma `publication_confirmation`. A mensagem posterior do usuário é evidência de sucesso reportado por ele; falta registrar conta, post e correspondência exata de mídia/legenda/produto para reconciliação independente. Não houve reconciliação ou novo envio nesta auditoria.

O Brain mantém D-023 como pausa geral; o pedido posterior autorizou um teste específico, sem tornar a capacidade READY. A documentação histórica dizendo que `app/mobile/` é somente leitura não descreve o módulo experimental acrescentado. Esta divergência de escopo deve ser alinhada na retomada; este relatório não adotou nova decisão arquitetural nem alterou o Brain.

## 4. Riscos confirmados

“Confirmado” refere-se à existência de regra/controle ausente/resultado local, nunca a sanção já aplicada.

1. **DOCUMENTADO:** interação por scripts é vedada pelos termos específicos. Não há autorização da plataforma registrada no projeto. `publish_authorized=true` registra consentimento do usuário, não consentimento da Shopee. [Termos Video, 4.1(g)](https://help.shopee.com.br/portal/4/article/150523).
2. **DOCUMENTADO no código:** ausência de rate limiter/budget global por conta, duração total de sessão, circuit breaker persistente e kill switch compartilhado. A trava por dispositivo não substitui esses controles.
3. **DOCUMENTADO no código:** título comercial, integridade do arquivo e preview não demonstram ID/variante, direitos, qualidade, disponibilidade ou revisão completa do vídeo. Esses gates não integram `validation_checks`.
4. **DOCUMENTADO na execução:** tentativa final permanece incerta no registro automático e não pode ser repetida com segurança. A reserva preservada foi a resposta correta à incerteza.
5. **DOCUMENTADO offline:** as três reproduções da seção 7 produzem os resultados descritos no arquivo de evidências, sem depender de hipótese sobre servidores da Shopee.

## 5. Riscos inferidos

### Método, frequência e navegação

**INFERÊNCIA:** 20–30 publicações multiplicam não só posts, mas buscas, seleção, compressão, navegação, uploads e chances de falha. A carga deve ser medida como ações e tempo por job, além de quantidade de posts. Um lote de 30 jobs não é justificável pela ausência de alerta no primeiro.

**INFERÊNCIA:** reabrir muitos produtos, curtir em lote ou executar coleta aberta aumenta carga e exposição a falhas; não há evidência suficiente para afirmar que uma sequência idêntica seja um sinal específico usado pela Shopee. A correção proposta é reduzir trabalho e exigir estado verificável, sem “humanizar” movimentos ou randomizar intervalos.

**INFERÊNCIA:** mudança de app, Android, idioma, densidade, zoom ou tema pode mudar IDs, árvore, thumbnail e cores. As verificações atuais podem parar corretamente, mas também podem aceitar uma estrutura comercial errada. App atualizado deve voltar a REVIEW até testes locais de navegação e seletores; não congelar uma versão antiga indefinidamente.

### Mídia: separar quatro riscos

| Eixo | Evidência e avaliação | Controle proposto — INFERÊNCIA |
|---|---|---|
| Upload técnico | **DOCUMENTADO local:** o último MP4 possui H.264, 720×1280, 25 fps, 15,023 s, vídeo ~0,963 Mb/s, AAC ~0,129 Mb/s, arquivo ~2,06 MB. FFprobe leu os metadados. Isso não prova decodificação integral nem requisito oficial. | Decodificação completa, MP4/H.264/AAC e dimensões verticalizadas como perfil interno; bloquear arquivos inválidos. |
| Moderação | **DESCONHECIDO:** aprovação de todos os seis vídeos; esta auditoria não revisou frames, áudio e claims de cada um. | Revisão do vídeo completo, áudio/legenda e produto. |
| Copyright | **DESCONHECIDO:** origem/licença dos vídeos, música e imagens. Nome de arquivo e download não provam titularidade. | `rights_status=VERIFIED`, licença/consentimento e escopo comercial arquivados. |
| Distribuição | **DESCONHECIDO:** alcance dos posts e impacto desse caso. Elegibilidade por originalidade é tema de política, distinto do aceite técnico. | Identidade criativa própria; evitar reposts/peças quase idênticas; avaliar métricas reais sem atribuição automática a punição. |

[Probe local e hash do MP4](</C:/Users/GAMER/Documents/SHOPEE AUTOMATION/ai-commerce-content-factory/docs/publishing/audit/offline-evidence-2026-10-06.json>), [regras de qualidade/originalidade](https://help.shopee.com.br/portal/10/article/165433), [orientação específica sobre IA](https://help.shopee.com.br/portal/10/article/224502).

**Proposta interna, não requisito oficial:** master 1080×1920, 30 fps, H.264/AAC, vídeo 4–8 Mb/s conforme complexidade, áudio 128 kb/s, 10–30 s no piloto. Manter 720×1280 se a revisão comprovar boa leitura e nitidez; não reencodar apenas para satisfazer um número arbitrário. Um codec adequado pode ainda falhar por rede ou processamento.

**Duplicação:** hash igual detecta bytes iguais; reencode pode produzir hash novo para a mesma peça. Usar ID lógico do asset/campanha e detecção perceptual para encaminhar a REVIEW; não publicar novamente para “testar”. Direitos de música são separados dos direitos do vídeo. Watermark concorrente deve causar revisão de origem e seleção de mídia autorizada, não remoção para disfarçar origem. Metadados devem guardar proveniência/versão/direitos e eliminar dados privados desnecessários, sem fabricação de identidade. [Regras de uso de conteúdo e música](https://help.shopee.com.br/portal/4/article/150523).

**IA:** se o arquivo tiver conteúdo de IA de terceiros, exigir indicação e direitos verificados. Não foi confirmado se o MP4 testado contém IA nem se tinha indicação. A automação hoje não tem esse gate. [Termos de IA, 3.3](https://help.shopee.com.br/portal/4/article/167605).

### Vídeo ↔ produto

**INFERÊNCIA:** um título exato pode existir em vendedores, variantes e anúncios distintos. Uma mochila semelhante não prova mesmo modelo. Thumbnail igual não prova que todos os frames, tamanhos, itens do kit ou cores correspondam à oferta.

Contrato proposto, ligado ao hash final da mídia, conta, copy e evidência atual do produto:

| Check | Critério de PASS proposto | Condição que bloqueia |
|---|---|---|
| `product_identity` | `shop_id + item_id` exatos, URL canônica e destino da vinculação conferidos. | Título apenas, redirecionamento inesperado ou anúncio diferente. |
| `variant_match` | Modelo, cor, tamanho e kit compatíveis com o que aparece/é dito. | Variante desconhecida ou incompatível. Se o vídeo mostra várias cores, comprovar que pertencem ao anúncio e esclarecer a escolha. |
| `product_match_status` | Revisão visual e factual PASS com evidência de frames + oferta. | REVIEW/UNKNOWN/FAIL. Não inventar `product_match_score` numérico sem calibração. |
| `product_available` | Disponibilidade da oferta/variante e vínculo confirmados no momento da preparação. | Sem estoque, anúncio removido, restrição de região ou estado desconhecido. |
| `media_quality` | QA técnico + revisão visual/áudio PASS. | QA ausente, arquivo corrompido ou descrição enganosa. |
| `rights_status` | VERIFIED com documentação aplicável a vídeo, música, voz e imagens. | UNKNOWN/REJECTED. |
| `caption_match` | Claims ligados a fatos confirmados; CTA e hashtags pertinentes. | Promessa sem prova, preço/cupom desatualizado ou produto incoerente. |
| `ai_disclosure` | Origem classificada; indicação presente quando aplicável. | IA de terceiros sem indicação ou origem UNKNOWN. |
| `human_review` | Aprovação específica com revisor, timestamp, hashes e validade. | Booleano antigo ou revisão de outro arquivo/produto. |

Alguns campos podem ser legitimamente não aplicáveis, com justificativa explícita. Falta de campo na API não permite preencher `true`; deve exigir fonte oficial/inspeção manual. Revalidar se mudarem mídia, produto, variante, preço citado ou legenda. Tudo acima é desenho, não implementação atual. A necessidade de correspondência comercial é [DOCUMENTADA](https://help.shopee.com.br/portal/10/article/165433); os checks são **INFERÊNCIA de engenharia**.

## 6. Pontos desconhecidos

| Pergunta | Resultado |
|---|---|
| A Shopee autoriza uiautomator2/ADB para esta conta? | DESCONHECIDO; nenhuma exceção registrada. A regra geral/específica desfavorece o uso. |
| Detecta depuração USB, processo uiautomator2, dumps, coordenadas ou timing? | DESCONHECIDO; a política de privacidade não confirma esses sinais específicos. |
| Qual a chance de banimento após um teste? | DESCONHECIDO; sem amostra, investigação ou confirmação da plataforma. |
| Existe quota diária pública uniforme de Shopee Video no Brasil? | Não localizada nas fontes pesquisadas; UNKNOWN. |
| 20–30/dia é permitido para este método? | NOT SUPPORTED BY OFFICIAL EVIDENCE. |
| Resolução mínima, bitrate, codecs, duração/tamanho máximos do upload? | Não confirmados por especificação oficial aplicável nesta pesquisa. Valores da seção 5 são internos. |
| Existe API oficial de publicação habilitada a este afiliado? | Não confirmada; API de ofertas é outra capability. |
| O Chrome está automatizado com segurança? | Implementação não localizada. |
| Direitos e originalidade dos seis vídeos? | Não auditados individualmente; UNKNOWN. |
| Houve perda de distribuição ou punição na conta? | Não comprovada. Nenhuma inferência a partir de poucas views. |
| Post anterior tem ID/URL e vínculo correto? | Usuário reportou sucesso; reconciliação independente pendente. |

Pesquisa incluiu termos de serviço gerais/Video, afiliados, diretrizes, IA, privacidade e buscas oficiais sobre “vídeos por dia”, limite de publicação, duração, resolução e codec. Ausência de resultado não prova ausência de limite interno. Não foi feita engenharia reversa ou análise de tráfego privado.

## 7. Problemas encontrados no código

Arquivos e linhas correspondem ao snapshot com SHA-256 no [manifest de evidências](</C:/Users/GAMER/Documents/SHOPEE AUTOMATION/ai-commerce-content-factory/docs/publishing/audit/offline-evidence-2026-10-06.json>). Severidade considera o cenário de futura execução em lote. Correções são recomendações; **nenhuma foi implementada**.

| ID | Arquivo / função / linha | Risco e evidência | Severidade | Correção recomendada |
|---|---|---|---|---|
| C01 | `app/mobile/shopee_video.py`, `publish`, 535; config de teste | `publish_authorized` e texto de origem só comprovam autorização local do usuário; não existe gate de autorização Shopee. | HIGH | Distinguir consentimentos e escopo. Desabilitar operação de plataforma por padrão até autorização aplicável. |
| C02 | Mesmo arquivo, `matching_product_rows`, 122–143 | Sobe até qualquer ancestral com um único Adicionar. Título solto e botão de outro produto podem ser associados. **REPRODUZIDO:** retornou “Mochila esperada” em XML cujo botão pertencia a Outro produto. O teste existente cobre dois botões, não um. Os checks posteriores de título no modal/vínculo podem bloquear o envio de outro título; o repro não demonstrou publicação errada. | MEDIUM | Delimitar o card comercial pelo container/ID observado; conferir IDs do anúncio antes e após vínculo. |
| C03 | Mesmo arquivo, `select_product`, 354; `validation_checks`, 97 | Confere título, não `shop_id/item_id`, variante, disponibilidade ou conteúdo completo do vídeo. Correspondência visual comercial não é validada automaticamente. | HIGH | Integrar contrato da seção 5; REVIEW para lacunas; bloquear anúncio/variante divergente. |
| C04 | Mesmo arquivo, `select_media`, 473; `media_matches`, 497; `publish`, 539 | Seleção nova registra `visual_preview_reviewed=False`, mas `media_matches` não exige esse check. **REPRODUZIDO:** mídia e oito checks passaram com revisão falsa. `adopt_selection` exige revisão, mas essa proteção não cobre o caminho novo. | HIGH | Gate explícito de revisão vinculada à mídia/produto/copy em todos os caminhos, antes de autorizar postagem. |
| C05 | Mesmo arquivo, `run_prepared`, 575; `reserve_attempt`, 515 | Outro job com mesmo hash só consulta o registro global no fim. **REPRODUZIDO com ações falsas:** seleção, legenda, produto e compartilhamento ocorreram antes do bloqueio. Não foi reproduzido segundo clique final. | MEDIUM | Consultar/reservar identidade de trabalho antes de efeitos na UI; resultado incerto bloqueia também preparação e novo upload. |
| C06 | Mesmo arquivo, `reserve_attempt`, 518; `device_lock`, 178 | Chave serial+hash e arquivos por raiz. Outra raiz/dispositivo, operação manual ou mídia reencodada não compartilham dedup. Não há identidade persistente por conta/post lógico. | HIGH para lote em várias raízes/dispositivos; parcialmente mitigado no teste único | Registro central transacional por plataforma+conta+asset lógico; hash adicional; escopo de lock compartilhado entre entrypoints. |
| C07 | Mesmo arquivo, `publish`, 557–573 | 60 s e regex de mensagem genérica; sem ID/URL, prova do post correspondente ou reconciliação. Timeout real observado. Uma mensagem genérica não vincula sozinha o post à mídia. | MEDIUM | Separar aceitação/upload/processamento/publicado; conciliar conta, conteúdo, produto e ID/URL com evidência. UNKNOWN bloqueia repost. |
| C08 | Mesmo arquivo, `run_prepared`, 575; CLI `main`, 11 | Não há orçamento por sessão/dia/conta, circuit breaker global, cooldown persistente ou kill switch. Parar uma chamada não impede novas chamadas externas. | HIGH no cenário proposto de 20–30/dia | Persistir orçamento e estado OPEN/HALF_OPEN/CLOSED; defaults da seção 9; falha crítica abre bloqueio manual. |
| C09 | Mesmo arquivo, `wait`, 237; `observe`, 230 | Loop tem deadline, não é infinito por lógica; mas deadline só é checado após chamadas de dump/foreground retornarem. Sem deadline total de worker, RPC bloqueante pode alongar sessão. | MEDIUM | Deadline total, RPCs com timeout conhecido e supervisor que encerra sem repetir efeitos; preservar tentativa incerta. |
| C10 | Mesmo arquivo, `select_media`, 392; `adopt_selection`, 481 | Conta é opcional, cheque por substring apenas ao entrar pelo perfil; começar na câmera/picker não confirma conta atual. Resume compara campo em prova antiga, sem freshness/identidade atual independente. | HIGH | Conta obrigatória e comparação exata no preflight; atestar sessão atual antes de efeitos; validade e hash de aprovação. |
| C11 | Mesmo arquivo, `select_media`, 431–455 | Mapeamento índice/duração dos seis primeiros não identifica univocamente células de vídeos com durações iguais. Hash prova o arquivo fonte consultado, não por si só que a célula escolhida é esse arquivo. | MEDIUM | Associação visual revisada e inequívoca; snapshot de inventário/célula; qualquer colisão vira REVIEW. Não expandir índice sem nova prova. |
| C12 | Mesmo arquivo, `sharing_disabled`, 310; `liked_tab_active`, 336 | Regra “cinza=inativo” pode aceitar branco/cinza de asset não carregado; underline depende de cor/tema. Pixel hash exato de thumbnail pode rejeitar variação benigna. Há risco de falso resultado ao mudar UI. | MEDIUM | Exigir imagem completa/estado estabilizado e referência aprovada por versão; preferir estado semântico; ambiguidade bloqueia. |
| C13 | Mesmo arquivo, `Screen.guard`, 73; `checkpoint`, 247 | Lista textual não cobre todo login/SMS/confirmação de aparelho/suspensão possível, WebView/canvas ou Chrome. PNG completo inclui barra/status; XML filtra só filhos superiores e mantém descendentes. Helpers não têm supressão de códigos. | MEDIUM | Estados permitidos e revisão quando tela desconhecida; testes de desafios; minimização/recorte/redação, retenção e ACL; nunca capturar códigos/senhas. |
| C14 | `scripts/probe_shopee_android.py`, `main`, 17, 91–105 | Docstring diz read-only, mas aceita cliques/edição/vínculo. Bloqueio de Postar é só por texto; seleção por ID não tem bloqueio equivalente. Após timeout de condição imprime erro e segue captura. Sem lock comum. | HIGH | Separar observador realmente read-only de ferramenta de ação; final exclusivamente no worker validado; falha fecha execução; lock comum e gates idênticos. |
| C15 | `scripts/research_shopee_hashtags.py`, `main`, 22–50 | Sobrescreve legenda para pesquisar tags, sem restaurar snapshot; quantidade de queries sem teto próprio; grava hierarquia/PNG completos; sem lock/guard comum. | MEDIUM | Pesquisa separada de sessão pronta; restaurar somente antes de tentativa e com autorização; teto, parada e logging seguro. |
| C16 | `scripts/prepare_shopee_android_resume.py`, `main`, 19–44 | Gera booleano de revisão verdadeiro a partir de arquivos fixos deste teste; verifica integridade, mas não executa revisão nem cria aprovação nova independente. Pode parecer genérico. | MEDIUM | Marcar ferramenta como específica de replay de evidência; revisão estruturada, revisor/tempo/hash/expiração; impedir reutilização como aprova-tudo. |
| C17 | `app/providers/shopee/client.py`, `execute`, 70–83; `scripts/execute_kbeauty_research.py`, `search_all_products`, 157 | Cliente reconhece 429 e falha, mas perde Retry-After na exceção. Script captura qualquer erro, espera 1 s e segue próxima query, inclusive após 429/403. Espera normal 0,4 s não é limiter global. | MEDIUM | Classificar erro, suspender lote em rate limit/acesso, respeitar sinal do servidor, budget compartilhado e backoff de consultas idempotentes. |
| C18 | `app/providers/shopee/live.py`, `get_product`, 81–como esta o progesso?107 | Caminho por ID devolve primeiro nó sem confirmar IDs; fallback por palavra retorna primeiro resultado. Não integrar essa conveniência como prova de binding. `research_bolsas_shopee.py` já demonstra filtro exato de IDs. | MEDIUM | Separar busca de candidato de lookup obrigatório por IDs; exigir coincidência exata e contrato explícito. |
| C19 | `app/mobile/shopee_video.py`, `validation_checks`, 97; `app/validation/media.py`, `TechnicalMediaValidator.validate`, 116 | RPA não chama QA técnico existente nem gate de direitos/originalidade/disclosure. Validador existente não solicita bitrate; dimensões/codecs são opcionais. | HIGH | Gate antes de selecionar/upload; estender relatório técnico só se necessário; REVIEW para direitos/semântica ausentes. |
| C20 | `tests/publishing/test_shopee_android.py`, classe de testes | 14 testes do núcleo + 15 assistidos passam, sem cobrir os três casos reproduzidos, expiração/aplicativo atualizado, confirmação tardia, conflito entre helpers e orçamento global. | MEDIUM | Adicionar testes de invariantes e falhas com fixtures reais sanitizadas; não usar publicação live como teste de regressão. |

### O que a inspeção não encontrou

Não foram encontrados sleeps excessivos no núcleo, retry ilimitado de publicação, loop infinito de navegação ou tabela de coordenadas fixas de cliques. `wait` usa deadline; observação posterior também é finita. Há fragilidade de ordem por `instance`, geometria de recorte e cores, que é diferente de clicar coordenadas absolutas. Os sleeps encontrados no script de pesquisa não provam abuso por si; o problema é continuar o lote após erros de acesso/frequência.

O núcleo costuma validar resultado após ações. Helpers têm verificações mais fracas e caminhos que continuam depois de falhar. Há estado e dedup locais; o problema é escopo e momento da verificação, não ausência total. Não há prova de múltiplas publicações já realizadas por uma falha.

### Verificação realizada

- `python -m unittest discover -s tests/publishing -v`: **29 aprovados, zero falhas/erros**, 5,147 s nesta rodada. Warning de depreciação de Pillow em `getdata`; sem mudança de código.
- Três reproduções sintéticas em `collect_offline_evidence.py`, com dispositivos/ações falsos e filesystem temporário. Não representam tráfego nem execução Shopee.
- FFprobe somente no MP4 local; SHA-256 e metadados no JSON.
- Hashes de 16 arquivos de implementação/testes e da sessão preservados no JSON. A suíte completa da fábrica não foi reexecutada; os testes existentes não provam autorização ou qualidade de todos os vídeos.

### Delegação ao Antigravity solicitada pelo usuário

**Status atual: revisão independente recebida e consolidada em 06/10/2026.** O escopo foi C02/C04/C05/C14, fundamento da classificação HIGH e distinção entre controles existentes e propostas. Não equivale a uma nova pesquisa das políticas nem à validação independente dos vinte achados completos.

O Antigravity Bridge passou no health check. A primeira task `b14b1b20-5f0a-49c7-8311-28d4af3f3335` retornou `completed` sem texto ou artefatos; a tentativa seguinte `7402bc30-ca69-4330-b3e8-8604f2c9addd` leu relatório/código, mas terminou por timeout de 420 s. O estado histórico `FAILED_NO_ARTIFACTS` da primeira tentativa permanece no [registro original](</C:/Users/GAMER/Documents/SHOPEE AUTOMATION/ai-commerce-content-factory/docs/publishing/audit/antigravity-delegation-2026-10-06.json>).

A resposta foi recuperada pelo CLI oficial `agy`, retomando a conversa `a2f2534b-741c-4a7c-a74d-9cdeea45d74d`, em modo de planejamento/sandbox, sem novas ações em dispositivo ou conta. O Codex salvou o texto recebido, sem atribuir a si a autoria do parecer. [Parecer independente](</C:/Users/GAMER/Documents/SHOPEE AUTOMATION/ai-commerce-content-factory/docs/publishing/audit/antigravity-review-2026-10-06.md>) e [complemento C14](</C:/Users/GAMER/Documents/SHOPEE AUTOMATION/ai-commerce-content-factory/docs/publishing/audit/antigravity-c14-2026-10-06.md>); os recibos registram horário, saída bem-sucedida e SHA-256 de cada arquivo.

| Ponto revisado | Resultado consolidado | Limite da evidência |
|---|---|---|
| C02 — associação de título/botão fora do card | CONFIRMADO / CORREÇÃO_NECESSÁRIA | Reprodução sintética; validações posteriores podem impedir vínculo errado. Não comprova publicação errada real. |
| C04 — revisão visual ignorada na seleção nova | CONFIRMADO / CORREÇÃO_NECESSÁRIA | Inspeção estática e reprodução offline; sem nova publicação. |
| C05 — dedup tardia em novo job | CONFIRMADO / CORREÇÃO_NECESSÁRIA | Há efeitos de preparação antes do bloqueio; o bloqueio existente ainda antecede o clique final. |
| C14 — trava textual insuficiente no probe | CONFIRMADO / CORREÇÃO_NECESSÁRIA | O complemento analisou o trecho literal das linhas 86–109 e substitui o UNKNOWN inicial; nenhuma ação de clique executada. |
| HIGH e piloto condicionado | Fundamentação confirmada | Exposição elevada; probabilidade de banimento desconhecida. Hardening não concede autorização da plataforma. |

Na recomendação C05, antecipar a consulta de tentativas anteriores e a reserva de trabalho antes dos efeitos de UI; preservar a reserva durável de tentativa de publicação imediatamente antes do clique final. Uma falha apenas de preparação não deve ser registrada como tentativa de envio. As correções continuam **propostas, não implementadas**. O runtime e o registro da tentativa anterior foram preservados. Créditos efetivamente usados não foram informados, portanto não há economia quantificada. [Registro consolidado](</C:/Users/GAMER/Documents/SHOPEE AUTOMATION/ai-commerce-content-factory/docs/publishing/audit/antigravity-review-status-2026-10-06.json>).

## 8. Risk Register

Probabilidade descreve ocorrência do evento, não uma nota de severidade. “Reproduzível” refere-se ao cenário sintético definido; probabilidade em produção continua desconhecida. Status é o estado observado, sem mitigação imaginária.

| Risco | Origem | Probabilidade | Impacto / severidade | Evidência | Mitigação proposta | Status |
|---|---|---|---|---|---|---|
| Restrição por interação automatizada não autorizada | Política/método | Aplicação de sanção UNKNOWN; regra documentada | Conta/receita — HIGH | 4.1(g), 6.2(k); C01 | Operação manual ou permissão aplicável | ABERTO |
| Comissão retida/vínculo encerrado | Programa afiliados | UNKNOWN, depende de violação/análise | Receita — HIGH | Termos afiliados 5.2/7.2 | Conformidade e autorização | EXPOSIÇÃO, sem sanção observada |
| Produto/variante incorretos | Binding | UNKNOWN; lacuna C02 reproduzível | Conteúdo/conta — HIGH | C02/C03/C18 | IDs, variante e revisão completa | ABERTO |
| Post sem revisão/direitos/QA | Gates ausentes | UNKNOWN; caminho C04 reproduzível | Conteúdo/receita — HIGH | C04/C19 | Gates fechados por padrão | ABERTO |
| Repost após envio incerto | Retry/observabilidade | Incertidão já observada; duplicata não observada | Conteúdo — MEDIUM local; HIGH se escalar | C05/C06/C07 | Ledger central + reconciliação | PARCIALMENTE MITIGADO |
| Excesso de ações em lote | Orçamento ausente | UNKNOWN; capacidades futuras não implementadas | Operação — HIGH para lote proposto | C08; sem quota pública confirmada | Budgets persistentes, piloto condicionado | ABERTO |
| Erros após atualização | Seletores/pixels | UNKNOWN | Operação/vínculo — MEDIUM | C09/C11/C12 | REVIEW de versão, timeout e regressão | ABERTO |
| Conta errada/sessão antiga | Preflight | UNKNOWN | Publicação indevida — HIGH | C10 | Conta exata, sessão atual, expiração | ABERTO |
| Captura de dados sensíveis | Evidências/helpers | UNKNOWN; capturas integrais documentadas | Privacidade — MEDIUM | C13/C15 | Supressão/redação/ACL/retenção | PARCIALMENTE MITIGADO no núcleo |
| Ferramenta auxiliar fora dos gates | Entry points | UNKNOWN | Publicação sem validação — HIGH | C14 | Ações centralizadas; probe read-only | ABERTO |
| Continuar depois de rate limit | Script Affiliate | Condicional; branch documentado, sem 429 live nesta auditoria | Operação — MEDIUM | C17 | Parar, respeitar Retry-After | ABERTO |
| Inelegibilidade para recomendação | Originalidade/qualidade | UNKNOWN para estes vídeos | Distribuição — MEDIUM | Políticas Video/IA; mídia não revisada | Autoria/qualidade/direitos | NÃO AVALIADO individualmente |
| Detecção específica de ADB/uiautomator2 | Telemetria interna | UNKNOWN | Penalidade potencial não mensurável | Sem confirmação pública específica | Permissão e conformidade, sem evasão | DESCONHECIDO |
| Falhas no fluxo Chrome | Componente não localizado | UNKNOWN | UNKNOWN | Declaração do usuário; sem adapter encontrado | Auditar implementação quando fornecida | NÃO AVALIADO |

Fontes das linhas de política: [termos Video](https://help.shopee.com.br/portal/4/article/150523), [termos gerais](https://help.shopee.com.br/portal/4/article/77113), [afiliados](https://help.shopee.com.br/portal/10/article/124094), [diretrizes](https://help.shopee.com.br/portal/10/article/165433), [IA/originalidade](https://help.shopee.com.br/portal/10/article/224502). Não se atribuiu HIGH à hipótese de telemetria desconhecida.

## 9. Checklist de Hardening

Todos os itens abaixo são **INFERÊNCIA / controles propostos**, não mudança aplicada ou requisito numérico oficial.

### Limites internos do MVP

**Sem autorização aplicável: zero jobs RPA que interajam com Shopee Video em produção.** Os valores de piloto abaixo só se aplicam a uma interface autorizada ou a um processo manual supervisionado; não são faixa de tolerância de bots. Para teste de UI, preferir fixtures/mocks até haver permissão.

| Controle | Valor inicial proposto | Razão / escopo |
|---|---|---|
| `MAX_POSTS_PER_SESSION` | 1 | Unidade revisável; reservar orçamento antes de efeitos. |
| `MAX_POSTS_PER_DAY` | 1 | Por conta/plataforma, incluindo tentativas incertas e publicações manuais registradas; dia America/Sao_Paulo. |
| `MAX_PRODUCT_VIEWS_PER_SESSION` | 5 | Apenas candidatos pré-selecionados; sem exploração aberta. |
| `MAX_PRODUCT_LIKES_PER_SESSION` | 0 automáticas | Curtidas não são necessárias ao piloto; seleção manual ou catálogo/API dentro do escopo. |
| `MAX_UPLOAD_ATTEMPTS_PER_SESSION` | 1 | Upload/aceitação são efeitos de negócio. |
| `MAX_UPLOAD_RETRIES` | 0 | Falha incerta não permite reenviar automaticamente. |
| `MAX_CONSECUTIVE_FAILURES` | 2 erros recuperáveis; 1 crítico | Contagem persistente; crítico inclui desafio, restrição, binding e envio incerto. |
| `SESSION_MAX_DURATION` | 15 min | Deadline total; revisão humana mais longa encerra/reabre com nova validação. |
| `COOLDOWN_AFTER_ERROR` | 15 min mínimo para erro recuperável | Não retomar automaticamente; erro de conta/envio incerto exige resolução humana. |
| `MAX_READ_RETRIES` | 2 | Somente leituras idempotentes, nunca click/post/upload/login. |
| `READ_BACKOFF` | 30 s, depois 120 s | Determinístico, para reduzir carga e dar tempo à recuperação; respeitar espera maior indicada pelo servidor. |
| `MAX_AFFILIATE_REQUESTS_PER_SESSION` | 10 | Budget interno separado da UI; cache por consulta/IDs. |
| `MAX_AFFILIATE_REQUESTS_PER_DAY` | 30 no piloto | Só com acesso concedido; reduzir caso a quota autorizada seja menor. Não representa quota oficial. |
| `CONCURRENCY_PER_ACCOUNT` | 1 | Lock central compartilhado pelos workers/helpers. |
| `APPROVAL_TTL` | 30 min, invalidada por mudança relevante | Evitar aprovação velha; direito/licença pode ter validade própria. |

Não iniciar próximo job para “compensar” timeout. Contabilizar `RESERVED`, `UPLOADING`, `PUBLISHING` e `UNKNOWN`, não apenas PUBLISHED. Dois workers devem consumir o mesmo orçamento numa transação. O limite efetivo sempre será o menor entre a política interna e o escopo autorizado.

### Ação → resultado → validação

| Etapa | Timeout interno inicial | Saída obrigatória |
|---|---|---|
| ADB/preflight | 15 s | Serial pronto, conta e app/versão permitidos. |
| Navegação/busca | 20 s | Estado esperado, sem erro/desafio. |
| Preview/preparação | 30 s | Mídia/copy/produto inequívocos. |
| Aceitação/processamento de upload | Até 180 s de observação, se autorizado e estado identificável | Progresso/aceitação documentados; nunca novo upload para resolver dúvida. |
| Confirmação do post | 60 s; depois até 180 s de reconciliação somente leitura autorizada | Post correspondente/ID ou UNKNOWN. |

Timeouts não são esperas fixas obrigatórias; são tetos sujeitos ao deadline da sessão e aos timeouts de RPC. Segurança e desafios interrompem imediatamente, independentemente do teto.

### Checklist priorizado

- [ ] **P0:** esclarecer permissão de interação; manter método não autorizado fora de produção.
- [ ] **P0:** reconciliar tentativa anterior sem excluir ledger ou repostar.
- [ ] **P0:** corrigir card comercial, revisão de seleção nova e conta obrigatória.
- [ ] **P0:** gates de IDs/variante, direitos, IA, disponibilidade e QA da mídia.
- [ ] **P0:** bloquear entrada auxiliar de clique final e compartilhar locks/gates.
- [ ] **P1:** ledger por conta+asset, orçamento transacional, circuit breaker e kill switch.
- [ ] **P1:** deadline total e recuperação de leitura; nunca retry de efeito incerto.
- [ ] **P1:** registro de versão do app/Android/idioma e testes de atualização.
- [ ] **P1:** minimizar evidências; reter dados técnicos suficientes, sem códigos, senhas, cookies, tokens ou telas financeiras.
- [ ] **P1:** alertar apenas falha/action-required/conclusão, com `job_id`, etapa, motivo e artefato.
- [ ] **P2:** testes de confirmação tardia, erro de upload, conflito entre scripts e budget em rollover diário.
- [ ] **P2:** telemetria local de tentativas, uploads, aberturas, curtidas, duração, erros consecutivos e consumo de orçamento; métricas ausentes ficam null.

Circuit breaker proposto: CLOSED permite dentro do orçamento; OPEN interrompe ações de plataforma; HALF_OPEN só após revisão, cooldown e preflight idempotente. CAPTCHA, restrição de conta, mídia/produto divergentes e envio UNKNOWN não reabrem pelo relógio. Revisor registra motivo e evidência. Backoff não serve para esconder automação.

## 10. Plano de implantação segura

### Fase 0 — Conformidade e auditoria offline

Resolver permissão/interface, reconciliação pendente e achados P0. Revisar origem/direitos dos seis vídeos. Manter geração local separada da conta Shopee. Auditar o componente Chrome real. Sem novas tentativas live de RPA como forma de descobrir tolerância.

### Fase 1 — Uma publicação revisada

Uma postagem manual no app ou por interface formalmente autorizada, com revisão completa do asset/copy/produto/variante, snapshot de disponibilidade e identidade da conta. Registrar ID/URL e confirmação correspondente. O sucesso reportado pelo usuário no teste anterior não substitui a correção das lacunas do worker.

### Fase 2 — Pequeno lote separado em dias

Depois dos controles e permissão, três publicações no total, uma por dia, cada uma com revisão. Conferir upload, vínculo e avisos disponíveis antes de avançar; nova conferência em 24 h é checkpoint interno, não prazo garantido de moderação. Não comprar nem gerar views/cliques para testar comissão.

### Fase 3 — Expansão limitada e revisável

Se houver autorização aplicável, zero pendências UNKNOWN, gates funcionando e observabilidade, propor no máximo três por dia em nova janela piloto, com rollback de operação. Aumento depende de revisão explícita do escopo e dos resultados. Ausência de alerta não torna o método autorizado nem descarta penalidade posterior.

**20–30/dia não é próxima fase aprovada.** Exige evidência de permissão/limites aplicáveis, qualidade e capacidade de operação. Não buscar uma frequência “não detectada”. Processo manual pode ter volume diferente; nenhum teto oficial uniforme foi confirmado nesta auditoria.

## 11. Critérios automáticos de STOP

Proposta para futura implementação; atualmente apenas parte é coberta.

| Trigger | Ação e condição de retomada |
|---|---|
| Sem autorização aplicável à interface/operação | Não conectar/interagir em modo de produção; manter local/manual. |
| CAPTCHA, login, SMS, confirmação de aparelho ou desafio | Parar; intervenção humana no app; sem leitura/gravação de códigos. Novo preflight depois. |
| Suspensão/limitação/alerta de segurança/frequência | Circuit breaker OPEN; seguir instrução oficial/recurso, sem novas tentativas ou troca de conta para contornar. |
| HTTP 429 ou limitação explícita observada | Parar lote e respeitar Retry-After quando houver; revisão antes de retomar. 403 não vira automaticamente “rate limit”. |
| Mídia, título/card, IDs, modelo/variante ou conta ambíguos | REVIEW; corrigir evidência e invalidar aprovação. |
| Direitos, IA, qualidade ou disponibilidade UNKNOWN/FAIL | NÃO PUBLICAR; obter prova/revisão. |
| Hash/copy/produto mudou após aprovação | Invalidar revisão e sessão preparada. |
| Tentativa anterior, upload aceito ou resultado incerto | Bloquear reenvio e próximo job da mesma mídia; reconciliar post/ID. |
| Desconexão ADB ou falha de rede durante efeito | Persistir UNKNOWN; não reiniciar upload/click automaticamente. |
| App/Android mudou ou tela/selector não corresponde | Parar em REVIEW; remapear a partir de evidência, sem exploração cega. |
| Orçamento, deadline, máximo de falhas ou kill switch | Encerrar; liberação explícita e nova validação. |
| Operador tocando aparelho/tela mudou entre check e ação | Suspender automação; revalidar sob controle exclusivo. |

**Conta/sessão legítima:** login pelo titular; não guardar senha/OTP, não extrair/copiar cookies e não repetir login ao primeiro timeout. Expiração interrompe. Atualizações de segurança devem ser mantidas e validadas antes do próximo job. Segregar leitura de estado, efeitos e reconciliação. ADB deve continuar restrito ao host autorizado; nenhuma necessidade de expor depuração em rede pública. [Operação e autorização ADB](https://developer.android.com/tools/adb).

## 12. Recomendação final

**RISCO ATUAL: HIGH**, por regra pública específica contrária à interação por script e lacunas operacionais demonstradas. Não por suposta detecção de ADB, e não como previsão de banimento iminente. Nenhuma penalidade foi comprovada nesta auditoria. [Termos Video, 4.1(g)](https://help.shopee.com.br/portal/4/article/150523).

**20–30 POSTS/DIA: NOT SUPPORTED BY OFFICIAL EVIDENCE.** Quota aplicável e probabilidade de restrição são **UNKNOWN**. Os limites sugeridos são internos e condicionais; não autorização ou garantia.

O nível defensável hoje é automação local de produção, validação e organização, descoberta comercial dentro de API/escopo concedidos e postagem manual. Revisão humana só no final de um RPA que já interage com o app não resolve a questão contratual. Uma integração oficial deve comprovar que permite a operação desejada, para essa conta e região; acesso a API de ofertas não basta.

O projeto contém controles úteis e pode ser endurecido. Ainda não é robusto para lote desassistido, não recebeu promoção READY e não teve comportamento alterado nesta auditoria. As propostas podem ser implementadas numa etapa posterior, após revisão do relatório e do caminho de conformidade.
