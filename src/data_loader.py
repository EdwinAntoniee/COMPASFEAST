import pandas as pd
import os

def load_ai4i_data(filepath=None):
    """Load dataset AI4I"""
    if filepath is None or not os.path.exists(filepath):
        possible_paths = [
            "data/raw/ai4i2020.csv",
            "../data/raw/ai4i2020.csv",
            "data/01_raw/ai4i2020.csv",
            "../data/01_raw/ai4i2020.csv"
        ]
        for p in possible_paths:
            if os.path.exists(p):
                filepath = p
                break
        
    df = pd.read_csv(filepath)

    # Formatting Columns' name
    df.columns = (df.columns.str.lower()
                             .str.replace(' ', '_')
                             .str.replace('[', '')
                             .str.replace(']', ''))
    return df