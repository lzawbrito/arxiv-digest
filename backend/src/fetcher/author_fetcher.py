"""Fetcher for recent papers by subscribed authors, via the arXiv API."""

import re
import time
import unicodedata
import urllib.parse
import urllib.request
from datetime import UTC, datetime, timedelta

from bs4 import BeautifulSoup
from loguru import logger

ARXIV_API_URL = "https://export.arxiv.org/api/query"

# arXiv asks API clients to wait 3 seconds between consecutive requests.
REQUEST_DELAY_SECONDS = 3.0


def normalize_subscription(entry: str | dict) -> tuple[str, list[str]]:
    """
    Normalize a config subscription entry to (name, categories).

    Entries are either a bare name ("Nathan Seiberg") or a dict with a "name" and
    optional "categories" list, used to disambiguate common names by restricting
    matches to the author's fields (e.g., {"name": "Meng Cheng", "categories":
    ["cond-mat.str-el", "hep-th"]}).
    """
    if isinstance(entry, str):
        return entry, []
    return entry["name"], entry.get("categories") or []


def _name_tokens(name: str) -> list[str]:
    """Lowercase, accent-free name tokens, ignoring periods (e.g. "Juven C. Wang")."""
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return ascii_name.lower().replace(".", " ").split()


def _same_author(subscribed: str, listed: str) -> bool:
    """
    Whether an author as listed on a paper is the subscribed author.

    arXiv's au: search ignores name order, so "Meng Cheng" also returns papers by
    "Cheng Meng". Requiring the first and last names to match in order rejects
    those while still accepting middle names/initials ("Juven C. Wang").
    """
    sub, lst = _name_tokens(subscribed), _name_tokens(listed)
    if not sub or not lst:
        return False
    return sub[0] == lst[0] and sub[-1] == lst[-1]


def _query_author(name: str, categories: list[str], max_results: int) -> list[dict]:
    """
    Query the arXiv API for an author's most recently submitted papers.

    Args:
        name: Author's full name as it appears on arXiv (e.g., "Nathan Seiberg")
        categories: If non-empty, only match papers cross-listed in one of these
            arXiv categories (e.g., ["hep-th", "cond-mat.str-el"])
        max_results: Maximum number of entries to request

    Returns:
        List of paper dicts with keys: id, title, authors, categories, abstract,
        abs_url, pdf_url, published, updated
    """
    search_query = f'au:"{name}"'
    if categories:
        search_query += " AND (" + " OR ".join(f"cat:{c}" for c in categories) + ")"

    params = urllib.parse.urlencode(
        {
            "search_query": search_query,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
            "max_results": max_results,
        }
    )
    url = f"{ARXIV_API_URL}?{params}"
    logger.info(f"Fetching papers by '{name}' from {url}")

    with urllib.request.urlopen(url, timeout=30) as response:
        soup = BeautifulSoup(response, features="xml")

    papers = []
    for entry in soup.find_all("entry"):
        try:
            # Entry ids look like http://arxiv.org/abs/2610.22485v1; strip the version
            # so ids line up with the daily digest's.
            raw_id = entry.find("id").text.strip().split("/abs/")[-1]
            paper_id = re.sub(r"v\d+$", "", raw_id)

            primary = entry.find("primary_category")
            categories = [c["term"] for c in entry.find_all("category")]
            # Keep the primary category first, matching arXiv's listing order.
            if primary and primary.get("term") in categories:
                categories.remove(primary["term"])
                categories.insert(0, primary["term"])

            papers.append(
                {
                    "id": paper_id,
                    # Titles and abstracts are hard-wrapped in the feed.
                    "title": " ".join(entry.find("title").text.split()),
                    "authors": [a.find("name").text.strip() for a in entry.find_all("author")],
                    "categories": categories,
                    "abstract": " ".join(entry.find("summary").text.split()),
                    "abs_url": f"https://arxiv.org/abs/{paper_id}",
                    "pdf_url": f"https://arxiv.org/pdf/{paper_id}",
                    "published": entry.find("published").text.strip(),
                    "updated": entry.find("updated").text.strip(),
                }
            )
        except Exception as e:
            logger.warning(f"Error parsing arXiv API entry for author '{name}': {e}")
            continue

    return papers


def fetch_author_papers(
    authors: list[str | dict],
    lookback_days: int = 30,
    max_per_author: int = 25,
) -> list[dict]:
    """
    Fetch papers first submitted within the lookback window by any subscribed author.

    Args:
        authors: Subscription entries, each a name or a {name, categories} dict
            (see normalize_subscription)
        lookback_days: Only keep papers whose first version is at most this many days old
        max_per_author: Maximum number of API results to request per author

    Returns:
        Deduplicated list of paper dicts (newest first), each with an extra
        "matched_authors" key listing which subscribed authors are on the paper and a
        "highlight_authors" key with those authors as spelled in the paper's author list
    """
    cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
    papers_dict: dict[str, dict] = {}

    for i, entry in enumerate(authors):
        if i > 0:
            time.sleep(REQUEST_DELAY_SECONDS)

        name, categories = normalize_subscription(entry)
        try:
            author_papers = _query_author(name, categories, max_per_author)
        except Exception as e:
            # One author failing (rate limit, network hiccup) shouldn't drop the rest.
            logger.error(f"Failed to fetch papers for author '{name}': {e}")
            continue

        kept = 0
        for paper in author_papers:
            # The API sorts by latest-version date, so old papers with fresh revisions
            # show up too; filter on the first-version date to keep only new work.
            published = datetime.fromisoformat(paper["published"].replace("Z", "+00:00"))
            if published < cutoff:
                continue

            spellings = [a for a in paper["authors"] if _same_author(name, a)]
            if not spellings:
                continue

            kept += 1
            if paper["id"] not in papers_dict:
                papers_dict[paper["id"]] = {**paper, "matched_authors": [], "highlight_authors": []}
            papers_dict[paper["id"]]["matched_authors"].append(name)
            papers_dict[paper["id"]]["highlight_authors"].extend(spellings)

        logger.info(f"Found {kept} papers by '{name}' in the last {lookback_days} days")

    papers = sorted(papers_dict.values(), key=lambda p: p["published"], reverse=True)
    logger.info(f"Total unique subscribed-author papers: {len(papers)}")

    return papers
