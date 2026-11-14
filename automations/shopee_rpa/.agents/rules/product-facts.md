---
description: Enforces Shopee API as source of truth and classifies facts by confidence levels.
always_on: true
---

# Product Facts Rule

1. **Source of Truth**: In this pipeline, all factual product statements must originate from the Shopee Affiliate API response preserved in the `Product` model. External manufacturer specifications require a separately recorded, traceable source before they may enter `CONFIRMED_FACTS`.
2. **Confidence Classification**:
   - `CONFIRMED_FACTS`: Explicitly returned by the API and recorded with its source. Only this class may become an objective commercial claim.
   - `INFERRED_CONTEXT`: A creative setting or plausible context. It may guide staging, but must never be phrased as a product fact or capability.
   - `UNKNOWN`: Not present in the API payload. Never promote it to a claim or fabricate price, rating, battery life, capacity, materials, popularity, or scarcity.
3. **No Hallucinated Claims**:
   - Strictly forbid claiming waterproofness, lifetime durability, or medical benefits unless recorded in `CONFIRMED_FACTS`.
   - Never carry over attributes from previous jobs (e.g. 250ml, garlic, USB) into unrelated categories.
