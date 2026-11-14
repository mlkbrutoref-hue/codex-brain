# E-01 — Repeat pre-flight record

**PREFLIGHT_DATE:** 24/09/2026  
**EXPERIMENT:** E-01 — Action Complexity  
**STATUS:** `READY_FOR_SCREENING_AUTHORIZATION / NOT_RUN`  
**FLOW_OPENED:** `YES — inspection only`  
**GENERATION_STARTED:** `NO`  
**CREDITS_SPENT:** `0`

## Decision

The repeated product-specific pre-flight passed. It authorizes a future operator to request approval for — but does not itself authorize — the four-output screening.

The exact live product identity remained unchanged: item `58267960935`, shop `1234187269`. The black variant is frozen. Live Affiliate data established current catalog presence; official media URLs were reachable and four originals were downloaded. The direct PDP UI returned a Shopee anti-bot challenge, which was not bypassed; no fact depends on bypassing it.

## Frozen evidence and variables

- moving part: lower sliding tray;
- static parts: upper tray, four posts and guide/base;
- motion: linear translation along the depth axis;
- grip: outer front-left lip of lower tray;
- limits: visually supported retracted and extended states only; numeric travel remains unknown;
- scene: minimal laundry/utility countertop;
- props: exactly three unbranded controls; P1 is the only removable prop;
- performer: one right hand/forearm; left hand, face and identity reference absent;
- camera/light: static 3/4 front-left medium-close, about 0.9 m, soft daylight from camera-left;
- style: one continuous photorealistic UGC take, no cuts, text, speech or camera motion.

The full machine-readable specification and SHA-256 manifest are under `experiments/visual-production/E-01/preflight/`.

## Flow and credit pre-flight

The current Flow interface exposed the `Add ingredients` workflow, `Confirm before generating: Always`, vertical/horizontal video ratios, x1–x4 output counts and Omni/Veo 3.1 model options. No setting was saved and `Start generation` was not pressed.

Frozen execution configuration:

`Ingredients to Video / Veo 3.1 Fast / 8 seconds / 9:16 / x1 / one black-product ingredient`

For the observed Pro/non-Ultra account tier, the current official table states 20 credits per Veo 3.1 Fast generation. With x1, the screening ceiling is 4 outputs × 20 = **80 credits**. Any different displayed price is a mandatory stop and new pre-flight.

## Blind package

Two runs per condition are instantiated as `E01-R01..E01-R04`. The private mapping is separate from the evaluator presentation order. Blind forms collect observed events, action adherence, physics, hands, product fidelity, continuity, camera plausibility, usability and hard failures. Conditions are unblinded only after all four scorecards are locked.

## Gate

| Check | Result |
|---|---|
| Product identity and live catalog presence | `PASS` |
| Facts/mechanism/grip/start/end state | `PASS` |
| Frozen variant and original hashes | `PASS` |
| Variables and semantic action isolation | `PASS` |
| Final prompts | `PASS` |
| Current Flow support/configuration | `PASS` |
| Exact screening credit ceiling | `PASS — 80` |
| Blind run/evaluation package | `PASS` |
| Runtime regression baseline | `PASS — 60/60 tests; compileall PASS` |
| Generation executed | `NO` |

`SAFE_TO_EXECUTE_E01 = YES`, conditional on explicit approval to spend up to 80 credits and an immediate in-UI check that cost/configuration still match the frozen record.
