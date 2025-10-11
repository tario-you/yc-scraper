import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Iterable, List, Tuple

import requests
from tqdm import tqdm

ALGOLIA_APP_ID_ENV = "ALGOLIA_APP_ID"
ALGOLIA_API_KEY_ENV = "ALGOLIA_API_KEY"
ALGOLIA_INDEX_ENV = "ALGOLIA_INDEX"
DEFAULT_ALGOLIA_INDEX = "YCCompany_production"
START_URLS_FILE = Path("scrapy-project/ycombinator/start_urls.txt")


def resolve_algolia_config() -> Tuple[str, str, str]:
    """Read Algolia credentials from environment variables."""

    app_id = os.getenv(ALGOLIA_APP_ID_ENV)
    api_key = os.getenv(ALGOLIA_API_KEY_ENV)
    index_name = os.getenv(ALGOLIA_INDEX_ENV, DEFAULT_ALGOLIA_INDEX)

    missing = [
        name
        for name, value in (
            (ALGOLIA_APP_ID_ENV, app_id),
            (ALGOLIA_API_KEY_ENV, api_key),
        )
        if not value
    ]
    if missing:
        joined = ", ".join(missing)
        raise RuntimeError(
            "Missing required environment variable(s): "
            f"{joined}. Set them before running the extractor."
        )

    return app_id, api_key, index_name


def _build_endpoint(app_id: str, index: str) -> str:
    return f"https://{app_id.lower()}-dsn.algolia.net/1/indexes/{index}/query"


def fetch_batches(endpoint: str, headers: dict) -> List[str]:
    """Return the list of YC batches present in the Algolia index."""
    response = requests.post(
        endpoint,
        headers=headers,
        json={"query": "", "hitsPerPage": 1, "facets": ["batch"]},
        timeout=30,
    )
    response.raise_for_status()
    facets = response.json().get("facets", {}).get("batch", {})
    return sorted(facets.keys())


def fetch_batch_urls(
    batch: str,
    endpoint: str,
    headers: dict,
    hits_per_page: int = 500,
) -> Tuple[str, List[str]]:
    """Retrieve company URLs for a given batch."""
    urls: List[str] = []
    page = 0
    while True:
        payload = {
            "query": "",
            "hitsPerPage": hits_per_page,
            "page": page,
            "facetFilters": [[f"batch:{batch}"]],
        }
        response = requests.post(
            endpoint, headers=headers, json=payload, timeout=30
        )
        response.raise_for_status()
        data = response.json()
        hits = data.get("hits", [])
        if not hits:
            break
        urls.extend(
            f"https://www.ycombinator.com/companies/{hit['slug']}" for hit in hits
        )
        page += 1
        if page >= data.get("nbPages", 0):
            break
    return batch, urls


def fetch_all_urls(
    batches: Iterable[str], endpoint: str, headers: dict, workers: int = 8
) -> List[str]:
    """Fetch URLs for all batches in parallel."""
    results: List[str] = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(fetch_batch_urls, batch, endpoint, headers): batch
            for batch in batches
        }
        progress = tqdm(as_completed(futures), total=len(futures), desc="Batches")
        for future in progress:
            batch = futures[future]
            try:
                _, urls = future.result()
                results.extend(urls)
            except Exception as exc:  # pragma: no cover - logging only
                print(f"Failed to fetch batch {batch}: {exc}")
    return sorted(set(results))


def write_urls_to_file(urls: List[str]) -> None:
    """Write the collected URLs to disk."""
    START_URLS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with START_URLS_FILE.open("w", encoding="utf-8") as f:
        json.dump(urls, f)


def yc_links_extractor() -> None:
    """Generate start URLs for all YC companies using the Algolia API."""
    app_id, api_key, index_name = resolve_algolia_config()
    endpoint = _build_endpoint(app_id, index_name)
    headers = {
        "x-algolia-api-key": api_key,
        "x-algolia-application-id": app_id,
        "Content-Type": "application/json",
    }

    print("Fetching batch list from Algolia…")
    batches = fetch_batches(endpoint, headers)
    print(f"Processing {len(batches)} batches in parallel…")
    urls = fetch_all_urls(batches, endpoint, headers)
    print(f"Collected {len(urls)} unique company URLs.")
    write_urls_to_file(urls)
    print(f"Wrote URLs to {START_URLS_FILE}")


if __name__ == "__main__":
    yc_links_extractor()
