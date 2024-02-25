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
    name = "url_viewer"
    description = "UrlViewer browses a specified URL and returns the content of the page."

    def run(self, *args, **kwargs) -> str:
        url = kwargs["url"]
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)
        text = html2text.html2text(driver.page_source)

        driver.quit()

        return text or "Could not retrieve content from the URL."