# Findings

Revisão: 08/10/2026. IDs de fonte definidos em [SOURCES.md](SOURCES.md). Inspeção de código comprova o contrato escrito; somente fixtures e registros identificados comprovam comportamento observado. Propostas não foram instaladas no runtime.

## WHAT WE KNOW

| ID | Achado | Classe | Evidência |
|---|---|---|---|
| F01 | Autorização do operador e autorização da plataforma são requisitos diferentes. `platform_authorized()` valida referência, escopo e validade temporal, sem comprovar emissor; a configuração histórica usa referência ao chat do operador. | OBSERVED no código/config; INFERRED insuficiência da prova | L01 `safety_runtime.py:82`, L04, S01–S03 |
| F02 | A implementação conserva um processo Android e uma conexão durante comandos normais. | OBSERVED | L01 `ui.py:_device_process`, `IsolatedAndroidDevice` |
| F03 | A leitura se repete em resolução de seletor, guardas e observação; `observe()` combina XML e foreground. O wait usa polling limitado por estado, não um sleep obrigatório de 20 s. | OBSERVED | L01 `ui.py:_execute`, `shopee_video.py:285` e `:293` |
| F04 | `uiautomator2==3.7.0` é a dependência fixada e instalada. E01 reproduz repetição de RPC em perda simulada de resposta. | OBSERVED + EXPERIMENTAL | requirements-android.txt, T04, E01 |
| F05 | O erro do modal com dois títulos é reproduzível a partir do XML histórico. Predicado atual reconhece a folha; antigo não reconhece. | EXPERIMENTAL sobre fixture OBSERVED | E02, L04 |
| F06 | Hash de nós incluindo bounds muda com geometria. Digest semântico atual resiste a essa mudança e rejeita título diferente no experimento. | EXPERIMENTAL | E03 |
| F07 | `publish()` despacha pelo gate e depois chama o reconciliador sem evidência; termina como publicação não confirmada. Não existe nesse caminho um observador que obtenha e vincule automaticamente a prova completa do post. | OBSERVED | L01 `shopee_video.py:663`; L02 `PublicationReconciler` |
| F08 | Erro em RPC de mutação de preparação pode marcar o job UNKNOWN e abrir breaker crítico. A fase/efeito ainda não é discriminada suficientemente. | OBSERVED | L01 `ui.py:_execute` |
| F09 | Toda ação bem-sucedida, inclusive leitura, chama `breaker.success()`. O contador de falhas pode perder significado como sequência de falhas do fluxo de negócio. Isso não significa que uma leitura feche automaticamente todo breaker crítico OPEN. | OBSERVED no código; impacto operacional INFERRED | L01, `app/operational/circuit_breaker.py` |
| F10 | O cronômetro de `latency_ms` começa depois de parte das verificações e IO. Orçamento interno em “tokens” não mede créditos de IA. | OBSERVED | L01 `ui.py:_execute`, L02 |
| F11 | `UPLOAD_START` existe no orçamento, mas não há consumo explícito desse tipo no fluxo nativo inspecionado. Zero no contador não prova ausência de upload interno do aplicativo. | OBSERVED + limite UNKNOWN | L01, L02 |
| F12 | Limite de ações do worker e duração de sessão têm escopos diferentes de limite diário de publicação. Retomadas com alias local não devem ser usadas para inferir custo ou número de tentativas globais. | OBSERVED | `action_budget.py`, config e logger |
| F13 | A modalidade assistida distingue direitos desconhecidos da autorização final; publicação mantém seus requisitos. A distinção técnica não resolve a questão F01. | OBSERVED | L01, PublishGate e requisitos do operador |
| F14 | Tamanho aceito no perfil de duração local (1–180 s) diverge da FAQ consultada (3–60 s). Recursos de cupom também apresentam divergência entre FAQ, termos e UI histórica. | OBSERVED + DOCUMENTED | config.MediaProfile, S03, S09, L04 |
| F15 | O usuário informou publicação manual; a última evidência de projeto mantém UNKNOWN, motivo específico, breaker OPEN e retry bloqueado. | OBSERVED: registro, não inspeção pública | L06 |

## WHAT SEEMS TO WORK

- Ledger, dedup, leases e reconciliação impedem diversos caminhos locais de repetição. Preservar; não equivalem a idempotência do servidor remoto (L02, T08).
- O fluxo real chegou ao editor final e vinculou produto após “Feito”, conforme evidências históricas. O registro central `ASSISTED_VALIDATED` falhou na revisão do binding; tela alcançada e estado certificado não são sinônimos (L06 e CURRENT_STATE).
- O seletor corrigido de Adicionar e o reconhecimento da folha têm sustentação em fixtures. A correção posterior do digest não foi recertificada no celular antes da publicação humana; não promover a validação offline a E2E real (L04, E02–E03).
- Entrada de legenda já usa operação de texto; não é necessário planejar digitação letra a letra. A captura para conferir compartilhamento já agrupa controles em um frame em `sharing_disabled`; reduzir apenas repetições restantes, sem “corrigir” um problema já corrigido (L01).
- Estados e seletores específicos oferecem uma base melhor que decisões livres do modelo para cada clique. Essa conclusão de design é INFERRED; o ganho exige benchmark controlado (T02–T05).

## WHAT IS UNCERTAIN

1. Probabilidade de punição, limiares antifraude e detecção específica de ADB/uiautomator2: UNKNOWN. Privacidade documentada não revela classificador interno (S07).
2. Autorização excepcional aplicável ao RPA nesta conta: não comprovada. O consentimento humano já registrado é real, mas não tem o mesmo emissor (F01).
3. Direitos de republicação e uso de IA no mousepad: UNKNOWN. Fonte de anúncio confirmada não preenche esses campos.
4. Instante de upload nativo e efeito remoto de chamadas antigas com resposta perdida: UNKNOWN. Nem ausência de rascunho nem arquivo presente na galeria respondem isso.
5. Causa exata do binding inválido após legenda: mudança de geometria é uma hipótese forte, não foi demonstrada por um par completo de evidências antes/depois do incidente (E03).
6. Ganho de remover consultas duplicadas, custo de SQLite, inicialização Windows e inferência do agente: faltam spans completos. 53,2 s de RPC não são o tempo total do trabalho.
7. Disponibilidade de API de publicação social Video: não confirmada. Portal de afiliados não documentou publicamente esse contrato na consulta (S11).

## WHAT NEEDS TESTING

Consultar [BENCHMARK_PLAN.md](BENCHMARK_PLAN.md). Prioridades: perdas de resposta em cada fase; transporte sem replay de mutação; lista carregando versus vazia; binding estável após legenda; estado persistido após intervenção humana; prova pós-publicação; atribuição de tempo por componente. Testes reais dependem da permissão aplicável e de gates satisfeitos; não usar o mousepad já publicado como ensaio novo.
