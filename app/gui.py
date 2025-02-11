import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from .parser_logic import ParserLogic

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
    
    def parse_excel(self):
        try:
            df = pd.read_excel(self.file_path.get(), engine='openpyxl')
            total_rows = len(df)

            for index, row in df.iterrows():
                if not self.running:
                    break

                bg_value = str(row.get('bg', '')).lower()
                
                if 'fashion' in bg_value:
                    result = self.parser.process_fashion(
                        row.get('URL_DAM', '').strip(),
                        row.get('URL_MM', '').strip(),
                        self.driver
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