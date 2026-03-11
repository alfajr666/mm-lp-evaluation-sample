import pandas as pd
import glob
import os

RAW_DATA_DIR = "/home/gilang/Documents/Project/mm-lp-evaluation-sample/data/raw"
FILTER_DATE = "2026-03-05 12:00:00+00:00"

def filter_csv_files():
    files = glob.glob(os.path.join(RAW_DATA_DIR, "*.csv"))
    for file_path in files:
        if "data_dictionary" in file_path:
            continue
        
        print(f"Processing {os.path.basename(file_path)}...")
        try:
            df = pd.read_csv(file_path)
            if 'timestamp_utc' not in df.columns:
                print(f"  Skipping (no timestamp_utc column)")
                continue
            
            initial_count = len(df)
            df['timestamp_utc'] = pd.to_datetime(df['timestamp_utc'], utc=True)
            df = df[df['timestamp_utc'] >= FILTER_DATE]
            final_count = len(df)
            
            if final_count < initial_count:
                df.to_csv(file_path, index=False)
                print(f"  Dropped {initial_count - final_count} rows. Remaining: {final_count}")
            else:
                print(f"  No rows to drop.")
                
        except Exception as e:
            print(f"  Error processing {file_path}: {e}")

if __name__ == "__main__":
    filter_csv_files()
