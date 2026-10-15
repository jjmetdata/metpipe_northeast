"""Explicit additive GHCNh dataset publication after exact-time overlap gates.

Entire 400-file import is one transaction. Production is protected by identical
before/after counts and a share lock. Reruns verify the immutable version
and row/element counts instead of appending duplicates.
"""
import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path

import pandas as pd
import psycopg2
from psycopg2.extras import Json
import pyarrow.parquet as pq

from audit_network_ghcnh import FIELDS, OUT as CACHE, STATIONS, select_records, screen_field
from verify_network_ghcnh import OUT as VERIFY, passes

ROOT = Path(__file__).resolve().parents[1]
VERSION = 'GHCNh_2005_2024_routine_v1'
OUT = ROOT / 'outputs/audits/network_ghcnh_verification'
COLUMNS = ['dataset_version', 'station', 'source_year', 'hour_utc',
           'observation_datetime_utc', 'report_type', 'temperature_c', 'dewpoint_c',
           'relative_humidity', 'station_pressure_hpa', 'sea_level_pressure_hpa',
           'altimeter_hpa', 'wind_speed_ms', 'wind_direction_deg', 'wind_state',
           'wind_gust_ms', 'precipitation_reported_mm', 'precipitation_trace', 'quality_flags']


def verification_guard():
    summary = json.loads((VERIFY / 'verification_summary.json').read_text())
    protocol = json.loads((VERIFY / 'verification_protocol.json').read_text())
    code = ROOT / 'analysis/verify_network_ghcnh.py'
    if protocol['code_sha256'] != hashlib.sha256(code.read_bytes()).hexdigest():
        raise ValueError('Verification code changed; rerun verification first')
    gates = pd.read_csv(VERIFY / 'element_agreement.csv')
    core = gates[gates.element.isin(protocol['gates'])]
    expected = {(s, y, f) for s in STATIONS for y in range(2020, 2025) for f in protocol['gates']}
    actual = set(core[['station', 'year', 'element']].itertuples(index=False, name=None))
    if (actual != expected or len(core) != 500 or not core.gate.eq('pass').all()
            or not summary['parallel_dataset_eligible'] or summary['failed'] != 0):
        raise ValueError('Complete passing verification required')
    if not all(passes(row, row['element']) for row in core.to_dict('records')):
        raise ValueError('Stored agreement metrics do not pass the fixed gates')
    return summary


def wind_value(raw_row, screened):
    code = str(raw_row.get('wind_direction_Measurement_Code', ''))
    if pd.isna(screened):
        return None, 'missing'
    if code in {'C', 'V'}:
        return None, 'calm' if code == 'C' else 'variable'
    return float(screened), 'numeric'


def cell(value):
    if value is None or pd.isna(value):
        return None
    return value.item() if hasattr(value, 'item') else value


def serialize(raw, chosen, station, year):
    _, precipitation = screen_field(raw, 'precipitation')
    stream = io.StringIO()
    writer = csv.writer(stream)
    raw_rows = raw.to_dict('index')
    for idx, row in chosen.iterrows():
        original = raw_rows[idx]
        direction, state = wind_value(original, row.wind_direction_reported)
        flags = {}
        for field in FIELDS:
            flags[field] = {'raw': cell(original.get(field))}
            for key, suffix in [('s', '_Source_Code'), ('q', '_Quality_Code'),
                                ('m', '_Measurement_Code'), ('r', '_Report_Type'),
                                ('sid', '_Source_Station_ID')]:
                value = cell(original.get(field + suffix))
                if value is not None:
                    flags[field][key] = value
        rain = cell(row.hourly_precipitation_mm)
        values = [VERSION, station, year, row.hour_utc.isoformat(), row.actual_time.isoformat(),
                  row.kind] + [cell(row[c]) for c in ['temperature_c', 'dewpoint_c',
                  'relative_humidity', 'station_pressure_hpa', 'sea_level_pressure_hpa',
                  'altimeter_hpa', 'wind_speed_ms']] + [direction, state, cell(row.wind_gust_ms),
                  rain, bool(precipitation['trace'].loc[idx]) if rain is not None else None,
                  json.dumps(flags, separators=(',', ':'), allow_nan=False)]
        writer.writerow(['\\N' if v is None else v for v in values])
    stream.seek(0)
    return stream


def verify_counts(cursor, sources, annual):
    # All selected numerical fields, not just aggregate row count.
    names = {c: c for c in FIELDS.values() if c != 'wind_direction_reported'}
    names['hourly_precipitation_mm'] = 'precipitation_reported_mm'
    expressions = ['count(*)'] + [f'count({column})' for column in names.values()]
    expressions += ["count(*) FILTER (WHERE wind_state <> 'missing')"]
    cursor.execute('SELECT station, source_year, ' + ','.join(expressions) +
        ' FROM ghcnh_parallel.hourly_observations WHERE dataset_version=%s '
        'GROUP BY station,source_year', (VERSION,))
    seen = set()
    for result in cursor.fetchall():
        station, year, rows, *counts = result
        expected = annual.loc[(station, year)]
        targets = [int(expected[name + '_hours']) for name in names]
        targets += [int(expected.wind_direction_reported_hours)]
        if rows != int(expected.routine_hours) or counts != targets:
            raise ValueError(f'Row/element-count mismatch {station} {year}')
        seen.add((station, year))
    if seen != {(r['station'], r['year']) for r in sources}:
        raise ValueError('Incomplete imported station-years')


