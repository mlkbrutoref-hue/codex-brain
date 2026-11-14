# E-01 — Product Evidence Acquisition Decision

**ACQUISITION_DATE:** 23/09/2026  
**STATUS:** `PRODUCT_SELECTED / EVIDENCE_GATES_PASS / PREFLIGHT_REPEAT_REQUIRED / NOT_RUN`  
**FLOW_OPENED:** `NO`  
**CREDITS_SPENT:** `0`

## Decision

`SELECTED`:

**Prateleira Deslizante 2 Andares Organizador Armário Gaveta Corrediça Cozinha Banheiro Preto Branco**  
`ITEM_ID: 58267960935`  
`SHOP_ID: 1234187269`  
`SELLER: Bravuuz Store`  
`PRODUCT_URL: https://shopee.com.br/product/1234187269/58267960935`

Este foi o único dos cinco produtos avaliados que passou por todos os elementos críticos do gate sem transformar hipótese em fato. Não foi usado score somado.

## Why selected

- a Affiliate API live confirmou identidade, item/shop IDs, seller, URL e imagem principal;
- a página real estava ativa durante a aquisição e expôs título, marca, material, dimensões, conteúdo da embalagem e descrição;
- a descrição da própria listagem identifica explicitamente uma **bandeja deslizante**, um **sistema corrediço** e sua função de dar acesso aos itens;
- a galeria mostra a geometria completa de dois níveis, montantes/base, a bandeja inferior em posições recolhida e estendida e uma mão na borda frontal-lateral da bandeja;
- o vídeo oficial da listagem reforça os estados do conjunto em uso doméstico;
- a bandeja inferior é uma parte móvel simples; estrutura, montantes e nível superior permanecem estáticos;
- o eixo é uma translação linear ao longo da profundidade, para fora/para dentro;
- a ação atômica e a sequência multi-step podem usar exatamente o mesmo contexto e mudar somente a complexidade da ação.

## Evidence ledger

| Fact/observation | Status | Source |
|---|---|---|
| Product identity, item/shop IDs, seller and product URL | `VERIFIED` | Shopee Affiliate `productOfferV2`, exact lookup `58267960935_1234187269`; snapshot in `product-candidates.json` |
| Two-level organizer with sliding/corrediça tray | `VERIFIED` | Shopee PDP title and description at the product URL |
| Material: metal with electrostatic paint and PP plastic | `VERIFIED_AS_LISTING_FACT` | Shopee PDP product details |
| Dimensions: 22 × 40 × 35 cm (H × W × D) | `VERIFIED_AS_LISTING_FACT` | Shopee PDP product details |
| Moving part: lower sliding tray | `VERIFIED` | PDP description plus official gallery/video |
| Static parts: upper tray, four posts and guide/base structure | `VERIFIED` | Official gallery/video; only lower tray changes position |
| Direction: pull outward / push inward on depth axis | `VERIFIED` | Official gallery/video state comparison and corrediça description |
| Plausible grip: front/side outer lip of lower tray | `VERIFIED` | Official image `sg-11134201-825bb-msztut8obw90b7` shows hand at this zone |
| Start state: lower tray retracted/aligned under structure | `VERIFIED` | Official gallery/video |
| End state: lower tray visibly extended | `VERIFIED` | Main image, official gallery and video |

### Official media observed

- main: <https://cf.shopee.com.br/file/sg-11134201-8259c-msztupjyr85cca>
- alternate/state: <https://down-br.img.susercontent.com/file/sg-11134201-8258t-mszturpw6k94b2>
- hand + extended tray: <https://down-br.img.susercontent.com/file/sg-11134201-825bb-msztut8obw90b7>
- alternate geometry: <https://down-br.img.susercontent.com/file/sg-11134201-82592-msztuv5n5gy086>
- listing video: <https://mms.vod.susercontent.com/api/v4/11110106/mms/sg-11110106-6vcbv-msztv15xlfr4da.16000081789145929.mp4>

These URLs are evidence references, not permission to generate. They must be revalidated and frozen with hashes if the repeated pre-flight downloads authorized originals into experiment storage.

## Evidence gate

| Element | Result |
|---|---|
| `PRODUCT_IDENTITY` | `VERIFIED` |
| `PRODUCT_GEOMETRY` | `VERIFIED` |
| `PRODUCT_FUNCTION` | `VERIFIED` |
| `MOVING_PARTS` | `VERIFIED` |
| `STATIC_PARTS` | `VERIFIED` |
| `INTERACTION_DIRECTION` | `VERIFIED` |
| `PLAUSIBLE_GRIP` | `VERIFIED` |
| `START_STATE` | `VERIFIED` |
| `END_STATE` | `VERIFIED` |
| `FACT_GATE` | `PASS` |
| `VISUAL_GATE` | `PASS` |
| `MECHANISM_VERIFIED` | `YES` |

## Conceptual actions — not prompts

### Atomic action candidate

`initial state` lower tray fully retracted and three marked props stationary  
→ hand grips the front/side outer lip  
→ one linear pull extends the tray to the visible open limit  
→ `final state` tray remains open and held briefly.

### Multi-step action candidate

Same initial context and props  
→ grip and pull tray open  
→ release the tray  
→ grasp one designated prop  
→ remove it  
→ replace the same prop in the same marked position  
→ re-grip the tray lip  
→ push tray closed to its visible retracted limit  
→ final hold.

No camera, light, aesthetics, risk mitigation or reference difference is authorized here. Those variables belong to the repeated product-specific pre-flight.

## Residual uncertainties

- Maximum travel is not specified numerically. The experiment must use only visually supported closed/open limits and must not invent a distance.
- White and black variants are present. One exact variant must be selected and frozen before prompt creation.
- The listing had no reviews and zero sales in the live snapshot. That does not invalidate the visible mechanism, but product/page availability must be rechecked.
- Listing facts are seller-provided facts, not independent durability/performance tests. E-01 must not make strength, load, moisture-resistance or performance claims.
- Exact original files and hashes have not yet been frozen into runtime storage; source URLs are persisted here. That is a required task in the repeated pre-flight.

## Boundary

`READY_TO_REPEAT_E01_PREFLIGHT = YES` does not mean `SAFE_TO_EXECUTE_E01 = YES`.

No Flow configuration was checked, no prompts were created, no blind mapping was instantiated, no generation was initiated and no credit was spent.

