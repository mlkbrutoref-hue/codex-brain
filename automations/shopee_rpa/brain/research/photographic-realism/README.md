# Sistema de fotografia plausível

Pesquisa solicitada pelo operador em 12/10/2026. Prioridade: **FOTOGRAFIA PLAUSÍVEL > IMAGEM BONITA**.

Esta entrega é pesquisa e procedimento de direção/revisão assistida. Não é um detector de autoria por IA, um renderer físico nem uma nova arquitetura do gerador. A eficácia dos prompts no provider ainda exige os testes propostos.

## Documentos

- [Relatório completo, nos 20 tópicos pedidos](REPORT.md).
- [Atlas: pixels, reconstruções e limites das referências](REFERENCE_ATLAS.md).
- [Taxonomia: reconhecimento, mecanismo, correção e instrução](AI_TELLS.md).
- [Template de especificação e exemplos preenchidos](PROMPT_TEMPLATE.md).
- [PHOTOREALISM ENGINE — módulo compacto](PHOTOREALISM_ENGINE.txt).
- [REALISM CHECK — revisão e plano de correção](REALISM_CHECK.md).
- [Testes A/B propostos e comparações já observadas](AB_PROTOCOLS.md).
- [Fontes e autoridade](SOURCES.md), [findings](FINDINGS.md), [regras](BEST_PRACTICES.md), [falhas](FAILURE_MODES.md), [decisões locais](DESIGN_DECISIONS.md).
- [Manifesto de fontes locais, EXIF e SHA-256](reference_manifest.json).

## Como usar na próxima criação

Ler a referência em pixels; separar identidade, produto, cena e design gráfico; preencher o template com observações e estimativas identificadas; gerar pelo provider autorizado; aplicar o REALISM CHECK ao arquivo final. Usar o módulo compacto apenas depois de resolver a direção específica da cena. Um texto genérico no fim do prompt não substitui essas etapas.

Para Nina, as duas imagens canônicas e as regras atuais de proporção continuam obrigatórias. O realismo não autoriza mudar seu corpo, idade, rosto ou sinais físicos, nem substituir o estilo visual do perfil. Em edição de texto sobre foto aprovada, preservar a fotografia; não reluminar ou refazer pose em nome do realismo. Textos e elementos de posts continuam executados pelo gerador de imagens, conforme instrução do operador.

## Evidência e cobertura

`DOCUMENTED`: fonte técnica ou configuração declarada. `OBSERVED`: leitura dos pixels. `INFERRED`: reconstrução compatível, não medição. `UNKNOWN`: ausente/conflitante. `EXPERIMENTAL`: reservado a experimentos próprios efetivamente executados; nenhum novo A/B generativo foi executado nesta pesquisa.

Corpus inspecionado: dois retratos de fotógrafos com proveniência/EXIF; sequência de produto Profoto; quatro situações fotografadas do estudo HDR+ (rosto, rua noturna, igreja e sala com piano); par fotográfico de abertura; fotografia de cabelo reproduzida em artigo; duas referências Pinterest já arquivadas e reinspecionadas. São **9 casos fotográficos com proveniência documentada + 2 exemplos Pinterest de autenticidade não verificada**, não 11 fotografias independentes: vários casos contêm comparações da mesma captura. O atlas explica cada caso. Não houve inspeção de RAW original; cópias publicadas podem ter retoque.

Novas buscas Pinterest foram feitas; dois candidatos não forneceram pixels recuperáveis. Não foram contados como analisados. Reutilizamos os dois exemplos efetivamente inspecionados da biblioteca, complementando com fontes de autoria/captura documentadas. Não extrapolar esta amostra para toda fotografia, todos os tons de pele, todas as roupas ou todos os providers.

Princípios físicos: `STABLE`. Eficácia de linguagem no provider: `FAST_CHANGING`, atualização quando houver troca de modelo, mudança de comportamento ou novo job que contradiga as regras. Data da pesquisa: 2026-10-12. Nenhuma promoção de capability para READY.
