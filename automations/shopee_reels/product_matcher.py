"""
Motor de Correspondência Estrita de Produtos (Baseado no projeto shopee-video-automation).
Garante que o produto demonstrado no vídeo do Instagram seja EXATAMENTE o mesmo produto na Shopee.
Rejeita categorias genéricas ou produtos divergentes.
"""

import re
import unicodedata
from typing import Dict, List, Tuple

STOPWORDS = {
    "de", "da", "do", "das", "dos", "e", "em", "um", "uma", "uns", "umas",
    "com", "para", "por", "sem", "o", "a", "os", "as", "que", "na", "no",
    "frete", "gratis", "promocao", "oferta", "shopee", "shoppee", "brasil",
    "br", "super", "envio", "imediato", "pronta", "entrega", "original",
    "barato", "barata", "melhor", "compre", "agora", "imperdivel", "novo", "nova",
    "eficiente", "incrivel", "util", "cozinha", "casa", "gadget", "gadgets", "smart",
    "maquina", "aparelho"
}

EQUIVALENTS = {
    "selador": "selador",
    "seladora": "selador",
    "seladores": "selador",
    "amassador": "amassador",
    "espremedor": "amassador",
    "triturador": "processador",
    "processador": "processador",
    "dispenser": "dispenser",
    "dosador": "dispenser",
    "porta": "dispenser"
}

def normalize(text: str) -> str:
    if not text:
        return ""
    norm = unicodedata.normalize("NFKD", text.lower()).encode("ascii", "ignore").decode()
    return " ".join(re.findall(r"[a-z0-9]+", norm))

def stem_or_alias(token: str) -> str:
    token = token.lower()
    # Plural em português: embalagens -> embalagem
    if token.endswith("ns") and len(token) > 3:
        token = token[:-2] + "m"
    # Plural simples: raladores -> ralador
    elif token.endswith("es") and len(token) > 4:
        token = token[:-2]
    elif token.endswith("s") and len(token) > 3:
        token = token[:-1]
    # Mapeia equivalentes diretos de categoria/função idêntica
    return EQUIVALENTS.get(token, token)

def clean_tokens(text: str) -> List[str]:
    norm = normalize(text)
    tokens = norm.split()
    return [t for t in tokens if len(t) > 2 and t not in STOPWORDS]

class StrictProductMatcher:
    """Valida se o produto do Instagram corresponde ao produto retornado pela Shopee."""

    @staticmethod
    def evaluate(video_query: str, shopee_title: str) -> Tuple[bool, float, str]:
        vq_clean = clean_tokens(video_query)
        sp_clean = clean_tokens(shopee_title)

        if not vq_clean or not sp_clean:
            return False, 0.0, "Termos insuficientes para validação"

        vq_stems = [stem_or_alias(t) for t in vq_clean]
        sp_stems = [stem_or_alias(t) for t in sp_clean]

        # Verifica quantos tokens essenciais do vídeo estão presentes no título da Shopee
        matched = []
        for t, s in zip(vq_clean, vq_stems):
            if t in sp_clean or s in sp_stems or any(s in x or x in s for x in sp_stems):
                matched.append(t)

        ratio = len(matched) / len(vq_clean)
        score = round(ratio * 100, 1)

        # Regra Estrita de Identidade:
        # Se for um produto de 1 ou 2 palavras (ex: amassador alho), deve ter pelo menos 50% de match.
        # Se for de 3+ palavras (ex: mini selador embalagens), deve ter pelo menos 60% de match e 2 termos coincidentes.
        if len(vq_clean) <= 2:
            is_match = (len(matched) >= 1 and ratio >= 0.5)
        else:
            is_match = (ratio >= 0.6 and len(matched) >= 2)

        if is_match:
            reason = f"PRODUTO IGUAL CONFIRMADO ({len(matched)}/{len(vq_clean)} termos coincidentes: {', '.join(matched)})"
        else:
            missing = [t for t in vq_clean if t not in matched]
            reason = f"PRODUTOS DIFERENTES! Faltam termos essenciais do produto do vídeo: {', '.join(missing)}"

        return is_match, score, reason
