import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def setup_driver():
    print("[Инициализация] Запуск браузера...")
    chrome_options = Options()
    chrome_options.add_argument(f"--user-data-dir={CHROME_USER_DATA_DIR}")
    chrome_options.add_argument("--profile-directory=Default")
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    service = Service(executable_path=CHROME_DRIVER_PATH)
    return webdriver.Chrome(service=service, options=chrome_options)