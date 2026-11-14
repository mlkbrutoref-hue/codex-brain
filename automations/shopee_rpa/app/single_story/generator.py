"""Deterministic generator for one independent 9:16 product Story."""

from __future__ import annotations
from app.creative.proportion_policy import proportion_rules, negative_constraints

import json
import re
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from app.single_story.models import (
    SingleStoryCreativePackage,
    SingleStoryRequest,
    StoryType,
)
from app.single_story.validator import SingleStoryValidator


class SingleStoryGenerator:
    """Creates a provider-independent creative and image-generation prompt."""

    NAME = "NINA_SINGLE_STORY_GENERATOR"
    VERSION = "1.0.0"
    STATUS = "READY"
    CANONICAL_NINA_REFERENCES = (
        "data/personas/nina_v1/references/persona_master.png",
        "data/personas/nina_v1/references/nina_360_master.png",
    )
    CANONICAL_STORY_STYLE_REFERENCE = (
        "data/brands/nina_v1/references/story_style_master.png"
    )

    _BENEFIT_WORDS = {
        "ajuda", "facilita", "pratico", "pratica", "dosa", "organiza",
        "protege", "limpa", "remove", "reduz", "evita", "compacto",
        "dobravel", "enrola", "economiza", "resistente", "2 em 1",
    }
    _USE_WORDS = {
        "aplica", "aplicar", "encaixa", "passa", "usar", "uso",
        "sobre a", "durante", "pressiona", "gira", "abre", "fecha",
    }
    _AESTHETIC_WORDS = {
        "design", "acabamento", "cor", "textura", "brilho", "decorativo",
        "transparente", "perolado", "minimalista", "estetica",
    }

    def __init__(self, base_dir: Optional[Path] = None) -> None:
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).resolve().parents[2]
        self.validator = SingleStoryValidator()

    def generate(self, request: SingleStoryRequest) -> SingleStoryCreativePackage:
        story_type, rationale = self._select_story_type(request)
        product_refs = [str(path) for path in request.product_reference_paths]
        style_refs = self._story_style_references(request)
        persona_refs = self._persona_references(request)
        headline = self._headline(request, story_type)
        supporting = request.confirmed_facts[0]
        benefit = request.confirmed_facts[1] if len(request.confirmed_facts) > 1 else ""
        cta = self._cta(request, story_type)
        concept = self._concept(request, story_type)
        colors = self._color_direction(request)
        composition = self._composition(story_type)
        scene = self._scene(request, story_type)
        realism = self._realism_notes(request, persona_refs)
        negative = self._negative_prompt(request)
        blockers = self._prompt_blockers(request, product_refs, style_refs, persona_refs)
        prompt_ready = not blockers
        trend_application = self._trend_application(request)
        style_application = self._style_reference_application(request)
        final_prompt = self._build_prompt(
            request=request,
            story_type=story_type,
            headline=headline,
            supporting=supporting,
            benefit=benefit,
            cta=cta,
            scene=scene,
            composition=composition,
            colors=colors,
            realism=realism,
            negative=negative,
            product_refs=product_refs,
            style_refs=style_refs,
            persona_refs=persona_refs,
            trend_application=trend_application,
            style_application=style_application,
        )
        package = SingleStoryCreativePackage(
            generator_name=self.NAME,
            generator_version=self.VERSION,
            generator_status=self.STATUS,
            product_name=request.product_name,
            confirmed_facts=list(request.confirmed_facts),
            story_type=story_type.value,
            concept_title=concept["title"],
            visual_concept=concept["visual"],
            scene_description=scene,
            composition_direction=composition,
            product_role=concept["product_role"],
            text_hierarchy={
                "primary": "headline; largest type; maximum two short lines",
                "secondary": "one confirmed fact; compact and highly legible",
                "tertiary": "optional second confirmed fact",
                "cta": "small pill or footer label; visually lighter than headline",
            },
            headline=headline,
            supporting_text=supporting,
            benefit_text=benefit,
            cta_text=cta,
            decorative_elements=self._decorative_elements(story_type),
            mood_keywords=["real", "natural", "clean", "warm", "editorial social"],
            color_direction=colors,
            realism_notes=realism,
            negative_prompt=negative,
            final_image_prompt=final_prompt,
            format_spec={
                "platform": "Instagram Stories",
                "aspect_ratio": "9:16",
                "width": 1080,
                "height": 1920,
                "artifact_count": 1,
                "standalone": True,
                "sequence_position": None,
                "safe_zone_rule": (
                    "Keep headline, product and CTA away from top and bottom interface overlays; "
                    "verify in the destination platform preview."
                ),
                "reuse": ["TikTok vertical still", "Reels cover", "other 9:16 placements"],
            },
            selection_rationale=rationale,
            trend_application=trend_application,
            style_reference_application=style_application,
            product_reference_paths=product_refs,
            style_reference_paths=style_refs,
            persona_reference_paths=persona_refs,
            fact_usage={
                "supporting_text": "confirmed_facts[0] verbatim",
                "benefit_text": "confirmed_facts[1] verbatim" if benefit else "not used",
                "headline": "neutral creative framing; no objective product claim added",
                "cta": "navigation or conversation action; no scarcity claim",
            },
            copy_variants=self._copy_variants(request, story_type),
            caption=self._caption(request, supporting) if request.caption_requested else "",
            hashtags=self._hashtags(request) if request.hashtags_requested else [],
            cover_logic=(
                "If reused as a cover, keep the same hero crop and headline; remove the CTA pill."
            ),
            final_image_prompt_ready=prompt_ready,
            prompt_blockers=blockers,
            validation_status="PENDING",
            validation_errors=[],
        )
        errors = self.validator.validate(package)
        package.validation_errors = errors
        package.validation_status = "PASS" if not errors else "FAIL"
        if errors:
            package.final_image_prompt_ready = False
        return package

    def generate_to_file(self, request: SingleStoryRequest, output_path: Path) -> SingleStoryCreativePackage:
        package = self.generate(request)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(package.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return package

    def generate_from_product(
        self,
        product: "Product",
        facts: "ProductFacts",
        *,
        story_type: StoryType = StoryType.AUTO,
        content_goal: str = "DISCOVERY",
        product_reference_paths: Optional[List[str]] = None,
        use_nina: bool = False,
        cta_text: str = "",
    ) -> SingleStoryCreativePackage:
        """Bridge existing Product/ProductFacts contracts without joining the video pipeline."""
        request = SingleStoryRequest(
            product_id=product.product_id,
            product_name=product.title,
            product_category=product.category or "",
            confirmed_facts=[item.claim for item in facts.confirmed_facts if item.claim.strip()],
            story_type=story_type,
            content_goal=content_goal,
            product_reference_paths=(
                list(product_reference_paths)
                if product_reference_paths is not None
                else list(product.images)
            ),
            use_nina=use_nina,
            cta_text=cta_text,
        )
        return self.generate(request)

    def _select_story_type(self, request: SingleStoryRequest) -> Tuple[StoryType, str]:
        if request.story_type != StoryType.AUTO:
            return request.story_type, "Tipo definido explicitamente no pedido."
        text = self._fold(" ".join(request.confirmed_facts + request.visual_evidence))
        benefit_hits = sum(1 for word in self._BENEFIT_WORDS if word in text)
        scores: Dict[StoryType, int] = {
            StoryType.PRODUCT_HIGHLIGHT: 1,
            StoryType.BENEFIT: benefit_hits * 2 + (2 if benefit_hits else 0),
            StoryType.USE_LIFESTYLE: sum(2 for word in self._USE_WORDS if word in text),
            StoryType.AESTHETIC_EMOTIONAL: sum(2 for word in self._AESTHETIC_WORDS if word in text),
            StoryType.LIGHT_CTA: 0,
        }
        if request.visual_evidence:
            scores[StoryType.USE_LIFESTYLE] += 1
        if request.content_goal == "CONVERSION" and request.cta_text.strip():
            scores[StoryType.LIGHT_CTA] += 6
        priority = (
            StoryType.BENEFIT,
            StoryType.USE_LIFESTYLE,
            StoryType.AESTHETIC_EMOTIONAL,
            StoryType.PRODUCT_HIGHLIGHT,
            StoryType.LIGHT_CTA,
        )
        winner = max(priority, key=lambda item: (scores[item], -priority.index(item)))
        return winner, (
            "Seleção automática por adequação do material confirmado; "
            f"placar heurístico interno: {winner.value}={scores[winner]}. "
            "O placar organiza direção criativa e não prevê performance."
        )

    def _persona_references(self, request: SingleStoryRequest) -> List[str]:
        if not request.use_nina:
            return []
        references = request.persona_reference_paths or list(self.CANONICAL_NINA_REFERENCES)
        return [str(self.base_dir / ref) if not Path(ref).is_absolute() else str(ref) for ref in references]

    def _story_style_references(self, request: SingleStoryRequest) -> List[str]:
        references = request.style_reference_paths or [self.CANONICAL_STORY_STYLE_REFERENCE]
        return [str(self.base_dir / ref) if not Path(ref).is_absolute() else str(ref) for ref in references]

    @staticmethod
    def _fold(text: str) -> str:
        normalized = unicodedata.normalize("NFKD", text.casefold())
        return "".join(char for char in normalized if not unicodedata.combining(char))

    @staticmethod
    def _short_name(name: str, limit: int = 30) -> str:
        clean = re.sub(r"\s+", " ", name).strip(" -–—,.;:")
        if len(clean) <= limit:
            return clean
        words: List[str] = []
        for word in clean.split():
            if len(" ".join(words + [word])) > limit:
                break
            words.append(word)
        return " ".join(words) or clean[:limit].rstrip()

    def _headline(self, request: SingleStoryRequest, story_type: StoryType) -> str:
        name = self._short_name(request.product_name)
        facts = self._fold(" ".join(request.confirmed_facts))
        if story_type == StoryType.BENEFIT and "aplicador" in facts:
            return "O segredo está no aplicador"
        if story_type == StoryType.USE_LIFESTYLE:
            return name.upper()
        templates = {
            StoryType.PRODUCT_HIGHLIGHT: f"Olha esse {name}",
            StoryType.BENEFIT: f"{name}: olha esse detalhe",
            StoryType.USE_LIFESTYLE: f"{name} na rotina",
            StoryType.AESTHETIC_EMOTIONAL: f"Um detalhe bonito: {name}",
            StoryType.LIGHT_CTA: f"Quer conhecer esse {name}?",
        }
        headline = templates[story_type]
        return headline if len(headline) <= 52 else f"Olha esse {self._short_name(name, 36)}"

    @staticmethod
    def _cta(request: SingleStoryRequest, story_type: StoryType) -> str:
        if request.cta_text.strip():
            return request.cta_text.strip()
        if story_type == StoryType.LIGHT_CTA:
            return "Confira os detalhes"
        return ""

    @staticmethod
    def _concept(request: SingleStoryRequest, story_type: StoryType) -> Dict[str, str]:
        concepts = {
            StoryType.PRODUCT_HIGHLIGHT: (
                "Produto em primeiro plano",
                "hero shot social com informação curta e espaço de respiro",
                "protagonista visual absoluto",
            ),
            StoryType.BENEFIT: (
                "O detalhe que importa",
                "close editorial do produto com o fato principal apresentado como prova legível",
                "prova visual do benefício confirmado",
            ),
            StoryType.USE_LIFESTYLE: (
                "Na rotina real",
                "momento único de uso plausível, simples e observável",
                "objeto em interação, sempre reconhecível",
            ),
            StoryType.AESTHETIC_EMOTIONAL: (
                "Desejo pelos detalhes",
                "still life de atmosfera natural com foco em forma, cor e textura reais",
                "centro do desejo visual",
            ),
            StoryType.LIGHT_CTA: (
                "Convite leve",
                "produto hero com leitura imediata e uma ação discreta",
                "razão visual para abrir ou responder",
            ),
        }
        title, visual, role = concepts[story_type]
        return {"title": title, "visual": visual, "product_role": role}

    @staticmethod
    def _composition(story_type: StoryType) -> str:
        if story_type == StoryType.BENEFIT:
            return (
                "Headline no terço superior esquerdo; produto grande no centro/inferior direito; "
                "fato confirmado em bloco curto abaixo do headline; bastante área limpa e contraste alto."
            )
        if story_type == StoryType.USE_LIFESTYLE:
            return (
                "Ação única no centro, produto totalmente identificável; headline no terço superior; "
                "texto de apoio em faixa discreta no terço inferior, fora das áreas de interface."
            )
        return (
            "Produto dominante no centro; headline no terço superior; apoio em um bloco curto; "
            "CTA opcional pequeno no terço inferior; margens generosas e leitura em menos de dois segundos."
        )

    @staticmethod
    def _scene(request: SingleStoryRequest, story_type: StoryType) -> str:
        setting = "ambiente doméstico brasileiro contemporâneo, organizado e vivido"
        if story_type == StoryType.AESTHETIC_EMOTIONAL:
            return f"Still life realista do produto em {setting}, luz natural lateral e poucos props funcionais."
        if story_type == StoryType.USE_LIFESTYLE:
            actor = "Nina" if request.use_nina else "uma mão humana natural"
            return (
                f"{actor} apresenta o produto em uma única ação simples sustentada pelas evidências fornecidas, "
                f"em {setting}; o produto permanece visível e sem alterações."
            )
        return (
            f"Produto apoiado ou segurado de forma plausível em {setting}, luz natural suave, "
            "texturas reais e fundo discretamente desfocado sem aparência publicitária artificial."
        )

    @staticmethod
    def _color_direction(request: SingleStoryRequest) -> str:
        if request.brand_palette:
            return "Paleta fornecida: " + ", ".join(request.brand_palette) + "."
        return "Base creme quente, marrom espresso e blush suave; ajustar o acento à cor real do produto."

    @staticmethod
    def _decorative_elements(story_type: StoryType) -> List[str]:
        elements = ["linha fina editorial", "sombra suave de contato"]
        if story_type == StoryType.BENEFIT:
            elements.append("microetiqueta factual sem selo promocional")
        if story_type == StoryType.LIGHT_CTA:
            elements.append("pill discreto para CTA")
        return elements

    @staticmethod
    def _realism_notes(request: SingleStoryRequest, persona_refs: List[str]) -> List[str]:
        notes = [
            "preservar exatamente forma, cor, materiais, rótulo e proporções visíveis nas referências do produto",
            "usar luz motivada, sombras de contato coerentes e reflexos compatíveis com cada material",
            "manter textura fotográfica natural; nada de plástico, CGI, 3D ou polimento excessivo",
            "mostrar somente mecanismo, aplicação ou resultado sustentado por fato/evidência fornecida",
            "tratar qualquer texto gerado como rascunho; para grafia exata, compor o texto na etapa de layout",
        ]
        if request.use_nina and persona_refs:
            notes.append(
                "usar as duas referências canônicas da Nina juntas para preservar rosto, corpo, cabelo e proporções"
            )
        return notes

    @staticmethod
    def _negative_prompt(request: SingleStoryRequest) -> str:
        negatives = [
            "AI look", "CGI", "3D render", "plastic skin", "waxy materials",
            "warped product", "changed packaging", "invented logo", "misspelled label",
            "wrong proportions", "floating object", "incoherent shadow", "impossible reflection",
            "cluttered layout", "low contrast text", "tiny text", "carousel", "multiple slides",
            "before-and-after without evidence", "fake discount", "scarcity claim", "unverified result",
        ]
        if request.use_nina:
            negatives.extend(("identity drift", "different face", "different body proportions", "extra fingers"))
            negatives.append(negative_constraints())
        return ", ".join(negatives)

    def _prompt_blockers(
        self,
        request: SingleStoryRequest,
        product_refs: List[str],
        style_refs: List[str],
        persona_refs: List[str],
    ) -> List[str]:
        blockers: List[str] = []
        if not product_refs:
            blockers.append("MISSING_PRODUCT_REFERENCE")
        elif not all(self._reference_is_resolvable(ref) for ref in product_refs):
            blockers.append("UNRESOLVABLE_PRODUCT_REFERENCE")
        if not style_refs:
            blockers.append("MISSING_STORY_STYLE_REFERENCE")
        elif not all(self._reference_is_resolvable(ref) for ref in style_refs):
            blockers.append("UNRESOLVABLE_STORY_STYLE_REFERENCE")
        if request.use_nina and len(persona_refs) < 2:
            blockers.append("MISSING_CANONICAL_NINA_REFERENCES")
        elif request.use_nina and not all(self._reference_is_resolvable(ref) for ref in persona_refs):
            blockers.append("UNRESOLVABLE_NINA_REFERENCE")
        return blockers

    def _reference_is_resolvable(self, reference: str) -> bool:
        if reference.startswith(("https://", "http://")):
            return True
        path = Path(reference)
        if not path.is_absolute():
            path = self.base_dir / path
        return path.is_file()

    @staticmethod
    def _trend_application(request: SingleStoryRequest) -> str:
        if request.trend_signals:
            signals = "; ".join(request.trend_signals)
            return (
                f"Sinais recebidos ({signals}) foram traduzidos em realismo, utilidade e prova factual; "
                "nenhum layout, slogan ou identidade de terceiro deve ser copiado."
            )
        return (
            "Aplicar realismo editorial, sensação de rotina e justificativa clara do porquê conhecer o produto; "
            "evitar perfeição artificial e modismo sem relação com o item."
        )

    @staticmethod
    def _style_reference_application(request: SingleStoryRequest) -> str:
        notes = request.external_reference_notes + request.style_notes
        if not notes:
            return "Usar a identidade natural, acolhedora, limpa e prática da Nina como direção base."
        return (
            "Extrair apenas princípios abstratos das referências: " + "; ".join(notes) +
            ". Reinterpretar na identidade da Nina, sem reproduzir composição, texto ou assinatura alheia."
        )

    def _build_prompt(
        self,
        request: SingleStoryRequest,
        story_type: StoryType,
        headline: str,
        supporting: str,
        benefit: str,
        cta: str,
        scene: str,
        composition: str,
        colors: str,
        realism: List[str],
        negative: str,
        product_refs: List[str],
        style_refs: List[str],
        persona_refs: List[str],
        trend_application: str,
        style_application: str,
    ) -> str:
        text_lines = [f'HEADLINE: "{headline}"', f'SUPPORT: "{supporting}"']
        if benefit:
            text_lines.append(f'BENEFIT: "{benefit}"')
        if cta:
            text_lines.append(f'CTA: "{cta}"')
        prompt_parts = [
            "Create exactly ONE independent Instagram Story still image, vertical 9:16, 1080x1920.",
            "This is a standalone creative, not a carousel, sequence, storyboard, collage or multi-panel layout.",
            f"PRODUCT: {request.product_name}.",
            "OFFICIAL PRODUCT REFERENCES: " + ("; ".join(product_refs) if product_refs else "MISSING — do not generate final media yet."),
            "CANONICAL NINA STORY STYLE REFERENCE: " + "; ".join(style_refs),
            "Follow its warm photo, centered white serif title, pink doodles and rounded lower blocks; ignore the top 'da série...' label and never copy its product or wording.",
            "CONFIRMED FACTS ONLY: " + " | ".join(request.confirmed_facts),
            f"CREATIVE JOB: {story_type.value}.",
            f"SCENE: {scene}",
            f"COMPOSITION: {composition}",
            f"COLOR: {colors}",
            f"TREND ADAPTATION: {trend_application}",
            f"STYLE ADAPTATION: {style_application}",
            "TEXT TO COMPOSE EXACTLY (correct Brazilian Portuguese, high contrast, no extra words): " + " | ".join(text_lines),
            "Keep all key text and the product away from the top and bottom interface overlay areas.",
            "REALISM: " + " | ".join(realism),
        ]
        if persona_refs:
            prompt_parts.extend((
                "NINA REFERENCES: " + "; ".join(persona_refs),
                "Preserve Nina's exact facial identity from persona_master and her body, hair, angles and physical details from nina_360_master.",
                proportion_rules(),
            ))
        prompt_parts.append("NEGATIVE: " + negative + ".")
        return "\n".join(prompt_parts)

    def _copy_variants(self, request: SingleStoryRequest, story_type: StoryType) -> List[Dict[str, str]]:
        name = self._short_name(request.product_name, 26)
        variants = [
            {"headline": f"Olha esse {name}", "cta": ""},
            {"headline": f"Já viu {name} assim?", "cta": "Confira os detalhes"},
            {"headline": f"Um detalhe do {name}", "cta": "Quer o link?"},
        ]
        return [item for item in variants if len(item["headline"]) <= 52]

    @staticmethod
    def _caption(request: SingleStoryRequest, supporting: str) -> str:
        cta = f" {request.cta_text.strip()}" if request.cta_text.strip() else ""
        return f"{request.product_name}: {supporting}{cta}".strip()

    def _hashtags(self, request: SingleStoryRequest) -> List[str]:
        category = re.sub(r"[^a-z0-9]+", "", self._fold(request.product_category))
        tags = ["#achadinhos", "#dicasdeproduto", "#rotinapratica"]
        if category:
            tags.insert(0, f"#{category[:28]}")
        return tags[:4]
