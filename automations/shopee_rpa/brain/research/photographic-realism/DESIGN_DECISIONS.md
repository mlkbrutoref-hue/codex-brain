# Decisões locais da pesquisa

Não há nova decisão arquitetural global; runtime e contratos não foram alterados.

| WHAT DID WE DECIDE? | WHY? | EVIDENCE? | ALTERNATIVES CONSIDERED? | NEEDS FUTURE VALIDATION? |
|---|---|---|---|---|
| Sistema assistido de especificação + revisão | Usuário pediu mecanismos reutilizáveis | Pedido, S01–S23 e atlas | Criar novo engine de código/gate automático | Sim, eficácia de prompts por provider; não implementar detector agora |
| Separar dado documentado, observado e estimado | Reconstrução não única e EXIF conflitante | R02 e RESEARCH_FIRST | Preencher setup exato pelo olhar | Manter classificação em cada novo job |
| Usar Pinterest para direção, fotos com proveniência para fundamentos | Pins não autenticam captura | P03/P04 e casos de fotógrafo/artigo | Tratar todo pin como real/viral | Melhorar proveniência futura; não bloquear pesquisa por pin indisponível |
| Imperfeições condicionais, nunca pacote obrigatório | Fotos reais podem ser limpas/retocadas/processadas | Atlas/S12/S15–S20 | Sempre grain, poros, flare e clipping | AB02/AB06 e avaliações do público |
| Preservar foto aprovada em edição gráfica | Usuário quer pose/formato originais | Contexto recente e invariantes | Gerar cena nova em cada overlay | QA final para fidelidade, sem promessa pixel-identical |
| Salvar template, módulo e pointer em AGENTS | Uso futuro solicitado explicitamente | Resultado prático do pedido | Só responder no chat | Conferir aplicação no próximo job; não alegar execução automática |
| A/B proposto, sem gerar novos assets nesta pesquisa | Pedido requer estudo e proposta; corpus já permite análise | Etapa 17 e comparações documentadas | Gastar gerações sem necessidade para completar relatório | Executar quando houver pedido de geração/teste concreto |
