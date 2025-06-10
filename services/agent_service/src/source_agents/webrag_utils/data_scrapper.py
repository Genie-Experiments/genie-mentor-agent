import requests
import re
import html2text
from llama_index.core import Document
from ...utils.logging import setup_logger, get_logger

setup_logger()
logger = get_logger("DataScraper")
class DataScraper:
    def __init__(self):
        self.converter = html2text.HTML2Text()
        self.converter.ignore_links = True
        self.converter.ignore_images = True
        self.converter.ignore_emphasis = True

    @staticmethod
    def clean_text(text):
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r'\s{2,}', ' ', text)
        return text.strip()

    def fetch_data_from_urls(self, urls):
        documents = []

        for url in urls:
            try:
               
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                html_content = response.content.decode('utf-8', errors='ignore')
                text = self.converter.handle(html_content)
                clean_text = self.clean_text(text)
                if clean_text:
                    documents.append(Document(text=clean_text))
                
            except Exception as e:
                logger.error(f"Error retrieving data from url:{e}")

        if not documents:
            logger.error("No documents Fetches")
            return documents
        
        return documents