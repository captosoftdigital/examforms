# Auto-Update System - Assumptions & Boundaries

## Assumptions (Before Code)

1. Official sources are authoritative (upsc.gov.in, ssc.nic.in, etc.).
2. Monitoring URLs are maintained in `monitoring_config` table.
3. Changes are detectable via keyword + content hash comparison.
4. False positives must be reduced via verification (confidence scoring).
5. System can degrade safely if sources are down.

## Conditions for Success
- URLs are accessible within timeout
- New content differs from stored hash
- Keywords detected with sufficient confidence
- Verification passes (official domain OR 2 trusted sources)

## Failure Modes
- Source unavailable → log + retry later
- HTML structure changes → lower confidence
- Keyword false match → manual review
- Database failure → backup log written

## Non-Goals (for now)
- Full ML classification
- NLP semantic change detection
- User notification system

