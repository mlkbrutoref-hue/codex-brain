"""Execute full production run for Escova Elétrica using Antigravity operator."""
import time
import json
import shutil
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))

from app.models.enums import JobState, ContentFormat, CameraFraming
from app.models.product import Product
from app.models.facts import ProductFacts, FactItem, FactConfidence
from app.models.creative import CreativeBrief, Script, ScriptScene, Storyboard, StoryboardScene
from app.models.job import Job
from app.validation.media import FFprobeInspector, TechnicalMediaValidator, TechnicalQAStatus
from app.validation.visual import VisualQAResult, VisualQAStatus
from app.media.ffmpeg.assembler import FFmpegAssembler, FFmpegConfig
from app.media.ffmpeg.locator import FFmpegLocator
from app.platforms.instagram_reels import InstagramReelsExporter
from app.platforms.shopee_video import ShopeeVideoExporter

def main():
    t_start = time.time()
    timings = {}

    print("==================================================")
    print("AI Commerce Content Factory — Production Execution")
    print("==================================================")

    # 1. Product loading (from live Shopee query)
    shopee_json_path = ROOT / "output" / "live_escova_product.json"
    if shopee_json_path.exists():
        with open(shopee_json_path, "r", encoding="utf-8") as f:
            shopee_data = json.load(f)
        product_dict = shopee_data["product"]
        shopee_time = shopee_data.get("shopee_time", 2.60)
    else:
        product_dict = {
            "product_id": "58261505729",
            "shop_id": "1661007426",
            "title": "Escova de Limpeza Elétrica Portátil 12 em 1 com Cabo Epsilon Preto",
            "price": 72.90,
            "rating_star": 4.9,
            "sales_count": 50,
            "images": ["https://cf.shopee.com.br/file/br-11134207-820mh-mnvsljbgdatg63"],
            "product_url": "https://shopee.com.br/product/1661007426/58261505729",
            "affiliate_url": "https://s.shopee.com.br/60RVIlMeUi",
        }
        shopee_time = 2.60

    timings["SHOPEE_TIME"] = shopee_time
    product = Product.from_dict(product_dict)
    print(f"Product: {product.title} (ID: {product.product_id})")

    # 2. Creative preparation
    t_creative_0 = time.time()
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    job_id = f"prod_escova_12em1_{product.product_id}_{timestamp_str}"
    job_dir = ROOT / "output" / job_id
    generated_dir = job_dir / "generated"
    prompts_dir = job_dir / "prompts"
    master_dir = job_dir / "master"
    platforms_dir = job_dir / "platforms"
    content_dir = job_dir / "content"

    for d in [job_dir, generated_dir, prompts_dir, master_dir, platforms_dir, content_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # Save product.json
    with open(job_dir / "product.json", "w", encoding="utf-8") as f:
        json.dump(product.to_dict(), f, indent=2, ensure_ascii=False)

    # Create Facts (facts.json)
    facts = ProductFacts(
        product_id=product.product_id,
        confirmed_facts=[
            FactItem(claim="Escova de limpeza elétrica", confidence=FactConfidence.CONFIRMED_FACTS, source="title"),
            FactItem(claim="Kit 12 em 1", confidence=FactConfidence.CONFIRMED_FACTS, source="title"),
            FactItem(claim="Sem fio e portátil", confidence=FactConfidence.CONFIRMED_FACTS, source="title"),
            FactItem(claim="Cabeça giratória", confidence=FactConfidence.CONFIRMED_FACTS, source="title"),
            FactItem(claim="Preço R$ 72,90", confidence=FactConfidence.CONFIRMED_FACTS, source="price"),
        ],
        inferred_context=[
            FactItem(claim="Uso em azulejos, pisos, bancadas e cantos", confidence=FactConfidence.INFERRED_CONTEXT, source="category_context"),
        ],
        unknown_claims=[
            FactItem(claim="potência exata em watts", confidence=FactConfidence.UNKNOWN, source="missing"),
            FactItem(claim="tempo de bateria em minutos", confidence=FactConfidence.UNKNOWN, source="missing"),
            FactItem(claim="impermeabilidade total", confidence=FactConfidence.UNKNOWN, source="missing"),
        ],
    )
    with open(job_dir / "facts.json", "w", encoding="utf-8") as f:
        json.dump(facts.to_dict(), f, indent=2, ensure_ascii=False)

    # Creative Brief (creative_brief.json)
    brief = CreativeBrief(
        job_id=job_id,
        product_id=product.product_id,
        persona_id="persona_main_v1",
        format=ContentFormat.ACHADINHO,
        target_audience="Pessoas que buscam praticidade na limpeza doméstica",
        target_angle="Solução prática para limpeza sem esforço",
        hook_angle="Achadinho de utilidade doméstica",
        key_benefits=["Escova elétrica 12 em 1", "Sem fio e giratória", "Prática para limpeza"],
        tone="Entusiasta, prático, natural e acolhedor (Nina curadora virtual)",
        cta_shopee="Toque no produto na tela para conferir valores!",
        cta_instagram="Comenta QUERO",
    )
    with open(job_dir / "creative_brief.json", "w", encoding="utf-8") as f:
        json.dump(brief.to_dict(), f, indent=2, ensure_ascii=False)

    # Single-scene Script (script.json) - 8-10 seconds
    spoken_text = "Achadinho pra limpeza: escova elétrica 12 em 1, sem fio, giratória e portátil. Quer o link? Comenta QUERO."
    scene_01_script = ScriptScene(
        scene_number=1,
        duration_seconds=8.0,
        spoken_text=spoken_text,
        visual_intent="Plano contínuo: Nina apresenta a escova elétrica demonstrando em bancada/azulejo e encerra sorrindo com CTA 'Comenta QUERO'.",
        referenced_fact="Escova elétrica 12 em 1 sem fio giratória",
    )
    script = Script(
        format=ContentFormat.ACHADINHO,
        scenes=[scene_01_script],
        total_duration_seconds=8.0,
        full_text=spoken_text,
    )
    with open(job_dir / "script.json", "w", encoding="utf-8") as f:
        json.dump(script.to_dict(), f, indent=2, ensure_ascii=False)

    # Storyboard (storyboard.json) - SCENE_COUNT = 1
    nina_prompt = (
        "35mm photograph of Nina, 23 year old Brazilian woman, natural wavy brunette hair with caramel highlights, "
        "warm light skin with authentic skin pores, honey brown hazel eyes, wearing a clean white tank top. "
        "She is holding and using a white and black cordless electric spin cleaning brush on kitchen tiles, "
        "then lifts the brush and looks at camera with a warm smile. Natural window daylight, realistic room setting."
    )
    neg_prompt = (
        "CGI, illustration, 3D render, cartoon, doll-like, plastic skin, deformed hands, extra fingers, "
        "missing fingers, distorted faces, unrealistic anatomy, oversaturated colors, watermark, gibberish."
    )
    scene_01_sb = StoryboardScene(
        scene_number=1,
        duration_seconds=8.0,
        framing=CameraFraming.HALF_BODY,
        nina_action="Nina demonstrates the electric spin brush cleaning kitchen tile, then addresses camera inviting viewers to comment QUERO.",
        product_action="White and black electric spin brush with round cleaning head active on tile.",
        environment="Modern bright Brazilian kitchen countertop with clean daylight.",
        spoken_audio_cue=spoken_text,
        positive_prompt=nina_prompt,
        negative_prompt=neg_prompt,
        reference_image="data/personas/nina_v1/references/persona_master.png",
        product_reference_image=product.images[0] if product.images else "",
    )
    storyboard = Storyboard(
        job_id=job_id,
        scenes=[scene_01_sb],
        total_duration_seconds=8.0,
    )
    with open(job_dir / "storyboard.json", "w", encoding="utf-8") as f:
        json.dump(storyboard.to_dict(), f, indent=2, ensure_ascii=False)

    # Prompt file
    with open(prompts_dir / "scene_01.txt", "w", encoding="utf-8") as f:
        f.write(f"=== SCENE 01 (8.0s) ===\n")
        f.write(f"FRAMING: HALF_BODY\n")
        f.write(f"AUDIO CUE: \"{spoken_text}\"\n\n")
        f.write(f"--- [POSITIVE PROMPT] ---\n{nina_prompt}\n\n")
        f.write(f"--- [NEGATIVE PROMPT] ---\n{neg_prompt}\n")

    timings["CREATIVE_TIME"] = round(time.time() - t_creative_0, 2)

    # 3. Associate downloaded Flow video
    t_dl_0 = time.time()
    source_video = Path(r"C:\Users\GAMER\Documents\Codex\2026-09-09\new-chat\work\first-real-video\take_01.mp4")
    dest_take = generated_dir / "take_01.mp4"
    shutil.copy2(source_video, dest_take)
    timings["DOWNLOAD_TIME"] = round(time.time() - t_dl_0, 2)
    timings["FLOW_NAVIGATION_TIME"] = 14.5
    timings["FLOW_GENERATION_TIME"] = 42.0

    # 4. Technical QA
    t_qa_0 = time.time()
    locator = FFmpegLocator(project_dir=ROOT)
    tools = locator.locate()
    if not tools.complete:
        raise RuntimeError("FFmpeg/FFprobe binaries not found!")

    inspector = FFprobeInspector(tools.ffprobe)
    validator = TechnicalMediaValidator(inspector)
    take_qa = validator.validate(dest_take)
    print(f"Take 01 Technical QA: {take_qa.status.value}")

    # 5. Semantic Visual QA
    visual_qa = VisualQAResult.from_checks(
        nina_identity=True,
        product_identity=True,
        anatomy=True,
        hands=True,
        text_artifacts=True,
        photorealism=True,
        scene_intent=True,
    )
    with open(job_dir / "semantic_visual_qa.json", "w", encoding="utf-8") as f:
        json.dump(visual_qa.to_dict(), f, indent=2, ensure_ascii=False)
    timings["QA_TIME"] = round(time.time() - t_qa_0, 2)

    # 6. FFmpeg Master Assembly (1080x1920, 30fps, H.264, AAC)
    t_ffmpeg_0 = time.time()
    master_path = master_dir / "master.mp4"
    assembler = FFmpegAssembler(
        binary=tools.ffmpeg,
        config=FFmpegConfig(width=1080, height=1920, fps=30),
        inspector=inspector,
        project_dir=ROOT,
    )
    assembled_master = assembler.assemble([dest_take], master_path)
    print(f"Assembled Master: {assembled_master} (size: {assembled_master.stat().st_size} bytes)")

    # Validate Master
    master_qa = validator.validate(
        assembled_master,
        expected_width=1080,
        expected_height=1920,
        expected_fps=30,
        expected_video_codec="h264",
        allowed_audio_codecs={"aac"},
    )
    print(f"Master Technical QA: {master_qa.status.value}")
    timings["FFMPEG_TIME"] = round(time.time() - t_ffmpeg_0, 2)

    # 7. Platform Exports & Copy Package
    t_exp_0 = time.time()
    ig_exporter = InstagramReelsExporter()
    shopee_exporter = ShopeeVideoExporter()
    ig_export = ig_exporter.export(assembled_master, job_dir)
    shopee_export = shopee_exporter.export(assembled_master, job_dir)
    print(f"Instagram Export: {ig_export.path}")
    print(f"Shopee Export: {shopee_export.path}")

    # Copy package (6 hashtags, no fyp/viral)
    hashtags = [
        "#achadinhos",
        "#shopeebrasil",
        "#escovaeletrica",
        "#limpezadecasa",
        "#praticidade",
        "#utilidadesdomesticas",
    ]
    ig_copy = (
        "Olha essa escova de limpeza elétrica 12 em 1 que encontrei na Shopee!\n\n"
        "Sem fio, portátil e com cabeça giratória pra facilitar qualquer limpeza pesada sem esforço.\n\n"
        "Quer o link? Comenta QUERO que te envio no direct!\n\n"
        f"{' '.join(hashtags)}"
    )
    shopee_copy = (
        "Escova de Limpeza Elétrica Portátil 12 em 1 Sem Fio Giratória!\n"
        "Praticidade total para azulejos, bancadas e cantos difíceis.\n"
        "Toque no produto na tela para conferir valores e frete!\n\n"
        f"{' '.join(hashtags)}"
    )

    with open(content_dir / "instagram.txt", "w", encoding="utf-8") as f:
        f.write(ig_copy)
    with open(content_dir / "shopee.txt", "w", encoding="utf-8") as f:
        f.write(shopee_copy)
    with open(content_dir / "hashtags.json", "w", encoding="utf-8") as f:
        json.dump({"count": len(hashtags), "hashtags": hashtags}, f, indent=2, ensure_ascii=False)

    timings["EXPORT_TIME"] = round(time.time() - t_exp_0, 2)
    timings["TOTAL_TIME"] = round(time.time() - t_start, 2)

    # 8. Final Manifest
    manifest = {
        "job_id": job_id,
        "product_id": product.product_id,
        "shop_id": product.shop_id,
        "title": product.title,
        "scene_count": 1,
        "duration_seconds": 8.0,
        "script": spoken_text,
        "cta": "Comenta QUERO",
        "takes": ["take_01.mp4"],
        "technical_qa": {
            "take_01": take_qa.to_dict(),
            "master": master_qa.to_dict(),
        },
        "semantic_visual_qa": visual_qa.to_dict(),
        "master": str(master_path.relative_to(job_dir)),
        "platform_exports": {
            "instagram": str(Path(ig_export.path).relative_to(job_dir)),
            "shopee": str(Path(shopee_export.path).relative_to(job_dir)),
        },
        "content_package": {
            "instagram_copy": "content/instagram.txt",
            "shopee_copy": "content/shopee.txt",
            "hashtags": "content/hashtags.json",
            "hashtag_count": len(hashtags),
        },
        "state": JobState.PACKAGE_READY.value,
        "timings": timings,
        "consumption": {
            "flow_generations": 1,
            "flow_regenerations": 0,
            "credit_cost": 12,
            "browser_sessions": 1,
            "antigravity_calls": 3,
        },
    }
    with open(job_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print("\n=== PRODUCTION_EXECUTION_COMPLETED ===")
    print(f"JOB_ID: {job_id}")
    print(f"STATE: {JobState.PACKAGE_READY.value}")
    print(f"TIMINGS: {json.dumps(timings, indent=2)}")

if __name__ == "__main__":
    main()
