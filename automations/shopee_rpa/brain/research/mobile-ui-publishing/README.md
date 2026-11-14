# Pesquisa: operação Android e publicação Shopee Video

Data: 08/10/2026. Escopo: código existente, incidentes preservados, documentação primária e experimentos offline. Estabilidade: FAST_CHANGING para Shopee/UI; SEMI_STABLE para SDKs; STABLE para princípios de rastreabilidade e tratamento de efeitos incertos.

RESEARCH_DATE: 2026-10-08. Refresh obrigatório antes de propor novo piloto real, após alteração relevante dos termos, da versão Shopee, do SDK Android ou do protocolo de transporte, e quando nova evidência contradizer um finding. Números e recursos do aplicativo não devem ser tratados como permanentes.

Status: **pesquisa consolidada; capability EXPERIMENTAL / PARTIAL; produção PAUSED**. Esta pesquisa não certifica `DESIGN_RESEARCHED`, autorização de plataforma, prontidão de produção nem publicação. Não houve conexão ao Android, alteração do publicador, nova tentativa, mudança do breaker ou reexecução do vídeo nesta rodada.

## Conclusão

O projeto tem componentes úteis e pode economizar trabalho, mas ainda não é um publicador autônomo confiável. A demora observada combina falhas reais de reconhecimento de tela, muitas leituras, tratamento excessivamente abrangente de incidentes e operação assistida por intervenções do agente. Não é explicada simplesmente pela velocidade do celular.

