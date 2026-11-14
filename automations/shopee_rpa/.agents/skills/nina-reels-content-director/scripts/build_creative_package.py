#!/usr/bin/env python3
"""Build a fact-safe Nina Reel CreativePackage from Product and ProductFacts."""

from __future__ import annotations

import re
from typing import Any, Dict, Mapping


def _fact_map(product_facts: Mapping[str, Any]) -> Dict[str, str]:
    facts: Dict[str, str] = {}
    for index, item in enumerate(product_facts.get("confirmed_facts", []), start=1):
        source = str(item.get("source", "confirmed_fact")).strip()
        key = re.sub(r"[^a-z0-9_]+", "_", source.casefold()).strip("_") or f"confirmed_fact_{index}"
        candidate = key
        suffix = 2
        while candidate in facts:
            candidate = f"{key}_{suffix}"
            suffix += 1
        facts[candidate] = str(item.get("claim", "")).strip()
    return facts


def _reliability(product: Mapping[str, Any], facts: Mapping[str, str], provider: str) -> tuple[int, str]:
    has_title = bool(facts.get("shopee_api_product_title"))
    direct_count = sum(key.startswith("shopee_") for key in facts)
    has_image = bool(product.get("images"))
    has_technical_detail = bool(product.get("description") or product.get("attributes"))

    if provider == "LIVE" and has_title and direct_count >= 4 and has_image:
        if has_technical_detail:
            return 8, "Registro LIVE oficial e atual com identidade, imagem, dados comerciais e detalhes técnicos; ainda é uma única fonte."
        return 7, "Registro LIVE oficial e atual com identidade, imagem e dados comerciais; faltam descrição e atributos técnicos."
    if provider == "LIVE" and has_title and direct_count >= 2:
        return 6, "Registro LIVE oficial e atual, porém com cobertura factual limitada."
    if provider == "FIXTURE" and has_title and direct_count >= 3:
        return 5, "Fixture rastreável com fatos estruturados, mas sem confirmação de atualidade ao vivo."
    return 2, "Evidência insuficiente ou sem identidade confirmada no ProductFacts."


