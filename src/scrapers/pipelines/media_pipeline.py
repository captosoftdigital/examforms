import os
from scrapy.pipelines.files import FilesPipeline
from scrapy import Request

class S3MediaPipeline(FilesPipeline):
    """
    Pipeline to download files to S3 (or local if configured).
    It expects 'file_urls' or maps specific fields like 'pdf_link' to it.
    """

    def get_media_requests(self, item, info):
        urls = []
        if item.get('pdf_link'):
            urls.append(item['pdf_link'])
        if item.get('download_link'):
            urls.append(item['download_link'])
        
        # Also check standard file_urls
        if item.get('file_urls'):
            urls.extend(item['file_urls'])
            
        return [Request(u) for u in urls]

    def file_path(self, request, response=None, info=None, *, item=None):
        # Generate a nice path: exam_name/year/filename.pdf
        exam_name = self._slugify(item.get('exam_name', 'unknown'))
        year = item.get('year', 'unknown')
        filename = request.url.split('/')[-1]
        
        # Sanitize filename
        filename = filename.split('?')[0] # Remove query params
        if not filename.endswith('.pdf'):
            filename += '.pdf'
            
        return f"{exam_name}/{year}/{filename}"

    def _slugify(self, text):
        import re
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s-]', '', text)
        text = re.sub(r'\s+', '-', text).strip('-')
        return text
