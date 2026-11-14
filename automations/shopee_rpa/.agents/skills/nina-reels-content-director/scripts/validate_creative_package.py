#!/usr/bin/env python3
"""Validate Nina Reel CreativePackage invariants."""

from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

FORMATS = {"ACHADINHO_RAPIDO", "PROBLEMA_SOLUCAO", "DEMONSTRACAO", "ANTES_DEPOIS", "PRODUTO_CURIOSO", "TRANSFORMACAO"}
SCORE_MAX = {"visual_proof": 25, "problem_clarity": 20, "curiosity": 15, "audience_breadth": 10, "compressibility": 10, "originality": 10, "reliability": 10}
FORBIDDEN_HASHTAGS = {"#fyp", "#fy", "#viral"}
FORBIDDEN_NINA = ("eu comprei", "eu testei", "uso todo dia", "chegou pra mim", "resolveu minha vida", "foi o meu resultado")
FORBIDDEN_CTA = ("link na bio", "clica na sacola", "link aqui embaixo")
FORBIDDEN_FLOW_CONDITIONAL = ("quando verificad", "se não verificad", "se nao verificad", "após verificar", "apos verificar", "quando confirmad", "se confirmad")
FORBIDDEN_SCOPE_KEYS = {"post_generator", "carousel_generator", "carousel_skill", "static_post_pipeline", "post_automation", "carousel_automation", "reels_automated"}
DECISIONS = {"RECOMMEND_REEL", "RESEARCH_REQUIRED", "REJECT"}
VISUAL_PROOF_BASES = {"CONFIRMED_OPERATION", "CONFIRMED_RESULT", "APPEARANCE_LED_REVEAL", "NONE"}
DURATION_RULES = {
    "30–45 s": {"scenes": (4, 6), "words": (65, 120)},
    "30-45 s": {"scenes": (4, 6), "words": (65, 120)},
    "45–60 s": {"scenes": (6, 8), "words": (95, 160)},
    "45-60 s": {"scenes": (6, 8), "words": (95, 160)},
    "60–90 s": {"scenes": (8, 12), "words": (130, 230)},
    "60-90 s": {"scenes": (8, 12), "words": (130, 230)},
}

def word_count(value):
    return len(re.findall(r"\b[\wÀ-ÿ'-]+\b", str(value), flags=re.UNICODE))

def all_text(value):
    if isinstance(value, dict): return " ".join(all_text(v) for v in value.values())
    if isinstance(value, list): return " ".join(all_text(v) for v in value)
    return str(value)

