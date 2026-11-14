# Research-First Capability Development

Este documento define o padrão global e obrigatório para desenvolver capabilities importantes no **AI Commerce Content Factory**.

Pesquisa não é uma etapa decorativa nem uma justificativa escrita depois da solução. Ela deve alterar concretamente o design, os contratos, os testes e as decisões do projeto. Quando a evidência disponível não for suficiente, a incerteza deve permanecer explícita e ser tratada por experimento controlado, não por suposição.

## 1. Processo obrigatório

```text
RESEARCH
  -> FINDINGS
  -> CAPABILITY DESIGN
  -> CONTRACT
  -> IMPLEMENTATION
  -> TEST / BENCHMARK
  -> PRODUCTION
  -> LEARNINGS
```

Nenhuma capability importante pode receber design profundo ou implementação de produção antes de a pesquisa específica responder ao gate `DESIGN_RESEARCHED` definido neste documento.

Cada transição deve deixar evidência rastreável:

- `RESEARCH -> FINDINGS`: fontes registradas, autoridade avaliada e evidências classificadas;
- `FINDINGS -> CAPABILITY DESIGN`: descobertas convertidas em responsabilidades, limites e regras acionáveis;
- `CAPABILITY DESIGN -> CONTRACT`: inputs, outputs, invariantes, falhas e comportamento provider-specific explícitos;
- `CONTRACT -> IMPLEMENTATION`: critérios verificáveis definidos antes do código de produção;
- `IMPLEMENTATION -> TEST / BENCHMARK`: implementação confrontada com testes ou benchmarks adequados;
- `TEST / BENCHMARK -> PRODUCTION`: quality gates satisfeitos e incertezas residuais declaradas;
- `PRODUCTION -> LEARNINGS`: falhas e resultados reais retornam ao conhecimento da capability.

Um protótipo criado para descobrir comportamento deve permanecer classificado como `EXPERIMENTAL`. Ele não satisfaz o gate e não pode ser apresentado como implementação pronta para produção.

## 2. Escopo global

Este padrão cobre, no mínimo:

- Product Discovery;
- Product Facts;
- Trend Research;
- Reference Analysis;
- Creative Direction;
- Script Writing;
- Storyboard;
- Scene Direction;
- Cinematography;
- Lighting;
- Physical Interaction;
- Generation Prompt Engineering;
- Visual Generation;
- Voice Generation;
- Video Editing;
- Caption/Subtitles;
- Technical QA;
- Visual QA;
- Packaging;
- Stock Management;
- Special Requests.

Ele também se aplica automaticamente a qualquer nova capability importante. Dividir uma capability, renomeá-la ou trocar seu provider não elimina a obrigação de pesquisa.

## 3. Hierarquia de fontes

As fontes não possuem a mesma autoridade. A prioridade padrão é:

| Prioridade | Fonte | Uso esperado |
|---|---|---|
| 1 | Documentação oficial | Contratos, recursos, limites e comportamento declarado. |
| 2 | Especificações técnicas e pesquisa confiável | Princípios, mecanismos e evidência técnica reproduzível. |
| 3 | Documentação das ferramentas | Operação e restrições da implementação ou provider atual. |
| 4 | Profissionais especializados e estudos de caso | Práticas aplicadas, contexto e resultados documentados. |
| 5 | Análise de exemplos reais do nicho | Padrões observáveis no domínio e na linguagem do conteúdo. |
| 6 | Comunidades e discussões práticas | Sinais, problemas recorrentes e hipóteses que exigem validação. |
| 7 | Testes próprios | Evidência empírica interna para o contexto específico do projeto. |

Prioridade não significa suficiência automática. Uma fonte oficial pode documentar um recurso sem provar sua eficácia criativa; um teste próprio pode ser decisivo para o projeto sem virar verdade universal. Conflitos entre fontes devem ser registrados, não escondidos.

## 4. Classificação de evidência

Toda descoberta relevante deve receber uma destas classificações:

