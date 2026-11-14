"""Read-only identification of the twelve user-supplied Shopee short links.

Uses the project's existing signed Affiliate API client and product query.
No product search, publication, or affiliate link generation is performed.
"""

import csv
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.providers.shopee.client import ShopeeAffiliateClient  # noqa: E402
from app.providers.shopee.queries import product_details_query  # noqa: E402


LINKS = [
    "https://s.shopee.com.br/30oAO1Fc2Q",
    "https://s.shopee.com.br/40ghZaaGvM",
    "https://s.shopee.com.br/3LR0mIRE67",
    "https://s.shopee.com.br/1BMWCsYSyw",
    "https://s.shopee.com.br/7Kx9YDFSXY",
    "https://s.shopee.com.br/6AlC9qPPzA",
    "https://s.shopee.com.br/qjfoGrCHL",
    "https://s.shopee.com.br/6fhSkUzBDr",
    "https://s.shopee.com.br/9peUWJraqr",
    "https://s.shopee.com.br/8plxKPAYAw",
    "https://s.shopee.com.br/LnPCraYfV",
    "https://s.shopee.com.br/8AWGXq5OVe",
]

# Checked against the title returned by the API and the API's main image.
# Keying by item ID prevents a later changed redirect from inheriting a match.
MATCHES = {
    "58268173541": ("A", "Bolsa baú monograma", "marrom escuro e caramelo", "ALTA", "Título e imagem: formato baú, monograma, duas alças e alça longa.", None),
    "58211968124": ("B", "Bolsa estilo Tabby", "preta", "MÉDIA", "Título diz Tabby; imagem mostra bolsa preta com aba e ferragem dourada.", "Formato de C da ferragem não é visível com segurança na imagem principal."),
    "52854076149": ("C", "Bolsa estilo sela", "creme e marrom", "ALTA", "Título e imagem: sela de contorno arredondado, contraste de cores e alça larga.", None),
    "58257055954": ("D", "Bolsa envelope monograma", "clara, bege rosado", "ALTA", "Título e imagem: monograma, aba, fecho metálico e corrente.", None),
    "58211528147": ("E", "Tote dobrável", "azul-marinho em destaque; outras cores na montagem", "ALTA", "Título diz tote dobrável/nylon; imagem mostra tote com aba pequena e várias cores.", "Disponibilidade das cores e variação selecionada não são expostas pela API."),
    "58217589058": ("F", "Bolsa matelassê", "preta na imagem principal", "ALTA", "Título diz matelassê vinho/marsala; imagem principal mostra modelo preto acolchoado com corrente dourada.", "Cor vinho/marsala do título não coincide com a foto principal; variação selecionada não confirmada."),
    "56814155508": ("G", "Bolsa JW PEI Yara", "preta em destaque; outras cores na montagem", "BAIXA", "Título diz JW PEI Yara/Baguete, mas a imagem mostra bolsa estruturada com duas alças longas.", "Conflito entre título e imagem: formato baguete e identidade JW PEI Yara não confirmados visualmente; cor creme aparece só como miniatura."),
    "54017791884": ("H", "Bolsa estilo Dionysus", "vinho/marrom", "ALTA", "Título diz Dionysus; imagem mostra peça retangular com aba, ferragem frontal prateada e corrente escura.", None),
    "58209963081": ("I", "Bolsa estilo Saddle", "marrom", "ALTA", "Título diz Saddle Bag; imagem mostra bolsa transversal marrom arredondada, com aba estreita e fecho frontal.", None),
    "58207645237": ("J", "Bolsa Asinha", "preta", "MÉDIA", "Título diz Asinha com duas correntes; imagem mostra peça preta com símbolo de asas e corrente.", "A segunda corrente não é distinguível na imagem principal."),
    "23494649232": ("K", "Bolsa monograma", "clara, bege", "ALTA", "Título diz monograma; imagem mostra bolsa clara curva, estampa repetida e detalhe metálico na alça.", None),
    "58206179161": ("L", "Bolsa com porta-moedas", "preta em destaque; outras cores na montagem", "ALTA", "Título e imagem: bolsa com bolsinha redonda, alça larga e várias cores mostradas.", "Disponibilidade das cores e variação selecionada não são expostas pela API."),
}

