-- MetPipe Northeast multi-year PostgreSQL schema.
-- This script is non-destructive: it preserves previously ingested observations.

CREATE TABLE IF NOT EXISTS "station_metadata" (
    "station" VARCHAR(3) PRIMARY KEY,
    "minute_offset" INT NOT NULL
        CHECK ("minute_offset" >= 0 AND "minute_offset" < 60)
);

-- The minute offsets identify each station's representative hourly report.
-- Update this metadata if a station's reporting schedule changes.
INSERT INTO "station_metadata" ("station", "minute_offset") VALUES
    ('BOS', 54),
    ('ALB', 51),
    ('JFK', 51),
    ('PVD', 51),
    ('BDL', 51),
    ('BTV', 54),
    ('MHT', 53),
    ('ORH', 54),
    ('PVC', 56),
    ('PWM', 51),
    ('AUG', 53),
    ('BAF', 53),
    ('DDH', 54),
    ('EWB', 53),
    ('HVN', 53),
    ('HYA', 56),
    ('LEB', 53),
    ('MVY', 53),
    ('PYM', 52),
    ('UUU', 53)
ON CONFLICT ("station") DO UPDATE
SET "minute_offset" = EXCLUDED."minute_offset";

CREATE TABLE IF NOT EXISTS "weather_observations" (
    "datetime" TIMESTAMP NOT NULL,
    "station" VARCHAR(3) NOT NULL,
    "report_type" VARCHAR(10),
    "temperature" DOUBLE PRECISION,
    "dewpoint" DOUBLE PRECISION,
    "relative_humidity" DOUBLE PRECISION,
    "precipitation" DOUBLE PRECISION,
    "sky_conditions" VARCHAR(50),
    "station_pressure" DOUBLE PRECISION,
    "wind_direction" VARCHAR(3),
    "wind_speed" DOUBLE PRECISION,
    "wind_gust" DOUBLE PRECISION,
    PRIMARY KEY ("datetime", "station"),
    FOREIGN KEY ("station") REFERENCES "station_metadata" ("station")
);

-- Existing databases created before report-type tracking gain the new column.
ALTER TABLE "weather_observations"
ADD COLUMN IF NOT EXISTS "report_type" VARCHAR(10);

-- GHCNh backfill provenance. Existing LCDv1 values remain unchanged.
ALTER TABLE "weather_observations"
    ADD COLUMN IF NOT EXISTS "datetime_utc" TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS "source_dataset" TEXT NOT NULL DEFAULT 'LCDv1',
    ADD COLUMN IF NOT EXISTS "source_file_year" INTEGER,
    ADD COLUMN IF NOT EXISTS "source_metadata" JSONB,
    ADD COLUMN IF NOT EXISTS "precipitation_trace" BOOLEAN;

CREATE TABLE IF NOT EXISTS "ghcnh_ingestion_files" (
    "station" VARCHAR(3) NOT NULL REFERENCES "station_metadata" ("station"),
    "source_year" INTEGER NOT NULL,
    "local_start" TIMESTAMP NOT NULL,
    "local_end" TIMESTAMP NOT NULL,
    "source_url" TEXT NOT NULL,
    "source_sha256" TEXT NOT NULL,
    "imported_rows" INTEGER NOT NULL,
    "ingested_at" TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY ("station", "source_year", "local_start", "local_end")
);

CREATE INDEX IF NOT EXISTS "weather_observations_station_datetime_idx"
ON "weather_observations" ("station", "datetime");

-- Legacy LCDv1 keeps its checked minute. Historical GHCNh uses routine report
-- priority, completeness and latest routine time within the hour, without
-- applying a modern fixed minute to changing historical schedules. Specials
-- remain stored but cannot silently fill a missing routine hour.
CREATE OR REPLACE VIEW "weather_hourly" AS
WITH "scheduled_observations" AS (
    SELECT w.*,
        ROW_NUMBER() OVER (
            PARTITION BY w."station", date_trunc('hour', w."datetime")
            ORDER BY
                CASE WHEN w."source_dataset" = 'GHCNh'
                     THEN CASE WHEN w."report_type" = 'FM-15' THEN 0
                               WHEN w."report_type" = 'FM-12' THEN 2 ELSE 1 END
                     ELSE 0 END,
                CASE WHEN w."source_dataset" = 'GHCNh'
                     THEN ((w."temperature" IS NOT NULL)::int +
                           (w."dewpoint" IS NOT NULL)::int +
                           (w."wind_speed" IS NOT NULL)::int) ELSE 0 END DESC,
                CASE WHEN w."source_dataset" = 'GHCNh' THEN w."datetime" END DESC,
                w."datetime" ASC
        ) AS "observation_rank"
    FROM "weather_observations" w
    JOIN "station_metadata" m ON w."station" = m."station"
    WHERE (w."source_dataset" = 'LCDv1' AND w."report_type" = 'FM-15'
           AND EXTRACT(MINUTE FROM w."datetime") = m."minute_offset")
       OR (w."source_dataset" = 'GHCNh' AND w."report_type" IN
           ('FM-15', 'FM-12', 'SAO', 'SY-SA', 'SYMT', 'SYAE', 'SYAU', 'SSA', 'SAAU'))
)
SELECT
    date_trunc('hour', w."datetime") AS "datetime",
    w."station",
    w."temperature",
    w."dewpoint",
    w."relative_humidity",
    w."precipitation",
    w."sky_conditions",
    w."station_pressure",
    w."wind_direction",
    w."wind_speed",
    w."wind_gust",
    w."datetime" AS "observation_datetime",
    w."source_dataset",
    w."source_file_year",
    w."source_metadata",
    w."precipitation_trace"
