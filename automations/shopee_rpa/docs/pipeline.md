# Pipeline de Produção & Ciclo de Vida dos Jobs

> **OUTDATED:** este lifecycle é anterior à consolidação do Project Brain. O lifecycle oficial está em [`../brain/ARCHITECTURE.md`](../brain/ARCHITECTURE.md); este arquivo permanece apenas como referência histórica até revisão posterior.

Este documento define a cadeia ponta a ponta de processamento de um produto até a geração do pacote final multimídia de afiliados.

---

## 1. Fluxo Sequencial do Pipeline

```
┌──────────────────────────────────────────────────────────┐
│ 1. PRODUCT (Dados crus extraídos da Shopee Affiliate API) │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│ 2. PRODUCT FACTS (Extração e categorização de fatos)     │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│ 3. CREATIVE BRIEF (Definição de ângulo, formato e persona)│
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│ 4. HOOK (Geração e seleção de ganchos de alta retenção)  │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│ 5. SCRIPT (Roteiro falado no tom informal da Nina)       │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│ 6. STORYBOARD (Divisão cena a cena com enquadramento)    │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│ 7. VISUAL PROMPTS (Prompts positivos e negativos p/ Flow)│
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│ 8. GENERATED IMAGES (Geração visual âncora/frames)       │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│ 9. GENERATED TAKES (Takes de vídeo individuais)          │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│ 10. VALIDATION (Conformidade com persona, fatos e visual)│
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│ 11. VOICE (Síntese de voz com entonação natural pt-BR)   │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│ 12. SUBTITLES (Geração de legendas sincronizadas SRT/VTT)│
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│ 13. FFMPEG (Montagem, ritmo de corte, mixagem e render)  │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│ 14. MASTER VIDEO (Vídeo base consolidado 1080x1920)      │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│ 15. VARIANTES DE PLATAFORMA                              │
│     ├── SHOPEE VARIANT (Direto, foco no produto e CTA)   │
│     └── INSTAGRAM VARIANT (Hook agressivo, retenção)     │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│ 16. PACKAGE_READY (Pacote final com mídias e copys)      │
└──────────────────────────────────────────────────────────┘
```

---

## 2. Contrato de Estados do Job (Job States)

O ciclo de vida de qualquer execução (`job_id`) é rastreado rigorosamente por meio dos seguintes estados contratuais:

| Estado | Significado / Condição de Transição |
| :--- | :--- |
| `CREATED` | Job inicializado no sistema com ID único e parâmetros de entrada. |
| `PRODUCT_LOADED` | Carga de dados crus realizada da Shopee Affiliate API ou fixture local. |
| `FACTS_READY` | Fatos extraídos e classificados (`CONFIRMED_FACTS`, `INFERRED_CONTEXT`, `UNKNOWN`). |
| `BRIEF_READY` | Briefing criativo gerado (formato de conteúdo, ângulo e público-alvo definidos). |
| `HOOKS_READY` | Ganchos opcionais preparados antes do roteiro; o fluxo atual pode ir direto ao roteiro. |
| `SCRIPT_READY` | Roteiro redigido e validado com tom informal da Nina e sem falsas promessas. |
| `STORYBOARD_READY` | Cenas descritas com enquadramento, ação da Nina e integração com produto. |
| `PROMPTS_READY` | Prompts positivos/negativos compostos com injeção de persona e restrições. |
| `WAITING_FOR_GENERATION` | Operação Flow preparada, referências registradas e nenhuma geração iniciada. |
| `GENERATING_MEDIA` | Processamento de imagens e takes de vídeo em andamento (via Flow ou manual). |
| `MEDIA_READY` | Todos os takes e imagens de apoio foram baixados e salvos localmente. |
| `VISUAL_QA` | Gate que mantém QA técnico separado da análise visual semântica. Sem modelo/revisor visual, o resultado semântico é `NOT_EXECUTED`. |
| `EDITING` | Processamento no FFmpeg (junção de takes, áudio, legendas, transições e color grading). |
| `VALIDATING` | Validação automatizada pós-render (integridade de áudio, resolução, duração e persona). |
| `PACKAGE_READY` | Pacote 100% concluído, contendo master, variantes, copys e metadados. |
| `REVIEW_REQUIRED` | Transição acionada quando alguma validação falha suavemente ou requer inspeção humana. |
| `FAILED` | Erro irrecuperável durante a execução (registrado em logs com causa raiz). |

---

## 3. Política de Segurança de Fatos (Fact Safety)

Para proteger a credibilidade da criadora virtual e evitar problemas regulatórios ou penalizações de afiliados, as informações do produto são estritamente particionadas em três níveis:

### 3.1. `CONFIRMED_FACTS`
- Fatos confirmados diretamente no catálogo oficial do vendedor na API da Shopee (especificações técnicas, voltagem, material, dimensões, certificações oficiais, preço atual).
- **Regra:** **Apenas informações nesta categoria podem ser utilizadas em alegações comerciais objetivas** nos roteiros e legendas.

### 3.2. `INFERRED_CONTEXT`
- Contexto de uso do dia a dia derivado do bom senso (ex: "ideal para ter na bancada da pia", "ajuda a economizar tempo na rotina matinal").
- **Regra:** Pode orientar cenário e abordagem criativa, mas não pode ser apresentado como capacidade, benefício ou fato do produto.

### 3.3. `UNKNOWN`
- Qualquer característica ausente ou incerta nos metadados oficiais (ex: "é à prova d'água", "bateria dura 48 horas", "cura problemas de pele").
- **Regra Estrita:** **É TERMINANTEMENTE PROIBIDO AFIRMAR ATRIBUTOS UNKNOWN.** Se a ficha do produto não cita expressamente que é à prova d'água, o roteiro **jamais** dirá "é resistente à água".

---

## 4. Adaptação por Plataforma

Do arquivo `master.mp4` montado pelo FFmpeg, o pipeline deriva duas entregas customizadas:

### Shopee Video (`shopee.mp4` + `shopee.txt`)
- Foco em demonstração prática imediata do produto.
- Ritmo objetivo, sem rodeios.
- CTA focado no clique na sacola/carrinho laranja da Shopee.
- Legenda curta com termos chave de busca e IDs de produto.

### Instagram Reels (`instagram.mp4` + `instagram.txt`)
- Hook visual e auditivo de alta retenção nos primeiros 2 segundos.
- Narrativa lifestyle mais envolvente no tom social da Nina.
- CTA factual para conferir os detalhes no link efetivamente disponibilizado pela publicação.
- Entre 4 e 8 hashtags factuais e relacionadas ao anúncio, preferencialmente 6; nunca `#fyp`, `#fy` ou `#viral`.
