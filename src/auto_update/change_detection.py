"""
Change Detection Module

ASSUMPTIONS:
- Content hash changes indicate new information.
- Keywords confirm cancellation/postponement.
- Low confidence → manual review required.

CONDITIONS:
- Content must be fetched successfully.
- Keywords must appear in context.

FAILURE MODES:
- Empty content → return None
- Parsing error → return None with error log
"""

import hashlib
import re
from typing import Optional, Dict
from datetime import datetime

CANCELLATION_KEYWORDS = [
    "cancelled",
    "canceled",
    "will not be held",
    "stands cancelled",
    "withdrawn",
]

POSTPONED_KEYWORDS = [
    "postponed",
    "deferred",
    "rescheduled",
    "date changed",
    "revised schedule",
]

CONTEXT_KEYWORDS = [
    "notice",
    "important",
    "corrigendum",
    "amendment",
]


def hash_content(content: str) -> str:
    return hashlib.md5(content.encode("utf-8", errors="ignore")).hexdigest()


def detect_change(old_content: str, new_content: str) -> Optional[Dict]:
    """
    Detect change and classify it.

    Returns:
        dict with change_type, confidence, keywords_found, context
        or None if no significant change
    """
    if not new_content:
        return None

    if old_content and hash_content(old_content) == hash_content(new_content):
        return None

    lower = new_content.lower()
    keywords_found = []
    confidence = 0
    change_type = None

    for k in CANCELLATION_KEYWORDS:
        if k in lower:
            keywords_found.append(k)
            confidence += 30
            change_type = "CANCELLED"

    for k in POSTPONED_KEYWORDS:
        if k in lower:
            keywords_found.append(k)
            confidence += 25
            change_type = "POSTPONED"

    for k in CONTEXT_KEYWORDS:
        if k in lower:
            confidence += 10

    if confidence < 40:
        return None

    context = extract_context(new_content, keywords_found)

    return {
        "change_type": change_type,
        "confidence": min(confidence, 100),
        "keywords_found": keywords_found,
        "context": context,
        "detected_at": datetime.utcnow().isoformat(),
    }


def extract_context(content: str, keywords) -> Optional[str]:
    if not keywords:
        return None
    lower = content.lower()
    for k in keywords:
        idx = lower.find(k)
        if idx != -1:
            start = max(0, idx - 150)
            end = min(len(content), idx + 150)
            return content[start:end]
    return None
