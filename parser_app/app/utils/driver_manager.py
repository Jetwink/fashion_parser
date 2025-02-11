from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from ..config import CHROME_DRIVER_PATH, CHROME_USER_DATA_DIR

class DriverManager:
    def create_driver(self):
        chrome_options = Options()
        chrome_options.add_argument(f"--user-data-dir={CHROME_USER_DATA_DIR}")
        service = Service(executable_path=CHROME_DRIVER_PATH)
        return webdriver.Chrome(service=service, options=chrome_options)
    
    def safe_quit(self, driver):
        try:
            if driver:
                driver.quit()
        except:
            pass