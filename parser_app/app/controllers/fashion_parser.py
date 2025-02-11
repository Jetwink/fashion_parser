import re
from .base_parser import BaseParser
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

class FashionParser(BaseParser):
    def process(self, url_dam, url_mm):
        original_window = self.driver.current_window_handle
        
        for attempt in range(5):
            try:
                current_url = self.modify_url(url_dam, attempt)
                self.driver.switch_to.new_window('tab')
                dam_window = self.driver.current_window_handle
                self.driver.get(current_url)

                if not self.find_main_table():
                    self.close_window(dam_window, original_window)
                    continue

                target_rows = self.filter_target_rows()
                
                for row in target_rows:
                    try:
                        img_name, final_img_url = self.process_row(row)
                        if self.compare_images(final_img_url, url_mm):
                            self.close_window(dam_window, original_window)
                            return img_name
                    except:
                        self.close_extra_windows(original_window)
                
                self.close_window(dam_window, original_window)

            except Exception as e:
                self.close_extra_windows(original_window)
        
        return ''

    def find_main_table(self):
        try:
            self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "tbody.Table-module__verticalAlignMiddle--b43f")
            ))
            return True
        except TimeoutException:
            return False

    def filter_target_rows(self):
        target_rows = []
        table = self.driver.find_element(
            By.CSS_SELECTOR, "tbody.Table-module__verticalAlignMiddle--b43f"
        )
        rows = table.find_elements(By.CSS_SELECTOR, "tr.Table-module__TableRow--c0b9")
        
        for row in rows:
            try:
                p_element = row.find_element(By.CSS_SELECTOR, "td:nth-child(2) > p")
                if any(s in p_element.text for s in ['_1.jpg', '_ 1.jpg']):
                    target_rows.append(row)
            except:
                continue
        
        return target_rows

    def process_row(self, row):
        p_element = row.find_element(By.CSS_SELECTOR, "td:nth-child(2) > p")
        img_name = p_element.text.strip()
        
        ActionChains(self.driver)\
            .move_to_element(p_element)\
            .click()\
            .key_down(Keys.SHIFT)\
            .send_keys('l')\
            .key_up(Keys.SHIFT)\
            .pause(1)\
            .perform()

        final_img_url = self.driver.execute_script("return navigator.clipboard.readText();")
        return img_name.replace('_1.jpg', '').replace('_ 1.jpg', '').strip(), final_img_url

    def close_window(self, window, fallback):
        try:
            self.driver.switch_to.window(window)
            self.driver.close()
            self.driver.switch_to.window(fallback)
        except:
            pass

    def close_extra_windows(self, main_window):
        for handle in self.driver.window_handles:
            if handle != main_window:
                self.driver.switch_to.window(handle)
                self.driver.close()
        self.driver.switch_to.window(main_window)