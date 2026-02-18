"""URL configuration for admin panel"""
from django.contrib import admin
from django.urls import path

admin.site.site_header = "ExamForms Admin"
admin.site.site_title = "ExamForms Admin"
admin.site.index_title = "Operational Dashboard"

urlpatterns = [
    path("admin/", admin.site.urls),
]
