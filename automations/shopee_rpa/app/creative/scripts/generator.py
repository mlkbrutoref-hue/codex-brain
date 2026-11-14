"""Script generator producing dynamic, factual pt-BR dialogue for Nina across any category."""
from typing import List
from app.models.product import Product
from app.models.facts import ProductFacts
from app.models.creative import CreativeBrief, Script, ScriptScene
from app.creative.hooks.bank import HookBank


class ScriptGenerator:
    """Produces authentic lifestyle scripts built strictly from confirmed product facts."""

    WORDS_PER_SECOND = 2.6

    def generate(self, brief: CreativeBrief, product: Product, facts: ProductFacts) -> Script:
        """Generates scene-by-scene script dynamically without hardcoded domain fallbacks."""
        scenes: List[ScriptScene] = []
        fmt = brief.format

        # 1. Opening Hook Scene (3-5s)
        hook_text = HookBank.get_hook(fmt, 0)
        scenes.append(
            ScriptScene(
                scene_number=1,
                duration_seconds=round(len(hook_text.split()) / self.WORDS_PER_SECOND, 1),
                spoken_text=hook_text,
                visual_intent=f"Nina apresentando {product.title[:35]} com expressão simpática e olhar direto na câmera.",
                referenced_fact="hook_lifestyle",
            )
        )

        # 2. Demonstration & Physical Attributes Scene (5-8s)
        # Pull 1-2 confirmed attributes if available
        attr_items = [
            f"{k.lower()} {v}" for k, v in product.attributes.items()
            if v and str(v).strip()
        ] if product.attributes else []
        if attr_items:
            selected_attrs = " e ".join(attr_items[:2])
            demo_text = f"Dá uma olhada nos detalhes confirmados no anúncio: {selected_attrs}."
            ref_fact = f"Atributos confirmados: {selected_attrs}"
        else:
            demo_text = "Confira o formato e os detalhes visíveis nas imagens oficiais do anúncio."
            ref_fact = "Imagem oficial do produto"

        scenes.append(
            ScriptScene(
                scene_number=2,
                duration_seconds=round(len(demo_text.split()) / self.WORDS_PER_SECOND, 1),
                spoken_text=demo_text,
                visual_intent=f"Tomada em plano detalhe mostrando as características e acabamento de {product.title[:30]}.",
                referenced_fact=ref_fact,
            )
        )

        # 3. Verified Price & Terms Scene (5-7s)
        price_parts = ([f"O valor atual tá saindo por R$ {product.price:.2f}"]
                       if product.price is not None else ["Confira o preço atual no anúncio"])
        if product.discount_percentage is not None and product.discount_percentage > 0:
            price_parts.append(f"com {product.discount_percentage:.0f}% de desconto")
        if product.rating_star is not None and product.rating_star >= 4.5:
            price_parts.append(f"e avaliação de {product.rating_star:.1f} estrelas")
        
        price_text = f"{', '.join(price_parts)} na Shopee!"
        scenes.append(
            ScriptScene(
                scene_number=3,
                duration_seconds=round(len(price_text.split()) / self.WORDS_PER_SECOND, 1),
                spoken_text=price_text,
                visual_intent=f"Nina apresentando {product.title[:30]} ao lado da imagem oficial de referência.",
                referenced_fact=(f"Preço confirmado R$ {product.price:.2f}"
                                 if product.price is not None else "Preço não informado"),
            )
        )

        # 4. Factual Closing CTA Scene (3-5s) - NO FALSE URGENCY
        has_link = bool(product.affiliate_url or product.product_url)
        cta_text = (
            "O link do anúncio está aqui embaixo para você conferir os detalhes!"
            if has_link else
            "Confira os detalhes disponíveis no anúncio antes de decidir!"
        )
        scenes.append(
            ScriptScene(
                scene_number=4,
                duration_seconds=round(len(cta_text.split()) / self.WORDS_PER_SECOND, 1),
                spoken_text=cta_text,
                visual_intent=(
                    "Nina apontando para a área do link com expressão amigável de curadora virtual."
                    if has_link else
                    "Nina encerrando a apresentação com expressão amigável de curadora virtual."
                ),
                referenced_fact="call_to_action_factual",
            )
        )

        total_duration = sum(s.duration_seconds for s in scenes)
        full_text = " ".join(s.spoken_text for s in scenes)

        return Script(
            format=fmt,
            scenes=scenes,
            total_duration_seconds=round(total_duration, 1),
            full_text=full_text,
        )
