"""Deterministic planner for Nina's spontaneous lifestyle Stories."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.lifestyle_story.history import LifestyleHistoryStore
from app.lifestyle_story.models import (
    LifestyleCategory,
    LifestyleStoryPlan,
    LifestyleStoryRequest,
    LifestyleStoryType,
    TextMode,
)
from app.lifestyle_story.validator import LifestyleStoryValidator
from app.creative.proportion_policy import proportion_rules, negative_constraints


class NinaLifestyleStoryGenerator:
    NAME = "NINA_LIFESTYLE_STORY_GENERATOR"
    VERSION = "1.2.0"
    CANONICAL_NINA_REFERENCES = (
        "data/personas/nina_v1/references/persona_master.png",
        "data/personas/nina_v1/references/nina_360_master.png",
    )

    LIBRARY: Dict[str, List[Dict[str, Any]]] = {
        "MORNING": [
            {
                "category": "MORNING_ROUTINE", "story_type": "CONNECTION", "text_mode": "LIGHT_TEXT",
                "scene_concept": "selfie de bom dia ainda na cama", "location": "quarto vivido com roupa de cama clara e levemente amassada",
                "action": "Nina faz uma selfie casual poucos minutos depois de acordar", "pose": "deitada de lado, cabeça apoiada no travesseiro e ombro relaxado",
                "camera_angle": "selfie frontal levemente acima dos olhos e inclinada", "camera_distance": "close de celular à distância de um braço",
                "phone_position": "celular na mão direita, fora do quadro, braço estendido de forma plausível", "body_position": "tronco parcialmente coberto pelo lençol",
                "hand_position": "mão direita segura o celular fora do quadro; mão esquerda repousa no travesseiro", "wardrobe": "camiseta oversized creme de dormir",
                "hair_state": "cabelo solto, volumoso e levemente bagunçado de manhã", "makeup_state": "sem maquiagem, pele natural",
                "props": ["travesseiros claros", "lençol com dobras naturais", "copo de água no criado-mudo"],
                "lighting": "luz suave de manhã entrando lateralmente pela janela", "expression": "olhar sonolento e sorriso pequeno",
                "mood": "leve, íntimo e natural", "optional_text": "bom diaaa ♡",
            },
            {
                "category": "FITNESS", "story_type": "ROUTINE", "text_mode": "LIGHT_TEXT",
                "scene_concept": "selfie rápida antes da academia", "location": "espelho do quarto perto da porta",
                "action": "Nina registra o look antes de sair", "pose": "peso em uma perna e ombros soltos",
                "camera_angle": "reflexo vertical de espelho com leve inclinação", "camera_distance": "plano de corpo quase inteiro",
                "phone_position": "celular na mão direita à altura do peito, cobrindo pequena parte do rosto", "body_position": "postura casual em três quartos",
                "hand_position": "mão direita no celular e mão esquerda segurando garrafa", "wardrobe": "top esportivo neutro e legging escura",
                "hair_state": "rabo de cavalo solto", "makeup_state": "sem maquiagem pesada",
                "props": ["garrafa de água", "tênis próximos à porta"], "lighting": "luz natural clara de manhã",
                "expression": "focada e tranquila", "mood": "energia leve", "optional_text": "indo treinar",
            },
        ],
        "AFTERNOON": [
            {
                "category": "MIRROR_SELFIE", "story_type": "LIFESTYLE", "text_mode": "NO_TEXT",
                "scene_concept": "selfie casual de look no espelho durante a tarde", "location": "sala pequena e vivida com espelho de corpo inteiro",
                "action": "Nina fotografa o look sem pose publicitária", "pose": "quadril levemente deslocado, uma perna relaxada",
                "camera_angle": "reflexo de espelho vertical, discretamente inclinado", "camera_distance": "plano de três quartos",
                "phone_position": "celular na mão direita à altura do rosto, cobrindo apenas uma pequena faixa lateral", "body_position": "corpo em três quartos, postura relaxada",
                "hand_position": "mão direita segura o celular; mão esquerda no bolso", "wardrobe": "jeans reto e camiseta branca levemente solta",
                "hair_state": "cabelo solto natural com movimento", "makeup_state": "maquiagem leve de rotina",
                "props": ["sofá com manta", "bolsa casual", "planta de interior"], "lighting": "luz natural lateral de meio da tarde",
                "expression": "meio sorriso discreto olhando para a tela", "mood": "casual, espontâneo e cotidiano", "optional_text": "",
            },
            {
                "category": "STUDY_WORK", "story_type": "ROUTINE", "text_mode": "LIGHT_TEXT",
                "scene_concept": "pausa real entre notebook e café", "location": "mesa de trabalho doméstica",
                "action": "Nina apoia o rosto na mão durante uma pausa", "pose": "sentada de lado com postura confortável",
                "camera_angle": "celular apoiado na mesa em ângulo casual", "camera_distance": "plano médio",
                "phone_position": "celular apoiado entre livros, sem aparecer", "body_position": "sentada com um ombro mais próximo da câmera",
                "hand_position": "cotovelo na mesa e mão no rosto", "wardrobe": "regata neutra e cardigan leve",
                "hair_state": "cabelo solto atrás de um ombro", "makeup_state": "maquiagem leve",
                "props": ["notebook", "caneca", "caderno aberto"], "lighting": "luz de janela de tarde",
                "expression": "cansada mas divertida", "mood": "vida real", "optional_text": "pausinha necessária",
            },
        ],
        "NIGHT": [
            {
                "category": "SKINCARE", "story_type": "ROUTINE", "text_mode": "LIGHT_TEXT",
                "scene_concept": "selfie noturna durante a limpeza do rosto", "location": "banheiro doméstico diante do box",
                "action": "Nina mostra o rosto com espuma de limpeza e segura um frasco pump neutro", "pose": "close inclinado com a cabeça virada suavemente para um lado",
                "camera_angle": "selfie frontal diagonal com enquadramento casual", "camera_distance": "close de rosto e ombros",
                "phone_position": "celular na mão direita fora do quadro, braço dobrado de forma plausível", "body_position": "um ombro mais próximo da câmera",
                "hand_position": "mão esquerda segura o frasco pump junto ao peito; mão direita segura o celular fora do quadro", "wardrobe": "regata rosa de alça fina, sem apelo publicitário",
                "hair_state": "cabelo escuro solto, molhado e penteado para trás", "makeup_state": "sem maquiagem, espuma real de cleanser no rosto",
                "props": ["frasco pump neutro sem marca", "box de vidro", "toalha fora de foco"],
                "lighting": "luz doméstica noturna levemente rosada e azul, plausível para banheiro", "expression": "olhos fechados e expressão relaxada",
                "mood": "self care íntimo, real e espontâneo", "optional_text": "20:23 💦",
            },
            {
                "category": "BED_RELAX", "story_type": "CONNECTION", "text_mode": "LIGHT_TEXT",
                "scene_concept": "selfie depois de finalmente deitar", "location": "cama com luz baixa de abajur",
                "action": "Nina faz selfie já deitada", "pose": "deitada de costas com cabeça apoiada e ombros relaxados",
                "camera_angle": "selfie alta e levemente inclinada", "camera_distance": "close de celular",
                "phone_position": "celular fora do quadro na mão direita", "body_position": "corpo coberto até o peito pelo edredom",
                "hand_position": "mão direita segura o celular; esquerda sobre o edredom", "wardrobe": "pijama de algodão claro",
                "hair_state": "cabelo solto no travesseiro", "makeup_state": "sem maquiagem",
                "props": ["abajur aceso", "livro fechado", "cobertor com dobras"], "lighting": "luz quente de abajur e azul noturno discreto na janela",
                "expression": "alívio e sorriso pequeno", "mood": "relax e fim do dia", "optional_text": "finalmente deitei",
            },
        ],
    }

    # Wider supported-phone alternatives avoid forcing short-range selfie anatomy.
    LIBRARY["AFTERNOON"].append({
        "category": "FEMALE_LIFESTYLE", "story_type": "LIFESTYLE", "text_mode": "NO_TEXT",
        "scene_concept": "autorretrato casual com temporizador no sofá",
        "location": "sala doméstica vivida com sofá de linho",
        "action": "Nina faz um autorretrato casual sentada na borda do sofá, pés no chão",
        "pose": "sentada ereta e relaxada, pernas sem cruzar, sem inclinar o tronco para a lente",
        "camera_angle": "celular apoiado e nivelado", "camera_distance": "2 m, corpo inteiro sentado",
        "phone_position": "celular apoiado em móvel com temporizador, fora do quadro",
        "body_position": "cabeça, tronco, quadris, joelhos e pés visíveis, distância semelhante da lente",
        "hand_position": "mãos relaxadas sobre as coxas, dedos visíveis",
        "wardrobe": "camiseta branca simples e shorts casuais de sarja bege",
        "hair_state": "cabelo solto castanho-escuro longo e volumoso", "makeup_state": "maquiagem leve",
        "props": ["sofá de linho", "manta usada", "caneca na mesa lateral"],
        "lighting": "luz natural suave de tarde", "expression": "sorriso pequeno para o celular",
        "mood": "autorretrato espontâneo e confortável", "optional_text": "",
    })
    LIBRARY["MORNING"].append({
        "category": "HOME_ROUTINE", "story_type": "ROUTINE", "text_mode": "NO_TEXT",
        "scene_concept": "pausa espontânea preparando o café da manhã",
        "location": "cozinha doméstica pequena com bancada usada",
        "action": "Nina segura uma caneca e olha para o celular apoiado enquanto prepara o café",
        "pose": "em pé relaxada em três quartos, sem se inclinar para a câmera",
        "camera_angle": "celular apoiado e nivelado", "camera_distance": "2.5 m, corpo inteiro",
        "phone_position": "celular apoiado em prateleira oposta, fora do quadro",
        "body_position": "corpo inteiro incluindo pés, tronco e pernas equilibrados",
        "hand_position": "uma mão segura a alça da caneca, outra repousa suavemente na bancada",
        "wardrobe": "regata de algodão creme e shorts de dormir cinza",
        "hair_state": "cabelo longo castanho-escuro solto com fios naturais", "makeup_state": "sem maquiagem pesada",
        "props": ["caneca simples", "pão no prato", "pano de cozinha"],
        "lighting": "luz de janela matinal", "expression": "sorriso discreto de rotina",
        "mood": "doméstico e natural", "optional_text": "",
    })

    REALISM_CONSTRAINTS = [
        "fotografia vertical realista de celular, não editorial publicitário",
        "preservar identidade facial, cabelo, tom de pele, idade aparente e proporções da Nina",
        "silhueta um pouco mais magra e definida: cintura marcada, braços e pernas menos volumosos, mantendo curvas naturais e anatomia realista",
        "não alargar tronco, quadril, braços ou coxas pela lente, pose, roupa ou edição",
        "usar textura natural da pele, poros discretos, fios soltos e pequenas imperfeições",
        "manter anatomia, mãos, reflexos e física do celular plausíveis",
        "usar luz motivada pelo ambiente e sombras coerentes",
        "manter o ambiente vivido, casual e ligeiramente imperfeito",
        "não gerar texto dentro da fotografia; texto leve será aplicado em camada determinística",
    ]

    NEGATIVE_PROMPT = (
        "advertising campaign, product ad, studio pose, fashion campaign, CGI, 3D render, plastic skin, "
        "waxy face, different identity, different face, different hair color, overweight body, widened torso, oversized hips, thickened arms, thickened thighs, body distortion, "
        "extra fingers, fused fingers, malformed hand, broken wrist, impossible phone reflection, duplicate phone, "
        "floating objects, perfect showroom, excessive symmetry, cinematic spotlight, HDR, over-retouched skin, "
        "text, caption, letters, logo, watermark, collage, split screen"
    )

    def __init__(self, base_dir: Optional[Path] = None) -> None:
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).resolve().parents[2]
        self.validator = LifestyleStoryValidator()

    def generate(
        self,
        request: LifestyleStoryRequest,
        history: Optional[List[Dict[str, Any]]] = None,
    ) -> LifestyleStoryPlan:
        history = history or []
        candidates = self._candidates(request)
        if not candidates:
            raise ValueError("No lifestyle scene matches the requested constraints")
        chosen = dict(min(candidates, key=lambda item: LifestyleHistoryStore.usage_count(history, self._signature(request.time_of_day.value, item))))
        signature = self._signature(request.time_of_day.value, chosen)
        # Replace conflicting close/tilted cues in structured fields, not only prose.
        mirror = "espelho" in chosen["camera_angle"]
        supported = "apoiado" in chosen["phone_position"]
        if mirror:
            chosen.update(camera_angle="espelho plano vertical, câmera quase paralela e nivelada",
                          camera_distance="1.5–2 m da personagem ao espelho; corpo inteiro com margem para cabeça e pés",
                          phone_position="celular à altura do peito superior, braço dobrado naturalmente, sem inclinação forte")
        elif supported:
            chosen.update(camera_angle="celular apoiado, lente nivelada, personagem centralizada",
                          camera_distance="1.8–2.5 m; " + ("corpo inteiro equilibrado" if "corpo inteiro" in chosen["camera_distance"] else "plano de três quartos equilibrado"))
        else:
            chosen.update(camera_angle="selfie frontal perto da altura dos olhos, sem inclinação extrema",
                          camera_distance="0.7–0.9 m, braço confortavelmente estendido; cabeça, ombros e tronco equilibrados",
                          phone_position="celular fora do quadro, braço estendido sem dominar o primeiro plano")
        category = chosen["category"] if request.category == LifestyleCategory.AUTO else request.category.value
        story_type = chosen["story_type"] if request.story_type == LifestyleStoryType.AUTO else request.story_type.value
        text_mode = chosen["text_mode"] if request.text_mode == TextMode.AUTO else request.text_mode.value
        optional_text = request.optional_text or (chosen["optional_text"] if text_mode == "LIGHT_TEXT" else "")
        if text_mode == "NO_TEXT":
            optional_text = ""
        references = request.reference_sources
        adaptation = self._reference_adaptation(request)
        persona_refs = [str(self.base_dir / path) for path in self.CANONICAL_NINA_REFERENCES]
        usage = LifestyleHistoryStore.usage_count(history, signature)
        prompt = self._prompt(request, chosen, category, story_type, references, adaptation, persona_refs)
        plan = LifestyleStoryPlan(
            generator_name=self.NAME,
            generator_version=self.VERSION,
            time_of_day=request.time_of_day.value,
            category=category,
            story_type=story_type,
            text_mode=text_mode,
            reference_source=references,
            reference_adaptation=adaptation,
            scene_concept=chosen["scene_concept"],
            location=chosen["location"],
            action=chosen["action"],
            pose=chosen["pose"],
            camera_angle=chosen["camera_angle"],
            camera_distance=chosen["camera_distance"],
            phone_position=chosen["phone_position"],
            body_position=chosen["body_position"],
            hand_position=chosen["hand_position"],
            wardrobe=chosen["wardrobe"],
            hair_state=chosen["hair_state"],
            makeup_state=chosen["makeup_state"],
            props=list(chosen["props"]),
            lighting=chosen["lighting"],
            expression=chosen["expression"],
            mood=chosen["mood"],
            optional_text=optional_text,
            persona_reference_paths=persona_refs,
            realism_constraints=list(self.REALISM_CONSTRAINTS),
            negative_prompt=self.NEGATIVE_PROMPT + ", " + negative_constraints(),
            final_image_prompt=prompt,
            format_spec={"platform": "Instagram Stories", "aspect_ratio": "9:16", "width": 1080, "height": 1920, "artifact_count": 1},
            scene_signature=signature,
            anti_monotony={
                "status": "PASS" if usage == 0 else "REVIEW",
                "prior_exact_uses": usage,
                "rule": "choose the least-used compatible scene signature",
                "objective": "SAME PERSON / DIFFERENT REAL MOMENTS",
            },
            validation_status="PENDING",
            validation_errors=[],
        )
        errors = self.validator.validate(plan)
        plan.validation_errors = errors
        plan.validation_status = "PASS" if not errors else "FAIL"
        return plan

    def generate_to_file(self, request: LifestyleStoryRequest, output: Path, history: Optional[List[Dict[str, Any]]] = None) -> LifestyleStoryPlan:
        plan = self.generate(request, history=history)
        output = Path(output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(plan.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return plan

    def _candidates(self, request: LifestyleStoryRequest) -> List[Dict[str, Any]]:
        items = list(self.LIBRARY[request.time_of_day.value])
        if request.category != LifestyleCategory.AUTO:
            items = [item for item in items if item["category"] == request.category.value]
        if request.story_type != LifestyleStoryType.AUTO:
            items = [item for item in items if item["story_type"] == request.story_type.value]
        if request.text_mode != TextMode.AUTO:
            items = [item for item in items if item["text_mode"] == request.text_mode.value]
        return items

    @staticmethod
    def _signature(time_of_day: str, item: Dict[str, Any]) -> str:
        return "|".join((time_of_day, item["category"], item["location"], item["pose"], item["camera_angle"], item["wardrobe"]))

    @staticmethod
    def _reference_adaptation(request: LifestyleStoryRequest) -> str:
        if request.reference_sources:
            details = "; ".join(request.reference_notes) if request.reference_notes else "pose, camera, light, setting and mood"
            return f"Use references only for {details}; recreate the visual logic with Nina and do not copy the original person."
        return "Use the internal time-of-day scene library; no external person or composition is copied."

    def _prompt(
        self,
        request: LifestyleStoryRequest,
        scene: Dict[str, Any],
        category: str,
        story_type: str,
        references: List[str],
        adaptation: str,
        persona_refs: List[str],
    ) -> str:
        parts = [
            "Create exactly ONE photorealistic vertical 9:16 smartphone Story image.",
            "This is a candid influencer moment, not an advertisement, campaign, collage or multi-panel image.",
            "NINA IDENTITY REFERENCES: " + "; ".join(persona_refs),
            "Preserve Nina's exact facial identity from persona_master and use nina_360_master for her recognizable anatomy, hair, angles and physical details.",
            proportion_rules(),
            f"TIME OF DAY: {request.time_of_day.value}.",
            f"CATEGORY: {category}. STORY TYPE: {story_type}.",
            f"SCENE CONCEPT: {scene['scene_concept']}.",
            f"LOCATION: {scene['location']}.",
            f"ACTION: {scene['action']}.",
            f"POSE: {scene['pose']}. BODY: {scene['body_position']}. HANDS: {scene['hand_position']}.",
            f"CAMERA: {scene['camera_angle']}; {scene['camera_distance']}; {scene['phone_position']}.",
            f"WARDROBE: {scene['wardrobe']}. HAIR: {scene['hair_state']}. MAKEUP: {scene['makeup_state']}.",
            "PROPS: " + "; ".join(scene["props"]) + ".",
            f"LIGHTING: {scene['lighting']}. EXPRESSION: {scene['expression']}. MOOD: {scene['mood']}.",
            "REFERENCE SOURCES: " + ("; ".join(references) if references else "internal scene library"),
            f"REFERENCE ADAPTATION: {adaptation}",
            "REALISM: " + " | ".join(self.REALISM_CONSTRAINTS),
            "Leave a small clean area for an optional short overlay, but generate absolutely no text inside the image.",
            "NEGATIVE: " + self.NEGATIVE_PROMPT + ", " + negative_constraints() + ".",
        ]
        return "\n".join(parts)