ID_PATTERNS = [
    re.compile(r"/opaanlp/(\d+)/(\d+)(?:/|$)"),
    re.compile(r"/product/(\d+)/(\d+)(?:/|$)"),
    re.compile(r"-i\.(\d+)\.(\d+)(?:/|$)"),
]


def resolve(entry):
    number, link = entry
    record = {"number": number, "short_url": link}
    try:
        request = urllib.request.Request(link, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(request, timeout=20) as response:
            final = response.url
            record["redirect_http_status"] = response.status
        parsed = urllib.parse.urlparse(final)
        record["redirect_host"] = parsed.netloc
        record["redirect_path"] = parsed.path
        record["final_url_without_tracking"] = urllib.parse.urlunparse(
            (parsed.scheme, parsed.netloc, parsed.path, "", "", "")
        )
        record["redirect_query_keys"] = sorted(urllib.parse.parse_qs(parsed.query))
        for pattern in ID_PATTERNS:
            match = pattern.search(parsed.path)
            if match:
                record["shop_id"] = match.group(1)
                record["item_id"] = match.group(2)
                record["canonical_url"] = (
                    f"https://shopee.com.br/product/{match.group(1)}/{match.group(2)}"
                )
                record["resolution_status"] = "resolved"
                return record
        record["resolution_status"] = "unresolved_path"
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        record["resolution_status"] = "error"
        record["resolution_error"] = type(exc).__name__
    return record


def main():
    with ThreadPoolExecutor(max_workers=3) as pool:
        records = list(pool.map(resolve, enumerate(LINKS, 1)))

    client = ShopeeAffiliateClient(timeout_seconds=20)
    for record in records:
        if record.get("resolution_status") != "resolved":
            continue
        try:
            data = client.execute(
                product_details_query(int(record["item_id"]), int(record["shop_id"]))
            )
            nodes = data.get("productOfferV2", {}).get("nodes", [])
            exact = [
                node for node in nodes
                if str(node.get("itemId")) == record["item_id"]
                and str(node.get("shopId")) == record["shop_id"]
            ]
            record["api_status"] = "confirmed" if exact else "not_found"
            record["api_product"] = exact[0] if exact else None
        except Exception as exc:
            record["api_status"] = "error"
            record["api_error"] = type(exc).__name__
            raise RuntimeError("AFFILIATE_BATCH_STOPPED_NO_AUTOMATIC_CONTINUATION") from None
        print(
            f"{record['number']:2} {record['resolution_status']:16} "
            f"{record.get('item_id', '-'):>14} {record.get('shop_id', '-'):>12} "
            f"{record.get('api_status', '-'):12} "
            f"{(record.get('api_product') or {}).get('productName', '')[:100]}",
            flush=True,
        )

    for record in records:
        node = record.get("api_product") or {}
        expected = MATCHES.get(record.get("item_id"))
        if record.get("api_status") == "confirmed" and expected:
            letter, label, color, confidence, evidence, issue = expected
            record["mapping"] = {
                "description_letter": letter,
                "product_label_from_user": label,
                "main_image_color_observed": color,
                "confidence": confidence,
                "evidence": evidence,
                "issue": issue,
            }
        else:
            record["mapping"] = {
                "description_letter": None,
                "product_label_from_user": None,
                "main_image_color_observed": None,
                "confidence": "BAIXA",
                "evidence": "NÃO CONFIRMADO",
                "issue": "Anúncio não confirmado ou ID diferente da identificação revisada.",
            }
        record["api_offer_link_matches_input"] = (
            node.get("offerLink") == record["short_url"] if node else None
        )
        record["fields_not_exposed_by_affiliate_api"] = [
            "original_price", "review_count", "description", "attributes",
            "variants", "available_colors", "category_name", "additional_images",
        ]

    output = {
        "researched_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": "Shopee short-link redirects and existing signed Affiliate productOfferV2 client",
        "notes": [
            "api_product preserves every field returned by the existing productOfferV2 query.",
            "The API schema exposes no description, variant names, review count, original price or image gallery in ProductOfferV2.",
            "main_image_color_observed and evidence are visual observations of imageUrl, not API variant data.",
            "Final redirect URLs omit affiliate tracking query values; their parameter names remain in redirect_query_keys.",
            "Product labels and description letters originate from the user's supplied list, not verified brands or materials.",
        ],
        "products": records,
    }
    path = ROOT / "data" / "research" / "bolsas_shopee_mapping.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    csv_path = path.with_suffix(".csv")
    fields = [
        "number", "short_url", "item_id", "shop_id", "canonical_url",
        "final_url_without_tracking", "title", "shop_name", "price",
        "price_min", "price_max", "discount_rate", "currency", "rating",
        "review_count", "sales", "main_image", "additional_images",
        "variations", "available_colors", "description", "attributes",
        "category_ids", "category_name", "commission_rate", "commission",
        "api_offer_link", "description_letter", "product_label",
        "main_image_color_observed", "confidence", "evidence", "issue",
        "api_status",
    ]
    with csv_path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for record in records:
            node = record.get("api_product") or {}
            mapping = record["mapping"]
            writer.writerow({
                "number": record["number"],
                "short_url": record["short_url"],
                "item_id": record.get("item_id", "NÃO CONFIRMADO"),
                "shop_id": record.get("shop_id", "NÃO CONFIRMADO"),
                "canonical_url": record.get("canonical_url", "NÃO CONFIRMADO"),
                "final_url_without_tracking": record.get("final_url_without_tracking", "NÃO CONFIRMADO"),
                "title": node.get("productName", "NÃO CONFIRMADO"),
                "shop_name": node.get("shopName", "NÃO CONFIRMADO"),
                "price": node.get("price", "NÃO CONFIRMADO"),
                "price_min": node.get("priceMin", "NÃO CONFIRMADO"),
                "price_max": node.get("priceMax", "NÃO CONFIRMADO"),
                "discount_rate": node.get("priceDiscountRate", "NÃO CONFIRMADO"),
                "currency": "NÃO CONFIRMADO",
                "rating": node.get("ratingStar", "NÃO CONFIRMADO"),
                "review_count": "NÃO CONFIRMADO",
                "sales": node.get("sales", "NÃO CONFIRMADO"),
                "main_image": node.get("imageUrl", "NÃO CONFIRMADO"),
                "additional_images": "NÃO CONFIRMADO",
                "variations": "NÃO CONFIRMADO",
                "available_colors": "NÃO CONFIRMADO",
                "description": "NÃO CONFIRMADO",
                "attributes": "NÃO CONFIRMADO",
                "category_ids": json.dumps(node.get("productCatIds"), ensure_ascii=False) if node else "NÃO CONFIRMADO",
                "category_name": "NÃO CONFIRMADO",
                "commission_rate": node.get("commissionRate", "NÃO CONFIRMADO"),
                "commission": node.get("commission", "NÃO CONFIRMADO"),
                "api_offer_link": node.get("offerLink", "NÃO CONFIRMADO"),
                "description_letter": mapping["description_letter"] or "NÃO CONFIRMADO",
                "product_label": mapping["product_label_from_user"] or "NÃO CONFIRMADO",
                "main_image_color_observed": mapping["main_image_color_observed"] or "NÃO CONFIRMADO",
                "confidence": mapping["confidence"],
                "evidence": mapping["evidence"],
                "issue": mapping["issue"] or "",
                "api_status": record.get("api_status", "NÃO CONFIRMADO"),
            })
    print(f"Saved {path}", flush=True)
    print(f"Saved {csv_path}", flush=True)


if __name__ == "__main__":
    main()
