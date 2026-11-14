"""Factual offline captions and bounded hashtag generation."""
import json
import os
from pathlib import Path
import re
import tempfile
import unicodedata
from typing import Dict, List

from app.models.creative import CreativeBrief
from app.models.facts import ProductFacts
from app.models.product import Product


class CopyPackageBuilder:
    BANNED = {"#fyp", "#fy", "#viral"}
    STOP_WORDS = {
        "a", "as", "com", "da", "das", "de", "do", "dos", "e", "em", "o", "os",
        "para", "por", "um", "uma", "kit",
    }

    @staticmethod
    def _plain(value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value)
        return "".join(char for char in normalized if not unicodedata.combining(char))

    @classmethod
    def _tokens(cls, value: str) -> List[str]:
        return [token for token in re.findall(r"[A-Za-z0-9]+", cls._plain(value))
                if len(token) >= 3 and token.lower() not in cls.STOP_WORDS]

    @staticmethod
    def _tag(tokens: List[str]) -> str:
        return "#" + "".join(token[:1].upper() + token[1:] for token in tokens)

    def hashtags(self, product: Product) -> List[str]:
        title_tokens = self._tokens(product.title)
        category_tokens = self._tokens(product.category or "")
        candidates = ["#ShopeeBrasil", "#AchadinhosShopee"]
        if title_tokens:
            candidates.append(self._tag(title_tokens[:3]))
            candidates.extend(self._tag([token]) for token in title_tokens[:3])
        if category_tokens:
            candidates.append(self._tag(category_tokens[:2]))
        candidates.extend(["#DetalhesDoProduto", "#ConfiraOAnuncio", "#CompraConsciente"])
        result = []
        for tag in candidates:
            lowered = tag.lower()
            if lowered in self.BANNED or lowered in {item.lower() for item in result}:
                continue
            result.append(tag)
            if len(result) == 6:
                break
        if len(result) < 4:
            raise ValueError("Could not create four factual hashtags")
        return result

    @staticmethod
    def _write_text(path: Path, value: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=".content-", suffix=path.suffix, dir=path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(value.rstrip() + "\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    def build(self, job_dir: Path, product: Product, facts: ProductFacts,
              brief: CreativeBrief) -> Dict[str, object]:
        confirmed = [item.claim for item in facts.confirmed_facts[:2]]
        fact_lines = "\n".join(f"- {claim}" for claim in confirmed)
        body = product.title + (f"\n{fact_lines}" if fact_lines else "")
        shopee = f"{body}\n\n{brief.cta_shopee}"
        instagram = f"{body}\n\n{brief.cta_instagram}"
        tags = self.hashtags(product)
        content_dir = Path(job_dir) / "content"
        shopee_path = content_dir / "shopee.txt"
        instagram_path = content_dir / "instagram.txt"
        hashtags_path = content_dir / "hashtags.json"
        self._write_text(shopee_path, shopee)
        self._write_text(instagram_path, instagram)
        self._write_text(hashtags_path, json.dumps(tags, ensure_ascii=False, indent=2))
        return {
            "shopee": str(shopee_path), "instagram": str(instagram_path),
            "hashtags": str(hashtags_path), "hashtag_count": len(tags),
        }
