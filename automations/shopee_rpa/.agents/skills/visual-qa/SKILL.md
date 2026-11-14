---
name: visual-qa
description: Inspects generated assets against Nina's canonical reference, official product imagery, photorealism, anatomy, and scene intent without inventing numeric scores.
---

# Visual QA Skill

## Purpose
Performs automated and semi-automated visual quality assurance on raw image generation outputs before video compilation.

## Output Contract

Return `PASS`, `REGENERATE`, or `REVIEW`, plus concrete reasons and regeneration instructions when applicable. If an image or required reference cannot be inspected, return `REVIEW`; never guess. Do not emit a numeric score unless a documented measurement method exists.

## Evaluation Criteria
1. **Nina Identity Consistency**:
   - Facial structure matches `data/personas/nina_v1/references/persona_master.png`, the authority source.
   - Preserve long dark-brown, slightly wavy hair, brown eyes, apparent age 22-24, and the reference skin tone.
   - Natural skin pores, realistic expressions, no uncanny plastic doll sheen.
2. **Photorealism & Anatomy**:
   - Correct hands and fingers (5 natural fingers per hand, no extra limbs or warped joints).
   - Coherent lighting matching the designated environment.
3. **Product Fidelity**:
   - Product appearance matches the official Shopee product image and only confirmed physical facts.
   - No hallucinatory features attached to the product.
4. **Resolution & Framing**:
   - Sharp 9:16 vertical crop, subject centered and within safe margins for mobile UI overlays.