FROM "scheduled_observations" w
WHERE w."observation_rank" = 1;

-- UTC/SI interface for future model/real-time joins. Legacy data has unknown
-- original QC/trace provenance; do not infer it from existing numeric amounts.
CREATE OR REPLACE VIEW "weather_hourly_utc" AS
SELECT
    (("datetime" + interval '5 hours') AT TIME ZONE 'UTC') AS "datetime_utc",
    (("observation_datetime" + interval '5 hours') AT TIME ZONE 'UTC') AS "observation_datetime_utc",
    "station", ("temperature" - 32) / 1.8 AS "temperature_c",
    ("dewpoint" - 32) / 1.8 AS "dewpoint_c", "relative_humidity",
    "precipitation" * 25.4 AS "precipitation_mm", "precipitation_trace",
    "sky_conditions", "station_pressure" * 33.8638866667 AS "station_pressure_hpa",
    "wind_direction", "wind_speed" / 2.2369362921 AS "wind_speed_ms",
    "wind_gust" / 2.2369362921 AS "wind_gust_ms",
    "source_dataset", "source_metadata"
FROM "weather_hourly";

CREATE OR REPLACE VIEW "weather_daily_summary" AS
SELECT
    DATE("datetime") AS "date",
    "station",
    ROUND(AVG("temperature")::numeric, 1) AS "avg_temperature",
    ROUND(AVG("dewpoint")::numeric, 1) AS "avg_dewpoint",
    ROUND(AVG("relative_humidity")::numeric, 1) AS "avg_relative_humidity",
    ROUND(SUM("precipitation")::numeric, 2) AS "total_precipitation",
    ROUND(AVG("station_pressure")::numeric, 2) AS "avg_station_pressure",
    ROUND(AVG("wind_speed")::numeric, 1) AS "avg_wind_speed",
    ROUND(AVG("wind_gust")::numeric, 1) AS "avg_wind_gust"
FROM "weather_hourly"
GROUP BY DATE("datetime"), "station";

-- date_trunc retains the year, so January 2024 and January 2025 remain distinct.
CREATE OR REPLACE VIEW "weather_monthly_summary" AS
SELECT
    date_trunc('month', "datetime")::date AS "month",
    "station",
    ROUND(AVG("temperature")::numeric, 1) AS "avg_temperature",
    ROUND(AVG("dewpoint")::numeric, 1) AS "avg_dewpoint",
    ROUND(AVG("relative_humidity")::numeric, 1) AS "avg_relative_humidity",
    ROUND(SUM("precipitation")::numeric, 2) AS "total_precipitation",
    ROUND(AVG("station_pressure")::numeric, 2) AS "avg_station_pressure",
    ROUND(AVG("wind_speed")::numeric, 1) AS "avg_wind_speed",
    ROUND(AVG("wind_gust")::numeric, 1) AS "avg_wind_gust"
FROM "weather_hourly"
GROUP BY date_trunc('month', "datetime")::date, "station";

CREATE OR REPLACE VIEW "weather_annual_summary" AS
SELECT
    EXTRACT(YEAR FROM "datetime")::int AS "year",
    "station",
    ROUND(AVG("temperature")::numeric, 1) AS "avg_temperature",
    ROUND(AVG("dewpoint")::numeric, 1) AS "avg_dewpoint",
    ROUND(AVG("relative_humidity")::numeric, 1) AS "avg_relative_humidity",
    ROUND(SUM("precipitation")::numeric, 2) AS "total_precipitation",
    ROUND(AVG("station_pressure")::numeric, 2) AS "avg_station_pressure",
    ROUND(AVG("wind_speed")::numeric, 1) AS "avg_wind_speed",
    ROUND(AVG("wind_gust")::numeric, 1) AS "avg_wind_gust"
FROM "weather_hourly"
GROUP BY EXTRACT(YEAR FROM "datetime")::int, "station";
