-- Explicit, additive research dataset. Never changes legacy tables or views.
CREATE SCHEMA IF NOT EXISTS ghcnh_parallel;

CREATE TABLE IF NOT EXISTS ghcnh_parallel.dataset_versions (
    dataset_version TEXT PRIMARY KEY,
    verification JSONB NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('loading', 'complete')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS ghcnh_parallel.source_files (
    dataset_version TEXT NOT NULL REFERENCES ghcnh_parallel.dataset_versions,
    station VARCHAR(3) NOT NULL REFERENCES public.station_metadata(station),
    source_year INTEGER NOT NULL CHECK (source_year BETWEEN 2005 AND 2024),
    station_id TEXT NOT NULL,
    source_url TEXT NOT NULL,
    source_sha256 TEXT NOT NULL,
    raw_file_path TEXT NOT NULL,
    routine_rows INTEGER NOT NULL,
    PRIMARY KEY (dataset_version, station, source_year)
);

CREATE TABLE IF NOT EXISTS ghcnh_parallel.hourly_observations (
    dataset_version TEXT NOT NULL,
    station VARCHAR(3) NOT NULL,
    source_year INTEGER NOT NULL,
    hour_utc TIMESTAMPTZ NOT NULL,
    observation_datetime_utc TIMESTAMPTZ NOT NULL,
    report_type TEXT NOT NULL,
    temperature_c DOUBLE PRECISION,
    dewpoint_c DOUBLE PRECISION,
    relative_humidity DOUBLE PRECISION,
    station_pressure_hpa DOUBLE PRECISION,
    sea_level_pressure_hpa DOUBLE PRECISION,
    altimeter_hpa DOUBLE PRECISION,
    wind_speed_ms DOUBLE PRECISION,
    wind_direction_deg DOUBLE PRECISION,
    wind_state TEXT NOT NULL CHECK (wind_state IN ('numeric', 'calm', 'variable', 'missing')),
    wind_gust_ms DOUBLE PRECISION,
    precipitation_reported_mm DOUBLE PRECISION,
    precipitation_trace BOOLEAN,
    quality_flags JSONB NOT NULL,
    PRIMARY KEY (dataset_version, station, hour_utc),
    FOREIGN KEY (dataset_version, station, source_year)
        REFERENCES ghcnh_parallel.source_files,
    CHECK (EXTRACT(YEAR FROM hour_utc AT TIME ZONE 'UTC') = source_year),
    CHECK (hour_utc = date_trunc('hour', observation_datetime_utc AT TIME ZONE 'UTC') AT TIME ZONE 'UTC'),
    CHECK (wind_direction_deg IS NULL OR wind_direction_deg BETWEEN 0 AND 360),
    CHECK (wind_state = 'numeric' OR wind_direction_deg IS NULL)
);

COMMENT ON TABLE ghcnh_parallel.hourly_observations IS
    'Separate GHCNh routine-hour research dataset, SI/UTC. Not unioned into production. Missing remains missing; calm/variable are not bearings. Raw Parquet + SHA retain full reports.';
COMMENT ON COLUMN ghcnh_parallel.hourly_observations.precipitation_reported_mm IS
    'QC-screened FM15 reported compatibility amount; accumulation timing not certified. Do not sum as validated hourly rainfall.';
