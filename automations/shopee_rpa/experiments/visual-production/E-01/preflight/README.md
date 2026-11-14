# E-01 — Repeat pre-flight package

**Frozen at:** `2026-09-24T10:55:01-03:00`  
**Experiment:** E-01 — Action Complexity  
**Golden scene:** GS-C — sliding organizer drawer  
**Status:** `READY_FOR_SCREENING_EXECUTION / NOT_RUN`  
**Credits spent:** `0`

This package is the executable specification for the four screening outputs. It does not contain generated media. The only independent variable is the action block: one drawer-opening action versus a dependent open/remove/replace/close sequence.

## Gate result

- exact SKU and shop identity were revalidated through the live Shopee Affiliate provider;
- the product remains present in the live catalog; direct PDP browser inspection was blocked by Shopee anti-bot and was not bypassed;
- the black variant, mechanism, grip zone, start/end states, scene, props, hand assignment, camera, light, Flow configuration and run plan are frozen;
- four official listing assets are preserved byte-for-byte with SHA-256 hashes;
- current Flow UI and official documentation were inspected without starting a generation;
- blind candidate IDs and blank evaluation records are instantiated;
- no performance, durability, load or water-resistance claim is authorized.

`SAFE_TO_EXECUTE_E01 = YES` means only that the future operator may run the four screening generations exactly as specified here. It is not permission to alter the prompt, references or configuration, and it does not mean E-01 has been run.

## Required operator sequence

1. Verify every asset hash against `asset-manifest.json`.
2. Open a dedicated Flow project/session and leave `Confirm before generating` on `Always`.
3. Select video generation with one ingredient image, Veo 3.1 Fast, vertical 9:16, 8 seconds and one output per generation.
4. Upload only `assets/original/product-primary-black.jpg` as the ingredient; do not upload the QA-only references.
5. Execute candidates in the order in `blinding/execution-key.json`, producing one file per candidate ID.
6. Stop immediately on a hash mismatch, unavailable model/mode, displayed cost different from 20 credits, reference rejection, or any unplanned prompt/config change.
7. Place outputs in `outputs/` using only the candidate ID as filename, then give the evaluator only `blinding/evaluator-order.json`, `evaluation/acceptance-checks.json` and the four blank scorecards.

## Package map

- `protocol-snapshot.json`: frozen experiment question, conditions, controls and screening design.
- `product-snapshot.json`: live identity/availability snapshot and evidence boundary.
- `facts.json`: compact verified-facts and unknowns ledger.
- `asset-manifest.json`: originals, dimensions, hashes and exact roles.
- `frozen-variables.json`: complete experimental controls.
- `flow-configuration.json`: one Flow configuration for every run.
- `credit-plan.json`: exact screening budget and stop rule.
- `risk-profile.json`: product-specific risks and mitigations.
- `prompts/`: shared invariant prompt, two final prompts and semantic diff.
- `blinding/`: private execution key plus evaluator presentation order.
- `evaluation/`: blind observation rubric and one blank record per run.
- `FINAL_STATUS.yaml`: final gate result in the requested return schema.
- `outputs/`: intentionally empty until an explicitly authorized execution.
