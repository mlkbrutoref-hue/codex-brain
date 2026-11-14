# Decisões da pesquisa e propostas de evolução

08/10/2026. Nenhuma alteração de arquitetura global foi adotada nesta rodada. O Brain global de decisões não é substituído por este documento. D-023 e decisões posteriores do projeto continuam com seus respectivos escopos; esta pesquisa não amplia autorização de operação.

## RD01 — Entregar diagnóstico reproduzível antes de mudar o runtime

WHAT DID WE DECIDE? Nesta pesquisa, limitar execução a leitura de artefatos e três replays offline, preservando operação e incidente vigentes.
WHY? O operador já publicou o candidato; repetir sua preparação seria inadequado e não isolaria a causa da demora.
EVIDENCE? L06, E01–E03.
ALTERNATIVES CONSIDERED? Refazer fluxo real, limpar UNKNOWN ou criar job substituto: descartados.
NEEDS FUTURE VALIDATION? Reconciliar o post existente exige evidência própria; não é resolvido pelo diagnóstico.

## P01 — Reaproveitar o controlador e limitar IA a tarefas que exigem interpretação

WHAT DID WE DECIDE? PROPOSTA: manter Python, worker persistente, uiautomator2 e infraestrutura de segurança; transformar o percurso normal em transições determinísticas observáveis.
WHY? Os defeitos identificados são contratos incompletos e falhas de observação/recuperação; trocar a biblioteca não os elimina.
EVIDENCE? F02–F10, T03–T06.
ALTERNATIVES CONSIDERED? Appium: útil se houver necessidade de ecossistema/cross-platform, mas adiciona componentes e exige benchmark. Coordenadas fixas: frágeis. Agente visual decidindo cada toque: útil para exploração, caro e variável como rotina. scrcpy: auxílio ao operador.
NEEDS FUTURE VALIDATION? Benchmark de fluxo, compatibilidade por versão e auditoria de transporte. Não afirmar que o uiautomator2 instalado já satisfaz o contrato de despacho único.

## P02 — Preparação local como produto útil imediato

WHAT DID WE DECIDE? PROPOSTA: produzir pacote revisável de mídia/copy/produto/evidências e handoff humano; manter automação de interação condicionada à permissão aplicável.
WHY? A preparação pode poupar trabalho sem depender de navegação robótica no aplicativo; conformidade não decorre da robustez do software.
EVIDENCE? F01, S01–S11.
ALTERNATIVES CONSIDERED? Escalar frequência com limites arbitrários, “parecer humano”, usar endpoints privados: não recomendados. API oficial documentada e concedida à conta: preferível se disponível para a função específica.
NEEDS FUTURE VALIDATION? Licença dos materiais, experiência do handoff, endpoint e escopo de autorização. Não presumir que vídeos de anúncios sejam materiais licenciados do programa.

## P03 — Modelar risco por efeito e fase

WHAT DID WE DECIDE? PROPOSTA: separar estado de UI, situação da publicação e incidentes, mantendo correlação ao mesmo job e eventos imutáveis.
WHY? Um único rótulo UNKNOWN é conservador, mas não explica se a dúvida é o produto no editor, transferência interna ou publicação final.
EVIDENCE? F08/F11/F15.
ALTERNATIVES CONSIDERED? Liberar todas as leituras e mutações sob OPEN: excessivo. Tratar toda falha como publicação possível sem discriminação: seguro em alguns casos, mas causa bloqueios indevidos em outros. Remover breaker: descartado.
NEEDS FUTURE VALIDATION? Invariantes de resolução por escopo, evidências de ausência de despacho e preservação de outros incidentes. Nenhum UNKNOWN atual é reclassificado automaticamente por esta proposta.

Contrato conceitual a avaliar, sem migração nesta rodada:

```text
ui_stage: MEDIA_SELECTED | PREVIEW | EDITOR | PRODUCT_SHEET | FINAL_EDITOR
effect_phase: NOT_DISPATCHED | DISPATCHED | ACKNOWLEDGED | OBSERVED
effect_scope: PREPARATION | POSSIBLE_UPLOAD | FINAL_PUBLICATION
incident_status: OPEN | RESOLVED_WITH_EVIDENCE
publication_status: NOT_ATTEMPTED | ATTEMPTED_UNKNOWN | CONFIRMED | LEGACY_CONFIRMED
```

São dimensões propostas, não nomes já aceitos pelo ledger. `ACKNOWLEDGED` significa resposta técnica, não prova de publicação; `NOT_ATTEMPTED` final não prova zero transferência de dados.

## P04 — Não prometer exactly-once remoto

WHAT DID WE DECIDE? PROPOSTA: intenção durável antes do despacho, nenhum replay automático de mutação incerta, observação posterior e reconciliação explícita.
WHY? Dedup local e reserva de tentativa não controlam todos os efeitos do transporte e do aplicativo.
EVIDENCE? E01, T08, F07.
ALTERNATIVES CONSIDERED? Repetir ao não receber resposta: rejeitado. Marcar publicado por toast/retorno ao perfil: evidência insuficiente para vincular asset/produto/post.
NEEDS FUTURE VALIDATION? Falhas antes/durante/depois do despacho e recuperação após queda; protocolo de publicação manual. Garantia remota única exige suporte contratual do serviço, não apenas cliente.

## P05 — Não fazer otimização invisível

WHAT DID WE DECIDE? PROPOSTA: apresentar progresso por etapa e uma única pergunta de REVIEW quando necessária; medir tempo desde iniciar até entregar resultado.
WHY? O usuário não deve esperar sem saber se o sistema está trabalhando, bloqueado ou repetindo diagnóstico.
EVIDENCE? F10 e relato do operador.
ALTERNATIVES CONSIDERED? Repetir checks amplos sem mudança de evidência ou perguntar novamente fatos já confirmados: não recomendado. Remover checks para parecer rápido: não recomendado.
NEEDS FUTURE VALIDATION? Benchmarks comparáveis e teste de compreensão do operador; custos de IA medidos separadamente.
