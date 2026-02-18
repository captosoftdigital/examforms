"""
Page Template Generator for ExamForms.org
Generates SEO-optimized pages from database data
"""

from typing import Dict, Any, List
from datetime import datetime
import json


class PageGenerator:
    """
    Generates HTML pages from templates and database data
    """
    
    def __init__(self, base_url: str = "https://examforms.org"):
        self.base_url = base_url
    
    def generate_notification_page(self, exam_data: Dict[str, Any], event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate notification page data
        """
        exam_name = exam_data['name']
        year = event_data['year']
        slug = f"{exam_data['slug']}-{year}-notification"
        
        context = {
            'page_type': 'notification',
            'slug': slug,
            'canonical_url': f"{self.base_url}/{slug}",
            
            # SEO
            'title': f"{exam_name} {year} Notification - Download PDF, Check Dates",
            'meta_description': f"Download {exam_name} {year} notification PDF. Check exam date, application process, eligibility criteria, vacancy details. Apply before {event_data.get('application_end', 'last date')}.",
            'h1': f"{exam_name} {year} Notification Released",
            
            # Content
            'exam_name': exam_name,
            'year': year,
            'organization': exam_data['organization'],
            'notification_date': event_data.get('notification_date'),
            'application_start': event_data.get('application_start'),
            'application_end': event_data.get('application_end'),
            'exam_date': event_data.get('exam_date'),
            'total_vacancies': event_data.get('total_vacancies'),
            'pdf_link': event_data.get('pdf_link'),
            'official_link': event_data.get('official_link'),
            
            # Related pages
            'related_pages': self._generate_related_links(exam_data, year),
            
            # FAQs
            'faqs': self._generate_notification_faqs(exam_name, year, event_data),
            
            # Schema markup
            'schema_markup': self._generate_schema_notification(exam_name, year, event_data),
            
            # Last updated
            'last_updated': datetime.now().isoformat()
        }
        
        return context
    
    def generate_admit_card_page(self, exam_data: Dict[str, Any], event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate admit card page data
        """
        exam_name = exam_data['name']
        year = event_data['year']
        slug = f"{exam_data['slug']}-{year}-admit-card"
        
        context = {
            'page_type': 'admit_card',
            'slug': slug,
            'canonical_url': f"{self.base_url}/{slug}",
            
            # SEO
            'title': f"{exam_name} {year} Admit Card Download - Hall Ticket Release Date",
            'meta_description': f"{exam_name} {year} admit card released. Download hall ticket from official website. Check exam date, reporting time, exam center details.",
            'h1': f"{exam_name} {year} Admit Card",
            
            # Content
            'exam_name': exam_name,
            'year': year,
            'organization': exam_data['organization'],
            'release_date': event_data.get('release_date'),
            'exam_date': event_data.get('exam_date'),
            'download_link': event_data.get('download_link'),
            'official_link': event_data.get('official_link'),
            
            # How to download steps
            'download_steps': self._generate_download_steps(exam_name),
            
            # Important instructions
            'instructions': self._generate_admit_card_instructions(),
            
            # Related pages
            'related_pages': self._generate_related_links(exam_data, year),
            
            # FAQs
            'faqs': self._generate_admit_card_faqs(exam_name, year),
            
            # Schema markup
            'schema_markup': self._generate_schema_event(exam_name, year, event_data),
            
            'last_updated': datetime.now().isoformat()
        }
        
        return context
    
    def generate_result_page(self, exam_data: Dict[str, Any], event_data: Dict[str, Any], result_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate result page data
        """
        exam_name = exam_data['name']
        year = event_data['year']
        slug = f"{exam_data['slug']}-{year}-result"
        
        context = {
            'page_type': 'result',
            'slug': slug,
            'canonical_url': f"{self.base_url}/{slug}",
            
            # SEO
            'title': f"{exam_name} {year} Result - Check Score Card, Cut Off Marks",
            'meta_description': f"{exam_name} {year} result declared. Check score card, cutoff marks category wise. Download result PDF from official website.",
            'h1': f"{exam_name} {year} Result",
            
            # Content
            'exam_name': exam_name,
            'year': year,
            'organization': exam_data['organization'],
            'result_date': event_data.get('result_date'),
            'result_link': event_data.get('result_link'),
            'pdf_link': event_data.get('pdf_link'),
            
            # Cutoff data (if available)
            'cutoffs': result_data if result_data else {},
            
            # How to check steps
            'check_steps': self._generate_result_check_steps(exam_name),
            
            # Related pages
            'related_pages': self._generate_related_links(exam_data, year),
            
            # FAQs
            'faqs': self._generate_result_faqs(exam_name, year),
            
            # Schema markup
            'schema_markup': self._generate_schema_result(exam_name, year, event_data),
            
            'last_updated': datetime.now().isoformat()
        }
        
        return context
    
    def generate_answer_key_page(self, exam_data: Dict[str, Any], event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate answer key page data
        """
        exam_name = exam_data['name']
        year = event_data['year']
        slug = f"{exam_data['slug']}-{year}-answer-key"
        
        context = {
            'page_type': 'answer_key',
            'slug': slug,
            'canonical_url': f"{self.base_url}/{slug}",
            
            # SEO
            'title': f"{exam_name} {year} Answer Key PDF Download - Official Key",
            'meta_description': f"Download {exam_name} {year} answer key PDF. Check official answer key, raise objections. Calculate expected score.",
            'h1': f"{exam_name} {year} Answer Key",
            
            # Content
            'exam_name': exam_name,
            'year': year,
            'organization': exam_data['organization'],
            'release_date': event_data.get('release_date'),
            'download_link': event_data.get('download_link'),
            'objection_start': event_data.get('objection_start'),
            'objection_end': event_data.get('objection_end'),
            
            # Related pages
            'related_pages': self._generate_related_links(exam_data, year),
            
            # FAQs
            'faqs': self._generate_answer_key_faqs(exam_name, year),
            
            'last_updated': datetime.now().isoformat()
        }
        
        return context
    
    def generate_syllabus_page(self, exam_data: Dict[str, Any], pattern_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate syllabus page data
        """
        exam_name = exam_data['name']
        slug = f"{exam_data['slug']}-syllabus"
        
        context = {
            'page_type': 'syllabus',
            'slug': slug,
            'canonical_url': f"{self.base_url}/{slug}",
            
            # SEO
            'title': f"{exam_name} Syllabus 2026 PDF Download - Complete Syllabus",
            'meta_description': f"Download {exam_name} complete syllabus PDF. Check subject wise topics, exam pattern, marking scheme.",
            'h1': f"{exam_name} Syllabus 2026",
            
            # Content
            'exam_name': exam_name,
            'organization': exam_data['organization'],
            'pattern_data': pattern_data if pattern_data else {},
            
            # Related pages
            'related_pages': self._generate_related_links(exam_data, 2026),
            
            # FAQs
            'faqs': self._generate_syllabus_faqs(exam_name),
            
            'last_updated': datetime.now().isoformat()
        }
        
        return context
    
    def _generate_related_links(self, exam_data: Dict[str, Any], year: int) -> List[Dict[str, str]]:
        """
        Generate related page links
        """
        slug = exam_data['slug']
        exam_name = exam_data['name']
        
        return [
            {
                'url': f"/{slug}-{year}-notification",
                'title': f"{exam_name} {year} Notification",
                'type': 'notification'
            },
            {
                'url': f"/{slug}-{year}-application-form",
                'title': f"{exam_name} {year} Application Form",
                'type': 'application'
            },
            {
                'url': f"/{slug}-{year}-admit-card",
                'title': f"{exam_name} {year} Admit Card",
                'type': 'admit_card'
            },
            {
                'url': f"/{slug}-{year}-answer-key",
                'title': f"{exam_name} {year} Answer Key",
                'type': 'answer_key'
            },
            {
                'url': f"/{slug}-{year}-result",
                'title': f"{exam_name} {year} Result",
                'type': 'result'
            },
            {
                'url': f"/{slug}-syllabus",
                'title': f"{exam_name} Syllabus",
                'type': 'syllabus'
            },
            {
                'url': f"/{slug}-exam-pattern",
                'title': f"{exam_name} Exam Pattern",
                'type': 'pattern'
            }
        ]
    
    def _generate_notification_faqs(self, exam_name: str, year: int, event_data: Dict) -> List[Dict[str, str]]:
        """
        Generate FAQs for notification page
        """
        return [
            {
                'question': f"When was {exam_name} {year} notification released?",
                'answer': f"The {exam_name} {year} notification was released on {event_data.get('notification_date', 'official website')}."
            },
            {
                'question': f"What is the last date to apply for {exam_name} {year}?",
                'answer': f"The last date to apply is {event_data.get('application_end', 'mentioned in official notification')}."
            },
            {
                'question': f"How many vacancies are there in {exam_name} {year}?",
                'answer': f"Total {event_data.get('total_vacancies', 'vacancies are')} announced for {exam_name} {year}."
            },
            {
                'question': f"Where can I download {exam_name} {year} notification PDF?",
                'answer': f"You can download the official notification PDF from the link provided on this page or from the official {exam_name} website."
            }
        ]
    
    def _generate_admit_card_faqs(self, exam_name: str, year: int) -> List[Dict[str, str]]:
        """
        Generate FAQs for admit card page
        """
        return [
            {
                'question': f"How to download {exam_name} {year} admit card?",
                'answer': f"Visit the official website, enter your registration number and date of birth to download {exam_name} {year} admit card."
            },
            {
                'question': f"What details are mentioned on {exam_name} admit card?",
                'answer': "Admit card contains exam date, time, exam center address, candidate details, instructions, and reporting time."
            },
            {
                'question': "What documents to carry with admit card?",
                'answer': "Carry original photo ID proof (Aadhaar/PAN/Driving License), admit card printout, and passport size photographs."
            },
            {
                'question': "What if there is an error on admit card?",
                'answer': "Contact the exam conducting authority immediately if you find any error in name, photograph, or other details."
            }
        ]
    
    def _generate_result_faqs(self, exam_name: str, year: int) -> List[Dict[str, str]]:
        """
        Generate FAQs for result page
        """
        return [
            {
                'question': f"How to check {exam_name} {year} result?",
                'answer': f"Visit the official website and enter your roll number or registration number to check {exam_name} {year} result."
            },
            {
                'question': f"What is the expected cutoff for {exam_name} {year}?",
                'answer': "Expected cutoff marks vary by category and are based on exam difficulty and number of candidates. Check category-wise cutoffs on this page."
            },
            {
                'question': "What is the next step after result declaration?",
                'answer': "Qualified candidates need to appear for the next stage (document verification/interview/skill test) as per exam pattern."
            }
        ]
    
    def _generate_answer_key_faqs(self, exam_name: str, year: int) -> List[Dict[str, str]]:
        """
        Generate FAQs for answer key page
        """
        return [
            {
                'question': f"How to download {exam_name} {year} answer key?",
                'answer': "Download the official answer key PDF from the link provided on this page or from the official website."
            },
            {
                'question': "Can I raise objections against answer key?",
                'answer': "Yes, candidates can raise objections during the objection window (usually 3-5 days) by paying a nominal fee."
            },
            {
                'question': "How to calculate score using answer key?",
                'answer': "Match your responses with the answer key. Add 1 mark for each correct answer and deduct marks for wrong answers as per negative marking scheme."
            }
        ]
    
    def _generate_syllabus_faqs(self, exam_name: str) -> List[Dict[str, str]]:
        """
        Generate FAQs for syllabus page
        """
        return [
            {
                'question': f"Where can I download {exam_name} syllabus PDF?",
                'answer': "Download the complete syllabus PDF from the official website or from the link provided on this page."
            },
            {
                'question': "Is the syllabus same every year?",
                'answer': "Generally the syllabus remains same, but candidates should check the official notification for any changes."
            }
        ]
    
    def _generate_download_steps(self, exam_name: str) -> List[str]:
        """
        Generate step-by-step download instructions
        """
        return [
            f"Visit the official {exam_name} website",
            "Click on 'Download Admit Card' or similar link",
            "Enter your Registration Number and Date of Birth",
            "Submit and download your admit card",
            "Take printout on A4 size paper",
            "Verify all details carefully"
        ]
    
    def _generate_result_check_steps(self, exam_name: str) -> List[str]:
        """
        Generate result checking steps
        """
        return [
            f"Visit the official {exam_name} website",
            "Click on 'Result' or 'Check Result' link",
            "Enter your Roll Number or Registration Number",
            "Enter Date of Birth if required",
            "Submit and view your result",
            "Download score card for future reference"
        ]
    
    def _generate_admit_card_instructions(self) -> List[str]:
        """
        Generate important instructions for admit card
        """
        return [
            "Carry original photo ID proof with admit card",
            "Reach exam center 30 minutes before reporting time",
            "No candidate will be allowed without valid admit card",
            "Verify exam date, time, and center address carefully",
            "Keep 2 passport size photographs ready",
            "Electronic devices are not allowed in exam hall",
            "Read all instructions on admit card carefully"
        ]
    
    def _generate_schema_notification(self, exam_name: str, year: int, event_data: Dict) -> str:
        """
        Generate JSON-LD schema for notification page
        """
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": f"{exam_name} {year} Notification Released",
            "description": f"Download {exam_name} {year} notification PDF and check important dates",
            "datePublished": event_data.get('notification_date', datetime.now().isoformat()),
            "dateModified": datetime.now().isoformat(),
            "author": {
                "@type": "Organization",
                "name": "ExamForms.org"
            }
        }
        return json.dumps(schema)
    
    def _generate_schema_event(self, exam_name: str, year: int, event_data: Dict) -> str:
        """
        Generate JSON-LD Event schema
        """
        schema = {
            "@context": "https://schema.org",
            "@type": "Event",
            "name": f"{exam_name} {year}",
            "startDate": event_data.get('exam_date', ''),
            "eventStatus": "https://schema.org/EventScheduled",
            "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
            "organizer": {
                "@type": "Organization",
                "name": event_data.get('organization', exam_name)
            },
            "location": {
                "@type": "Place",
                "name": "Multiple Exam Centers"
            }
        }
        return json.dumps(schema)
    
    def _generate_schema_result(self, exam_name: str, year: int, event_data: Dict) -> str:
        """
        Generate JSON-LD schema for result page
        """
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": f"{exam_name} {year} Result Declared",
            "description": f"Check {exam_name} {year} result and cutoff marks",
            "datePublished": event_data.get('result_date', datetime.now().isoformat()),
            "author": {
                "@type": "Organization",
                "name": "ExamForms.org"
            }
        }
        return json.dumps(schema)
