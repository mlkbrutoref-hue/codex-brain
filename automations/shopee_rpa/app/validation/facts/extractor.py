"""Fact extractor enforcing strict Fact Safety rules across ANY product category."""
import re
from typing import List, Optional
from app.models.product import Product
from app.models.facts import FactItem, ProductFacts
from app.models.enums import FactConfidence


class FactExtractor:
    """Extracts confirmed facts, inferred lifestyle context and flags unverified claims generically."""

    SENSITIVE_UNVERIFIED_PATTERNS = [
        (r"\b(à\s*prova\s*d['\w]+água|impermeável|waterproof)\b", "resistência à água/impermeabilidade"),
        (r"\b(garantia\s*vitalícia|dura\s*para\s*sempre)\b", "garantia vitalícia"),
        (r"\b(cura|elimina\s*100%|milagroso|rejuvenesce)\b", "alegações médicas ou milagrosas"),
        (r"\b(silencioso\s*0db|ruído\s*zero)\b", "ausência total de ruído"),
        (r"\b(bateria\s*infinita|nunca\s*descarrega)\b", "bateria infinita"),
        (r"\b(corre\s*antes\s*que\s*acabe|últimas\s*unidades|vai\s*esgotar)\b", "falsa escassez ou urgência"),
        (r"\b(mais\s*vendido|viral\s*da\s*internet|sucesso\s*absoluto)\b", "alegação de ranking ou viralidade sem evidência"),
    ]

    def extract(self, product: Product) -> ProductFacts:
        """Categorizes product information strictly based on confirmed data."""
        confirmed: List[FactItem] = []
        inferred: List[FactItem] = []
        unknown: List[FactItem] = []

        # 1. Price (Always confirmed if positive)
        if product.price and product.price > 0:
            confirmed.append(
                FactItem(
                    claim=f"Preço atual de R$ {product.price:.2f}",
                    confidence=FactConfidence.CONFIRMED_FACTS,
                    source="shopee_api_price",
                    verifiable=True,
                )
            )

        # 2. Discount (ONLY if present and > 0)
        if product.discount_percentage is not None and product.discount_percentage > 0:
            confirmed.append(
                FactItem(
                    claim=f"Desconto de {product.discount_percentage:.0f}% ativo no anúncio",
                    confidence=FactConfidence.CONFIRMED_FACTS,
                    source="shopee_api_discount",
                    verifiable=True,
                )
            )

        # 3. Sales count (ONLY if present and verified)
        if product.sales_count is not None and product.sales_count > 0:
            confirmed.append(
                FactItem(
                    claim=f"{product.sales_count} unidades vendidas",
                    confidence=FactConfidence.CONFIRMED_FACTS,
                    source="shopee_api_sales",
                    verifiable=True,
                )
            )

        # 4. Rating (ONLY if present and verified)
        if product.rating_star is not None and product.rating_star > 0:
            confirmed.append(
                FactItem(
                    claim=f"Avaliação média de {product.rating_star:.1f} estrelas",
                    confidence=FactConfidence.CONFIRMED_FACTS,
                    source="shopee_api_rating",
                    verifiable=True,
                )
            )

        # 5. Attributes explicitly listed in product catalog
        for k, v in (product.attributes or {}).items():
            if v and str(v).strip():
                confirmed.append(
                    FactItem(
                        claim=f"{k}: {v}",
                        confidence=FactConfidence.CONFIRMED_FACTS,
                        source=f"shopee_attribute_{k.lower().replace(' ', '_')}",
                        verifiable=True,
                    )
                )

        # 6. Physical properties from title/description (generic, not domain-restricted)
        text_corpus = f"{product.title} {product.description or ''}"

        # Dimensions pattern
        dim_match = re.search(r"\b(\d+\s*(?:x|X)\s*\d+(?:\s*(?:x|X)\s*\d+)?\s*(?:cm|mm|m))\b", text_corpus)
        if dim_match and not any("dimens" in f.claim.lower() for f in confirmed):
            confirmed.append(
                FactItem(
                    claim=f"Dimensões de {dim_match.group(0)}",
                    confidence=FactConfidence.CONFIRMED_FACTS,
                    source="shopee_description_dimensions",
                    verifiable=True,
                )
            )

        # Voltage pattern
        volt_match = re.search(r"\b(110v|220v|bivolt|5v|12v)\b", text_corpus, re.IGNORECASE)
        if volt_match and not any("voltagem" in f.claim.lower() or "tensão" in f.claim.lower() for f in confirmed):
            confirmed.append(
                FactItem(
                    claim=f"Tensão/Voltagem: {volt_match.group(0).upper()}",
                    confidence=FactConfidence.CONFIRMED_FACTS,
                    source="shopee_description_voltage",
                    verifiable=True,
                )
            )

        # 7. Category-aware Inferred Context (strictly non-hardcoded)
        cat_lower = f"{product.category} {product.title}".lower()
        if any(w in cat_lower for w in ["fone", "bluetooth", "audio", "som", "eletrônic", "gadget", "smart"]):
            inferred.append(
                FactItem(
                    claim="Contexto criativo sugerido: rotina com áudio ou eletrônicos",
                    confidence=FactConfidence.INFERRED_CONTEXT,
                    source="lifestyle_inferred_audio",
                    verifiable=False,
                )
            )
        elif any(w in cat_lower for w in ["almofada", "decoraç", "sofá", "sala", "cama", "quarto", "cortina"]):
            inferred.append(
                FactItem(
                    claim="Contexto criativo sugerido: ambiente de casa ou decoração",
                    confidence=FactConfidence.INFERRED_CONTEXT,
                    source="lifestyle_inferred_decor",
                    verifiable=False,
                )
            )
        elif any(w in cat_lower for w in ["cozinha", "culinária", "panela", "alimento", "processador", "liquidificador"]):
            inferred.append(
                FactItem(
                    claim="Contexto criativo sugerido: ambiente de cozinha",
                    confidence=FactConfidence.INFERRED_CONTEXT,
                    source="lifestyle_inferred_kitchen",
                    verifiable=False,
                )
            )
        else:
            inferred.append(
                FactItem(
                    claim="Contexto criativo sugerido: rotina cotidiana",
                    confidence=FactConfidence.INFERRED_CONTEXT,
                    source="lifestyle_inferred_general",
                    verifiable=False,
                )
            )

        # 8. Flag UNKNOWN claims that are NOT substantiated
        for pattern, label in self.SENSITIVE_UNVERIFIED_PATTERNS:
            found_in_confirmed = any(re.search(pattern, f.claim, re.IGNORECASE) for f in confirmed)
            if not found_in_confirmed:
                unknown.append(
                    FactItem(
                        claim=f"Não há confirmação oficial de '{label}'",
                        confidence=FactConfidence.UNKNOWN,
                        source="safety_audit_unverified",
                        verifiable=False,
                    )
                )

        return ProductFacts(
            product_id=product.product_id,
            confirmed_facts=confirmed,
            inferred_context=inferred,
            unknown_claims=unknown,
        )
