"""Fact safety validator strictly blocking false urgency, false testimonials and unverified claims."""
import re
import unicodedata
from typing import List, Tuple
from app.models.facts import ProductFacts
from app.models.creative import Script


def strip_accents(text: str) -> str:
    """Strips diacritics for robust matching in pt-BR."""
    nfkd = unicodedata.normalize('NFKD', text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


class FactSafetyValidator:
    """Quality gate ensuring no unconfirmed claims, false urgency or unverified hype appear in scripts."""

    STRICT_PROHIBITIONS = [
        # Waterproofing
        (r"\b(a prova d['\w]+agua|100% impermeavel|impermeavel|a prova de agua|waterproof)\b", "Afirmação não comprovada de impermeabilidade"),
        # Lifetime warranty
        (r"\b(garantia vitalicia|nunca estraga|dura a vida toda|garantia eterna)\b", "Afirmação enganosa de garantia eterna"),
        # Medical / miracles
        (r"\b(cura|tratamento medico|reverte doenca|elimina 100% das dores|milagroso)\b", "Alegação médica ou milagrosa proibida"),
        # Counterfeit claims
        (r"\b(original da apple|original da samsung)\b", "Alegação de marca não comprovada"),
        # False scarcity and false urgency (PROHIBITED)
        (r"\b(corre antes que acabe|ultimas unidades|estoque acabando|vai esgotar|compre antes que esgote|compre ja antes que acabe)\b", "Falsa urgência ou escassez não comprovada"),
        # Unverified virality and hype
        (r"\b(mais vendido da shopee|mais vendido do brasil|viral da internet|resolveu minha vida)\b", "Alegação de viralidade ou ranking sem evidência factual comprovada"),
        # False human personal testimonial for virtual persona (PROHIBITED)
        (r"\b(eu comprei|chegou pra mim|eu testei na minha|uso todo dia na minha|meu resultado real)\b", "Testemunho pessoal simulado não permitido para persona virtual"),
    ]

    def validate(self, script: Script, facts: ProductFacts) -> Tuple[bool, List[str]]:
        """Validates the script against strict fact safety and virtual persona rules."""
        violations: List[str] = []
        normalized_text = strip_accents(script.full_text.lower())

        for pattern, reason in self.STRICT_PROHIBITIONS:
            matches = re.findall(pattern, normalized_text, re.IGNORECASE)
            if matches:
                # Check if it was explicitly confirmed in confirmed_facts
                is_confirmed = False
                for f in facts.confirmed_facts:
                    norm_fact = strip_accents(f.claim.lower())
                    if re.search(pattern, norm_fact, re.IGNORECASE):
                        is_confirmed = True
                        break
                if not is_confirmed:
                    matched_str = matches[0] if isinstance(matches[0], str) else matches[0][0]
                    violations.append(f"Violação de Fact Safety: {reason} ('{matched_str}')")

        is_valid = len(violations) == 0
        return is_valid, violations