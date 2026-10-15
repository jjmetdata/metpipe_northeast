-- Auxiliary observations do not change public.station_metadata/core membership.
CREATE SCHEMA IF NOT EXISTS metpipe_aux;
CREATE TABLE IF NOT EXISTS metpipe_aux.stations (
    station VARCHAR(3) PRIMARY KEY,
    station_id TEXT NOT NULL UNIQUE,
    station_name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role='auxiliary')
);
CREATE TABLE IF NOT EXISTS metpipe_aux.source_files (
    dataset_version TEXT NOT NULL,
    station VARCHAR(3) NOT NULL REFERENCES metpipe_aux.stations,
    source_year INTEGER NOT NULL CHECK (source_year BETWEEN 2005 AND 2024),
    station_id TEXT NOT NULL,
    source_url TEXT NOT NULL,
    source_sha256 TEXT NOT NULL,
    raw_file_path TEXT NOT NULL,
    routine_rows INTEGER NOT NULL,
    PRIMARY KEY (dataset_version,station,source_year)
);
CREATE TABLE IF NOT EXISTS metpipe_aux.hourly_observations (
    LIKE ghcnh_parallel.hourly_observations INCLUDING DEFAULTS INCLUDING CONSTRAINTS,
    PRIMARY KEY (dataset_version,station,hour_utc),
    FOREIGN KEY (dataset_version,station,source_year) REFERENCES metpipe_aux.source_files
);
COMMENT ON TABLE metpipe_aux.hourly_observations IS
    'Separately identified auxiliary station observations, not substitutes relabeled as another station. Not automatically included in the core-20 finalized view or frozen models.';
