# Project Brain

Este diretório é a fonte principal de contexto, decisões e direção arquitetural do **AI Commerce Content Factory**.

Quando houver divergência entre os arquivos deste diretório e documentação anterior, o conteúdo de `brain/` prevalece. Código, testes e artefatos executados continuam sendo a evidência do comportamento real; o Brain não deve declarar uma capacidade como pronta sem essa evidência.

## Hierarquia de autoridade

Para decisões de produto e arquitetura, a ordem de autoridade é:

1. `brain/MISSION.md`
2. `brain/CHIA.md`
3. `brain/ARCHITECTURE.md`
4. `brain/DECISIONS.md`
5. `brain/CURRENT_STATE.md`
6. documentação histórica e especializada fora de `brain/`

Se houver conflito, prevalece o documento mais alto nessa hierarquia. Código, testes e artefatos continuam sendo a evidência do que está realmente implementado; uma inconsistência entre essa evidência e o Brain deve ser registrada e corrigida, não ocultada.

`brain/RESEARCH_FIRST.md` é a norma operacional canônica que detalha o princípio arquitetural registrado em `brain/ARCHITECTURE.md` e na decisão D-013. Ela permanece subordinada à hierarquia acima e não altera a autoridade relativa dos documentos.

## Navegação

- `MISSION.md`: missão estável e independente de ferramentas.
- `CHIA.md`: mapa de Contexto, Habilidades, Integrações e Automação.
- `RESEARCH_FIRST.md`: padrão global de pesquisa, evidência, experimentação e expertise para capabilities.
- `CURRENT_STATE.md`: fotografia honesta do estado atual.
- `DECISIONS.md`: decisões arquiteturais vigentes e seus motivos.
- `ARCHITECTURE.md`: arquitetura-alvo, lifecycle e limites dos componentes.
- `ROADMAP.md`: sequência controlada de evolução.
- `research/visual-production/`: primeira deep research concluída; evidências, regras, falhas, capability design e estudos de caso de produção visual.
- `research/visual-production/experiments/`: protocolos E-01..E-05, golden scenes, rubric, orçamento e armazenamento; framework pronto, ainda sem runs.

## Regras de governança

1. Toda produção deve possuir um único `job_id` e um estado verificável.
2. Conversas, abas de navegador e projetos externos não são fonte de verdade do job.
3. Uma capacidade só pode ser marcada como `READY` quando existir implementação reutilizável, validação e evidência de execução.
4. Ferramentas externas são substituíveis. A missão, os contratos e os artefatos do job não devem depender de uma marca específica.
5. Integrações manuais devem ser declaradas como `MANUAL`, mesmo quando um agente executa os cliques.
6. Falhas, pendências e consumo conhecido não devem ser escondidos.
7. O estado `PACKAGE_READY` exige pacote local verificável; sucesso apenas dentro de uma interface externa não é suficiente.
8. Toda capability importante segue `RESEARCH -> FINDINGS -> CAPABILITY DESIGN -> CONTRACT -> IMPLEMENTATION -> TEST / BENCHMARK -> PRODUCTION -> LEARNINGS`; documentação isolada não autoriza `DESIGN_RESEARCHED` nem `READY`.

## Classificação da documentação existente

| Documento | Classificação | Tratamento |
|---|---|---|
| `brain/*` | `CANONICAL` | Fonte principal a partir desta reorganização. |
| `docs/persona.md` | `CANONICAL` | Referência especializada da Nina, subordinada ao Brain. |
| `docs/content-formats.md` | `CANONICAL` | Catálogo especializado de formatos, subordinado ao Brain. |
| `README.md` | `OUTDATED` | Visão geral útil, mas superestima partes da automação atual. Deve ser alinhado em etapa posterior. |
| `docs/architecture.md` | `OUTDATED` | Fonte histórica para módulos existentes; arquitetura oficial passa a ser `brain/ARCHITECTURE.md`. |
| `docs/pipeline.md` | `OUTDATED` | Contém lifecycle anterior e etapas ainda não implementadas integralmente. |
| `docs/providers.md` | `OUTDATED` | Retrata um momento anterior e contém estados que divergem de outras evidências. |
| `docs/flow-integration.md` | `OUTDATED` | Afirma zero gerações e FFmpeg indisponível, em conflito com artefatos posteriores. |
| `docs/status.md` | `ARCHIVE_CANDIDATE` | Snapshot de 11/09/2026; não representa sozinho o estado atual. |
| `docs/handoff.md` | `ARCHIVE_CANDIDATE` | Relatório de uma execução específica, não especificação do sistema. |

Nenhum documento antigo é removido nesta etapa.
