---
description: Prohibits unmonitored AI generations, enforces explicit human checkpoints, and preserves platform credits.
always_on: true
---

# Cost Control & Budget Rule

1. **Explicit Approval Gate**:
   - Zero automated credit consumption. Any action that consumes image or video generation credits (Google Flow, Midjourney, Kling, Runway, etc.) requires explicit human-in-the-loop authorization.
   - Script generation, storyboard planning, prompt generation, and copy writing must always complete and be reviewed first.
2. **Batching & Iteration Limit**:
   - Never generate multiple full batches in parallel without evaluating the first output.
   - If Scene 1 fails visual QA, do not generate Scenes 2, 3, or 4 until prompts or reference anchors are adjusted.
3. **Dry-Run & Mock First**:
   - All tests in CI/CD or local test suites must use mock providers or fixture data.
   - Never trigger live AI generation during unit testing.
