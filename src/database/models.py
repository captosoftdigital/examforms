"""
Database Models for ExamForms.org
Using SQLAlchemy ORM
"""

from sqlalchemy import Column, Integer, String, Date, Boolean, DECIMAL, ForeignKey, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Exam(Base):
    """
    Main exam table
    Stores basic information about each exam
    """
    __tablename__ = 'exams'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(500), nullable=False)
    slug = Column(String(500), unique=True, nullable=False, index=True)
    organization = Column(String(255))
    category = Column(String(100))  # Central/State/University/Banking/Defense
    exam_type = Column(String(100))  # Recruitment/Scholarship/Fellowship/Entrance
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    events = relationship('ExamEvent', back_populates='exam')
    eligibility = relationship('Eligibility', back_populates='exam')
    patterns = relationship('ExamPattern', back_populates='exam')
    
    def __repr__(self):
        return f"<Exam(id={self.id}, name='{self.name}')>"


class ExamEvent(Base):
    """
    Exam events table
    Stores notifications, forms, admit cards, results, etc.
    """
    __tablename__ = 'exam_events'
    
    id = Column(Integer, primary_key=True)
    exam_id = Column(Integer, ForeignKey('exams.id'), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)  
    # notification/form/admit_card/result/answer_key/cutoff
    
    event_date = Column(Date)
    application_start = Column(Date)
    application_end = Column(Date)
    exam_date = Column(Date)
    
    status = Column(String(50), default='upcoming')  # upcoming/active/completed
    
    official_link = Column(Text)
    pdf_link = Column(Text)
    download_link = Column(Text)
    
    total_vacancies = Column(Integer)
    
    # Flexible metadata storage
    details = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    exam = relationship('Exam', back_populates='events')
    results = relationship('Result', back_populates='event')
    
    def __repr__(self):
        return f"<ExamEvent(id={self.id}, exam_id={self.exam_id}, type='{self.event_type}', year={self.year})>"


class Eligibility(Base):
    """
    Eligibility criteria for exams
    """
    __tablename__ = 'eligibility'
    
    id = Column(Integer, primary_key=True)
    exam_id = Column(Integer, ForeignKey('exams.id'), nullable=False)
    year = Column(Integer)
    
    min_age = Column(Integer)
    max_age = Column(Integer)
    age_relaxation = Column(JSON)  # Category-wise relaxation
    
    education_qualification = Column(Text)
    nationality = Column(Text)
    
    additional_criteria = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    exam = relationship('Exam', back_populates='eligibility')
    
    def __repr__(self):
        return f"<Eligibility(exam_id={self.exam_id}, year={self.year})>"


class ExamPattern(Base):
    """
    Exam pattern and syllabus
    """
    __tablename__ = 'exam_patterns'
    
    id = Column(Integer, primary_key=True)
    exam_id = Column(Integer, ForeignKey('exams.id'), nullable=False)
    year = Column(Integer)
    
    total_marks = Column(Integer)
    duration_minutes = Column(Integer)
    
    # JSON structure: [{"section": "General Awareness", "marks": 50, "questions": 50}]
    sections = Column(JSON)
    
    negative_marking = Column(Boolean, default=False)
    negative_marking_details = Column(Text)
    
    exam_mode = Column(String(50))  # Online/Offline/Both
    
    pattern_details = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    exam = relationship('Exam', back_populates='patterns')
    
    def __repr__(self):
        return f"<ExamPattern(exam_id={self.exam_id}, year={self.year})>"


class Result(Base):
    """
    Results and cutoffs
    """
    __tablename__ = 'results'
    
    id = Column(Integer, primary_key=True)
    exam_event_id = Column(Integer, ForeignKey('exam_events.id'), nullable=False)
    
    result_date = Column(Date)
    
    # Category-wise cutoffs
    cutoff_general = Column(DECIMAL(10, 2))
    cutoff_obc = Column(DECIMAL(10, 2))
    cutoff_sc = Column(DECIMAL(10, 2))
    cutoff_st = Column(DECIMAL(10, 2))
    cutoff_ews = Column(DECIMAL(10, 2))
    
    # Statistics
    total_appeared = Column(Integer)
    total_qualified = Column(Integer)
    
    result_pdf_link = Column(Text)
    
    # Additional cutoff data (state-wise, post-wise)
    additional_cutoffs = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    event = relationship('ExamEvent', back_populates='results')
    
    def __repr__(self):
        return f"<Result(event_id={self.exam_event_id})>"


class PageMetadata(Base):
    """
    SEO metadata for generated pages
    """
    __tablename__ = 'page_metadata'
    
    id = Column(Integer, primary_key=True)
    page_type = Column(String(50), nullable=False)  # notification/admit_card/result/etc
    exam_id = Column(Integer, ForeignKey('exams.id'))
    year = Column(Integer)
    
    slug = Column(String(500), unique=True, nullable=False, index=True)
    title = Column(String(255))
    meta_description = Column(Text)
    canonical_url = Column(Text)
    
    # Schema.org markup
    schema_markup = Column(JSON)
    
    # Analytics
    page_views = Column(Integer, default=0)
    last_crawled = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<PageMetadata(slug='{self.slug}')>"


class ScraperLog(Base):
    """
    Track scraping activity
    """
    __tablename__ = 'scraper_logs'
    
    id = Column(Integer, primary_key=True)
    scraper_name = Column(String(100), nullable=False)
    source_url = Column(Text)
    
    status = Column(String(50))  # success/failed/partial
    items_scraped = Column(Integer, default=0)
    
    error_message = Column(Text)
    
    started_at = Column(DateTime, default=datetime.now)
    completed_at = Column(DateTime)
    
    def __repr__(self):
        return f"<ScraperLog(scraper='{self.scraper_name}', status='{self.status}')>"
