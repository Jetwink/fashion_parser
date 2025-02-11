import requests
from PIL import Image
from io import BytesIO
import imagehash

#def compare_images(dam_url, mm_url):
#    try:
#        dam_img = Image.open(BytesIO(requests.get(dam_url, timeout=15).content)
#        mm_img = Image.open(BytesIO(requests.get(mm_url, timeout=15).content)
#        
#        hash_diff = imagehash.average_hash(dam_img) - imagehash.average_hash(mm_img)
#        return hash_diff <= 3
#    
#    except Exception as e:
#        print(f"Ошибка сравнения изображений: {str(e)}")
#        return False
		
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
