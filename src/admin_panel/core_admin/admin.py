from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from .models import Exam, ExamEvent, PageMetadata, StatusChangeEvent, MonitoringConfig, ManualReviewQueue


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "category", "status", "is_active")
    search_fields = ("name", "organization", "slug")
    list_filter = ("category", "status", "is_active")
    ordering = ("name",)


@admin.register(ExamEvent)
class ExamEventAdmin(admin.ModelAdmin):
    list_display = ("exam", "year", "event_type", "status", "event_date")
    search_fields = ("exam__name", "event_type")
    list_filter = ("event_type", "status", "year")
    ordering = ("-year",)


@admin.register(PageMetadata)
class PageMetadataAdmin(admin.ModelAdmin):
    list_display = ("slug", "page_type", "page_views", "needs_regeneration")
    search_fields = ("slug", "title")
    list_filter = ("page_type", "needs_regeneration")
    ordering = ("-page_views",)


@admin.register(StatusChangeEvent)
class StatusChangeEventAdmin(admin.ModelAdmin):
    list_display = ("exam", "change_type", "old_status", "new_status", "confidence_score", "detected_at")
    search_fields = ("exam__name", "change_type")
    list_filter = ("change_type",)
    ordering = ("-detected_at",)


@admin.register(MonitoringConfig)
class MonitoringConfigAdmin(admin.ModelAdmin):
    list_display = ("exam", "priority", "check_frequency_minutes", "is_active", "last_checked")
    list_filter = ("priority", "is_active")
    search_fields = ("exam__name",)


@admin.register(ManualReviewQueue)
class ManualReviewQueueAdmin(admin.ModelAdmin):
    list_display = ("event", "priority", "status", "due_at", "created_at")
    list_filter = ("priority", "status")
    ordering = ("-created_at",)


@admin.register(LogEntry)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action_time", "user", "content_type", "object_repr", "action_flag")
    list_filter = ("action_flag", "content_type")
    search_fields = ("object_repr", "user__username")
    ordering = ("-action_time",)
    readonly_fields = (
        "action_time",
        "user",
        "content_type",
        "object_id",
        "object_repr",
        "action_flag",
        "change_message",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