def run():
    verification = verification_guard()
    manifest = json.loads((CACHE / 'source_manifest.json').read_text())
    sources = [r for r in manifest if 2005 <= r['year'] <= 2024]
    if len(sources) != 400 or any(r['status'] != 'read' for r in sources):
        raise ValueError('400 audited files required')
    annual = pd.read_csv(CACHE / 'annual_availability.csv').set_index(['station', 'year'])
    # Check all identities/hashes before any database mutation.
    for source in sources:
        if hashlib.sha256(Path(source['path']).read_bytes()).hexdigest() != source['sha256']:
            raise ValueError('Raw source changed since audit')
    connection = psycopg2.connect(host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'), dbname=os.getenv('DB_NAME', 'metpipe_northeast'),
        user=os.getenv('DB_USER') or os.getenv('USER'), password=os.getenv('DB_PASSWORD'))
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("SET LOCAL TIME ZONE 'UTC'")
                cursor.execute("SELECT pg_advisory_xact_lock(hashtext('metpipe-ghcnh-parallel-v1'))")
                cursor.execute('LOCK TABLE public.weather_observations IN SHARE MODE')
                cursor.execute('SELECT count(*) FROM public.weather_observations')
                before = cursor.fetchone()[0]
                cursor.execute((ROOT / 'sql/migrations/002_ghcnh_parallel_dataset.sql').read_text())
                cursor.execute('SELECT status FROM ghcnh_parallel.dataset_versions WHERE dataset_version=%s', (VERSION,))
                previous = cursor.fetchone()
                if previous and previous[0] != 'complete':
                    raise ValueError('Unexpected incomplete existing version')
                if not previous:
                    cursor.execute('INSERT INTO ghcnh_parallel.dataset_versions (dataset_version,verification,status) '
                                   "VALUES (%s,%s,'loading')", (VERSION, Json(verification)))
                for number, source in enumerate(sources, 1):
                    station, year = source['station'], source['year']
                    if previous:
                        cursor.execute('SELECT source_sha256 FROM ghcnh_parallel.source_files '
                            'WHERE dataset_version=%s AND station=%s AND source_year=%s', (VERSION, station, year))
                        found = cursor.fetchone()
                        if not found or found[0] != source['sha256']:
                            raise ValueError('Existing immutable version differs from audited sources')
                        continue
                    path = Path(source['path'])
                    columns = [n for n in pq.ParquetFile(path).schema.names if n in {'DATE', 'STATION'}
                               or any(n == f or n.startswith(f + '_') for f in FIELDS)]
                    raw = pq.read_table(path, columns=columns, use_threads=False).to_pandas()
                    if set(raw.STATION) != {source['station_id']} or set(pd.to_datetime(raw.DATE, utc=True).dt.year) != {year}:
                        raise ValueError('Identity/year mismatch')
                    chosen, _ = select_records(raw)
                    cursor.execute('INSERT INTO ghcnh_parallel.source_files VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',
                        (VERSION, station, year, source['station_id'], source['file_url'],
                         source['sha256'], str(path), len(chosen)))
                    stream = serialize(raw, chosen, station, year)
                    cursor.copy_expert('COPY ghcnh_parallel.hourly_observations (' + ','.join(COLUMNS) +
                                      ") FROM STDIN WITH (FORMAT CSV, NULL '\\N')", stream)
                    if number % 20 == 0:
                        print(f'Staged {number}/400 station-years (uncommitted)', flush=True)
                verify_counts(cursor, sources, annual)
                cursor.execute('SELECT count(*) FROM public.weather_observations')
                after = cursor.fetchone()[0]
                if before != after:
                    raise ValueError('Production count changed')
                cursor.execute("UPDATE ghcnh_parallel.dataset_versions SET status='complete', completed_at=COALESCE(completed_at,now()) "
                               'WHERE dataset_version=%s', (VERSION,))
                cursor.execute('SELECT count(*) FROM ghcnh_parallel.hourly_observations WHERE dataset_version=%s', (VERSION,))
                rows = cursor.fetchone()[0]
        result = {'dataset_version': VERSION, 'status': 'complete', 'station_years': 400,
                  'hourly_rows': rows, 'production_rows_before': before, 'production_rows_after': after,
                  'production_tables_views_changed': False, 'idempotent_rerun': bool(previous)}
        (OUT / 'parallel_ingestion_summary.json').write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps(result, indent=2), flush=True)
        return result
    finally:
        connection.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish', action='store_true', help='Explicitly create/add the parallel dataset')
    if not parser.parse_args().publish:
        parser.error('No default writes; use --publish after verification')
    run()
