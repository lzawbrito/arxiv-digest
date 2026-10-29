"""JSON exporter for subscribed-author papers."""

import json
from datetime import UTC, datetime
from pathlib import Path

from loguru import logger


def export_author_papers(
    papers: list[dict],
    authors: list[str],
    lookback_days: int,
    output_path: str = "frontend/public/authors.json",
) -> None:
    """
    Export subscribed-author papers to a JSON file for the frontend's Authors tab.

    Args:
        papers: Paper dicts from fetch_author_papers
        authors: The subscribed author names, in config order
        lookback_days: Lookback window the papers were fetched with
        output_path: Output file path
    """
    output_data = {
        "metadata": {
            "timestamp": datetime.now(UTC).isoformat(),
            "authors": authors,
            "lookback_days": lookback_days,
        },
        "papers": [
            {
                "arxiv_id": paper["id"],
                "title": paper["title"],
                "authors": paper["authors"],
                "categories": paper["categories"],
                "abstract": paper["abstract"],
                "pdf_url": paper["pdf_url"],
                "abs_url": paper["abs_url"],
                "published": paper["published"],
                "updated": paper["updated"],
                "matched_authors": paper["matched_authors"],
                "highlight_authors": paper["highlight_authors"],
            }
            for paper in papers
        ],
    }

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    logger.success(f"Subscribed-author papers exported to: {output_path}")
