# Arquitetura e Contratos de Providers

> **OUTDATED:** snapshot dos providers em uma etapa anterior. Para distinguir capability obrigatória de provider substituível e consultar o estado atual, use [`../brain/CHIA.md`](../brain/CHIA.md) e [`../brain/CURRENT_STATE.md`](../brain/CURRENT_STATE.md).

Este documento especifica as interfaces abstratas que conectam o sistema aos serviços externos e agentes inteligentes.

---

## 1. ShopeeProductProvider (Validado e Comprovado)

A integração com a **Shopee Affiliate Open API** (`https://open-api.affiliate.shopee.com.br/graphql`) foi inspecionada e reutilizada diretamente da implementação de referência do projeto anterior (`shopee-video-automation`), eliminando suposições e garantindo paridade total com o contrato oficial da Shopee Brasil.

### Modos de Operação Estritamente Separados:
- **`SHOPEE_PROVIDER=live` (`ShopeeLiveProductProvider`):**
  - Conecta-se diretamente à Shopee Affiliate API em produção.
  - **Zero Fallback Silencioso:** Se a API recusar a requisição, se a credencial estiver incorreta ou se o produto não existir, a operação **falha imediatamente** (`AffiliateAPIError`). Nunca retorna fixtures ou dados sintéticos.
- **`SHOPEE_PROVIDER=fixture` (`LocalFixtureShopeeProvider`):**
  - Carrega dados locais a partir de `data/products/<product_id>.json`.
  - Modo padrão para desenvolvimento offline e testes unitários/CI sem custo de rede.
  - Nunca é apresentado como teste real de API.

### Especificação Criptográfica e Protocolar da Shopee API:
1. **Endpoint Oficial:** `https://open-api.affiliate.shopee.com.br/graphql`
2. **Algoritmo de Assinatura:** SHA256 simples concatenando `app_id + timestamp + payload + secret`:
   ```python
   signature = hashlib.sha256(
       app_id.encode("utf-8") + timestamp.encode("utf-8") + payload + secret.encode("utf-8")
   ).hexdigest()
   ```
   *(Nota: A Shopee Affiliate API BR utiliza essa concatenação SHA256 direta e NÃO HMAC-SHA256).*
3. **Formatação do Cabeçalho de Autorização:**
   ```http
   Authorization: SHA256 Credential={app_id}, Timestamp={timestamp}, Signature={signature}
   ```
4. **Serialização Estrita do Payload:**
   ```python
   payload = json.dumps(
       {"query": query, "variables": variables or {}},
       ensure_ascii=False,
       separators=(",", ":"),
       allow_nan=False
   ).encode("utf-8")
   ```
   *(Sem espaços em branco para não corromper o cálculo da assinatura).*
5. **Schema GraphQL Oficial:**
   - Query de busca: `productOfferV2(page: $page, limit: $limit, keyword: $keyword, ...)`
   - Query detalhada: `product_details_query(item_id: int, shop_id: int)` emitindo literais numéricos Int64 (pois o GraphQL da Shopee BR rejeita variáveis JSON numéricas para Int64 com o erro 10010).

---

## 2. VisualGenerationProvider

Interface responsável por produzir as imagens conceituais, âncoras e takes de vídeo dinâmicos com base nos storyboards e prompts da Nina.

- **`ManualFlowProvider` (Fallback Primário Operacional):**
  - Escreve `output/<job_id>/prompts/scene_XX.txt` com instruções detalhadas para o operador ou agente injetar no Google Flow com `persona_master.png`.
  - Registra em cada cena a referência oficial do produto.
  - Verifica se os takes correspondentes foram depositados em `output/<job_id>/generated/`.
  - `start_operation()` apenas devolve `READY`; nunca clica em Generate.
- **`AntigravityFlowProvider` (Preparado, não comprovado live):**
  - Implementa a mesma interface sem alterar o orquestrador.
  - Fica desabilitado e marcado `BLOCKED_BY_ANTIGRAVITY_QUOTA` por padrão.
  - Exige cota disponível e `generation_authorized=True` em todas as cenas antes de qualquer chamada.
  - Retorna estados tipados e rejeita resposta estruturada inválida.

Contratos: `FlowOperationRequest`, `FlowOperationResult`, `SceneGenerationRequest` e `SceneGenerationResult`. Estados: `READY`, `LOGIN_REQUIRED`, `GENERATING`, `SUCCESS`, `FAILED` e `REVIEW_REQUIRED`.

Nenhum provider visual realizou geração nesta retomada (`FLOW_GENERATIONS=0`).

---

## 3. VoiceProvider & CreativeAgentProvider

- **`VoiceProvider`:** Síntese de voz pt-BR natural (status atual: `none`).
- **`CreativeAgentProvider`:** ainda não existe como provider externo; briefs, roteiros e storyboards são gerados atualmente por módulos Python determinísticos que respeitam `CONFIRMED_FACTS`.
