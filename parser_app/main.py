from app.views.main_window import ParserApp
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = ParserApp(root)
    root.mainloop()