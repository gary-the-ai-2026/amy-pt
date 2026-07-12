#!/usr/bin/env python3
"""
Food macro lookup via Open Food Facts (Australian products).

Usage:
    food_lookup.py --search "Bonsoy soy milk"
    food_lookup.py --barcode 9300633556150
    food_lookup.py --search "Uncle Tobys rolled oats" --json

Rate limited to 1 request per 2 seconds internally.
"""
import sys
import json
import time
import urllib.parse
import urllib.request
import argparse
from pathlib import Path

# Internal cooldown tracker
_last_call = 0.0
MIN_INTERVAL = 2.0  # seconds

AU_BASE = "https://world.openfoodfacts.net"


def _throttle():
    global _last_call
    elapsed = time.time() - _last_call
    if elapsed < MIN_INTERVAL:
        time.sleep(MIN_INTERVAL - elapsed)
    _last_call = time.time()


def _api_get(url: str) -> dict:
    """GET JSON from Open Food Facts with throttling."""
    _throttle()
    req = urllib.request.Request(url, headers={"User-Agent": "Gary-PA/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e), "status": 0}


def search(term: str, page_size: int = 1) -> dict:
    """Search for a food product by name. Returns parsed product dict or error."""
    params = urllib.parse.urlencode({
        "search_terms": term,
        "search_simple": "1",
        "json": "1",
        "page_size": str(page_size),
        "fields": "product_name,brands,nutriments,code",
        "sort_by": "unique_scans_n",
    })
    url = f"{AU_BASE}/cgi/search.pl?{params}"
    data = _api_get(url)
    if "error" in data:
        return data
    products = data.get("products", [])
    if not products:
        return {"error": "no products found", "status": 0}
    return products[0]


def barcode(code: str) -> dict:
    """Look up a product by barcode. Returns parsed product dict or error."""
    params = urllib.parse.urlencode({"fields": "product_name,brands,nutriments,code"})
    url = f"{AU_BASE}/api/v2/product/{code}?{params}"
    data = _api_get(url)
    if "error" in data:
        return data
    if data.get("status") != 1:
        return {"error": data.get("status_verbose", "product not found"), "status": 0}
    return data["product"]


def extract_macros(product: dict) -> dict:
    """Extract standardised macros from an OFF product dict."""
    n = product.get("nutriments", {})
    return {
        "product_name": product.get("product_name", "Unknown"),
        "brands": product.get("brands", ""),
        "barcode": product.get("code", ""),
        "per_100g": {
            "protein": n.get("proteins_100g"),
            "fat": n.get("fat_100g"),
            "carbs": n.get("carbohydrates_100g"),
            "fibre": n.get("fiber_100g"),
            "energy_kcal": n.get("energy-kcal_100g"),
        },
        "source": "world.openfoodfacts.net",
    }


def lookup(term: str | None = None, code: str | None = None) -> dict:
    """Main entry point. Returns standardised macro dict or error."""
    if code:
        product = barcode(code)
    elif term:
        product = search(term)
    else:
        return {"error": "must provide --search or --barcode"}

    if "error" in product:
        return product

    return extract_macros(product)


def main():
    parser = argparse.ArgumentParser(description="Food macro lookup via Open Food Facts")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--search", "-s", type=str, help="Search term (e.g. 'Bonsoy soy milk')")
    group.add_argument("--barcode", "-b", type=str, help="Barcode (e.g. 9300633556150)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    result = lookup(term=args.search, code=args.barcode)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if "error" in result:
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)
        m = result["per_100g"]
        print(f"{result['product_name']}  ({result['brands']})")
        print(f"  Protein: {m['protein']}g  |  Fat: {m['fat']}g  |  Carbs: {m['carbs']}g")
        print(f"  Fibre:   {m['fibre']}g  |  Energy: {m['energy_kcal']} kcal")
        print(f"  Source:  {result['source']}")


if __name__ == "__main__":
    main()
