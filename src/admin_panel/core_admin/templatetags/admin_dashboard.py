"""Admin dashboard template tags.

Assumptions:
- Django admin is used for internal operations only.
- Queries must be fast; use lightweight counts.
- Database tables exist and are populated.
"""

from django import template
from django.db.models import Count
from core_admin.models import Exam, ExamEvent, PageMetadata, StatusChangeEvent, ManualReviewQueue

register = template.Library()


@register.inclusion_tag("admin/dashboard_cards.html")
def dashboard_cards():
    """Provide summary metrics for admin dashboard."""
    return {
        "exam_count": Exam.objects.count(),
        "active_exams": Exam.objects.filter(is_active=True).count(),
        "event_count": ExamEvent.objects.count(),
        "pages_needing_regen": PageMetadata.objects.filter(needs_regeneration=True).count(),
        "pending_reviews": ManualReviewQueue.objects.filter(status__in=["PENDING", "IN_PROGRESS"]).count(),
        "recent_status_changes": StatusChangeEvent.objects.order_by("-detected_at")[:5],
    }