def build_creative_package(
    product: Mapping[str, Any],
    product_facts: Mapping[str, Any],
    *,
    product_provider: str,
    pipeline_integrated: bool = True,
) -> Dict[str, Any]:
    """Return a CreativePackage without invoking Flow or any external generator."""
    provider = product_provider.strip().upper()
    confirmed = _fact_map(product_facts)
    title = confirmed.get("shopee_api_product_title", "")
    title_folded = title.casefold()
    is_electric_brush = "escova" in title_folded and "limpeza" in title_folded and "elétrica" in title_folded
    is_twelve_in_one = bool(re.search(r"\b12\s*em\s*1\b", title_folded))

    if is_electric_brush:
        label = "escova de limpeza elétrica" + (" 12 em 1" if is_twelve_in_one else "")
        hook = "Tem cantinho da casa que dá trabalho demais?"
        on_screen_start = ("ESCOVA ELÉTRICA 12 EM 1?" if is_twelve_in_one else "ESCOVA ELÉTRICA?")
        cover_title = ("ESCOVA 12 EM 1?" if is_twelve_in_one else "ESCOVA ELÉTRICA?")
        hashtags = ["#escovaeletrica", "#escovadelimpeza", "#limpeza", "#utilidadesdomesticas", "#achadinhos", "#ninaachadinhos"]
        visual_scores = (8, 16, 13, 8, 10, 8)
    else:
        label = title or "produto apresentado"
        hook = "Isso também complica sua rotina?"
        on_screen_start = "OLHA ESTE ACHADO"
        cover_title = "UM ACHADO PARA CONHECER"
        hashtags = ["#achadinhos", "#shopee", "#utilidades", "#comprasonline", "#ninaachadinhos", "#produtos"]
        visual_scores = (6, 12, 8, 7, 9, 8)

    reliability_score, reliability_reason = _reliability(product, confirmed, provider)
    score_values = dict(zip(
        ("visual_proof", "problem_clarity", "curiosity", "audience_breadth", "compressibility", "originality"),
        visual_scores,
    ))
    score_reasons = {
        "visual_proof": "Há imagem oficial, mas apresentação estática não comprova funcionamento nem resultado visual.",
        "problem_clarity": "A finalidade de limpeza aparece no título oficial, sem superfície ou resultado específico.",
        "curiosity": "A descrição 12 em 1 no título cria curiosidade, sem detalhar acessórios ausentes.",
        "audience_breadth": "A categoria de limpeza é compreensível para público amplo.",
        "compressibility": "O produto tem uma promessa central, mas precisa sustentar contexto, demonstração e payoff sem repetição.",
        "originality": "A execução pode usar enquadramento e atuação próprios da Nina.",
    }
    maxima = {"visual_proof": 25, "problem_clarity": 20, "curiosity": 15, "audience_breadth": 10, "compressibility": 10, "originality": 10}
    product_score = {
        key: {"score": value, "max": maxima[key], "reason": score_reasons[key]}
        for key, value in score_values.items()
    }
    product_score["reliability"] = {"score": reliability_score, "max": 10, "reason": reliability_reason}
    total = sum(item["score"] for item in product_score.values())
    product_score["total"] = total

    reliability_status = "PASS" if reliability_score >= 5 and bool(title) else "FAIL"
    profile_coherence_status = "FAIL"
    visual_proof_basis = "NONE"
    flow_prompt_ready = False
    recommend = False
    decision = "RESEARCH_REQUIRED" if reliability_status == "PASS" else "REJECT"
    fact_safety = "PASS" if reliability_status == "PASS" else "FAIL"
    final_script = (
        f"{hook} Então presta atenção neste achado. "
        f"O anúncio identifica este modelo como {label}. "
        "A história começa mostrando o problema de perto, revela o produto, acompanha a ação e compara o resultado no mesmo enquadramento. "
        "Como o funcionamento e o resultado deste modelo ainda não foram confirmados, essa demonstração continua bloqueada para pesquisa. "
        "Quando a prova estiver validada, o vídeo termina com o resultado e uma única ação: quer o link? Comenta QUERO."
    )
    script_structure = [
        {"beat": "HOOK", "purpose": "Abrir com uma dor cotidiana reconhecível."},
        {"beat": "IDENTIFICACAO", "purpose": "Dar contexto suficiente para a pessoa se reconhecer."},
        {"beat": "DESCOBERTA", "purpose": "Revelar o produto como achado, sem interromper a narrativa."},
        {"beat": "DEMONSTRACAO", "purpose": "Mostrar operação confirmada em etapas; bloqueado até pesquisa."},
        {"beat": "PAYOFF", "purpose": "Comparar o resultado no mesmo enquadramento; bloqueado até pesquisa."},
        {"beat": "CTA", "purpose": "Encerrar com uma única ação."},
    ]
    caption = f"{label.capitalize()}: um achado para conhecer.\n\nQuer o link? Comenta QUERO.\n\n{' '.join(hashtags)}"
    unknown_facts = [str(item.get("claim", "")).strip() for item in product_facts.get("unknown_claims", [])]
    for missing in ("detalhes dos acessórios", "mecanismo de operação", "desempenho de limpeza"):
        if missing not in unknown_facts:
            unknown_facts.append(missing)

    return {
        "product": title or str(product.get("title", "")),
        "product_provider": provider,
        "product_score": product_score,
        "reliability_status": reliability_status,
        "decision": decision,
        "recommend_reel": recommend,
        "profile_coherence_status": profile_coherence_status,
        "visual_proof_basis": visual_proof_basis,
        "flow_prompt_ready": flow_prompt_ready,
        "research_required": ["Confirmar em referência oficial a operação visual do produto e o resultado que pode ser mostrado."],
        "selected_format": "ACHADINHO_RAPIDO",
        "format_reasoning": "Rascunho narrativo de problema e solução; a aprovação depende de confirmar a demonstração e o payoff visual.",
        "video_duration_target": "30–45 s",
        "flow_take_duration_target": "5–10 s",
        "scene_count": 5,
        "multi_take_justification": "Cinco takes sustentam problema, descoberta, demonstração, payoff e CTA; cada bloco avança o argumento e respeita a duração curta de geração do Flow.",
        "hook_type": "PERGUNTA" if hook.endswith("?") else "DESCOBERTA",
        "hook": hook,
        "script_structure": script_structure,
        "script_word_count": len(re.findall(r"\b[\wÀ-ÿ'-]+\b", final_script, flags=re.UNICODE)),
        "final_script": final_script,
        "scene_plan": [
            {
                "scene": 1, "timing": "0–6 s", "narrative_role": "HOOK_E_IDENTIFICACAO",
                "action": "Mostrar um problema doméstico reconhecível ainda a confirmar; Nina reage ao contexto, sem apresentar o produto como catálogo.",
                "framing": "Vertical 9:16, detalhe do problema e reação curta de Nina.",
                "environment_light": "Ambiente doméstico original e neutro, luz natural lateral suave, estética UGC fotorealista.",
                "audio_speech": hook, "flow_prompt": "", "fact_keys": [],
            },
            {
                "scene": 2, "timing": "6–13 s", "narrative_role": "DESCOBERTA_DO_PRODUTO",
                "action": "Revelar o produto exato da referência oficial em close e conectá-lo ao problema.",
                "framing": "Close funcional; produto domina o quadro e Nina permanece como curadora.",
                "environment_light": "Mesmo ambiente e continuidade de luz natural.",
                "audio_speech": f"Então presta atenção neste achado. O anúncio identifica este modelo como {label}.", "flow_prompt": "", "fact_keys": ["shopee_api_product_title"],
            },
            {
                "scene": 3, "timing": "13–23 s", "narrative_role": "DEMONSTRACAO",
                "action": "BLOQUEADO: definir a ação somente depois de confirmar operação e acessórios deste modelo.",
                "framing": "Close nas mãos e no mecanismo, com continuidade espacial.",
                "environment_light": "Mesmo ambiente; leitura clara do produto.",
                "audio_speech": "Explicação da ação será escrita após confirmação factual.", "flow_prompt": "", "fact_keys": [],
            },
            {
                "scene": 4, "timing": "23–34 s", "narrative_role": "PAYOFF_E_RESULTADO",
                "action": "BLOQUEADO: comparar o resultado no mesmo enquadramento sem inventar desempenho.",
                "framing": "Mesmo ângulo do problema inicial para comparação legível.",
                "environment_light": "Continuidade visual e luz natural.",
                "audio_speech": "Benefício e objeção serão definidos a partir da prova confirmada.", "flow_prompt": "", "fact_keys": [],
            },
            {
                "scene": 5, "timing": "34–42 s", "narrative_role": "CTA",
                "action": "Nina retoma o produto e encerra olhando para a câmera; o resultado permanece visível.",
                "framing": "Plano próximo com produto dominante.",
                "environment_light": "Mesmo ambiente e continuidade de luz.",
                "audio_speech": "Quer o link? Comenta QUERO.", "flow_prompt": "", "fact_keys": [],
            },
        ],
        "on_screen_text_start": on_screen_start,
        "on_screen_text_end": "COMENTA QUERO",
        "cta": "Quer o link? Comenta QUERO.",
        "caption": caption,
        "hashtags": hashtags,
        "cover_concept": {
            "cover_title": cover_title,
            "cover_subtitle": "OLHA ESTE ACHADO",
            "product_position": "Produto central em close, ocupando aproximadamente dois terços da capa.",
            "nina_position": "Nina lateral em segundo plano, apontando sem cobrir o produto.",
        },
        "flow_prompt": "",
        "negative_prompt": "CGI, 3D render, plastic skin, doll appearance, deformed hands, extra fingers, product deformation, floating objects, impossible motion, AI-looking background, unreadable text, logos not present in reference, invented buttons, invented accessories, invented rotation, unverified before-and-after result, exaggerated cleaning performance",
        "confirmed_facts": confirmed,
        "facts_used": ["shopee_api_product_title"],
        "fact_ledger": [{
            "claim": f"O título oficial identifica o produto como {title}.",
            "source_key": "shopee_api_product_title",
            "used_in": ["product", "final_script", "scene_plan", "caption", "cover_concept"],
        }],
        "unknown_facts": unknown_facts,
        "fact_safety": fact_safety,
        "nina_safety": "PASS",
        "posts_manual": True,
        "carousels_manual": True,
        "reels_creative_skill_ready": True,
        "reels_pipeline_integrated": bool(pipeline_integrated),
        "flow_integrated_with_skill": False,
        "flow_generations": 0,
    }
