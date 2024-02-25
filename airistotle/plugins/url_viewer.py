import openai
import json
import html2text
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

from .base import BasePlugin


class UrlViewer(BasePlugin):
    name = "url_viewer"
    description = "UrlViewer browses a specified URL and returns the content of the page."

    def run(self, *args, **kwargs) -> str:
        url = kwargs["url"]
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        driver = Firefox(options=options)

        time.sleep(3)
        driver.get(url)
        text = html2text.html2text(driver.page_source)

        driver.quit()
        
        return text or "Could not retrieve content from the URL."