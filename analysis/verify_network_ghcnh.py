"""Read-only exact-time LCD/GHCNh overlap checks; no claim of independent accuracy.

Engineering gates are declared before opening the overlap. They test source
compatibility for a parallel research dataset, not suitability for replacement.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from sqlalchemy import text

from audit_network_ghcnh import FIELDS, OUT as CACHE, select_records
from eda_utils import database_engine

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/audits/network_ghcnh_verification'
# (median absolute difference, 95th-percentile absolute difference), SI units.
# Allow reporting precision/rounding, but catch systematic unit/source mistakes.
GATES = {'temperature_c': (.3, 1.1), 'dewpoint_c': (.3, 1.1),
         'relative_humidity': (2., 7.), 'station_pressure_hpa': (.2, .6),
         'wind_speed_ms': (.6, 1.2)}
MIN_PAIRS = 500


def metrics(pair, field):
    a, b = pair[field + '_ghcnh'], pair[field + '_lcd']
    valid = a.notna() & b.notna() & np.isfinite(a) & np.isfinite(b)
    delta = (a - b)[valid]
    n = len(delta)
    return {'paired_values': n, 'bias': float(delta.mean()) if n else None,
            'mae': float(delta.abs().mean()) if n else None,
            'median_abs': float(delta.abs().median()) if n else None,
            'p95_abs': float(delta.abs().quantile(.95)) if n else None,
            'p99_abs': float(delta.abs().quantile(.99)) if n else None,
            'max_abs': float(delta.abs().max()) if n else None,
            'rmse': float(np.sqrt((delta ** 2).mean())) if n else None}


def passes(result, field):
    median, p95 = GATES[field]
    return bool(result['paired_values'] >= MIN_PAIRS and
                result['median_abs'] <= median and result['p95_abs'] <= p95)


def exact_pairs(ghcnh, lcd):
    if ghcnh.actual_time.duplicated().any() or lcd.actual_time.duplicated().any():
        raise ValueError('Duplicate actual report times')
    return ghcnh.merge(lcd, on='actual_time', suffixes=('_ghcnh', '_lcd'),
                      how='inner', validate='one_to_one')


def pc24(frame, field):
    series = frame.set_index('actual_time')[field].sort_index()
    prior = series.reindex(series.index - pd.Timedelta(hours=24))
    prior.index = series.index
    return series - prior


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    protocol = {'purpose': 'Parallel research dataset compatibility, not replacement or sensor accuracy',
                'scope': '20 stations, UTC 2020–2024; exact selected routine report time',
                'gates': GATES, 'minimum_pairs_per_station_year_element': MIN_PAIRS,
                'precipitation': 'Diagnostic only; hourly accumulation semantics not certified',
                '2025': 'Excluded: known network-wide pressure gaps',
                'code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (OUT / 'verification_protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
    manifest = json.loads((CACHE / 'source_manifest.json').read_text())
    sources = [r for r in manifest if 2020 <= r['year'] <= 2024]
    if len(sources) != 100 or any(r['status'] != 'read' for r in sources):
        raise ValueError('Expected 100 successful modern source files')
    engine = database_engine()
    records, outliers, timing = [], [], []
    with engine.connect() as conn:
        if conn.execute(text('SHOW transaction_read_only')).scalar() != 'on':
            raise ValueError('Read-only connection required')
        before = conn.execute(text('SELECT count(*) FROM weather_observations')).scalar()
        for i, source in enumerate(sources, 1):
            station, year = source['station'], source['year']
            path = Path(source['path'])
            if hashlib.sha256(path.read_bytes()).hexdigest() != source['sha256']:
                raise ValueError('Source file changed since availability audit')
            names = pq.ParquetFile(path).schema.names
            columns = [n for n in names if n in {'DATE', 'STATION'} or
                       any(n == f or n.startswith(f + '_') for f in FIELDS)]
            raw = pq.read_table(path, columns=columns, use_threads=False).to_pandas()
            if set(raw.STATION) != {source['station_id']}:
                raise ValueError('Station mismatch')
            chosen, _ = select_records(raw)
            if set(chosen.actual_time.dt.year) != {year}:
                raise ValueError('Unexpected UTC year')
            fields = list(GATES) + ['hourly_precipitation_mm', 'wind_gust_ms']
            sql = text('''SELECT observation_datetime_utc AS actual_time,
                temperature_c, dewpoint_c, relative_humidity, station_pressure_hpa,
                wind_speed_ms, precipitation_mm AS hourly_precipitation_mm, wind_gust_ms
                FROM weather_hourly_utc WHERE station=:station AND source_dataset='LCDv1'
                AND observation_datetime_utc >= :start AND observation_datetime_utc < :end
                ORDER BY observation_datetime_utc''')
            lcd = pd.read_sql_query(sql, conn, params={'station': station,
                'start': pd.Timestamp(f'{year}-01-01', tz='UTC').to_pydatetime(),
                'end': pd.Timestamp(f'{year+1}-01-01', tz='UTC').to_pydatetime()})
            lcd['actual_time'] = pd.to_datetime(lcd.actual_time, utc=True)
            gh = chosen[['actual_time'] + fields].copy()
            pair = exact_pairs(gh, lcd)
            timing.append({'station': station, 'year': year, 'ghcnh_hours': len(gh),
                           'lcd_hours': len(lcd), 'exact_time_pairs': len(pair),
                           'ghcnh_other_times': len(gh) - len(pair),
                           'lcd_other_times': len(lcd) - len(pair)})
            for field in fields:
                m = metrics(pair, field)
                records.append({'station': station, 'year': year, 'element': field,
                                **m, 'gate': 'pass' if passes(m, field) else 'fail'
                                if field in GATES else 'diagnostic'} if field in GATES else
                               {'station': station, 'year': year, 'element': field, **m, 'gate': 'diagnostic'})
                delta = pair[field + '_ghcnh'] - pair[field + '_lcd']
                for idx in delta.abs().nlargest(3).index:
                    if pd.notna(delta.loc[idx]):
                        outliers.append({'station': station, 'year': year, 'element': field,
                            'actual_time': pair.loc[idx, 'actual_time'].isoformat(),
                            'ghcnh': float(pair.loc[idx, field + '_ghcnh']),
                            'lcd': float(pair.loc[idx, field + '_lcd']), 'delta': float(delta.loc[idx])})
            for frame, suffix in [(gh, 'ghcnh'), (lcd, 'lcd')]:
                frame['pc24'] = frame.actual_time.map(pc24(frame, 'station_pressure_hpa'))
            pc = exact_pairs(gh[['actual_time', 'pc24']], lcd[['actual_time', 'pc24']])
            records.append({'station': station, 'year': year, 'element': 'pc24_hpa',
                            **metrics(pc, 'pc24'), 'gate': 'diagnostic'})
            if i % 10 == 0:
                print(f'Compared {i}/100 station-years', flush=True)
        after = conn.execute(text('SELECT count(*) FROM weather_observations')).scalar()
    engine.dispose()
    if before != after:
        raise ValueError('Production count changed during verification')
    results = pd.DataFrame(records)
    results.to_csv(OUT / 'element_agreement.csv', index=False)
    pd.DataFrame(timing).to_csv(OUT / 'report_time_overlap.csv', index=False)
    pd.DataFrame(outliers).to_csv(OUT / 'largest_discrepancies.csv', index=False)
    failed = results[results.gate.eq('fail')]
    failed.to_csv(OUT / 'failed_gates.csv', index=False)
    summary = {'core_gate_cases': 500, 'passed': int(results.gate.eq('pass').sum()),
               'failed': len(failed), 'parallel_dataset_eligible': failed.empty,
               'production_rows_before': before, 'production_rows_after': after,
               'database_writes': False, 'source_files': 100, 'protocol': protocol}
    (OUT / 'verification_summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    report = ['# GHCNh overlap verification', '',
              f"Core engineering checks: {summary['passed']}/500 passed; {len(failed)} failed.", '',
              'These are source-compatibility checks, not independent sensor accuracy or replacement approval.', '',
              'Exact UTC report timestamps are paired, not simply hourly buckets. Missing values remain missing. '
              '2025 is excluded. Gust and rainfall are diagnostics only; precipitation accumulation semantics '
              'are not certified. PC24 uses an exact 24-hour earlier timestamp, never a 24-row shift.', '',
              '## Failed station-year/element checks', '',
              '```', failed.to_string(index=False), '```', '',
              '## Mean station-level differences across annual comparisons', '', '```',
              results.groupby('element')[['bias', 'mae', 'p95_abs', 'max_abs']].mean().round(4).to_string(),
              '```', '', 'Production database unchanged. Full CSV results and source hashes accompany this report.']
    (OUT / 'verification_report.md').write_text('\n'.join(report) + '\n')
    print(json.dumps({k: v for k, v in summary.items() if k != 'protocol'}, indent=2), flush=True)
    return summary


if __name__ == '__main__':
    run()