| Classe | Significado |
|---|---|
| `DOCUMENTED` | Declarada por fonte autoritativa ou sustentada diretamente por especificação/pesquisa confiável. |
| `OBSERVED` | Verificada em exemplo, execução ou comportamento real, sem afirmar causalidade não demonstrada. |
| `INFERRED` | Conclusão racional derivada de evidências, ainda não confirmada diretamente. |
| `EXPERIMENTAL` | Resultado de teste próprio controlado, com método, contexto e limitações registrados. |
| `UNKNOWN` | Informação ausente, conflitante ou insuficiente para uma conclusão responsável. |

Uma evidência pode mudar de classificação quando surgirem dados melhores. `INFERRED` nunca deve ser apresentado como `DOCUMENTED`, e `UNKNOWN` nunca deve ser preenchido por invenção.

## 5. Estrutura canônica de pesquisa

Quando uma capability entrar realmente em pesquisa, criar:

```text
brain/research/<capability>/
  SOURCES.md
  FINDINGS.md
  BEST_PRACTICES.md
  FAILURE_MODES.md
  DESIGN_DECISIONS.md
```

Não criar diretórios ou arquivos vazios antecipadamente. A estrutura nasce somente quando a pesquisa profunda daquela capability começa.

O nome `<capability>` deve ser estável, legível e independente do provider. Materiais específicos de provider ficam dentro da pesquisa da capability correspondente e devem ser marcados como provider-specific.

## 6. SOURCES.md

Cada fonte deve registrar:

- fonte ou título;
- autor ou organização, quando disponível;
- URL ou referência recuperável;
- data de acesso;
- tipo da fonte;
- nível e justificativa de autoridade;
- descoberta relevante;
- classificação da evidência;
- decisão do projeto que a fonte influencia.

Não copiar páginas inteiras. Registrar somente o necessário para rastrear a evidência e entender sua influência.

## 7. FINDINGS.md

Consolidar o conhecimento nas seções:

```text
WHAT WE KNOW
WHAT SEEMS TO WORK
WHAT IS UNCERTAIN
WHAT NEEDS TESTING
```

Cada finding deve apontar para as fontes ou experimentos que o sustentam e preservar sua classificação de evidência. Divergências relevantes permanecem explícitas.

## 8. BEST_PRACTICES.md

Conter apenas regras acionáveis. Cada regra deve registrar:

- `RULE`;
- `SCOPE`;
- `EVIDENCE`;
- `RATIONALE`;
- `EXCEPTIONS_OR_LIMITS`;
- `VALIDATION` associada.

Conselhos vagos, como “faça vídeos atraentes”, não são best practices. Uma regra válida descreve comportamento verificável, por exemplo: manter o produto visível durante a ação principal quando isso não prejudicar a compreensão da função.

## 9. FAILURE_MODES.md

Cada falha conhecida ou risco relevante deve usar o padrão:

```text
CAPABILITY:
FAILURE:
TRIGGER:
IMPACT:
EVIDENCE:
DETECTION:
MITIGATION:
RESIDUAL_RISK:
```

O registro deve distinguir causa observada de causa inferida. Uma mitigação proposta continua incerta até ser documentada ou testada.

## 10. DESIGN_DECISIONS.md

Toda decisão importante da pesquisa da capability deve responder:

```text
WHAT DID WE DECIDE?
WHY?
EVIDENCE?
ALTERNATIVES CONSIDERED?
NEEDS FUTURE VALIDATION?
```

Decisões locais da pesquisa não substituem `brain/DECISIONS.md`. Quando uma conclusão mudar a arquitetura global, ela também deve ser promovida para o registro global de decisões.

## 11. Estabilidade e atualização

Cada pesquisa deve declarar uma classe de estabilidade:

| Classe | Interpretação |
|---|---|
| `STABLE` | Princípios duráveis; atualização orientada por nova evidência relevante. |
| `SEMI_STABLE` | Comportamento técnico que pode mudar entre versões ou ao longo do tempo. |
| `FAST_CHANGING` | Recursos de providers, tendências, políticas ou práticas que envelhecem rapidamente. |

Exemplos de classificação inicial, a confirmar na pesquisa correspondente:

