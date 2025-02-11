import pandas as pd  # Добавить эту строку
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from threading import Thread
from ..controllers.dam_parser import DamParser
from ..controllers.fashion_parser import FashionParser
from ..utils.file_utils import save_results
from ..utils.image_utils import compare_images
from ..utils.driver_manager import DriverManager

class ParserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Парсер сайтов")
        self.root.geometry("500x200")
        
        self.file_path = tk.StringVar()
        self.progress = tk.DoubleVar()
        self.running = False
        self.driver_manager = DriverManager()
        self.driver = None

        self.create_widgets()
        self.setup_driver()

    def create_widgets(self):
        file_frame = tk.Frame(self.root)
        file_frame.pack(pady=10)
        
        tk.Label(file_frame, text="Файл Excel:").pack(side=tk.LEFT)
        tk.Entry(file_frame, textvariable=self.file_path, width=40).pack(side=tk.LEFT, padx=5)
        tk.Button(file_frame, text="Обзор", command=self.browse_file).pack(side=tk.LEFT)

        progress_frame = tk.Frame(self.root)
        progress_frame.pack(pady=20)
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress,
            maximum=100,
            length=300
        )
        self.progress_bar.pack()

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        self.start_btn = tk.Button(
            button_frame,
            text="Старт",
            command=self.start_parsing,
            state=tk.DISABLED
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        self.cancel_btn = tk.Button(
            button_frame,
            text="Остановить",
            command=self.cancel_parsing,
            state=tk.DISABLED
        )
        self.cancel_btn.pack(side=tk.LEFT)

    def setup_driver(self):
        try:
            self.driver = self.driver_manager.create_driver()
            self.driver.minimize_window()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить браузер:\n{str(e)}")

    def browse_file(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if filename:
            self.file_path.set(filename)
            self.start_btn.config(state=tk.NORMAL)

    def start_parsing(self):
        self.running = True
        self.start_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        Thread(target=self.parse_excel).start()

    def parse_excel(self):
        try:
            df = pd.read_excel(self.file_path.get(), engine='openpyxl')
            total_rows = len(df)

            dam_parser = DamParser(self.driver)
            fashion_parser = FashionParser(self.driver)

            for index, row in df.iterrows():
                if not self.running:
                    break

                bg_value = str(row.get('bg', '')).lower()
                
                if 'fashion' in bg_value:
                    result = fashion_parser.process(
                        row.get('URL_DAM', '').strip(),
                        row.get('URL_MM', '').strip()
                    )
                    df.at[index, 'ШК DAM'] = result
                else:
                    result = dam_parser.process(row.get('URL_DAM', '').strip())
                    df.at[index, 'DAM'] = result.get('dam_result', '')
                    df.at[index, 'photo_count'] = result.get('photo_count', 0)
                    df.at[index, 'best_size'] = result.get('best_size', '')
                    df.at[index, 'best_resolution'] = result.get('best_resolution', '')

                self.update_progress((index + 1) / total_rows * 100)

            if self.running:
                save_results(df, self.file_path.get())
                messagebox.showinfo("Готово", "Обработка завершена!")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Критическая ошибка:\n{str(e)}")
        finally:
            self.reset_ui()

    def update_progress(self, value):
        self.progress.set(value)
        self.root.update_idletasks()

    def reset_ui(self):
        self.start_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.progress.set(0)
        self.running = False

    def cancel_parsing(self):
        self.running = False
        self.cancel_btn.config(state=tk.DISABLED)