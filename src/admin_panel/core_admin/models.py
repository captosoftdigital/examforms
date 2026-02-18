"""Django models for ExamForms.org admin panel.

For development: managed = True (Django creates tables)
For production: managed = False (tables managed externally)
"""
from django.db import models


class Exam(models.Model):
    name = models.CharField(max_length=500)
    slug = models.CharField(max_length=500, unique=True, db_index=True)
    organization = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    category = models.CharField(max_length=100, null=True, blank=True)
    exam_type = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = "exams"

    def __str__(self):
        return self.name


class ExamEvent(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='events')
    year = models.IntegerField(db_index=True)
    event_type = models.CharField(max_length=50, db_index=True)  
    
    event_date = models.DateField(null=True, blank=True)
    application_start = models.DateField(null=True, blank=True)
    application_end = models.DateField(null=True, blank=True)
    exam_date = models.DateField(null=True, blank=True)
    
    status = models.CharField(max_length=50, default='upcoming', db_index=True)  # upcoming/active/completed
    
    official_link = models.TextField(null=True, blank=True)
    pdf_link = models.TextField(null=True, blank=True)
    download_link = models.TextField(null=True, blank=True)
    
    total_vacancies = models.IntegerField(null=True, blank=True)
    
    # Flexible metadata storage
    details = models.JSONField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = "exam_events"

    def __str__(self):
        return f"{self.exam.name} {self.year} {self.event_type}"


class Eligibility(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='eligibility')
    year = models.IntegerField(null=True, blank=True)
    
    min_age = models.IntegerField(null=True, blank=True)
    max_age = models.IntegerField(null=True, blank=True)
    age_relaxation = models.JSONField(null=True, blank=True)  # Category-wise relaxation
    
    education_qualification = models.TextField(null=True, blank=True)
    nationality = models.TextField(null=True, blank=True)
    
    additional_criteria = models.JSONField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = "eligibility"


class ExamPattern(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='patterns')
    year = models.IntegerField(null=True, blank=True)
    
    total_marks = models.IntegerField(null=True, blank=True)
    duration_minutes = models.IntegerField(null=True, blank=True)
    
    # JSON structure: [{"section": "General Awareness", "marks": 50, "questions": 50}]
    sections = models.JSONField(null=True, blank=True)
    
    negative_marking = models.BooleanField(default=False)
    negative_marking_details = models.TextField(null=True, blank=True)
    
    exam_mode = models.CharField(max_length=50, null=True, blank=True)  # Online/Offline/Both
    
    pattern_details = models.JSONField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = "exam_patterns"


class Result(models.Model):
    exam_event = models.ForeignKey(ExamEvent, on_delete=models.CASCADE, related_name='results')
    
    result_date = models.DateField(null=True, blank=True)
    
    # Category-wise cutoffs
    cutoff_general = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cutoff_obc = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cutoff_sc = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cutoff_st = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cutoff_ews = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Statistics
    total_appeared = models.IntegerField(null=True, blank=True)
    total_qualified = models.IntegerField(null=True, blank=True)
    
    result_pdf_link = models.TextField(null=True, blank=True)
    
    # Additional cutoff data (state-wise, post-wise)
    additional_cutoffs = models.JSONField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = "results"


class PageMetadata(models.Model):
    page_type = models.CharField(max_length=50)  # notification/admit_card/result/etc
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    
    slug = models.CharField(max_length=500, unique=True, db_index=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    meta_description = models.TextField(null=True, blank=True)
    canonical_url = models.TextField(null=True, blank=True)
    
    # Schema.org markup
    schema_markup = models.JSONField(null=True, blank=True)
    
    # Analytics
    page_views = models.IntegerField(default=0)
    last_crawled = models.DateTimeField(null=True, blank=True)
    
    needs_regeneration = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = "page_metadata"

    def __str__(self):
        return self.slug


class StatusChangeEvent(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    old_status = models.CharField(max_length=50)
    new_status = models.CharField(max_length=50)
    change_type = models.CharField(max_length=50)
    confidence_score = models.IntegerField()
    source_url = models.TextField()
    detected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = "status_change_events"

    def __str__(self):
        return f"{self.exam.name} {self.change_type}"


class MonitoringConfig(models.Model):
    exam = models.OneToOneField(Exam, on_delete=models.CASCADE)
    urls_to_monitor = models.JSONField()
    check_frequency_minutes = models.IntegerField()
    priority = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    last_checked = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = True
        db_table = "monitoring_config"

    def __str__(self):
        return f"{self.exam.name} monitoring"


class ManualReviewQueue(models.Model):
    event = models.ForeignKey(StatusChangeEvent, on_delete=models.CASCADE)
    priority = models.CharField(max_length=20)
    status = models.CharField(max_length=50)
    due_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = "manual_review_queue"

    def __str__(self):
        return f"Review {self.event.exam.name}"


class ScraperLog(models.Model):
    scraper_name = models.CharField(max_length=100)
    source_url = models.TextField(null=True, blank=True)
    
    status = models.CharField(max_length=50, null=True, blank=True)  # success/failed/partial
    items_scraped = models.IntegerField(default=0)
    
    error_message = models.TextField(null=True, blank=True)
    
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = True
        db_table = "scraper_logs"

    def __str__(self):
        return f"{self.scraper_name} - {self.status}"
