"""Creative brief generator tailored for Nina across any product category."""
from typing import Optional
from app.models.product import Product
from app.models.facts import ProductFacts
from app.models.creative import CreativeBrief
from app.models.enums import ContentFormat


class BriefGenerator:
    """Generates structured creative briefs strictly aligning with verified product facts."""

    def generate(
        self,
        job_id: str,
        product: Product,
        facts: ProductFacts,
        format_type: ContentFormat = ContentFormat.ACHADINHO,
    ) -> CreativeBrief:
        """Constructs a creative brief dynamically for the requested format."""
        # Select confirmed benefits only
        key_benefits = [
            f.claim for f in facts.confirmed_facts
            if not f.source.startswith("shopee_api_price") and not f.source.startswith("shopee_api_discount")
        ][:4]

        # Keep audience language descriptive; do not convert category inference into a benefit claim.
        target_audience = (
            f"Pessoas interessadas em itens como {product.title[:45]} e que desejam conferir os detalhes do anúncio"
        )

        # CTAs strictly factual (no false scarcity)
        if product.discount_percentage is not None and product.discount_percentage > 0:
            cta_shopee = f"Clica na sacola laranja aqui embaixo pra conferir com {product.discount_percentage:.0f}% de desconto!"
        else:
            cta_shopee = "Clica na sacola laranja aqui embaixo pra conferir todos os detalhes!"

        cta_instagram = "Confira os detalhes no link indicado."

        if format_type == ContentFormat.ACHADINHO:
            hook_angle = "Descoberta e conferência dos detalhes do anúncio"
            price_context = (f" e preço atual de R$ {product.price:.2f}"
                             if product.price is not None else "")
            target_angle = f"Apresentação factual de {product.title[:30]}{price_context}"
        elif format_type == ContentFormat.PROBLEMA_SOLUTION:
            hook_angle = "Apresentação de uma opção relacionada a uma necessidade da rotina"
            target_angle = f"Conferência factual da proposta de {product.title[:30]}"
        else:
            hook_angle = f"Conferência dos dados e imagens de {product.title[:30]}"
            target_angle = "Apresentação objetiva do que está confirmado no anúncio"

        return CreativeBrief(
            job_id=job_id,
            product_id=product.product_id,
            persona_id="persona_main_v1",
            format=format_type,
            target_audience=target_audience,
            target_angle=target_angle,
            hook_angle=hook_angle,
            key_benefits=key_benefits,
            tone="informal, natural, amiga que compartilha achadinhos úteis sem forçar a barra",
            cta_shopee=cta_shopee,
            cta_instagram=cta_instagram,
        )
