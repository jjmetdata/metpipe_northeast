"""Read-only database validation, with a generated JSON evidence artifact."""
import json
import os
from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor

ROOT = Path(__file__).resolve().parents[1]
BASELINE_COUNT = 1297439
BASELINE_HASH = "49070fb6deaa6c8600c9e5819d54bb13"
EXPECTED_STATIONS = set("ALB AUG BAF BDL BOS BTV DDH EWB HVN HYA JFK LEB MHT MVY ORH PVC PVD PWM PYM UUU".split())


def main():
    connection = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"), port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "metpipe_northeast"),
        user=os.getenv("DB_USER") or os.getenv("USER"), password=os.getenv("DB_PASSWORD"))
    connection.set_session(readonly=True, isolation_level="REPEATABLE READ")
    results = {}
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            def query(name, sql):
                cursor.execute(sql)
                results[name] = [dict(row) for row in cursor.fetchall()]
                return results[name]

            query("sources", """SELECT source_dataset, count(*) AS observations,
                min(datetime) AS first_observation, max(datetime) AS last_observation
                FROM weather_observations GROUP BY source_dataset ORDER BY source_dataset""")
            original = query("original_preservation", """SELECT count(*) AS observations,
                md5(string_agg(md5(ROW(datetime,station,report_type,temperature,dewpoint,
                relative_humidity,precipitation,sky_conditions,station_pressure,
                wind_direction,wind_speed,wind_gust)::text), '' ORDER BY station,datetime)) AS checksum
                FROM weather_observations WHERE datetime >= '2020-01-01'""")[0]
            query("manifest", """SELECT count(*) AS files, sum(imported_rows) AS observations
                FROM ghcnh_ingestion_files WHERE local_start='2005-01-01'
                AND local_end='2020-01-01'""")
            query("integrity", """SELECT
                count(*) FILTER (WHERE datetime_utc IS NULL OR datetime <>
                    (datetime_utc AT TIME ZONE 'UTC') - interval '5 hours') AS time_mismatches,
                count(*) FILTER (WHERE datetime < '2005-01-01' OR datetime >= '2020-01-01') AS outside_backfill,
                count(*) FILTER (WHERE source_file_year IS NULL OR
                    extract(year FROM datetime_utc AT TIME ZONE 'UTC')::int <> source_file_year) AS source_year_mismatches,
                count(*) FILTER (WHERE source_metadata IS NULL) AS missing_provenance,
                count(*) FILTER (WHERE precipitation_trace IS TRUE AND
                    (precipitation IS NULL OR precipitation <> 0)) AS inconsistent_trace,
                count(*) FILTER (WHERE temperature IS NOT NULL AND abs(temperature -
                    ((source_metadata #>> '{fields,temperature,raw}')::float8 * 1.8 + 32)) > 1e-8) AS temperature_mismatches,
                count(*) FILTER (WHERE wind_speed IS NOT NULL AND abs(wind_speed -
                    (source_metadata #>> '{fields,wind_speed,raw}')::float8 * 2.2369362921) > 1e-8) AS wind_mismatches,
                count(*) FILTER (WHERE station_pressure IS NOT NULL AND abs(station_pressure -
                    (source_metadata #>> '{fields,station_level_pressure,raw}')::float8 / 33.8638866667) > 1e-8) AS pressure_mismatches,
                count(*) FILTER (WHERE precipitation IS NOT NULL AND precipitation_trace IS NOT TRUE
                    AND abs(precipitation - (source_metadata #>> '{fields,precipitation,raw}')::float8 / 25.4) > 1e-8) AS precipitation_mismatches,
                count(*) FILTER (WHERE precipitation IS NOT NULL AND
                    source_metadata #>> '{fields,precipitation,r}' NOT IN ('FM15','FM-15')) AS nonroutine_precipitation,
                count(*) FILTER (WHERE precipitation IS NOT NULL AND
                    source_metadata #>> '{fields,precipitation,s}'='382' AND
                    source_metadata #>> '{fields,precipitation,q}' IN ('X','N','Y','K','G','O','Z','A','M','D','Q')) AS rejected_precipitation_382,
                count(*) FILTER (WHERE precipitation_trace IS TRUE AND
                    source_metadata #>> '{fields,precipitation,m}'='2' AND
                    source_metadata #>> '{fields,precipitation,s}' NOT IN
                    ('220','221','222','223','347','348','313','314','315','322','335','343','344','346')) AS unexpected_trace_source,
                count(*) FILTER (WHERE wind_direction='VRB' AND
                    ((source_metadata #>> '{fields,wind_direction,s}' IN ('220','221','222','223','347','348') AND
                      source_metadata #>> '{fields,wind_direction,q}' IN ('2','3','5')) OR
                     (source_metadata #>> '{fields,wind_direction,s}' IN ('313','314','315','322','335','343','344','346') AND
                      source_metadata #>> '{fields,wind_direction,q}' IN ('2','3','6','7')) OR
                     source_metadata #>> '{fields,wind_direction,q}' ~ '[a-z]')) AS rejected_variable_wind
                FROM weather_observations WHERE source_dataset='GHCNh'""")
            qc_checks = []
            for column, field in {
                "temperature":"temperature", "dewpoint":"dew_point_temperature",
                "relative_humidity":"relative_humidity", "precipitation":"precipitation",
                "station_pressure":"station_level_pressure", "wind_direction":"wind_direction",
                "wind_speed":"wind_speed", "wind_gust":"wind_gust",
            }.items():
                source = "source_metadata #>> '{fields,%s,s}'" % field
                quality = "source_metadata #>> '{fields,%s,q}'" % field
                report = "source_metadata #>> '{fields,%s,r}'" % field
                failed = ("((%s IN ('220','221','222','223','347','348') AND %s IN ('2','3','5')) OR "
                          "(%s IN ('313','314','315','322','335','343','344','346') AND %s IN ('2','3','6','7')) OR "
                          "%s ~ '[a-z]')") % (source,quality,source,quality,quality)
                qc_checks.append("count(*) FILTER (WHERE %s IS NOT NULL AND (%s OR %s IN ('NSRDB','SOD','SOM'))) AS %s" % (column,failed,report,column))
            query("element_qc_integrity", "SELECT " + ",".join(qc_checks) +
                  " FROM weather_observations WHERE source_dataset='GHCNh'")
            query("point_station_years", """SELECT station, extract(year FROM datetime)::int AS year,
                count(*) AS observations FROM weather_observations
                GROUP BY station, extract(year FROM datetime)::int ORDER BY station, year""")
            # One grouped query captures all element/year coverage measures.
            query("hourly_station_years", """SELECT station, extract(year FROM datetime)::int AS year,
                source_dataset, count(*) AS routine_hours, count(temperature) AS temperature_hours,
                count(dewpoint) AS dewpoint_hours, count(wind_speed) AS wind_hours,
                count(relative_humidity) AS humidity_hours, count(station_pressure) AS pressure_hours,
                count(precipitation) AS precipitation_hours,
                count(*) FILTER (WHERE precipitation_trace IS TRUE) AS trace_hours,
                count(DISTINCT extract(month FROM datetime)) AS represented_months
                FROM weather_hourly GROUP BY station, extract(year FROM datetime)::int, source_dataset
                ORDER BY station, year""")
            query("missing_hourly_months", """WITH expected AS (
                SELECT station, month FROM station_metadata CROSS JOIN
                generate_series(timestamp '2005-01-01',timestamp '2024-12-01',interval '1 month') AS month
                ), actual AS (SELECT DISTINCT station, date_trunc('month',datetime) AS month FROM weather_hourly)
                SELECT e.station,e.month FROM expected e LEFT JOIN actual a USING(station,month)
                WHERE a.station IS NULL ORDER BY e.station,e.month""")
            query("missing_report_types", """SELECT source_dataset, count(*) AS observations
                FROM weather_observations WHERE report_type IS NULL GROUP BY source_dataset""")
        connection.rollback()
    finally:
        connection.close()
    ghcnh = next(row["observations"] for row in results["sources"] if row["source_dataset"] == "GHCNh")
    years = {(row["station"], row["year"]) for row in results["point_station_years"]}
    stations = {station for station, _ in years}
    results["checks"] = {
        "original_values_preserved": original["observations"] == BASELINE_COUNT and original["checksum"] == BASELINE_HASH,
        "manifest_complete": results["manifest"][0]["files"] == 320,
        "manifest_matches_rows": results["manifest"][0]["observations"] == ghcnh,
        "all_400_station_years_represented": stations == EXPECTED_STATIONS and
                        years == {(s,y) for s in EXPECTED_STATIONS for y in range(2005,2025)},
        "integrity_passed": all(value == 0 for value in results["integrity"][0].values()) and
                            all(value == 0 for value in results["element_qc_integrity"][0].values()),
        "legacy_hourly_count_preserved": sum(row["routine_hours"] for row in results["hourly_station_years"] if row["source_dataset"] == "LCDv1") == 874057,
    }
    output = ROOT / "outputs/audits/ingestion_2005_2024.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, indent=2, default=str) + "\n")
    print(json.dumps({key: results[key] for key in ["sources","manifest","integrity","element_qc_integrity","checks","missing_hourly_months"]}, indent=2, default=str))
    print("Full element/year evidence:", output)
    if not all(results["checks"].values()):
        raise SystemExit("Validation failed; inspect the evidence artifact")


if __name__ == "__main__":
    main()
