# Falhas e riscos

08/10/2026. Capability: mobile-ui-publishing em todos os itens. HIGH/MEDIUM descrevem prioridade de mitigação qualitativa, não probabilidade medida de punição. Risco atual agregado recomendado: HIGH. Nenhuma mitigação proposta abaixo foi aplicada nesta pesquisa.

| ID / prioridade | FAILURE / TRIGGER | IMPACT | EVIDENCE | DETECTION | MITIGATION | RESIDUAL_RISK |
|---|---|---|---|---|---|---|
| R01 HIGH | Operar sob suposta autorização da plataforma baseada em chat do operador | Exposição de conformidade independente de frequência | F01, S01–S03; OBSERVED/DOCUMENTED | Auditar emissor, escopo e documento | Separar permissões; preparar localmente e manter publicação humana enquanto permissão aplicável não é comprovada | Regras mudam; nenhuma arquitetura promete zero punição |
| R02 HIGH | Usar material de anúncio sem prova separada de direitos | Reclamação ou medida sobre conteúdo/conta | F13, S04; rights atual UNKNOWN | Revisão de origem e licença | Mídia própria/licenciada; preservar UNKNOWN no candidato atual | Originalidade, música e alegações comerciais continuam independentes |
| R03 HIGH | Resposta perdida após efeito; SDK repete RPC | Mutação duplicada apesar de uma chamada local | F04/E01; EXPERIMENTAL | Instrumentar dispatcher e transporte; injetar perda de resposta | Contrato sem replay para mutações e reconciliação | Sem idempotência remota, efeito após timeout pode continuar desconhecido |
| R04 HIGH | Caminho de publicação sem coleta de prova final | Publicações sempre pendentes; impossível declarar automação E2E pronta | F07; OBSERVED | Teste de saída de `publish()` | Projetar observador/handoff e reconciliador com evidência suficiente | Moderação e ausência temporária de post não provam falha |
| R05 HIGH | Preparação e tentativa final compartilharem reação ampla a efeito incerto | Conta bloqueada; retomadas demoradas e confusas | F08/F11; OBSERVED | Registrar fase, comando, despacho e escopo | Incidentes discriminados com resolução auditada | Não relaxar bloqueio se envio/publicação puderem ter ocorrido |
| R06 HIGH | Operador publica enquanto automação ainda considera editor pendente | Nova ação sobre o mesmo candidato | F15; OBSERVED | Evento explícito de handoff e retorno | Bloquear concorrência; reconciliar post existente | URL/ID e demais provas podem depender do operador |
| R07 MEDIUM | Lista de curtidas ainda carrega quando código decide pesquisar | Busca redundante e confusão de estado | Relato/run histórico e F03; OBSERVED/INFERRED | Distinguir loading, ready, empty e error | Espera pela pós-condição real; usar card exato já visível | Interface pode não expor sinal de carregamento; precisa fallback validado |
| R08 MEDIUM | Predicado exige título único onde modal repete legitimamente título | Timeout depois de Add bem-sucedido | F05/E02; reproduzido | Fixture real `add-result.xml` | Preservar predicado corrigido e exigir contexto da folha + Feito | Mudanças de versão podem introduzir outras estruturas |
| R09 MEDIUM | Hash inclui bounds/foco e invalida binding após edição | REVIEW/FAILED apesar de mesmo produto | E03 reproduz fragilidade; causalidade real INFERRED | Comparação de identidade e apresentação separadas | Digest semântico já corrigido offline; recertificação ainda pendente | Digest estreito demais pode aceitar troca de produto; IDs/fonte continuam necessários |
| R10 MEDIUM | Guardas repetem XML/foreground sem observação compartilhada | Mais IO e consumo de orçamento; execução menos fluida | F03/L03; OBSERVED | Contagem por etapa + tracing | BP03, sem remover guarda imediata | UI muda entre leitura e toque; o risco não desaparece por cache |
| R11 MEDIUM | Read bem-sucedido limpa sequência de falhas | Saúde pode parecer melhor que o fluxo de negócio | F09; impacto INFERRED | Teste falha → leitura → falha | Separar saúde de transporte, etapa e incidente crítico | Não implica automaticamente que OPEN crítico seja fechado |
| R12 MEDIUM | Erro filho reduzido a `DEVICE_RPC_FAILED`; processo morto perde contexto | Diagnóstico custa mais tempo e efeito fica incerto | `ui.py:_receive`, T10; OBSERVED | Erro estruturado e fase pré/pós-despacho | Preservar classe sanitizada, operação e correlação; novo canal após terminação | Processo remoto pode ter executado ação mesmo depois de terminar host |
| R13 MEDIUM | Contadores/aliases interpretados como publicações reais ou créditos | Orçamento e relatório enganosos | F10–F12 | Comparar contadores com contrato e job central | Métricas por escopo, incluindo publicação manual relatada | Upload nativo sem sinal observável não pode ser contado como comprovado |
| R14 MEDIUM | Perfil técnico aceita limites divergentes da documentação atual | Candidato aprovado localmente falha no app | F14/S09 | Testes de fronteira e versão da política | Revisar perfil mediante evidência aplicável | FAQ e app podem divergir por rollout/conta |
| R15 HIGH | Mídia escolhida só por posição, duração ou produto parecido | Publicação errada | T07, regras do operador | Hash + referência + preview + binding | Identidade estável; ambiguidade em REVIEW | UI pode não expor todos os IDs comerciais |

## Conclusões que estes riscos NÃO sustentam

- Não foi demonstrado que a Shopee detectou o robô ou puniu esta conta.
- Não foi demonstrada duplicação real pelo SDK; E01 usa efeito simulado.
- Não há prova de que o banco seja o principal gargalo.
- Não há base para resolver o UNKNOWN atual apagando registros, reduzindo gates ou criando outro job equivalente.
- Não há justificativa para proxy rotativo, troca de identidade, falsificação de fingerprint, CAPTCHA bypass ou “humanização” destinada a evitar detecção.
