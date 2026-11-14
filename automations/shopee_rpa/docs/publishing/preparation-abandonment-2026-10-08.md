# Validação assistida — 08/10/2026

## Resultado real

- Mesmo job central: `a87ba2d7f7f867c58a173b40d5d0755b42e3892ea69ab162cd44c890762c1212`.
- Vídeo 5 da galeria, mousepad preto de 39,04 segundos: selecionado e preview/editor alcançados.
- Minhas Curtidas: produto exato identificado, Adicionar e Feito executados; vínculo presente no editor.
- Legenda definitiva preenchida; oito checks de UI verdadeiros; Postar alcançado, nunca clicado.
- Nenhuma publicação ou autorização final; attempted=0. Direitos e IA UNKNOWN; tamanho não confirmado.
- ASSISTED_VALIDATED central: **NÃO**. `complete_assisted` falhou em PRODUCT_BINDING_REVIEW_INVALID.
- Ledger final: FAILED. Breaker final: OPEN pelo novo erro de binding, não pelo UNKNOWN antigo.
- READY_FOR_PUBLISH: NÃO. A tela final continua pronta para conferência humana; não repetir seleção/Add.

## Correções e reconciliação

1. Abandono explícito da preparação antiga, mantendo snapshot UNKNOWN, arquivos/eventos, dedup e upload nativo UNKNOWN. Mesmo job central, sem nova tentativa diária final. Liberação administrativa OPEN/HALF_OPEN/CLOSED com preflight.
2. Ordenação da grade corroborada por date_modified, sem resort silencioso por date_added.
3. Parser de card aceita preços em faixa mantendo título exato e botão vinculado ao card.
4. Folha Editar informações repete o título no card e no nome editável. A condição antiga exigia uma ocorrência e gerava timeout depois de Add SUCCESS. Corrigida e testada com duas ocorrências.
5. Efeito do Add reconciliado por evidência corrente da folha, log de sucesso, prova do card/candidato e hashes; incidente arquivado no ledger. Continuou em Feito sem repetir Add.
6. A comparação do produto vinculado incluía posição/foco do nó. Esses atributos transitórios foram retirados do digest de identidade; título, pacote, classe e resource-id continuam protegidos. Regressão de mudança de layout passa, mudança de título e alteração da prova continuam bloqueadas. Essa última correção ainda não foi revalidada no telefone: não foi forçada promoção de FAILED para ASSISTED_VALIDATED.

## Por que demorou

O tempo foi consumido por falsos bloqueios sucessivos do código e pela forma de conduzir a depuração. Ordenação, preço em faixa, duplicação normal do título e comparação de layout foram tratados como problemas de evidência. O timeout de uma etapa preparatória abriu o breaker e exigiu reconciliação antes de continuar. Também houve excesso de comandos de inspeção, inicializações Python/conexões após paradas e execução de testes durante a operação assistida. Várias verificações tinham custo de segundos por chamada. Não era demora do clique Feito em si.

A condução misturou desenvolvimento de recuperação com operação do telefone e aumentou o custo para o operador. Próximo trabalho deve começar pelos contratos observados dessas telas, usar replay de fixtures nativas e uma única sessão persistente, e retomar por estado sem repetir ações. O cálculo atual de identidade de produto foi corrigido offline. A espera da lista carregar antes de decidir pesquisar ainda precisa melhorar: nesta execução houve busca após reabrir Minhas Curtidas, embora o produto estivesse anteriormente visível. Não alegamos que essa otimização ficou concluída.

## Testes e integridade

- Rodada anterior desta sessão: 87 testes direcionados passaram; 12 de abandono passaram após correção do fixture.
- Execução ampla de 199 teve 198 passes e um erro de fixture; o caso foi corrigido e passou na rodada direcionada. Não é uma suíte final integral verde.
- Preço/card/seletor: 3/3 PASS; diagnóstico de timeout somente leitura: 1/1 PASS.
- Retomada de Add: 4/4 PASS, incluindo outro incidente, modal divergente e tentativa final bloqueados. Teste do fluxo com título duplicado passou.
- Digest após reflow e prova alterada: 2/2 PASS.
- SQLite integrity=ok; nenhuma violação FK; mesmos jobs centrais; autorizações e tentativa final inalteradas; publicação legada, eventos e fontes antigas intactos.

## Evidências

- `output/preparation_abandonment_20261008/live-feito-02/final-editor.png`
- `output/preparation_abandonment_20261008/live-feito-02/result.json`
- `output/preparation_abandonment_20261008/live-feito-02/reconciliation.json`
- `output/preparation_abandonment_20261008/final-integrity.json`
- `output/preparation_abandonment_20261008/latency-analysis.json`

Não foi usado Chrome, pesquisa de hashtags, nova licença, fingerprint legado inventado nem novo job equivalente. Capability EXPERIMENTAL / PARTIAL; produção PAUSED.

## Atualização posterior: publicação manual informada

O operador informou que publicou manualmente. O resultado acima descreve a execução automática antes dessa ação. Declaração preservada, job bloqueado para retry como UNKNOWN/MANUAL_PUBLICATION_REPORTED_PENDING_RECONCILIATION e breaker OPEN. Falta URL/ID do post para reconciliação; não repetir postagem. Nenhuma tentativa automática adicional foi registrada.

Refresh operacional: a etapa de preparar o vídeo terminou e foi seguida de publicação manual; a tarefa operacional agora é reconciliar o post existente. A revisão de desempenho usa os logs locais: no alias de execução 03 houve 155 ações nativas registradas, 146 delas leituras, somando 53,2 segundos de RPC. Esse valor não inclui análise do agente, testes offline, inicializações de processos, espera por revisão ou overhead de ferramentas e não representa o tempo total da tarefa. O excesso de inspeção e as recuperações sucessivas explicam parte relevante da demora, além dos falsos bloqueios já descritos.
