from pathlib import Path
import os
import pandas as pd
from sqlalchemy import URL, create_engine, text

'''
This script is used to ingest the cleaned CSV files into a database. 
It reads the files from the specified directory, processes them, and then inserts the data into the database.
'''

'''PART I: Gather the cleaned CSV files from the specified directory and store them in a dictionary with the station name as the key.'''
# Resolve paths relative to the repository, not the caller's working directory.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "processed"


# List all cleaned CSV files in the processed-data directory.
csv_list = sorted(DATA_DIR.glob("*_hourly_*_cleaned.csv"))
#print(csv_list)
#print(len(csv_list))

# Create a dictionary to store the station name (derived from the file name) and the corresponding file path
station_files = {
    path.name.split("_")[0].upper(): path for path in csv_list
}
#print(station_files)


''' PART II: Ingest the cleaned CSV files into a PostgreSQL database using SQLAlchemy. '''
# ingest to a PostgreSQL database using SQLAlchemy
# Connection settings come from the DB_* environment variables.

database_url = URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("DB_USER") or os.getenv("USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.getenv("DB_NAME", "northeast_weather_2024_phase2"),
)
engine = create_engine(database_url)

insert_sql = text('''
    INSERT INTO "northeast_weather_2024" (
        "datetime",
        "station",
        "temperature",
        "dewpoint",
        "relative_humidity",
        "precipitation",
        "sky_conditions",
        "station_pressure",
        "wind_direction",
        "wind_speed",
        "wind_gust" 
    ) 
    VALUES (
        :datetime,
        :station,
        :temperature,
        :dewpoint,
        :relative_humidity,
        :precipitation,
        :sky_conditions,
        :station_pressure,
        :wind_direction,
        :wind_speed,
        :wind_gust
    )
    ON CONFLICT ("datetime", "station") DO NOTHING;
''')

with engine.begin() as conn:
    for station, file_path in station_files.items():
        print(f'Ingesting data for station "{station}" from file: {file_path.name}...')
        
        # Read the cleaned CSV file into a DataFrame
        df = pd.read_csv(file_path)
        
        df = df.rename(columns={
            'DATE': 'datetime',
            'HourlyDryBulbTemperature': 'temperature',
            'HourlyDewPointTemperature': 'dewpoint',
            'HourlyRelativeHumidity': 'relative_humidity',
            'HourlyPrecipitation': 'precipitation',
            'HourlySkyConditions': 'sky_conditions',
            'HourlyStationPressure': 'station_pressure',
            'HourlyWindDirection': 'wind_direction',
            'HourlyWindSpeed': 'wind_speed',
            'HourlyWindGustSpeed': 'wind_gust'
        })
        
        df["station"] = station  # Add a new column for the station name
        df["datetime"] = pd.to_datetime(df["datetime"])  # Ensure the datetime column is in datetime format
        df["precipitation"] = df["precipitation"].replace('T', 0.001)  # Replace 'T' with 0.001 in the precipitation column
        df["precipitation"] = pd.to_numeric(df["precipitation"], errors='coerce')  # Convert precipitation to numeric, coercing errors to NaN
        
        df = df.drop_duplicates(subset=["datetime", "station"])  # Drop duplicate rows based on datetime and station
        
        records = df[
            [
                'datetime',
                'station',
                'temperature',
                'dewpoint',
                'relative_humidity',
                'precipitation',
                'sky_conditions',
                'station_pressure',
                'wind_direction',
                'wind_speed',
                'wind_gust'
            ]
        ].to_dict(orient='records')
        
        conn.execute(insert_sql, records)  # Insert the records into the database
        
        print(f'Data ingestion completed for station "{station}".')
        print(f"Number of records processed: {len(records)}")
        print("=" * 50)
