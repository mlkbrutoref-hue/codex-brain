"""Curated hooks bank for Nina as a virtual creator, adhering to transparent presentation rules."""
from typing import Dict, List
from app.models.enums import ContentFormat


class HookBank:
    """Library of high-retention hooks presenting products objectively without false personal testimonials."""

    HOOKS: Dict[ContentFormat, List[str]] = {
        ContentFormat.ACHADINHO: [
            "Dá uma olhada nessa opção de achadinho que encontrei na Shopee!",
            "Olha essa opção que apareceu na Shopee; vamos conferir o anúncio!",
            "Se você procura um item como este, confere os detalhes do produto!",
            "Vem ver o que a página deste achadinho informa na Shopee!",
        ],
        ContentFormat.PROBLEMA_SOLUTION: [
            "Procurando uma opção para essa necessidade da rotina? Vamos conferir esta proposta.",
            "Olha este item relacionado à tarefa e os detalhes confirmados no anúncio.",
            "Antes de decidir, vale conferir o que a página deste produto realmente informa.",
            "Esta é uma opção da categoria; vamos olhar os dados disponíveis.",
        ],
        ContentFormat.QUICK_REVIEW: [
            "Vamos analisar os detalhes e a ficha técnica desse item da Shopee!",
            "Confere aqui as características que aparecem no anúncio desse produto.",
            "Um tour rápido pelos dados e imagens oficiais desse achadinho.",
        ],
        ContentFormat.PRODUCT_IN_USE: [
            "Confere a apresentação deste produto com base no anúncio oficial!",
            "Dá uma olhada nos detalhes visíveis deste item.",
            "Acompanha a apresentação das características confirmadas deste modelo.",
        ],
        ContentFormat.POV: [
            "POV: Explorando os detalhes e o design desse achadinho da Shopee.",
            "POV: Conferindo um item e as informações disponíveis no anúncio.",
        ],
        ContentFormat.AESTHETIC: [
            "Olha os detalhes visíveis desse produto no ambiente...",
            "Uma composição visual baseada na imagem oficial do anúncio.",
        ],
        ContentFormat.LIST: [
            "Achadinhos da Shopee para conferir com atenção aos dados do anúncio!",
            "Seleção de produtos para conhecer e comparar na Shopee!",
        ],
    }

    @classmethod
    def get_hook(cls, format_type: ContentFormat, index: int = 0) -> str:
        """Returns a hook template strictly adhering to virtual persona safety."""
        hooks = cls.HOOKS.get(format_type, cls.HOOKS[ContentFormat.ACHADINHO])
        return hooks[index % len(hooks)]
