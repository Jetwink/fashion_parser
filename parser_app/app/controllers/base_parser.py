from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

class BaseParser:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)

    def safe_click(self, selector):
        try:
            element = self.wait.until(EC.element_to_be_clickable(selector))
            element.click()
            return True
        except TimeoutException:
            return False

    def get_element_text(self, selector):
        try:
            element = self.wait.until(EC.presence_of_element_located(selector))
            return element.text.strip()
        except TimeoutException:
            return ""

    def modify_url(self, original_url, attempt):
        modified = original_url
        for _ in range(min(attempt, 4)):
            modified = re.sub(r'\d$', '', modified)
        return modified.rstrip('/')