"""Executes and validates an End-to-End pipeline job using a REAL Shopee Affiliate API product."""
import sys
import json
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from app.providers.shopee.live import ShopeeLiveProductProvider
from app.orchestration.pipeline import PipelineOrchestrator
from app.models.enums import ContentFormat, JobState


def run_live_pipeline():
    print("==================================================")
    print("AI Commerce Content Factory — Pipeline LIVE Shopee")
    print("==================================================")

    live_provider = ShopeeLiveProductProvider()
    print("1. Consultando Shopee Affiliate API ao vivo para selecionar 1 produto real...")
    
    # Query live offers dynamically (no hardcoded permanent IDs)
    live_products = live_provider.search_products("decoracao casa", limit=3)
    if not live_products:
        print("ERRO: Nenhum produto retornado pela API da Shopee.")
        return None

    # Pick the first real product
    real_product = live_products[0]
    target_id = f"{real_product.product_id}_{real_product.shop_id}"

    print(f"   Produto Real Selecionado da API:")
    print(f"   - Item ID: {real_product.product_id}")
    print(f"   - Shop ID: {real_product.shop_id}")
    print(f"   - Título: {real_product.title}")
    print(f"   - Preço: {f'R$ {real_product.price:.2f}' if real_product.price is not None else 'não informado'}")
    print(f"   - Link Afiliado: {'SIM' if real_product.affiliate_url else 'NÃO'}")
    print(f"   - Imagens: {len(real_product.images)}")

    print("\n2. Executando Pipeline com SHOPEE_PROVIDER=live...")
    orchestrator = PipelineOrchestrator(
        base_dir=project_root,
        product_provider=live_provider,
    )

    job = orchestrator.run_up_to_prompts(
        product_id=target_id,
        format_type=ContentFormat.ACHADINHO,
    )

    print(f"   Job Concluído no estado: {job.state.value}")
    print(f"   Diretório de Output: {job.output_dir}")

    # 3. Validações estritas de conformidade
    print("\n3. Validando artefatos gerados contra regras contratuais...")
    job_dir = Path(job.output_dir)

    # Validate generated files
    required_files = [
        "product.json",
        "facts.json",
        "creative_brief.json",
        "script.json",
        "storyboard.json",
        "manifest.json",
    ]
    for rf in required_files:
        f_path = job_dir / rf
        assert f_path.exists() and f_path.stat().st_size > 0, f"Arquivo {rf} não foi gerado ou está vazio!"
        print(f"   - {rf}: OK ({f_path.stat().st_size} bytes)")

    # Validate prompts
    prompt_files = list((job_dir / "prompts").glob("scene_*.txt"))
    assert len(prompt_files) >= 4, f"Esperado pelo menos 4 prompts, encontrado {len(prompt_files)}"
    print(f"   - prompts/ ({len(prompt_files)} arquivos): OK")

    # Inspect product.json
    with open(job_dir / "product.json", "r", encoding="utf-8") as f:
        prod_data = json.load(f)
    assert prod_data["product_id"] == real_product.product_id, "Product ID não corresponde ao item retornado da API!"
    assert prod_data["title"] == real_product.title, "Título diverge da API!"
    assert float(prod_data["price"]) == float(real_product.price), "Preço diverge da API!"
    print("   - Integridade de product.json (Preço, ID e Título): OK")

    # Inspect script.json
    with open(job_dir / "script.json", "r", encoding="utf-8") as f:
        script_data = json.load(f)
    script_full = script_data["full_text"].lower()

    # Ensure no leakage of food processor / garlic / 250ml
    forbidden_terms = ["alho", "tempero", "250ml", "triturador", "processador", "lâminas de aço", "corre antes que acabe", "viral"]
    for ft in forbidden_terms:
        assert ft not in script_full, f"Termo proibido/vazado '{ft}' encontrado no roteiro!"
    print("   - Roteiro livre de termos vazados ou hardcoded: OK")

    # Inspect manifest.json
    with open(job_dir / "manifest.json", "r", encoding="utf-8") as f:
        manifest_data = json.load(f)
    assert manifest_data["state"] == JobState.PROMPTS_READY.value
    assert manifest_data["product_id"] == real_product.product_id

    print("\n--- FASE A CONCLUÍDA COM SUCESSO ---")
    print(f"LIVE_PIPELINE_PRODUCT_ID={real_product.product_id}")
    print(f"LIVE_PIPELINE_SHOP_ID={real_product.shop_id}")
    print(f"LIVE_PIPELINE_TITLE={real_product.title}")
    print(f"LIVE_PIPELINE_JOB_ID={job.job_id}")

    return {
        "product_id": real_product.product_id,
        "shop_id": real_product.shop_id,
        "title": real_product.title,
        "job_id": job.job_id,
    }


if __name__ == "__main__":
    res = run_live_pipeline()
    if not res:
        sys.exit(1)
