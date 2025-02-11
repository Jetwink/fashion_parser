import time
import re
import pandas as pd
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from PIL import Image
from io import BytesIO
import imagehash

class ParserLogic:
    def __init__(self):
        self.columns_to_create = ['ШК DAM', 'DAM', 'photo_count', 'best_size', 'best_resolution']

    # Все оригинальные методы парсинга без изменений
    def process_fashion(self, url_dam, url_mm):
        original_window = self.driver.current_window_handle  # Запоминаем исходную вкладку
        
        for attempt in range(5):
            try:
                current_url = self.modify_url(url_dam, attempt)
                print(f"\n[Fashion] Попытка {attempt+1}/5 | URL: {current_url}")
    
                # Открываем DAM-страницу в новой вкладке
                self.driver.switch_to.new_window('tab')
                self.driver.get(current_url)
    
                # Поиск основной таблицы с явным ожиданием
                try:
                    WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "tbody.Table-module__verticalAlignMiddle--b43f"))
                    )
                except TimeoutException:
                    print("[!] Таблица не найдена, пробуем другой URL")
                    self.driver.close()
                    self.driver.switch_to.window(original_window)
                    continue
    
                # Работа с таблицей
                table = self.driver.find_element(By.CSS_SELECTOR, "tbody.Table-module__verticalAlignMiddle--b43f")
                rows = table.find_elements(By.CSS_SELECTOR, "tr.Table-module__TableRow--c0b9")
                
                # Предварительная фильтрация строк
                target_rows = []
                for row in rows:
                    try:
                        p_element = row.find_element(By.CSS_SELECTOR, "td:nth-child(2) > p")
                        img_name = p_element.text.strip()
                        if any(s in img_name for s in ['_1.jpg', '_ 1.jpg']):
                            target_rows.append(row)
                    except:
                        continue
                                        
                print(f"Найдено целевых строк: {len(target_rows)}")
    
                for row_idx, row in enumerate(target_rows, 1):
                    try:
                        # Открываем изображение в новой вкладке
                        link = row.find_element(By.CSS_SELECTOR, "td:nth-child(2) > p")
                        ActionChains(self.driver)\
                            .key_down(Keys.CONTROL)\
                            .click(link)\
                            .key_up(Keys.CONTROL)\
                            .perform()
    
                        # Переключаемся на новую вкладку
                        WebDriverWait(self.driver, 10).until(lambda d: len(d.window_handles) > 1)
                        self.driver.switch_to.window(self.driver.window_handles[-1])
    
                        # Получаем URL изображения
                        try:
                            img_element = WebDriverWait(self.driver, 15).until(
                                EC.visibility_of_element_located((
                                    By.CSS_SELECTOR, 
                                    "div.yarl__slide_current div.yarl__fullsize img.yarl__slide_image"
                                ))
                            )
                            final_img_url = img_element.get_attribute("src")
                        except:
                            self.driver.close()
                            self.driver.switch_to.window(self.driver.window_handles[0])
                            continue
    
                        # Закрываем вкладку с изображением и возвращаемся
                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])
    
                        # Сравнение изображений
                        if self.compare_images(final_img_url, url_mm):
                            self.driver.close()  # Закрываем DAM-вкладку
                            self.driver.switch_to.window(original_window)
                            return img_name.replace('_1.jpg', '').replace('_ 1.jpg', '').strip()
    
                    except Exception as e:
                        print(f"[!] Ошибка в строке: {str(e)}")
                        #self.driver.save_screenshot(f"error_row_{row_idx}.png")
    
                # Закрываем DAM-вкладку после обработки
                self.driver.close()
                self.driver.switch_to.window(original_window)
    
            except Exception as e:
                print(f"[!] Критическая ошибка: {str(e)}")
                self.driver.save_screenshot(f"error_attempt_{attempt+1}.png")
                
        return ''

    def compare_images(self, dam_url, mm_url):
        try:
            print("\nСравнение изображений:")
            print(f"DAM: {dam_url}")
            print(f"MM: {mm_url}")
    
            # Загрузка DAM
            dam_res = requests.get(dam_url, timeout=15)
            if dam_res.status_code != 200:
                print(f"[!] DAM: Ошибка {dam_res.status_code}")
                return False
            dam_img = Image.open(BytesIO(dam_res.content))
    
            # Загрузка MM
            mm_res = requests.get(mm_url, timeout=15)
            if mm_res.status_code != 200:
                print(f"[!] MM: Ошибка {mm_res.status_code}")
                return False
            mm_img = Image.open(BytesIO(mm_res.content))
    
            # Проверка размеров
            #if dam_img.size != mm_img.size:
            #    print(f"Размеры разные: DAM {dam_img.size} vs MM {mm_img.size}")
            #    return False
    
            # Хеш-сравнение
            #hash_diff = imagehash.average_hash(dam_img) - imagehash.average_hash(mm_img)
            hash1 = imagehash.average_hash(dam_img)
            hash2 = imagehash.average_hash(mm_img)
            #print(f"Разница хешей: {hash_diff}")
    
            # Побайтовое сравнение
            #diff = ImageChops.difference(dam_img, mm_img).getbbox()
            #print(f"Разница пикселей: {'есть' if diff else 'нет'}")
    
           # return hash_diff <= 3 and not diff
            if hash1 == hash2:
                return ''
            else:
                return False
			
        
    
        except Exception as e:
            print(f"[!] Ошибка сравнения: {str(e)}")
            return False

    def process_dam(self, url):
        result = {
            'dam_result': 'Ошибка',
            'photo_count': 0,
            'best_size': 'Н/Д',
            'best_resolution': 'Н/Д'
        }
    
        try:
            self.driver.get(url)

            # Проверка пустого состояния
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".EmptyState-module__Container--d8ca"))
                )
                result.update({'dam_result': 'Нет'})
                return result
            except TimeoutException:
                pass

            # Поиск таблицы
            try:
                table = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "tbody.TableBody-module__TableBody--fbaa"))
                )
            except TimeoutException:
                result['dam_result'] = 'Ошибка: таблица не найдена'
                return result

            # Парсинг данных
            photos = []
            rows = table.find_elements(By.CSS_SELECTOR, "tr.Table-module__TableRow--c0b9")
            for row in rows:
                try:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) < 5:
                        continue

                    # Парсинг размера
                    size_text = cells[3].text.strip()
                    size_match = re.search(r'(\d+\.?\d*)\s*(КБ|МБ)', size_text)
                    if not size_match:
                        continue
                    
                    size = float(size_match.group(1))
                    if size_match.group(2) == 'МБ':
                        size *= 1024  # Конвертация в КБ

                    # Парсинг разрешения
                    res_match = re.search(r'(\d+)x(\d+)', cells[4].text)
                    if not res_match:
                        continue

                    width = int(res_match.group(1))
                    height = int(res_match.group(2))

                    photos.append({
                        'size_kb': size,
                        'width': width,
                        'height': height,
                        'original_size': size_text,
                        'resolution': f"{width}x{height}"
                    })

                except Exception as e:
                    print(f"[DAM] Ошибка обработки строки: {str(e)}")

            # Формирование результата
            if photos:
                valid_photos = [p for p in photos if p['size_kb'] >= 50 and p['width'] >= 1000 and p['height'] >= 1000]
                best_photo = max(valid_photos if valid_photos else photos, key=lambda x: (x['size_kb'], x['width'], x['height']))
                
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

            return result
    
        except Exception as e:
            print(f"[DAM] Критическая ошибка: {str(e)}")
            result['dam_result'] = f'Ошибка: {str(e)}'
            return result
    
    def save_results(self, df, file_path):
        print("\n[Сохранение] Генерация файла результатов...")
        new_filename = f"Результат_{os.path.basename(file_path)}"
        df.to_excel(new_filename, index=False)