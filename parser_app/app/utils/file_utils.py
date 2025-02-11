import os
import pandas as pd

def save_results(df, original_path):
    new_filename = f"Результат_{os.path.basename(original_path)}"
    df.to_excel(new_filename, index=False)