- princípios de cinematografia: `STABLE`;
- comportamento central do FFmpeg: `SEMI_STABLE`;
- capabilities do Google Flow: `FAST_CHANGING`;
- tendências de TikTok e Reels: `FAST_CHANGING`.

Toda pesquisa `FAST_CHANGING` deve registrar `RESEARCH_DATE` e critérios ou gatilhos para refresh. A classificação de estabilidade não substitui a data de acesso de cada fonte.

## 12. Pesquisa e experimentação

Quando documentação e literatura não forem suficientes, registrar antes do teste:

```text
HYPOTHESIS:
EVIDENCE_GAP:
TEST:
CONTROL_OR_BASELINE:
SUCCESS_CRITERIA:
RESULT:
DECISION:
LIMITATIONS:
```

`RESULT` e `DECISION` permanecem pendentes até a execução. Não completar resultados imaginados nem converter hipótese em regra antes da evidência.

Este documento cria o padrão; nenhum experimento é executado nesta etapa.

## 13. Project Learnings

O conhecimento produzido por jobs reais deve usar o conceito `PROJECT_LEARNING`:

```text
PROJECT_LEARNING:
JOB:
CAPABILITY:
OBSERVED_FAILURE_OR_RESULT:
ROOT_CAUSE:
EVIDENCE_CLASSIFICATION:
GENERALIZED_RULE:
AFFECTED_ARTIFACTS:
FOLLOW_UP_VALIDATION:
```

Se a causa ainda não estiver demonstrada, `ROOT_CAUSE` deve ser marcada como `INFERRED` ou `UNKNOWN`. Um aprendizado validado pode alimentar:

- `BEST_PRACTICES.md`;
- `FAILURE_MODES.md`;
- `DESIGN_DECISIONS.md`;
- testes e benchmarks da capability.

Um incidente isolado não se transforma automaticamente em regra geral. A generalização deve indicar escopo e necessidade de validação.

## 14. Gate de expertise

Uma capability só pode receber a maturidade `DESIGN_RESEARCHED` quando houver evidência suficiente para responder, de forma rastreável:

1. What is this capability responsible for?
2. What inputs does it need?
3. What outputs must it produce?
4. What are accepted best practices?
5. What are common failure modes?
6. What is provider-specific?
7. What remains uncertain?
8. How will we test it?

O gate deve apontar para os arquivos da pesquisa que sustentam cada resposta. Criar documentação, sozinho, não satisfaz o gate.

`DESIGN_RESEARCHED` mede maturidade de conhecimento e design. `READY` mede implementação reutilizável, validação e evidência de execução. Uma capability pode ser `DESIGN_RESEARCHED` sem estar implementada, e nenhuma capability se torna `READY` por ter passado apenas pela pesquisa.

## 15. Primeira pesquisa profunda concluída

A primeira capability a passar por este processo foi **Visual Production / Scene Direction**, com pesquisa concluída em 23/09/2026, cobrindo:

- cinematography;
- lighting;
- physical interaction;
- temporal direction;
- continuity;
- AI video realism;
- Google Flow prompting como conhecimento provider-specific.

O gate `DESIGN_RESEARCHED` foi aprovado com evidência em `brain/research/visual-production/`. Os experimentos provider-specific permanecem pendentes e nenhum schema, pipeline ou integração de runtime foi implementado por essa pesquisa.


## Direção visual de conteúdo — Pinterest (27/09/2026)

Por instrução explícita do usuário, a operação assistida separa pesquisa de tendências da pesquisa fotográfica. Após estratégia/copy e antes de scene direction/provider, são obrigatórias análise dos exemplos prioritários do usuário, pesquisa/seleção visual Pinterest, inspeção dos pixels, metadados e mapa referência/asset. Cada capa, CTA fotográfico e Story de manhã/tarde/noite precisa de seleção. Cenas internas podem reutilizar referência compatível, sem repetir composição.

Norma detalhada: `docs/visual-reference-workflow.md`. Biblioteca: `references/library.json`; DNA: `references/style_dna.json`. Isso formaliza processo manual; não implementa scheduler, novo gerador ou validador automático. Identidade, produto e cena continuam com autoridades distintas. Não promover status de capability pela documentação.
