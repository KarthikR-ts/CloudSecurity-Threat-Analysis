
import pandas as pd
import numpy as np
import os
import pyarrow as pa
import pyarrow.parquet as pq

from pathlib import Path

# Base directory of the project (root)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "backend" / "data"
os.makedirs(DATA_DIR, exist_ok=True)

def generate_file(filename, rows=100_000): # 100k rows to test performance slightly
    print(f"Generating {filename} with {rows} rows...")
    df = pd.DataFrame({
        'id': np.arange(rows),
        'feature_1': np.random.randn(rows),
        'feature_2': np.random.randn(rows),
        'category': np.random.choice(['A', 'B', 'C'], rows),
        'IncidentGrade_Encoded': np.random.randint(0, 3, rows)
    })
    
    path = os.path.join(DATA_DIR, filename)
    table = pa.Table.from_pandas(df)
    pq.write_table(table, path)
    print(f"Saved to {path}")

if __name__ == "__main__":
    generate_file("train_ml_ready.parquet", 1000)
    generate_file("test_ml_ready.parquet", 500)