def validate(data):
    errors = []
    required = {"product", "product_provider", "product_score", "reliability_status", "decision", "recommend_reel", "profile_coherence_status", "visual_proof_basis", "flow_prompt_ready", "research_required", "selected_format", "video_duration_target", "flow_take_duration_target", "scene_count", "hook", "script_structure", "script_word_count", "final_script", "scene_plan", "on_screen_text_start", "on_screen_text_end", "cta", "caption", "hashtags", "cover_concept", "flow_prompt", "negative_prompt", "confirmed_facts", "facts_used", "fact_ledger", "unknown_facts", "fact_safety", "nina_safety", "posts_manual", "carousels_manual", "reels_creative_skill_ready", "reels_pipeline_integrated", "flow_integrated_with_skill", "flow_generations"}
    errors.extend(f"missing field: {k}" for k in sorted(required - data.keys()))
    if errors: return errors

    score_data = data["product_score"]
    subtotal = 0
    for key, maximum in SCORE_MAX.items():
        item = score_data.get(key)
        if not isinstance(item, dict):
            errors.append(f"missing score component: {key}"); continue
        score = item.get("score")
        if item.get("max") != maximum: errors.append(f"{key}.max must be {maximum}")
        if not isinstance(score, (int, float)) or not 0 <= score <= maximum: errors.append(f"{key}.score out of range")
        else: subtotal += score
        if not str(item.get("reason", "")).strip(): errors.append(f"{key}.reason is required")
    if score_data.get("total") != subtotal: errors.append("product_score.total does not equal component sum")

    provider = data["product_provider"]
    reliability_score = score_data.get("reliability", {}).get("score")
    if provider not in {"LIVE", "FIXTURE"}: errors.append("product_provider must be LIVE or FIXTURE")
    if isinstance(reliability_score, (int, float)):
        if provider == "FIXTURE" and reliability_score > 5: errors.append("fixture reliability cannot exceed 5")
        if provider == "LIVE" and reliability_score > 8: errors.append("single LIVE response reliability cannot exceed 8")

    reliability_pass = data["reliability_status"] == "PASS"
    if not reliability_pass:
        if data["decision"] != "REJECT" or data["recommend_reel"] is not False: errors.append("reliability failure must reject Reel")
        if data["fact_safety"] != "FAIL": errors.append("reliability failure must set fact_safety FAIL")
    if subtotal < 70 and data["recommend_reel"] is not False: errors.append("score below 70 cannot recommend Reel")
    if data["decision"] not in DECISIONS: errors.append("decision is not supported")
    if data["profile_coherence_status"] not in {"PASS", "FAIL"}: errors.append("profile_coherence_status must be PASS or FAIL")
    if data["visual_proof_basis"] not in VISUAL_PROOF_BASES: errors.append("visual_proof_basis is not supported")
    if not isinstance(data["flow_prompt_ready"], bool): errors.append("flow_prompt_ready must be boolean")
    if not isinstance(data["research_required"], list): errors.append("research_required must be a list")
    if data["recommend_reel"] is True:
        if data["decision"] != "RECOMMEND_REEL": errors.append("recommended Reel must use decision RECOMMEND_REEL")
        if data["profile_coherence_status"] != "PASS": errors.append("recommended Reel requires profile coherence PASS")
        if data["visual_proof_basis"] == "NONE": errors.append("recommended Reel requires confirmed visual proof")
        if data["flow_prompt_ready"] is not True: errors.append("recommended Reel requires flow_prompt_ready true")
    if data["profile_coherence_status"] == "FAIL" or data["visual_proof_basis"] == "NONE" or data["flow_prompt_ready"] is False:
        if data["recommend_reel"] is not False: errors.append("missing visual coherence cannot recommend Reel")
        if reliability_pass and data["decision"] != "RESEARCH_REQUIRED": errors.append("missing visual coherence requires RESEARCH_REQUIRED")
        if not data["research_required"]: errors.append("missing visual coherence requires research_required")
    visual_score = score_data.get("visual_proof", {}).get("score")
    if data["visual_proof_basis"] == "NONE" and isinstance(visual_score, (int, float)) and visual_score > 8:
        errors.append("visual proof score cannot exceed 8 without confirmed visual proof")
    if data["selected_format"] not in FORMATS: errors.append("selected_format is not a supported Reel format")
    duration_rule = DURATION_RULES.get(data["video_duration_target"])
    if duration_rule is None: errors.append("video_duration_target must be 30–45 s, 45–60 s, or 60–90 s")
    if data["flow_take_duration_target"] not in {"5–10 s", "5-10 s"}: errors.append("flow_take_duration_target must be 5–10 s")

    beats = data["script_structure"]
    if not isinstance(beats, list) or len(beats) < 5: errors.append("script_structure must contain at least 5 narrative beats")
    else:
        beat_names = {str(item.get("beat", "") if isinstance(item, dict) else item).strip().upper() for item in beats}
        for required_beat in {"HOOK", "DEMONSTRACAO", "CTA"}:
            if required_beat not in beat_names: errors.append(f"script_structure requires {required_beat} beat")
    actual_words = word_count(data["final_script"])
    if data["script_word_count"] != actual_words: errors.append("script_word_count must match final_script")
    if duration_rule is not None:
        min_words, max_words = duration_rule["words"]
        if not min_words <= actual_words <= max_words: errors.append(f"final_script word count must be {min_words} to {max_words} for selected duration")

    scenes = data["scene_plan"]
    if not isinstance(scenes, list) or not 4 <= len(scenes) <= 12: errors.append("scene_plan must contain 4 to 12 narrative takes")
    if data["scene_count"] != len(scenes): errors.append("scene_count must match scene_plan")
    if not str(data.get("multi_take_justification", "")).strip(): errors.append("narrative take sequence requires multi_take_justification")
    if duration_rule is not None and isinstance(scenes, list):
        min_scenes, max_scenes = duration_rule["scenes"]
        if not min_scenes <= len(scenes) <= max_scenes: errors.append(f"scene_count must be {min_scenes} to {max_scenes} for selected duration")
    for scene in scenes if isinstance(scenes, list) else []:
        if not str(scene.get("narrative_role", "")).strip(): errors.append("each scene requires narrative_role")
        if "flow_prompt" not in scene: errors.append("each scene requires flow_prompt")
        elif data["flow_prompt_ready"] is True and not str(scene.get("flow_prompt", "")).strip(): errors.append("flow_prompt_ready requires a prompt for every scene")

    confirmed = data["confirmed_facts"]
    confirmed_keys = set(confirmed) if isinstance(confirmed, dict) else set()
    used = set(data["facts_used"]) if isinstance(data["facts_used"], list) else set()
    if not used <= confirmed_keys: errors.append("facts_used contains unconfirmed keys")
    for scene in scenes if isinstance(scenes, list) else []:
        if not set(scene.get("fact_keys", [])) <= confirmed_keys: errors.append("scene references unconfirmed fact key")
    for item in data["fact_ledger"] if isinstance(data["fact_ledger"], list) else []:
        if item.get("source_key") not in confirmed_keys: errors.append("fact_ledger references unconfirmed source_key")

    generated = {k: data[k] for k in ("hook", "final_script", "scene_plan", "on_screen_text_start", "on_screen_text_end", "cta", "caption", "cover_concept", "flow_prompt", "negative_prompt")}
    text = all_text(generated).casefold()
    for phrase in FORBIDDEN_NINA:
        if phrase.casefold() in text: errors.append(f"forbidden Nina experience claim: {phrase}")
    for phrase in FORBIDDEN_CTA:
        if phrase.casefold() in text: errors.append(f"forbidden CTA channel: {phrase}")
    flow_text = str(data["flow_prompt"]).casefold()
    for phrase in FORBIDDEN_FLOW_CONDITIONAL:
        if phrase in flow_text: errors.append(f"Flow prompt cannot delegate factual verification: {phrase}")
    if data["flow_prompt_ready"] is True and not str(data["flow_prompt"]).strip(): errors.append("flow_prompt_ready requires a non-empty prompt")
    if "quero" not in data["cta"].casefold(): errors.append("CTA must use QUERO")
    if data["on_screen_text_end"].strip().upper() != "COMENTA QUERO": errors.append("on_screen_text_end must be COMENTA QUERO")

    hashtags = data["hashtags"]
    if not isinstance(hashtags, list) or not 4 <= len(hashtags) <= 8: errors.append("hashtags must contain 4 to 8 items")
    else:
        normalized = [h.casefold() for h in hashtags]
        if len(normalized) != len(set(normalized)): errors.append("hashtags must be unique")
        bad = FORBIDDEN_HASHTAGS.intersection(normalized)
        if bad: errors.append("forbidden hashtags: " + ", ".join(sorted(bad)))
        if any(not re.fullmatch(r"#[\wÀ-ÿ]+", h) for h in hashtags): errors.append("each hashtag must be a single valid hashtag")

    for key in FORBIDDEN_SCOPE_KEYS:
        if key in data: errors.append(f"out-of-scope field present: {key}")
    if data["posts_manual"] is not True or data["carousels_manual"] is not True: errors.append("posts and carousels must remain manual")
    if data["reels_creative_skill_ready"] is not True: errors.append("reels_creative_skill_ready must be true")
    if not isinstance(data["reels_pipeline_integrated"], bool): errors.append("reels_pipeline_integrated must be boolean")
    if data["flow_integrated_with_skill"] is not False: errors.append("flow_integrated_with_skill must be false")
    if data["flow_generations"] != 0: errors.append("flow_generations must remain 0 in planning/dry-run stage")
    if data["fact_safety"] not in {"PASS", "FAIL"} or data["nina_safety"] not in {"PASS", "FAIL"}: errors.append("safety statuses must be PASS or FAIL")
    return errors

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("package", type=Path); args = parser.parse_args()
    data = json.loads(args.package.read_text(encoding="utf-8")); errors = validate(data)
    if errors:
        print("FAIL"); [print(f"- {error}") for error in errors]; return 1
    print("PASS"); return 0

if __name__ == "__main__": sys.exit(main())
