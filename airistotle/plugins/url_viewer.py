import openai
import json
import html2text
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from .base import BasePlugin


class UrlViewer(BasePlugin):
    """
    {
        "name": "url_viewer",
        "description": "Browses a single specified URL and returns the contents of the page.",
        "parameters": {
            "type": "object",
            "properties": {
            "url": {
                "type": "string",
                "description": "The URL to view."
            }
            },
            "required": [
            "url"
            ]
        }
    }
    """
    name = "url_viewer"
    description = "UrlViewer browses a specified URL and returns the content of the page."

    def run(self, *args, **kwargs) -> str:
        url = kwargs["url"]
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        time.sleep(1)
        driver.get(url)
        time.sleep(1)
        text = html2text.html2text(driver.page_source)

        driver.quit()

        return text or "Could not retrieve content from the URL."