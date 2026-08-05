import pandas as pd
import os

def load_ai4i_data(filepath="../data/raw/ai4i2020.csv"):
    """Load dataset AI4I"""
    if not os.path.exists(filepath):
        filepath = "data/01_raw/ai4i2020.csv"
        
    df = pd.read_csv(filepath)

    # Formatting Columns' name
    df.columns = (df.columns.str.lower()
                             .str.replace(' ', '_')
                             .str.replace('[', '')
                             .str.replace(']', ''))
    return df