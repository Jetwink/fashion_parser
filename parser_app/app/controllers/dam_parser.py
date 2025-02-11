import re
from .base_parser import BaseParser
from selenium.webdriver.common.by import By

class DamParser(BaseParser):
    def process(self, url):
        result = {
            'dam_result': 'Ошибка',
            'photo_count': 0,
            'best_size': 'Н/Д',
            'best_resolution': 'Н/Д'
        }
        
        try:
            self.driver.get(url)
            
            if self.check_empty_state():
                result['dam_result'] = 'Нет'
                return result

            photos = self.parse_photos_table()
            
            if photos:
                valid_photos = [p for p in photos if p['size_kb'] >= 50 
                              and p['width'] >= 1000 
                              and p['height'] >= 1000]
                
                best_photo = max(valid_photos if valid_photos else photos, 
                               key=lambda x: (x['size_kb'], x['width'], x['height']))
                
                result.update({
                    'dam_result': 'Да' if any([
                        best_photo['size_kb'] >= 50,
                        best_photo['width'] >= 1000,
                        best_photo['height'] >= 1000
                    ]) else 'Нет',
                    'photo_count': len(photos),
                    'best_size': best_photo['original_size'],
                    'best_resolution': best_photo['resolution']
                })
            else:
                result['dam_result'] = 'Нет'

        except Exception as e:
            result['dam_result'] = f'Ошибка: {str(e)}'
        
        return result

    def check_empty_state(self):
        try:
            self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".EmptyState-module__Container--d8ca")
            ))
            return True
        except TimeoutException:
            return False

    def parse_photos_table(self):
        photos = []
        try:
            table = self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "tbody.TableBody-module__TableBody--fbaa")
            ))
            rows = table.find_elements(By.CSS_SELECTOR, "tr.Table-module__TableRow--c0b9")
            
            for row in rows:
                try:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) < 5:
                        continue

                    size_text = cells[3].text.strip()
                    size_match = re.search(r'(\d+\.?\d*)\s*(КБ|МБ)', size_text)
                    if not size_match:
                        continue
                    
                    size = float(size_match.group(1))
                    if size_match.group(2) == 'МБ':
                        size *= 1024

                    res_match = re.search(r'(\d+)x(\d+)', cells[4].text)
                    if not res_match:
                        continue

                    photos.append({
                        'size_kb': size,
                        'width': int(res_match.group(1)),
                        'height': int(res_match.group(2)),
                        'original_size': size_text,
                        'resolution': f"{res_match.group(1)}x{res_match.group(2)}"
                    })
                except:
                    continue
        except TimeoutException:
            pass
        
        return photos