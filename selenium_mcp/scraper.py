import json
import os
import base64
from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

PROFILES_FILE = "profiles.json"

def get_profile_config(profile_id: str) -> dict:
    if not os.path.exists(PROFILES_FILE):
        return {}
    with open(PROFILES_FILE, 'r', encoding='utf-8') as f:
        profiles = json.load(f)
        for p in profiles:
            if p.get('id') == profile_id or p.get('name') == profile_id:
                return p
    return {}

class Scraper:
    def __init__(self, profile_id: str = "default"):
        self.profile = get_profile_config(profile_id)
        self.driver = self._init_driver()

    def _init_driver(self) -> webdriver.Chrome:
        options = Options()

        if self.profile.get("headless", True):
            options.add_argument("--headless=new")

        if self.profile.get("disable_images", False):
            options.add_argument('--blink-settings=imagesEnabled=false')

        if self.profile.get("user_data_dir"):
            options.add_argument(f"--user-data-dir={self.profile.get('user_data_dir')}")

        if self.profile.get("user_agent"):
            options.add_argument(f"user-agent={self.profile.get('user_agent')}")

        if self.profile.get("proxy"):
            options.add_argument(f"--proxy-server={self.profile.get('proxy')}")

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=options)
        return driver

    def navigate(self, url: str) -> str:
        self.driver.get(url)
        return f"Navigated to {url}"

    def get_text(self, selector: str, by: str = "css") -> str:
        by_type = By.CSS_SELECTOR if by.lower() == "css" else By.XPATH
        element = self.driver.find_element(by_type, selector)
        return element.text

    def click(self, selector: str, by: str = "css") -> str:
        by_type = By.CSS_SELECTOR if by.lower() == "css" else By.XPATH
        element = self.driver.find_element(by_type, selector)
        element.click()
        return f"Clicked element with selector: {selector}"

    def type_text(self, selector: str, text: str, by: str = "css") -> str:
        by_type = By.CSS_SELECTOR if by.lower() == "css" else By.XPATH
        element = self.driver.find_element(by_type, selector)
        element.send_keys(text)
        return f"Typed text into element: {selector}"

    def wait_for_element(self, selector: str, by: str = "css", timeout: int = 10) -> str:
        by_type = By.CSS_SELECTOR if by.lower() == "css" else By.XPATH
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by_type, selector))
        )
        return f"Element {selector} appeared"

    def execute_js(self, script: str) -> Any:
        return self.driver.execute_script(script)

    def take_screenshot(self) -> str:
        return self.driver.get_screenshot_as_base64()

    def export_html(self) -> str:
        return self.driver.page_source

    def close(self):
        if self.driver:
            self.driver.quit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