Há também uma restrição anterior à otimização: o item 4.1(g) dos [termos do Shopee Vídeo](https://help.shopee.com.br/portal/4/article/150523) proíbe scripts automatizados para coletar informações ou interagir com o serviço. Tratar a conta como sua, usar aparelho físico ou parar antes do botão final não demonstra uma exceção. **Classificação recomendada do risco atual: HIGH**, avaliação qualitativa de conformidade e operação, sem estimar probabilidade de banimento.

O caminho recomendado agora é aproveitar preparação, conteúdo, QA, identidade de mídia, produto e ledger, com publicação humana e registro do post resultante. O controlador Android pode continuar sendo desenvolvido e testado offline; uma operação real automatizada precisa de autorização aplicável da plataforma ou de uma integração oficialmente permitida. Não foi confirmada nesta pesquisa uma API pública de publicação em Shopee Video disponível para esta conta.

## Como a automação existente funciona

```text
configuração/candidato + gates + ledger
                 ↓
Python: controlador de estados e evidências
                 ↓
processo isolado persistente: uiautomator2
                 ↓
transporte ADB + servidor de automação no Android
                 ↓
árvore de acessibilidade / seletores / toque nativo
                 ↓
Shopee: processamento próprio e comunicação com seus servidores
```

ADB é o canal de controle do dispositivo; `uiautomator2` expõe operações como ler elementos e clicar. O XML descreve a interface acessível, não toda a lógica interna da Shopee. Um RPC é uma chamada entre esses componentes, como “localize e clique neste elemento”. Um timeout significa que a resposta não chegou no prazo; não prova que o toque deixou de acontecer. [ADB](https://developer.android.com/tools/adb), [uiautomator2](https://github.com/openatx/uiautomator2).

O vídeo já estar na galeria elimina a necessidade de copiá-lo novamente para o celular. Não elimina o processamento do aplicativo nem permite concluir em qual momento ele transmite dados aos servidores. Galeria, rascunho, envio e publicação são evidências distintas.

A conexão já é persistente durante o fluxo normal. Portanto, “manter uma conexão” é algo a preservar, não uma otimização ainda inexistente. O custo adicional aparece nas verificações repetidas, nas transições não reconhecidas e nas retomadas de diagnóstico.

## Por que demorou

| Achado | Evidência e limite | Consequência |
|---|---|---|
| 146 leituras em 155 ações registradas | Recorte histórico `latency-analysis.json`; aproximadamente 94,2% das ações | Há espaço para diminuir chamadas redundantes, preservando a leitura imediatamente anterior à ação |
| 53,2 s somados em latências registradas de RPC | Não inclui todo o tempo de preparação, políticas, interação com agente ou usuário | Não explica nem mede o tempo total que o usuário esperou |
| Folha “Feito” contém o título duas vezes | Replay de XML real: predicado antigo falha; atual passa | O aplicativo avançou, mas a validação antiga não reconheceu corretamente a tela |
| Evidência de produto sensível à geometria | Replay sintético comprova fragilidade; causa exata do incidente real continua inferida | Preencher legenda pode alterar o layout sem alterar o produto; identidade deve ser semântica |
| Uma falha em mutação de preparação pode abrir incidente global | Código de `_execute` | Retomadas passam a exigir reconciliação mesmo quando o botão final não foi acionado |
| SDK repete chamada após determinada falha de transporte | Versão instalada 3.7.0; experimento E01 | Contar uma chamada no Python não assegura um único efeito no Android |

Não há medição suficiente para atribuir uma porcentagem da demora ao modelo, ao ADB, ao SQLite ou ao telefone. Também não há extrato de consumo de créditos nesta pesquisa. Os `token_cost` do orçamento operacional são unidades internas de ações; não representam cobrança de tokens do modelo.

O vídeo manual já analisado mostra adição de produto em aproximadamente 8,6 s e 5,4 s em dois trechos. É referência de fluidez, não benchmark equivalente do mousepad nem promessa de desempenho. Fonte: [diagnóstico da gravação](../../../docs/publishing/manual-flow-diagnosis-2026-10-07.md).

## O problema novo mais importante no transporte

O experimento E01 substitui o transporte por uma função simulada: registra um efeito, perde a resposta e lança timeout. A implementação instalada reinicia seu servidor e chama o método novamente. Resultado: **uma chamada externa e dois efeitos simulados**. Isso demonstra uma possibilidade concreta de repetição em uma camada abaixo do ledger. Não demonstra postagem duplicada real, nem afirma que isso aconteceu no teste do mousepad. [Código da versão 3.7.0](https://github.com/openatx/uiautomator2/blob/3.7.0/uiautomator2/core.py).

Para uma futura implementação, operações de leitura e operações com efeito precisam de contratos de repetição diferentes. Após despacho incerto de “Postar”, a saída é observar/reconciliar, nunca repetir por timeout. Um ledger local impede certas duplicações locais, mas não oferece a garantia de execução única que dependeria também do servidor remoto.

## O que manter

Preservar ledger, dedup do asset, leases, budgets, QA, PublishGate, reconciliação legada, isolamento do processo e guardas pré-ação. Preservar também a distinção:

- `ASSISTED_VALIDATED`: fluxo de interface comprovado até a tela final.
- `READY_FOR_PUBLISH`: todos os requisitos finais satisfeitos.

Nenhum desses nomes, isoladamente, comprova permissão da plataforma. Origem comprovada de um arquivo também não comprova licença de republicação. Direitos e IA do candidato atual continuam UNKNOWN; tamanho não observado continua UNKNOWN.

Não recomendo trocar todo o projeto por Appium ou por cliques em coordenadas. Appium é uma alternativa madura, mas não resolve sozinho os contratos de evidência, o estado do aplicativo ou a reconciliação. `scrcpy` pode ajudar a pessoa a acompanhar o aparelho; não substitui esses componentes.

## Funcionamento recomendado

### Etapa utilizável sem robô interagindo com a Shopee

Preparar um pacote único por candidato: mídia própria/licenciada, hash, fonte, produto exato, variante comprovada, texto aprovado, informações sobre IA e checklist. Validar tudo localmente antes de abrir o aplicativo. A pessoa faz a publicação e informa o post resultante. O sistema preserva a evidência do handoff e a reconciliação, sem assumir que um clique humano não aconteceu.

Isso reaproveita boa parte do projeto e reduz o trabalho repetitivo onde ele pode ser realmente determinístico. O uso de APIs oficiais para dados deve permanecer limitado aos recursos e permissões efetivamente concedidos. Download automatizado via Chrome é uma questão separada, com seus próprios termos; não foi implementado nesta pesquisa.

### Controlador Android futuro, condicionado à autorização aplicável

```text
preflight local → sessão única → conta comprovada
→ mídia exata → Próximo → preview → Próximo → editor
→ Minhas Curtidas → aguardar lista carregada
→ card exato já visível? usar; caso contrário, busca controlada
→ Adicionar → folha correta → Feito → editor com produto comprovado
→ legenda definitiva → validação final → ASSISTED_VALIDATED → parar
```

O caminho normal deve rodar como programa de estados, sem pedir ao modelo para decidir cada toque. A IA participa na preparação e em exceções que exigem interpretação; uma ambiguidade abre REVIEW com uma pergunta específica e evidências já organizadas. O controlador não escolhe outro item pela semelhança nem usa “o quinto vídeo” como identidade permanente.

As leituras podem ser compartilhadas dentro de uma observação coerente, com prazo de validade e invalidação após mudanças. Não se elimina validação de conta, seletor, produto ou botão final para melhorar números. Também não se introduzem sleeps artificiais ou comportamento destinado a parecer humano.

## Precauções que realmente importam

São eixos independentes: permissão do método, direitos do conteúdo, originalidade, correspondência comercial, qualidade e estabilidade operacional. Reduzir frequência pode reduzir carga e repetição acidental; não concede autorização. Não foi encontrado suporte oficial para declarar **20–30 vídeos/dia seguros**. Não há probabilidade pública confiável de detecção nem limiar garantido de punição.

A orientação oficial de duração consultada difere do perfil local de mídia: FAQ informa 3–60 s, enquanto a configuração local aceita 1–180 s. O mousepad de 39,04 s cabe em ambos; outros candidatos exigem revisão do perfil. Documentos e interface também divergem sobre cupons. Registrar versão/data/escopo antes de converter esses detalhes em regras universais. [FAQ oficial](https://help.shopee.com.br/portal/10/article/171162-Principais-d%C3%BAvidas-sobre-Shopee-Video).

## Estado do vídeo já publicado pelo operador

O registro vigente continua `UNKNOWN / MANUAL_PUBLICATION_REPORTED_PENDING_RECONCILIATION`, breaker OPEN e retry bloqueado. Isso preserva a declaração de publicação manual sem inventar URL ou verificação técnica. O próximo passo operacional desse job é reconciliar o post existente, quando sua identificação estiver disponível. Nenhum teste proposto aqui autoriza republicá-lo ou reutilizá-lo como nova tentativa.

## Entregáveis e próximos passos técnicos

1. [Fontes primárias e limites](SOURCES.md).
2. [Achados classificados](FINDINGS.md).
3. [Regras propostas e critérios de verificação](BEST_PRACTICES.md).
4. [Falhas e registro de riscos](FAILURE_MODES.md).
5. [Decisões de pesquisa e alternativas](DESIGN_DECISIONS.md).
6. [Experimentos e plano de benchmark](BENCHMARK_PLAN.md).
7. [Resultado executado dos replays offline](experiments/offline-replay-results.json).

A ordem proposta é: separar autorização do operador e da plataforma; tornar o transporte de mutações auditável; completar os contratos das telas; distinguir incidentes pelo efeito e escopo; medir o percurso inteiro; só então validar operação real permitida. Estas são recomendações de implementação, não alterações já executadas.
