# Parecer independente do Antigravity

Origem: resposta textual do CLI oficial agy, retomada da conversa a2f2534b-741c-4a7c-a74d-9cdeea45d74d. Salvamento realizado pelo Codex.

# Parecer de Auditoria Independente — RPA Shopee Video

**Data:** 06/10/2026  
**Escopo:** Avaliação independente de riscos, conformidade com políticas e inspeção estática do código local. Nenhuma ação em dispositivo, rede ou conta externa foi executada.

---

### 1. Avaliação dos Pontos Técnicos

* **C02 — `matching_product_rows` e limite de busca no card:**  
  **Status: CONFIRMADO / CORREÇÃO_NECESSÁRIA**  
  **Evidência:** `app/mobile/shopee_video.py:122-143`.  
  A função percorre ancestrais (`ancestor = parents.get(...)`, L135-142) sem delimitar o container do card (ex.: `CardView` ou item de lista). Se um título corresponder à busca e não possuir botão no nível imediato, o loop sobe na árvore até encontrar qualquer nó com `"Adicionar"`. Se um ancestral comum a múltiplos produtos contiver apenas um botão desse tipo, ele associa indevidamente o título a esse botão.  
  *Limite da evidência:* A falha foi reproduzida em XML sintético. Em execução real, validações posteriores no modal/vínculo podem mitigar a publicação errônea, mas a lógica de seleção de linha é frágil e exige contenção explícita de escopo.

* **C04 — `visual_preview_reviewed` no fluxo de nova seleção:**  
  **Status: CONFIRMADO / CORREÇÃO_NECESSÁRIA**  
  **Evidência:** `app/mobile/shopee_video.py:474`, `497-513`, `539`.  
  Em `select_media()` (L474), o registro de evidência é criado com `visual_preview_reviewed=False`. Durante `publish()` (L539), a checagem invoca `media_matches()` (L497-513), que valida hashes de arquivos locais, `sha256sum` remoto e recorte de pixels, mas **nunca** verifica `visual_preview_reviewed`. Apenas `adopt_selection()` (L490) exige essa revisão. Portanto, o fluxo novo avança e autoriza a postagem ignorando o gate de revisão visual humana.

* **C05 — Desduplicação tardia em novo job:**  
  **Status: CONFIRMADO / CORREÇÃO_NECESSÁRIA**  
  **Evidência:** `app/mobile/shopee_video.py:515-530`, `575-592`.  
  Em `run_prepared()` (L580), a checagem no início avalia apenas a sessão local do job. A trava global por hash (`attempts/{identity}.json`) ocorre exclusivamente em `reserve_attempt()` (L518-527), chamado dentro de `publish()` (L549). Consequentemente, um novo job com a mesma mídia executa navegação, seleção, digitação de legenda e produto na UI antes de ser abortado imediatamente antes do clique final. A reserva deve ocorrer no preflight.

* **C14 — Bloqueio do botão final no script de probe:**  
  **Status: UNKNOWN**  
  **Evidência:** A leitura direta de `scripts/probe_shopee_android.py` foi cancelada por timeout na sessão anterior antes da inspeção minuciosa das linhas de código. Por estrita aderência ao critério de evidência auditada, o ponto permanece como UNKNOWN nesta revisão.

---

### 2. Avaliação da Classificação de Risco (HIGH)

A classificação de **RISCO ATUAL: HIGH** no relatório está **corretamente fundamentada**:
1. **Exposição Contratual vs. Probabilidade:** O relatório distingue com clareza a exposição da probabilidade. A exposição é alta porque os Termos Específicos do Shopee Video (item **4.1(g)**) proíbem expressamente o uso de scripts automatizados para interagir com o serviço. Isso não equivale a afirmar que há alta probabilidade ou certeza de banimento imediato; as chances de detecção, thresholds de telemetria e prazos de penalidade são explicitamente tratados como **DESCONHECIDOS / UNKNOWN**.
2. **Exposição Operacional:** Lacunas no código (ausência de reconciliação automática, verificação tardia de desduplicação e inexistência de circuit breaker central) elevam o risco operacional caso haja execução concorrente ou em lote.

---

### 3. Proposta de Piloto: Controles Propostos vs. Implementados

É fundamental separar a realidade do código atual das recomendações:
* **Controles Implementados:** Locks locais por serial, verificação de hashes SHA-256 de mídia/preview, waits finitos de UI e reserva de clique único (que registrou erro seguro `PUBLICATION_UNCONFIRMED_DO_NOT_REPOST` no teste anterior).
* **Controles Propostos (Não Implementados):** Orçamento diário (`MAX_POSTS_PER_DAY = 1`), limites de requisições, circuit breaker com estados OPEN/CLOSED e validação estrita de `shop_id/item_id`.
* **Condicionalidade do Piloto:** A proposta de piloto apresentada no relatório está **estritamente condicionada** à existência de uma interface oficial autorizada ou à condução de processo operacional manual assistido. O hardening de engenharia mitiga falhas técnicas locais, mas **não substitui autorização formal** da plataforma. Sem permissão, a recomendação é zero jobs de automação em produção.
