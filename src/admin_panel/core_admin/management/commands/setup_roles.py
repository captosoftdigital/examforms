"""Set up admin roles and permissions.

ASSUMPTIONS:
- Django auth is enabled
- Admin will use role-based access
- Permissions map to registered admin models

CONDITIONS:
- Must be run by superuser
- Idempotent: safe to re-run
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from core_admin.models import Exam, ExamEvent, PageMetadata, StatusChangeEvent, MonitoringConfig, ManualReviewQueue


ROLE_DEFINITIONS = {
    "Admin": {
        "models": [Exam, ExamEvent, PageMetadata, StatusChangeEvent, MonitoringConfig, ManualReviewQueue],
        "perms": ["add", "change", "delete", "view"],
    },
    "Editor": {
        "models": [Exam, ExamEvent, PageMetadata],
        "perms": ["add", "change", "view"],
    },
    "Reviewer": {
        "models": [StatusChangeEvent, ManualReviewQueue, MonitoringConfig],
        "perms": ["change", "view"],
    },
    "Viewer": {
        "models": [Exam, ExamEvent, PageMetadata, StatusChangeEvent, MonitoringConfig, ManualReviewQueue],
        "perms": ["view"],
    },
}


class Command(BaseCommand):
    help = "Create role-based groups with least-privilege permissions"

    def handle(self, *args, **options):
        for role_name, config in ROLE_DEFINITIONS.items():
            group, _ = Group.objects.get_or_create(name=role_name)
            group.permissions.clear()

            for model in config["models"]:
                content_type = ContentType.objects.get_for_model(model)
                for perm in config["perms"]:
                    codename = f"{perm}_{model._meta.model_name}"
                    try:
                        permission = Permission.objects.get(codename=codename, content_type=content_type)
                        group.permissions.add(permission)
                    except Permission.DoesNotExist:
                        self.stdout.write(self.style.WARNING(
                            f"Permission not found: {codename} for {model.__name__}"
                        ))

            self.stdout.write(self.style.SUCCESS(f"Role configured: {role_name}"))

        self.stdout.write(self.style.SUCCESS("All roles created/updated."))
