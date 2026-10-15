"""Add audited CQX observations in an auxiliary schema, not the core network."""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

from add_parallel_ghcnh import serialize, COLUMNS
from audit_network_ghcnh import FIELDS, select_records, BASE, STATIONS
from publish_final_observations import connect

ROOT = Path(__file__).resolve().parents[1]
VERSION = 'CQX_GHCNh_2005_2024_auxiliary_v1'
ID = 'USW00094624'
OUT = ROOT / 'outputs/auxiliary_cqx'


def auxiliary_stream(raw, chosen, year):
    source = serialize(raw,chosen,'CQX',year)
    stream = io.StringIO()
    writer = csv.writer(stream)
    for values in csv.reader(source):
        values[0] = VERSION
        writer.writerow(values)
    stream.seek(0)
    return stream


def run():
    OUT.mkdir(parents=True,exist_ok=True)
    audit = json.loads((ROOT/'outputs/audits/pvc_neighbors/annual_audit.json').read_text())
    sources = sorted([r for r in audit if r['station']=='CQX' and 2005<=r['year']<=2024],key=lambda r:r['year'])
    if len(sources)!=20 or any(r['status']!='read' for r in sources):
        raise ValueError('Twenty successful audited CQX years required')
    for source in sources:
        path = ROOT/f"outputs/audits/pvc_neighbors/raw/CQX_{source['year']}.parquet"
        if hashlib.sha256(path.read_bytes()).hexdigest()!=source['sha256']:
            raise ValueError('CQX source changed since audit')
    connection = connect()
    totals = {field:0 for field in FIELDS.values()}
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("SET LOCAL TIME ZONE 'UTC'")
                cursor.execute("SELECT pg_advisory_xact_lock(hashtext('metpipe-aux-CQX-v1'))")
                cursor.execute('LOCK TABLE public.weather_observations,public.station_metadata IN SHARE MODE')
                cursor.execute('SELECT count(*) FROM public.weather_observations')
                original_before = cursor.fetchone()[0]
                cursor.execute('SELECT station FROM public.station_metadata ORDER BY station')
                network = [r[0] for r in cursor.fetchall()]
                if network!=sorted(STATIONS):
                    raise ValueError('Unexpected core membership')
                cursor.execute((ROOT/'sql/migrations/004_auxiliary_stations.sql').read_text())
                cursor.execute("INSERT INTO metpipe_aux.stations VALUES ('CQX',%s,'CHATHAM MUNICIPAL AIRPORT (MA)','auxiliary') ON CONFLICT DO NOTHING",(ID,))
                expected_rows = 0
                reused = 0
                for source in sources:
                    year = source['year']
                    path = ROOT/f'outputs/audits/pvc_neighbors/raw/CQX_{year}.parquet'
                    names = pq.ParquetFile(path).schema.names
                    columns = [n for n in names if n in {'DATE','STATION'} or any(n==f or n.startswith(f+'_') for f in FIELDS)]
                    raw = pq.read_table(path,columns=columns,use_threads=False).to_pandas()
                    if set(raw.STATION)!={ID} or set(pd.to_datetime(raw.DATE,utc=True).dt.year)!={year}:
                        raise ValueError('CQX source identity/year mismatch')
                    chosen,_ = select_records(raw)
                    expected_rows += len(chosen)
                    for field in totals:
                        totals[field] += int(chosen[field].notna().sum())
                    cursor.execute('SELECT source_sha256,routine_rows FROM metpipe_aux.source_files WHERE dataset_version=%s AND station=%s AND source_year=%s',(VERSION,'CQX',year))
                    previous = cursor.fetchone()
                    if previous:
                        if previous!=(source['sha256'],len(chosen)):
                            raise ValueError('Immutable auxiliary version differs')
                        reused += 1
                    else:
                        cursor.execute('INSERT INTO metpipe_aux.source_files VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',
                            (VERSION,'CQX',year,ID,f'{BASE}/{year}/parquet/GHCNh_{ID}_{year}.parquet',source['sha256'],str(path),len(chosen)))
                        cursor.copy_expert('COPY metpipe_aux.hourly_observations ('+','.join(COLUMNS)+") FROM STDIN WITH (FORMAT CSV, NULL '\\N')",auxiliary_stream(raw,chosen,year))
                    cursor.execute('SELECT count(*) FROM metpipe_aux.hourly_observations WHERE dataset_version=%s AND station=%s AND source_year=%s',(VERSION,'CQX',year))
                    if cursor.fetchone()[0]!=len(chosen):
                        raise ValueError('CQX station-year count mismatch')
                    print(f'Checked/staged CQX {year}: {len(chosen):,} routine hours',flush=True)
                if reused not in {0,20}:
                    raise ValueError('Unexpected partially published auxiliary version')
                cursor.execute('SELECT count(*),count(DISTINCT source_year) FROM metpipe_aux.source_files WHERE dataset_version=%s',(VERSION,))
                if cursor.fetchone()!=(20,20):
                    raise ValueError('Incomplete auxiliary source registry')
                mappings = {k:k for k in totals if k!='wind_direction_reported'}
                mappings['hourly_precipitation_mm']='precipitation_reported_mm'
                expressions = [f'count({column})' for column in mappings.values()]+["count(*) FILTER (WHERE wind_state<>'missing')"]
                cursor.execute('SELECT '+','.join(expressions)+' FROM metpipe_aux.hourly_observations WHERE dataset_version=%s',(VERSION,))
                if list(cursor.fetchone())!=[totals[k] for k in mappings]+[totals['wind_direction_reported']]:
                    raise ValueError('Auxiliary element counts differ from selected raw records')
                cursor.execute('SELECT count(*) FROM public.weather_observations')
                original_after = cursor.fetchone()[0]
                cursor.execute('SELECT station FROM public.station_metadata ORDER BY station')
                if original_after!=original_before or [r[0] for r in cursor.fetchall()]!=network:
                    raise ValueError('Original data/core membership changed')
        result = {'dataset_version':VERSION,'station':'CQX','station_id':ID,'role':'auxiliary','years':[2005,2024],
                  'hourly_rows':expected_rows,'source_files':20,'core_stations_unchanged':20,
                  'original_rows_unchanged':original_after,'idempotent_rerun':reused==20,
                  'element_hours':totals,'availability_pct':{k:100*v/175320 for k,v in totals.items()}}
        (OUT/'ingestion_summary.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result,indent=2),flush=True)
        return result
    finally:
        connection.close()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish',action='store_true')
    if not parser.parse_args().publish:
        parser.error('Explicit --publish required; no default writes')
    run()
