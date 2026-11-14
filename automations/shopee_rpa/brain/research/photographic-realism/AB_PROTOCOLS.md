# Testes A/B: aprender sem mudar dez variáveis

**Estado:** PROPOSED / NOT_EXECUTED para novos testes generativos. Esta pesquisa fez análise de comparações publicadas; não rodou um benchmark próprio nem concluiu melhoria percentual do gerador.

## Comparações já observadas

- R07 / [Cambridge in Colour](https://www.cambridgeincolour.com/tutorials/depth-of-field.htm): par de abertura f/8 versus f/2.8; primeiro plano legível e diferença de blur nos planos posteriores. Sustenta mecanismo óptico; não mede percepção de “foto vs IA”. Exposição/processamento não foram auditados em RAW.
- R05 / [Profoto](https://www.fimeko.fi/pdf/Creating_long_and_even_highlights_with_softboxes.pdf): progressão de fontes cria/refina highlights; múltiplas mudanças de luz ao longo da sequência. Não é A/B de variável única nem comparação entre “perfeito” e “real”.
- R06 / [Hasinoff et al.](https://people.csail.mit.edu/hasinoff/pubs/HasinoffEtAl16-hdrplus-preprint.pdf): resultados de processamento da captura real; evidenciam mudança de ruído/detalhe, com limitações documentadas. Não concluir que adicionar grain ou retirar HDR torna geração mais real.

## Método para futuros testes

1. Congelar fotografia/cena, canônicas, produto, formato, pose e provider/versão. Arquivar prompt, request, hashes, opções e ordem.
2. Definir **uma variável de direção** e seu efeito esperado antes de gerar. Se a alteração força mudança física em outra variável, registrar dependência em vez de afirmar controle perfeito.
3. Usar edição localizada ou seed pareada quando disponível. Se o provider não oferece seed/máscara/determinismo, repetir pares independentes e registrar essa limitação; mesmo prompt não mantém pixels/cena iguais.
4. Planejamento inicial: 3–5 pares, não garantia estatística. Mais observadores/pares podem ser necessários. Não aumentar custo sem objetivo e autorização de geração pertinente.
5. Randomizar A/B e ocultar rótulos para avaliação. Perguntar separadamente “captura plausível?” e “mais bonita?”. Aceitar empate. A/B é comparação de resultados, não reconhecimento da origem real.
6. Aplicar REALISM CHECK e identidade/produto antes da preferência. Imagem mais bonita com produto ou corpo errado não ganha.
7. Relatar defeitos observados, preferências e variação entre pares; não transformar unanimidade pequena em verdade universal. Só incorporar regra de prompt ao escopo/versionamento realmente testado.

## Protocolos pré-registrados

| Teste | HYPOTHESIS / EVIDENCE_GAP | TEST e CONTROL_OR_BASELINE | SUCCESS_CRITERIA / LIMITATIONS | RESULT / DECISION |
|---|---|---|---|---|
| AB01 Luz e ambiente | Direção causal explícita reduz iluminação sem origem; falta teste do provider | A: pedido genérico de luz natural. B: mesma cena com janela/dominante/fill especificados; variável = explicitação do campo de luz | Menos contradições e preferência de plausibilidade, preservando sujeito. Texto adicional tem várias relações: é teste de pacote de instruções, não fator físico único. | NOT_EXECUTED / PENDING |
| AB02 Pele por escala | Texture localizada evita poros gravados; prompt pode alterar rosto | A: poros visíveis uniformes. B: detalhe apenas na escala resolvida; variável = política de textura | Mesma identidade/luz, menos textura artificial em área distante; interpretação é qualitativa. | NOT_EXECUTED / PENDING |
| AB03 Distância de selfie | Distância alcançável menos curta reduz ampliação extrema | A: câmera muito próxima. B: distância proposta maior, mesma classe de lente; variável = distância | Cabeça/arm coerentes; enquadramento naturalmente muda, portanto não alegar comparação de composição idêntica. | NOT_EXECUTED / PENDING |
| AB04 Contato | Descrição de apoio melhora integração sem halo | A: referência sem instrução de apoio. B: somente apoio/oclusão no objeto identificado | Base deixa de flutuar sem sombra negra ampla; geom/luz congeladas quando edição permite. | NOT_EXECUTED / PENDING |
| AB05 Blur | Planos de profundidade reduzem recorte artificial | A: “fundo desfocado”. B: foco e transição por distância; variável = descrição de foco | Transição em cabelo/props coerente, não apenas fundo mais borrado; resultado pode variar por provider. | NOT_EXECUTED / PENDING |
| AB06 Ruído | Ruído arbitrário não garante fotografia | A: sem grain adicional. B: só grain solicitado, mesmo resto | Verificar se melhora plausibilidade ou apenas degrada nitidez; não selecionar B automaticamente. | NOT_EXECUTED / PENDING |
| AB07 Material | Acabamento específico melhora diferenciação | A: “headset realista”. B: mesma peça com plástico fosco/metal conforme oficial; variável = spec material | Shape/logo/escala preservados e reflexão coerente; não inventar material diferente do anúncio. | NOT_EXECUTED / PENDING |
| AB08 Cor | Remover grade padrão aproxima intenção doméstica | A: grade dourado. B: somente WB/curva domésticos; variável = tratamento de cor | Pele/ambiente mais coerentes, sem trocar paleta gráfica; não prova cor histórica exata sem calibração. | NOT_EXECUTED / PENDING |

## Registro de execução futura

```text
HYPOTHESIS:
EVIDENCE_GAP:
TEST / VARIABLE:
CONTROL_OR_BASELINE:
FROZEN_INPUTS / REFERENCE_HASHES:
PROVIDER_VERSION / OPTIONS / SEED_AVAILABLE:
SUCCESS_CRITERIA:
OUTPUT_FILES / SHA256:
BLIND_REVIEW / CHECK_RESULTS / TIES:
RESULT:
DECISION:
LIMITATIONS / CONFOUNDS:
```

Não usar o resultado de uma alteração de luz como evidência de que todas as regras de pele/câmera funcionaram. Não rodar correções ilimitadas para favorecer B. Registrar falhas descartadas de ambos os lados, evitando cherry-picking.
