"""CLI script to execute a pilot generation job for Nina."""
import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from app.orchestration.pipeline import PipelineOrchestrator
from app.models.enums import ContentFormat


def main():
    print("==================================================")
    print("AI Commerce Content Factory — Executando Job Piloto")
    print("==================================================")

    orchestrator = PipelineOrchestrator(base_dir=project_root)

    product_id = "sample_product"
    format_type = ContentFormat.ACHADINHO

    print(f"Produto Alvo: {product_id}")
    print(f"Formato: {format_type.value}")
    print("Persona: Nina (persona_main_v1)")

    job = orchestrator.run_up_to_prompts(
        product_id=product_id,
        format_type=format_type,
    )

    print("\n--- JOB CONCLUÍDO COM SUCESSO ---")
    print(f"Job ID: {job.job_id}")
    print(f"Estado Final: {job.state.value}")
    print(f"Diretório de Saída: {job.output_dir}")
    print(f"Arquivos de Prompt Gerados: {len(job.metadata.get('prompt_files', []))}")
    print("\nPróximo passo: Alimentar o Google Flow ou depositar mídias em:")
    print(f"{Path(job.output_dir) / 'generated'}")


if __name__ == "__main__":
    main()