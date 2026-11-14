---
name: create-product-storyboard
description: Produces complete 4-scene video storyboards with precise visual prompts, negative prompts, camera directions, and environment detection.
---

# Create Product Storyboard Skill

## Purpose
Transforms `ProductFacts` and `CreativeBrief` into a sequential 4-scene `Storyboard`. Emits generation-ready visual prompts tailored for Google Flow or image diffusion models without category hardcoding.

## Storyboard Standard (4 Scenes / 15-20s Total)
1. **Scene 1 (Hook & Presentation)**: Medium shot of Nina showing the product in its natural room context.
2. **Scene 2 (Visible Product Detail)**: Close-up / Macro shot limited to details visible in the official image or present in `CONFIRMED_FACTS`.
3. **Scene 3 (Factual Presentation)**: Interaction shot showing conservative handling or placement without inventing scale, materials, mechanisms, or performance.
4. **Scene 4 (CTA & Verdict)**: Medium close-up of Nina smiling naturally next to the product, inviting viewers to check details in bio.

## Dynamic Environment Detection
- Infer room setting strictly from product title and confirmed facts (e.g. kitchen for culinary items, desk/office for electronics/accessories, reception/counter for signs/business items, bedroom/living room for decor).
- Never default to kitchen or garlic unless explicitly confirmed by the product payload!

## Visual Prompt Composition
Every prompt must combine:
- `persona_prompt`: Nina's visual master description (when Nina is in scene).
- `scene_action`: Exact action and product positioning.
- `environment`: Detected environment description.
- `photorealism_tags`: 35mm photograph, soft natural light, detailed skin texture, raw photo, f/2.0.
- `negative_prompt`: CGI, illustration, 3D render, cartoon, oversaturated, plastic skin, distorted fingers.
