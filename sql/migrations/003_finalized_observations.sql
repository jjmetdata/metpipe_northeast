-- Additive versioned finalized layer. Never changes either input dataset.
CREATE SCHEMA IF NOT EXISTS metpipe_final;
CREATE TABLE IF NOT EXISTS metpipe_final.policy_versions (
    policy_version TEXT PRIMARY KEY,
    policy JSONB NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('loading','complete')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ
);
CREATE TABLE IF NOT EXISTS metpipe_final.evidence_files (
    policy_version TEXT NOT NULL REFERENCES metpipe_final.policy_versions,
    station VARCHAR(3) NOT NULL,
    local_file_year INTEGER NOT NULL,
    source_path TEXT NOT NULL,
    source_sha256 TEXT NOT NULL,
    PRIMARY KEY (policy_version,station,local_file_year)
);
CREATE TABLE IF NOT EXISTS metpipe_final.hour_decisions (
    policy_version TEXT NOT NULL REFERENCES metpipe_final.policy_versions,
    station VARCHAR(3) NOT NULL,
    hour_utc TIMESTAMPTZ NOT NULL,
    decisions JSONB NOT NULL,
    PRIMARY KEY (policy_version,station,hour_utc)
);
CREATE TABLE IF NOT EXISTS metpipe_final.hourly_snapshots (
    policy_version TEXT NOT NULL REFERENCES metpipe_final.policy_versions,
    station VARCHAR(3) NOT NULL,
    hour_utc TIMESTAMPTZ NOT NULL,
    primary_observation_datetime_utc TIMESTAMPTZ,
    temperature_c DOUBLE PRECISION,
    dewpoint_c DOUBLE PRECISION,
    relative_humidity DOUBLE PRECISION,
    station_pressure_hpa DOUBLE PRECISION,
    sea_level_pressure_hpa DOUBLE PRECISION,
    altimeter_hpa DOUBLE PRECISION,
    wind_speed_ms DOUBLE PRECISION,
    wind_direction_deg DOUBLE PRECISION,
    wind_state TEXT NOT NULL,
    wind_gust_ms DOUBLE PRECISION,
    precipitation_reported_mm DOUBLE PRECISION,
    precipitation_trace BOOLEAN,
    PRIMARY KEY (policy_version,station,hour_utc),
    CHECK (wind_state IN ('numeric','calm','variable','missing','conflict')),
    CHECK (wind_state='numeric' OR wind_direction_deg IS NULL)
);

CREATE OR REPLACE VIEW metpipe_final.weather_hourly_utc AS
SELECT h.*, h.hour_utc AS datetime_utc,
    COALESCE(d.decisions,'{}'::jsonb) AS selection_decisions,
    g.quality_flags AS primary_quality_flags,
    p.policy->>'primary_dataset_version' AS primary_dataset_version,
    provenance.element_provenance
FROM metpipe_final.hourly_snapshots h
JOIN metpipe_final.policy_versions p USING (policy_version)
LEFT JOIN metpipe_final.hour_decisions d USING (policy_version,station,hour_utc)
LEFT JOIN ghcnh_parallel.hourly_observations g
    ON g.dataset_version=p.policy->>'primary_dataset_version'
    AND g.station=h.station AND g.hour_utc=h.hour_utc
CROSS JOIN LATERAL (
    SELECT jsonb_object_agg(f.name,
        CASE WHEN d.decisions ? f.name THEN d.decisions->f.name
        ELSE jsonb_build_object(
            'source', CASE WHEN f.present THEN 'GHCNh' ELSE NULL END,
            'reason', CASE WHEN f.present THEN 'primary_GHCNh' ELSE 'no_usable_value' END,
            'observation_datetime_utc', CASE WHEN f.present THEN h.primary_observation_datetime_utc ELSE NULL END,
            'selected_qc', g.quality_flags->f.raw_name)
        END) AS element_provenance
    FROM (VALUES
        ('temperature_c','temperature',h.temperature_c IS NOT NULL),
        ('dewpoint_c','dew_point_temperature',h.dewpoint_c IS NOT NULL),
        ('relative_humidity','relative_humidity',h.relative_humidity IS NOT NULL),
        ('station_pressure_hpa','station_level_pressure',h.station_pressure_hpa IS NOT NULL),
        ('sea_level_pressure_hpa','sea_level_pressure',h.sea_level_pressure_hpa IS NOT NULL),
        ('altimeter_hpa','altimeter',h.altimeter_hpa IS NOT NULL),
        ('wind_speed_ms','wind_speed',h.wind_speed_ms IS NOT NULL),
        ('wind_direction_deg','wind_direction',h.wind_state IN ('numeric','calm','variable')),
        ('wind_gust_ms','wind_gust',h.wind_gust_ms IS NOT NULL),
        ('precipitation_reported_mm','precipitation',h.precipitation_reported_mm IS NOT NULL)
    ) AS f(name,raw_name,present)
) provenance
WHERE h.policy_version='observed_2005_2024_v1' AND p.status='complete';

COMMENT ON VIEW metpipe_final.weather_hourly_utc IS
    'Versioned core-20 expected-hour observation snapshot. Per-element unresolved conflicts are NULL; sources untouched. LCD embedded METAR support is not independent truth. No modeled fills. Reported precipitation is not certified hourly rainfall.';
