# Antigravity: Performance / Time Optimization v1

Pedido integral: `antigravity_performance_request.txt` neste diretório.

## Ownership e isolamento

Antigravity trabalha exclusivamente no worktree `output/worktrees/antigravity-performance`, branch `antigravity/performance-learning`, base `a4c7a00`. A árvore principal contém alterações anteriores NÃO commitadas: não copiá-las, descartá-las nem assumir que estão no HEAD. Brain e AGENTS foram copiados como contexto somente leitura.

Permitido criar/editar: `app/performance/**`, `tests/performance/**`, `docs/performance/**` nesse worktree. Proibido todo o restante, incluindo Brain, publishing, mobile, Instagram/TikTok automation, carousel, single_story, lifestyle_story, geração de conteúdo e arquivos compartilhados. Não publicar, acessar contas, gerar imagens, fazer merge nem commit automático.

Codex: `app/publishing/**`, `app/mobile/**`, `tests/publishing/**`, `docs/publishing/**`, handoff e atualização final do Brain, na árvore principal.

## Tarefa

Implementar Performance Tracker, persistência local de posts/snapshots, Learning Engine simples e Time Optimizer. Ler Brain na ordem README, MISSION, CHIA, CURRENT_STATE, DECISIONS. Respeitar padrão dataclass/to_dict/from_dict e unittest do projeto. Sem serviços externos, ML complexo ou coleta automática. Marcar protótipo EXPERIMENTAL; não alegar produção validada.

Publicação: post_id, platform, content_type, category, campaign_id, publish_datetime com timezone, day_of_week e publish_hour derivados no timezone declarado, theme, hook_type, cta_type, story_type, product_ids, publish_method, followers_at_publish. Snapshots +1h/+6h/+24h/+72h: views, reach, likes, comments, shares, saves, profile_visits, follows, link_clicks. Desconhecido é null, nunca zero fabricado. Validar valores, datas, duplicatas e plataforma; manter chaves compostas para evitar colisão de IDs.

Taxas com denominadores explícitos e desconhecidos preservados; documentar cobertura e limitações. Comparar somente métricas/horizontes/coortes compatíveis. v1 prioriza horário por platform + content_type + category + dia + janela; hooks/CTA/theme armazenados para evolução. Scoring transparente; tamanho amostral mínimo configurável; INSUFFICIENT_DATA, LOW_CONFIDENCE, MEDIUM_CONFIDENCE, HIGH_CONFIDENCE. Não inferir campeão de um post. Exploração 20%, exploitation 80%, configuráveis e reproduzíveis por seed/chave ou política determinística. Sem histórico: não fingir melhor horário nem estatística.

## Contrato esperado

API pública documentada e importável em `app.performance`: `record_publication(...)`, `record_metrics(...)`, `recommend_publish_time(...)`, ou métodos equivalentes de um serviço com storage injetável. Recomendação serializável: recommended_time (ISO timezone-aware ou null), confidence, reason, samples, alternatives; explicitar coorte, horizonte, score e exploração quando possível. Documentar assinaturas exatas e exemplo executável em `docs/performance/INTEGRATION.md`. Nenhuma dependência do Mobile Publisher. Nunca registrar rascunho como publicação real.

## Sucesso e entrega

Testes unittest em tests/performance para registro, snapshots, unknown/null, taxas/denominador zero, comparação de horários, sample size/confidence, exploração, recomendação, persistência/reabertura, ausência de dados, isolamento de plataformas e snapshots comparáveis. Rodar testes com resultado real. Documentar scoring, limitações e integração. Entregar lista de arquivos, comando/resultado de testes e riscos. Não editar arquivos fora do ownership; não fazer merge.

## Prompt exato de execução

Leia este handoff e o pedido integral indicado acima na árvore principal. Execute a tarefa completa SOMENTE no working_directory fornecido pelo bridge, dentro dos três diretórios permitidos. O usuário autorizou explicitamente a delegação deste projeto Shopee após validação do bridge; health_check confirmou healthy=true. Codex trabalha simultaneamente em Mobile Publisher e Phone Link. Implemente, teste e documente a infraestrutura de analytics/time optimization, sem aguardar o Codex e sem modificar os arquivos dele. Não faça merge nem commit automático. Retorne resultado honesto com as assinaturas públicas, arquivos alterados e testes executados.
