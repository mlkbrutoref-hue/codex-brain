---
name: flow-operator
description: Controls interaction with Google Flow UI for image generation, maintaining credit budget and strict cost control.
---

# Flow Operator Skill

## Purpose
Operates the Google Flow web interface via browser automation or Antigravity browser tools. Responsible for prompt input, reference image attachment, seed management, and asset retrieval.

## Safety & Budget Guardrails
1. **Approval Required**: Never trigger generation or click "Generate" without explicit run approval. Zero unexpected credit consumption.
2. **Batching**: Generate one scene at a time. Validate output through `visual-qa` before proceeding to subsequent scenes.
3. **Reference Assets**: Attach `persona_master.png` and real product images as reference anchors when composing scenes.
4. **Session Persistence**: Use only an already authenticated browser session exposed by the approved browser tool. Never extract, copy, print, or persist cookies or credentials. If login or CAPTCHA is required, return `LOGIN_REQUIRED` for the user to handle.
5. **Format**: Default to 9:16 vertical ratio suitable for Reels, TikTok, and Shopee Video.

## Operational Contract

- Build one `SceneGenerationRequest` from the Nina reference, official product image, and scene prompt.
- Inspect the current UI before acting; do not invent selectors or button state.
- Return only `READY`, `LOGIN_REQUIRED`, `GENERATING`, `SUCCESS`, `FAILED`, or `REVIEW_REQUIRED`.
- A prepared request is not authorization to generate. Each request must carry explicit generation authorization.
