# Experimentos executados e plano de validação

Data: 08/10/2026. Execução desta pesquisa: exclusivamente offline. Não houve conexão ao aparelho, criação de tentativa nem publicação. Não foi executada novamente a suíte completa do projeto; os resultados antigos continuam históricos.

## Ambiente e reprodução

- Python local: `C:\Python314\python.exe`.
- uiautomator2 instalado e fixado: 3.7.0; adbutils instalado: 2.12.0.
- Script: `brain/research/mobile-ui-publishing/experiments/offline_replay.py`.
- Resultado: `experiments/offline-replay-results.json`.
- SHA-256 do `uiautomator2/core.py` testado: `9be432219b652cc44b4c32750aa0525976b3fd212dcd0237447fbe087b1508cc`.
- A simulação substitui `_jsonrpc_call`, stop e start por funções locais. Nenhum device real é construído. Fixtures existentes são apenas lidas.

Comando a partir da raiz do repositório:

```powershell
& 'C:\Python314\python.exe' 'brain/research/mobile-ui-publishing/experiments/offline_replay.py'
```

Reproduzir regrava somente o JSON de resultado da pesquisa, não o ledger. Requer a mesma dependência instalada e os fixtures referenciados.

## E01 — Repetição abaixo do ledger

HYPOTHESIS: cliente instalado repete uma chamada mutante quando perde a resposta.
EVIDENCE_GAP: revisão superficial do dispatcher do projeto não determina se o SDK repete comandos.
TEST: chamar o método real `BasicUiautomatorServer.jsonrpc_call` com transporte simulado que aplica efeito fictício e lança HTTPTimeoutError na primeira resposta.
CONTROL_OR_BASELINE: contar chamadas externas e chamadas ao transporte separadamente; retorno normal ocorre na segunda chamada.
SUCCESS_CRITERIA: identificar número de despachos e recuperação de servidor sem tocar no Android.
RESULT: PASS_REPRODUCED; 1 chamada externa, 2 chamadas de transporte, 2 efeitos simulados, stop/start do servidor simulado.
DECISION: propor contrato de não repetição de mutações em todas as camadas.
LIMITATIONS: não prova que o incidente real passou por esse ramo, que houve duplicação real ou qual seria a latência. Não mede comportamento do serviço Shopee.

## E02 — Predicado da folha de produto

HYPOTHESIS: duplicação legítima do título derrota a condição antiga após Adicionar.
EVIDENCE_GAP: distinguir falha do toque de falha de reconhecimento da tela.
TEST: carregar `product-current.xml` e `add-result.xml`, localizar card exato e comparar predicados antigo/atual.
CONTROL_OR_BASELINE: mesma fixture para ambos os predicados.
SUCCESS_CRITERIA: card único correspondente, duas ocorrências de título na folha, antigo falso e atual verdadeiro.
RESULT: PASS_REPRODUCED; todos os critérios atendidos. SHA da folha no JSON do experimento.
DECISION: preservar correção atual e testar Feito como transição explícita.
LIMITATIONS: fixture representa uma versão/tela; não certifica todos os layouts nem substitui teste de produto incorreto.

## E03 — Binding semântico versus geometria

HYPOTHESIS: mover bounds de um nó sem alterar produto muda o hash bruto, mas não sua identidade semântica.
EVIDENCE_GAP: avaliar plausibilidade da falha após edição de legenda sem confundir hipótese com causa provada.
TEST: comparar dois nós sintéticos iguais em conteúdo e diferentes em geometria; depois alterar título.
CONTROL_OR_BASELINE: digest bruto e digest semântico atual sobre as mesmas entradas.
SUCCESS_CRITERIA: bruto muda com geometria; semântico não muda; título diferente muda o semântico.
RESULT: PASS_REPRODUCED; mudança de título rejeitada.
DECISION: conservar separação entre identidade e layout e exigir evidência mais completa de produto.
LIMITATIONS: root cause do incidente real permanece INFERRED_NOT_PROVEN. Não certifica resistência a produtos homônimos.

