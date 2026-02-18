"""
Verification Module

ASSUMPTIONS:
- Official domains are trusted sources.
- Secondary trusted sources can confirm changes.

CONDITIONS:
- Official source → auto-approve if confidence >= 70
- Otherwise require 2 independent confirmations
"""

from urllib.parse import urlparse

TRUSTED_DOMAINS = {
    "upsc.gov.in",
    "ssc.nic.in",
    "ibps.in",
    "rbi.org.in",
    "rrbcdg.gov.in",
    "employmentnews.gov.in",
    "pib.gov.in",
}


def is_official_source(url: str) -> bool:
    try:
        domain = urlparse(url).netloc.replace("www.", "")
        return domain in TRUSTED_DOMAINS
    except Exception:
        return False


def should_auto_approve(source_url: str, confidence: int, confirmations: int) -> bool:
    if is_official_source(source_url) and confidence >= 70:
        return True
    if confirmations >= 2:
        return True
    return False
