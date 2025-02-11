import tkinter as tk
from tkinter import *
from tkinter import ttk, filedialog, messagebox
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
import pandas as pd  # Добавить эту строку
from .parser_logic import ParserLogic
from .config import *

class ParserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Парсер сайтов")
        self.root.geometry("500x200")
        
        self.file_path = tk.StringVar()
        self.progress = tk.DoubleVar()
        self.running = False
        self.driver = None
        self.parser = ParserLogic()

        self.create_widgets()
        self.setup_driver()

    def create_widgets(self):
        file_frame = Frame(self.root)
        file_frame.pack(pady=10)
        
        Label(file_frame, text="Файл Excel:").pack(side=LEFT)
        Entry(file_frame, textvariable=self.file_path, width=40).pack(side=LEFT, padx=5)
        Button(file_frame, text="Обзор", command=self.browse_file).pack(side=LEFT)

        progress_frame = Frame(self.root)
        progress_frame.pack(pady=20)
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress,
            maximum=100,
            length=300
        )
        self.progress_bar.pack()

        button_frame = Frame(self.root)
        button_frame.pack(pady=10)
        self.start_btn = Button(
            button_frame,
            text="Старт",
            command=self.start_parsing,
            state=DISABLED
        )
        self.start_btn.pack(side=LEFT, padx=5)
        self.cancel_btn = Button(
            button_frame,
            text="Остановить",
            command=self.cancel_parsing,
            state=DISABLED
        )
        self.cancel_btn.pack(side=LEFT)

    def setup_driver(self):
        try:
            chrome_options = Options()
            chrome_options.add_argument(f"--user-data-dir={CHROME_USER_DATA_DIR}")
            chrome_options.add_argument("--profile-directory=Default")
            chrome_options.add_experimental_option("detach", True)
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--ignore-certificate-errors")
            chrome_options.add_argument("--allow-insecure-localhost")
            chrome_options.add_argument("--enable-clipboard")

            service = Service(executable_path=CHROME_DRIVER_PATH)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.minimize_window()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить браузер:\n{str(e)}")

    def browse_file(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if filename:
            self.file_path.set(filename)
            self.start_btn.config(state=NORMAL)

    def start_parsing(self):
        self.running = True
        self.start_btn.config(state=DISABLED)
        self.cancel_btn.config(state=NORMAL)
        threading.Thread(target=self.parse_excel).start()

    # ... (полный код методов create_widgets, setup_driver, browse_file и т.д.)
    def modify_url(self, original_url, attempt):
        """Удаляет N цифр с конца URL, где N = номер попытки (макс. 4)"""
        modified = original_url
        for _ in range(min(attempt, 4)):
            modified = re.sub(r'\d$', '', modified)
        return modified.rstrip('/')
		
		
    def update_progress(self, value):
        self.progress.set(value)
        self.root.update_idletasks()

    def reset_ui(self):
        self.start_btn.config(state=NORMAL)
        self.cancel_btn.config(state=DISABLED)
        self.progress.set(0)
        self.running = False

    def cancel_parsing(self):
        self.running = False
        self.cancel_btn.config(state=DISABLED)	
    def parse_excel(self):
        try:
            df = pd.read_excel(self.file_path.get(), engine='openpyxl')
            total_rows = len(df)

            for index, row in df.iterrows():
                if not self.running:
                    break

                bg_value = str(row.get('bg', '')).lower()
                print(f"\n[Fashion] Попытка {self.driver}/5")
                print(f"\n[Fashion] Попытк {row.get('URL_DAM', '').strip()}/5")
                print(f"\n[Fashion] Попыт {row.get('URL_MM', '').strip()}/5")
                if 'fashion' in bg_value:
                    result = self.parser.process_fashion(
                        #self.driver,
                        row.get('URL_DAM', '').strip(),
                        row.get('URL_MM', '').strip()
                    )
                    df.at[index, 'ШК DAM'] = result
                else:
                    result = self.parser.process_dam(
                        row.get('URL_DAM', '').strip(),
                        self.driver
                    )
                    df.at[index, 'DAM'] = result.get('dam_result', '')
                    df.at[index, 'photo_count'] = result.get('photo_count', 0)
                    df.at[index, 'best_size'] = result.get('best_size', '')
                    df.at[index, 'best_resolution'] = result.get('best_resolution', '')

                self.update_progress((index + 1) / total_rows * 100)

            if self.running:
                self.parser.save_results(df, self.file_path.get())
                messagebox.showinfo("Готово", "Обработка завершена!\nБраузер остается открытым.")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Критическая ошибка:\n{str(e)}")
        finally:
            self.reset_ui()