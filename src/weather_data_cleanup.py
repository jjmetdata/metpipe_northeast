from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

airport_list = ['alb', 'bos', 'jfk', 'pvd']

cols = [
    'DATE',
    'HourlyDryBulbTemperature',
    'HourlyDewPointTemperature',
    'HourlyRelativeHumidity',
    'HourlyPrecipitation',
    'HourlySkyConditions',
    'HourlyStationPressure',
    'HourlyWindDirection',
    'HourlyWindSpeed',
    'HourlyWindGustSpeed'
]

numeric_cols = [
    'HourlyDryBulbTemperature',
    'HourlyDewPointTemperature',
    'HourlyRelativeHumidity',
    'HourlyPrecipitation',
    'HourlyStationPressure',
    'HourlyWindSpeed',
    'HourlyWindGustSpeed'
]

for acronym in airport_list:
    csv_file = RAW_DATA_DIR / f"{acronym}_hourly_2024.csv"
    print(f"Reading data from {csv_file}...")
    
    df = pd.read_csv(csv_file, usecols=cols, low_memory=False)[cols] # ensure the columns are in the correct order
    df = df.copy()
    
    print(f"Data read successfully. Cleaning data for {acronym}...")
    # handle 'T' values in HourlyPrecipitation by replacing them with 0.001
    df['HourlyPrecipitation'] = df['HourlyPrecipitation'].replace('T', '0.001')
    
    df[numeric_cols] = df[numeric_cols].astype(str).apply(lambda col: col.str.replace(r's$', '', regex=True))
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
    df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')
    
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    cleaned_csv_file = PROCESSED_DATA_DIR / f"{acronym}_hourly_2024_cleaned.csv"
    df.to_csv(cleaned_csv_file, index=False)
    
    print(f"Data cleaned and saved to {cleaned_csv_file}.")