## Medição histórica reutilizada

O agregado existente L03 tem 155 ações nativas, 146 leituras e 53,2 s somados de latência registrada. Leitura corresponde a cerca de 94,2% da contagem, não da duração. O conjunto reúne operações de um alias histórico em retomadas; não é uma única execução limpa. Não foram calculados percentis a partir desse agregado, porque ele não contém amostras suficientes para isso.

## Plano offline antes de qualquer novo teste real

| Cenário | Critério de aceitação |
|---|---|
| Galeria muda de ordem; duas mídias têm mesma duração | Hash/referência/preview selecionam só a mídia comprovada; ambiguidade → REVIEW |
| Minhas Curtidas carrega lentamente | Nenhuma busca enquanto estado ainda é loading; card exato visível evita busca |
| Card errado, homônimo, preço em faixa, título truncado | Só correspondência respaldada é aceita; parser não seleciona aproximação |
| Add respondeu, modal não respondeu, modal com título duplicado | Reconciliar estado antes de repetir ação; Feito explícito |
| Perda de resposta após efeito de cada mutação | No máximo um despacho pelo transporte testado; UNKNOWN preservado quando necessário |
| Legenda muda layout | Mesmo produto mantém binding; produto diferente invalida |
| Troca de foreground ou conta entre checks | Mutação bloqueada imediatamente antes do despacho |
| rights UNKNOWN ou REJECTED | Nunca há autorização final; regra assistida atual permanece separada |
| Handoff humano seguido de publicação relatada | Nenhum retry, novo job equivalente ou novo clique final |
| Falha de preparação resolvida e outro incidente de conta aberto | Breaker não fecha ignorando incidente remanescente |
| Reconciliado legado | Retry permanente bloqueado, asset dedup preservado, lacunas históricas visíveis |
| Queda do host antes/depois do despacho | Estado durável distingue as fases; nenhum “sucesso” inventado |

O conjunto deve comparar versão atual e proposta com fixtures e falhas determinísticas; não acrescentar testes que apenas repetem o código sem distinguir comportamento.

## Piloto real somente com permissão e gates satisfeitos

Não definir quantidade de posts como “segura”. Começar por validação do fluxo autorizado sem publicação, com candidato independente e conteúdo de direitos comprovados; o mousepad atual está excluído como novo teste. Documentar conta, aparelho, versão do app, cenário e evidências. Um piloto de publicação, se autorizado separadamente, precisa de escopo próprio e prova de reconciliação final.

Métricas: tempo completo; tempo por etapa; XML/foreground/screenshots por transição; conexões/restarts; erros pré/pós-despacho; intervenções humanas; consumo de orçamento operacional; tokens/custo de IA medidos à parte. Separar carregamento/transcodificação/rede de trabalho do controlador.

Metas iniciais de engenharia, **a validar e não prometer**: uma conexão normal, zero decisões do modelo por toque no caminho já conhecido, zero repetição de mutação incerta e zero avanço com alvo ambíguo. Para mídia já preparada até editor final, explorar p50 ≤ 60 s e p95 ≤ 120 s do segmento automatizável; reportar também wall time total, sem esconder espera do aplicativo/rede/humano. Somente fixar SLA após baseline do mesmo percurso e amostra comparável.

STOP: conta/asset/produto divergente; CAPTCHA ou desafio de segurança; rate limit ou notificação de política; layout desconhecido; permissão expirada/ausente; transporte com efeito incerto; budget excedido; operador assume o controle; publicação potencial ainda não reconciliada. Parar significa preservar evidência e dar um motivo específico, sem contornar o desafio ou criar nova identidade.

## Critério de saída da pesquisa para implementação

A pesquisa identifica mecanismo e experimentos suficientes para mudanças locais de contrato, mas mantém gaps de autorização, prova pós-publicação e latência real. Não declarar `READY_FOR_PUBLISH`, produção pronta ou garantia antiban por existência deste relatório. Implementar por mudanças pequenas, com regressões proporcionais; promover decisões arquiteturais somente quando adotadas explicitamente.
