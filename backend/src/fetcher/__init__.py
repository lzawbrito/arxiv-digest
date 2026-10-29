"""HTML fetcher and crawler for arXiv papers."""

from .arxiv_fetcher import fetch_arxiv_papers
from .author_fetcher import fetch_author_papers, normalize_subscription
from .html_crawler import ArxivHTMLCrawler

__all__ = [
    "ArxivHTMLCrawler",
    "fetch_arxiv_papers",
    "fetch_author_papers",
    "normalize_subscription",
]
