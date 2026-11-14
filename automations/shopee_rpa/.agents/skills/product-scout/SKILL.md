---
name: product-scout
description: Discovers, evaluates, and selects real products from Shopee Affiliate API based on viability criteria without hallucinating features.
---

# Product Scout Skill

## Purpose
Specialized skill for querying the Shopee Affiliate API (GraphQL `productOfferV2`), evaluating commercial viability, extracting factual product attributes, and preparing the raw product payload for the pipeline.

## Guidelines
1. **Source of Truth**: All product data must come directly from Shopee Affiliate API queries or verified raw product responses. Never invent sales figures, ratings, or specifications.
2. **Missing Fields**: If ratings, reviews, or sales count are missing, treat them as `None`/absent. Do not fabricate a 5.0 rating or high sales count.
3. **Extraction**:
   - Extract title, item ID, shop ID, current price, original price, product link, and real product image URLs.
   - Categorize into broad domain (electronics, home/decor, beauty, kitchen, fashion) dynamically.
4. **Handoff**: Passes raw `Product` JSON model to `ProductFactSheet` extractor.
