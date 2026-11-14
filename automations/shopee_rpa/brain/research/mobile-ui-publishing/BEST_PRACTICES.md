# Regras de implementação propostas

08/10/2026. Regras de pesquisa, não mudanças aplicadas. Evidência referenciada em SOURCES/FINDINGS. Validações descritas aqui são critérios futuros salvo E01–E03.

## BP01 — Permissões com emissores distintos
RULE: separar consentimento do operador, direitos da mídia e autorização de integração/plataforma, cada um com escopo, emissor, referência recuperável, revisão e validade quando aplicável.
SCOPE: preflight, UI e publicação.
EVIDENCE: F01, F13.
RATIONALE: um campo preenchido não autentica o que sua etiqueta afirma.
EXCEPTIONS_OR_LIMITS: não inventar autorização nem promover referências de chat a licença da plataforma; revisão humana deve avaliar o documento aplicável.
VALIDATION: consentimento do operador sozinho não satisfaz platform permission; rights UNKNOWN continua sem autorização final.

## BP02 — Uma ação com contrato de estado
RULE: cada transição declara estado de origem, seletor único, efeito permitido, pós-condição, prazo e destino se ambígua.
SCOPE: controlador Android autorizado.
EVIDENCE: F03, F05, T02.
RATIONALE: o código precisa reconhecer que uma tela mudou, inclusive quando a resposta do clique é inconclusiva.
EXCEPTIONS_OR_LIMITS: “Feito” é uma transição própria; não tratar como sinônimo de Adicionar. Lista ainda carregando não é lista vazia.
VALIDATION: fixtures de estados intermediários, duplicação legítima de título, controle ausente, produto incorreto e timeout.

## BP03 — Evidência fresca sem consultas duplicadas sem propósito
RULE: transportar uma observação coerente por etapa, com timestamp, versão/época, foreground e nós pertinentes; invalidar depois de mutação e diante de mudanças relevantes.
SCOPE: validações na mesma etapa.
EVIDENCE: F03, T02, T05.
RATIONALE: reduzir IO mantendo validação imediata do alvo.
EXCEPTIONS_OR_LIMITS: não reutilizar captura antiga para autorizar Postar; prazo de frescor deve ser medido, não escolhido para encobrir mudança de tela.
VALIDATION: injetar reflow, troca de conta/app, scroll e alterações de card entre observação e despacho; ação incorreta deve ser bloqueada.

## BP04 — Repetição explícita por classe de efeito
RULE: reads podem ter repetição limitada dentro do prazo; mutações não podem ser reenviadas automaticamente quando o efeito é desconhecido, inclusive dentro do SDK.
SCOPE: todas as camadas, não apenas `publish()`.
EVIDENCE: F04, T08, T10, E01.
RATIONALE: timeout de resposta não é prova de não execução.
EXCEPTIONS_OR_LIMITS: idempotência deve ser demonstrada por operação; “adicionar de novo” não é recuperação genérica. Desligar recuperação automática sem testar conexão também não resolve sozinho.
VALIDATION: aplicar efeito simulado e perder resposta; deve haver no máximo um despacho de mutação, incidente persistido e ausência de retry.

## BP05 — Identidade estável e vínculo preservado
RULE: identidade da mídia por hash e referência local; título/card/fonte/IDs disponíveis como evidências distintas de binding. Geometria serve para localizar, não para definir identidade comercial.
SCOPE: galeria, preview e produto.
EVIDENCE: T07, F06, E03.
RATIONALE: mudança de posição não troca produto; vídeo de mesma duração pode ser outro asset.
EXCEPTIONS_OR_LIMITS: IDs não visíveis ficam não observados; revisão explícita de card assistido não equivale a todos os IDs verificados para publicação.
VALIDATION: mudança de bounds mantém identidade; mudança de título/produto/asset invalida; homônimos e mesma duração param em REVIEW.

## BP06 — Escopo de incidente baseado em evidência
RULE: distinguir efeito local incerto de preparação, possível envio, despacho final e publicação relatada; toda resolução preserva eventos e lacunas.
SCOPE: ledger e breaker; proposta exige revisão de arquitetura antes de implementação.
EVIDENCE: F08, F11, F15.
RATIONALE: evitar bloquear uma conta inteira por falha recuperável sem ignorar efeito remoto desconhecido.
EXCEPTIONS_OR_LIMITS: não converter UNKNOWN atual em seguro por ausência de rascunho. Breaker crítico de conta continua global; outros incidentes impedem fechamento.
VALIDATION: local seguro demonstrado não libera incidente de publicação; OPEN → HALF_OPEN → preflight → CLOSED somente quando todos os requisitos forem satisfeitos.

## BP07 — Handoff humano durável
RULE: registrar antes da entrega ao operador qual candidato/editor foi preparado; registrar retorno publicado, cancelado ou desconhecido; proibir continuação concorrente do robô.
SCOPE: modo assistido e publicação manual.
EVIDENCE: F15, L06.
RATIONALE: o usuário pode publicar enquanto o assistente ainda explica; esse é um evento do fluxo, não uma exceção descartável.
EXCEPTIONS_OR_LIMITS: não exigir dados que a interface não fornece para inventar certeza; manter pendência de reconciliação.
VALIDATION: resposta humana tardia e interrupção de processo não autorizam repetir upload/Add/Postar nem criar candidato equivalente.

## BP08 — Medir o trabalho que a pessoa sente
RULE: correlacionar job central, sessão e operação; medir wall time completo, regras/DB, RPC, espera do app, revisão humana e tempo de orquestração separadamente.
SCOPE: observabilidade.
EVIDENCE: F10, T09.
RATIONALE: otimizar 53 s não explica uma tarefa que consumiu muito mais tempo.
EXCEPTIONS_OR_LIMITS: créditos/modelo requerem medição própria; não registrar segredos, conteúdo privado irrelevante ou payloads sem necessidade.
VALIDATION: soma/decomposição coerente com intervalos sobrepostos identificados; percentis sobre várias execuções comparáveis.

## BP09 — Conteúdo com fonte, direitos e qualidade próprios
RULE: manter proveniência, licença, originalidade, disclosure de IA e correspondência de produto em campos independentes; revisar limites de mídia por política/versionamento.
SCOPE: preparação de candidatos.
EVIDENCE: S04–S06, F14.
RATIONALE: qualidade técnica não autoriza conteúdo nem corrige vinculação comercial.
EXCEPTIONS_OR_LIMITS: gerar com IA não apaga obrigações sobre música, imagem, marca ou fontes; não inventar característica do produto.
VALIDATION: anúncio de origem não implica rights VERIFIED; tamanho não observado permanece UNKNOWN; perfil de duração divergente requer revisão.
