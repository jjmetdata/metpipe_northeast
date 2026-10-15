"""Publish a frozen, per-element reconciled core-20 snapshot; inputs untouched."""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg2
from psycopg2.extras import Json, execute_values

from audit_network_ghcnh import STATIONS
from observation_selection import POLICY, PRIMARY, FIELDS, MATCH, decode_metar, resolve_number, resolve_wind, lcd_wind_state

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/finalized_observations'
GH_FIELDS = list(FIELDS) + ['wind_direction_deg', 'wind_state', 'precipitation_trace']
L_FIELDS = {f: f for f in FIELDS}
L_FIELDS['precipitation_reported_mm'] = 'precipitation_mm'
DB_EXPR = {'temperature_c':'(temperature-32)/1.8', 'dewpoint_c':'(dewpoint-32)/1.8',
           'relative_humidity':'relative_humidity', 'station_pressure_hpa':'station_pressure*33.8638866667',
           'wind_speed_ms':'wind_speed/2.2369362921', 'wind_gust_ms':'wind_gust/2.2369362921',
           'precipitation_reported_mm':'precipitation*25.4'}


def connect():
    return psycopg2.connect(host=os.getenv('DB_HOST','localhost'),port=os.getenv('DB_PORT','5432'),
        dbname=os.getenv('DB_NAME','metpipe_northeast'),user=os.getenv('DB_USER') or os.getenv('USER'),
        password=os.getenv('DB_PASSWORD'))


def number(value):
    return None if value is None or pd.isna(value) else float(value)


def raw_lcd(station, year):
    path = ROOT / f'data/raw/{year}/{station.lower()}_hourly_{year}.csv'
    columns = ['DATE','REPORT_TYPE','REM','HourlyWindDirection'] + [v[1] for v in FIELDS.values()]
    names = pd.read_csv(path,nrows=0).columns
    frame = pd.read_csv(path,usecols=[c for c in columns if c in names],dtype=str)
    frame = frame[frame.REPORT_TYPE.eq('FM-15')].copy()
    frame['actual_time'] = pd.to_datetime(frame.DATE).dt.tz_localize('Etc/GMT+5').dt.tz_convert('UTC')
    # Collapse exact duplicate rows once; conflicting duplicate times are not
    # suitable evidence. Equivalent to per-time grouping, without 8,000 tiny
    # DataFrame allocations per file.
    frame = frame.drop_duplicates()
    frame = frame[~frame.actual_time.duplicated(keep=False)]
    result = frame.set_index('actual_time').to_dict('index')
    return result, {'station':station,'year':year,'path':str(path),
                    'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def lcd_quality(raw, field, stored):
    if raw is None:
        return True
    text = str(raw.get(FIELDS[field][1],''))
    if text.endswith('s'):
        return True
    if field == 'precipitation_reported_mm' and text == 'T':
        expected = .0254  # Preserved legacy cleaner trace marker, not true rainfall.
    else:
        try:
            expected = float(text)
        except (ValueError,TypeError):
            return stored is not None
        if field in {'temperature_c','dewpoint_c'}:
            expected = (expected-32)/1.8
        elif field == 'station_pressure_hpa':
            expected *= 33.8638866667
        elif field in {'wind_speed_ms','wind_gust_ms'}:
            expected /= 2.2369362921
        elif field == 'precipitation_reported_mm':
            expected *= 25.4
    return stored is None or not np.isfinite(expected) or abs(stored-expected) > 1e-7


def prepare_decisions(cursor):
    evidence, decisions, counts = [], [], Counter()
    original_modern_hours = 0
    for station in sorted(STATIONS):
        previous = {}
        for year in range(2020,2025):
            current, file = raw_lcd(station,year)
            evidence.append(file)
            lookup = {**previous,**current}
            start, end = pd.Timestamp(f'{year}-01-01',tz='UTC'),pd.Timestamp(f'{year+1}-01-01',tz='UTC')
            cursor.execute('SELECT hour_utc,observation_datetime_utc,' + ','.join(GH_FIELDS) +
                ' FROM ghcnh_parallel.hourly_observations WHERE dataset_version=%s AND station=%s '
                'AND hour_utc >= %s AND hour_utc < %s ORDER BY hour_utc', (PRIMARY,station,start.to_pydatetime(),end.to_pydatetime()))
            gh = pd.DataFrame(cursor.fetchall(),columns=['hour_utc','actual_time']+GH_FIELDS)
            expressions = [f'{expression} AS {field}' for field,expression in DB_EXPR.items()]
            # Index-friendly equivalent of the frozen LCDv1 checked-minute view:
            # same FM15 rule, coherent earliest row at its checked minute/hour.
            cursor.execute('''SELECT ((date_trunc('hour',w.datetime)+interval '5 hours') AT TIME ZONE 'UTC') AS hour_utc,
                ((w.datetime+interval '5 hours') AT TIME ZONE 'UTC') AS actual_time,'''+','.join(expressions)+''',wind_direction
                FROM (SELECT DISTINCT ON (date_trunc('hour',o.datetime)) o.*
                      FROM public.weather_observations o JOIN public.station_metadata m USING(station)
                      WHERE o.station=%s AND o.source_dataset='LCDv1' AND o.report_type='FM-15'
                      AND o.datetime >= %s AND o.datetime < %s AND EXTRACT(MINUTE FROM o.datetime)=m.minute_offset
                      ORDER BY date_trunc('hour',o.datetime),o.datetime ASC) w ORDER BY hour_utc''',
                (station,start.tz_convert('Etc/GMT+5').tz_localize(None).to_pydatetime(),
                 end.tz_convert('Etc/GMT+5').tz_localize(None).to_pydatetime()))
            lcd = pd.DataFrame(cursor.fetchall(),columns=['hour_utc','actual_time']+list(L_FIELDS)+['wind_direction'])
            original_modern_hours += len(lcd)
            pair = gh.merge(lcd,on='hour_utc',suffixes=('_gh','_lcd'),how='outer',validate='one_to_one')
            masks = pd.Series(False,index=pair.index)
            for field,(_,_,tol,bounds) in FIELDS.items():
                g,l = pair[field+'_gh'],pair[field+'_lcd']
                aligned = pair.actual_time_gh.eq(pair.actual_time_lcd)
                masks |= l.notna() & (g.isna() | ~aligned | (g-l).abs().gt(tol+1e-10))
                masks |= g.notna() & ~g.between(*bounds)
                if field == 'precipitation_reported_mm':
                    # Legacy trace marker is >0; preserve/resolve the trace state.
                    masks |= l.notna() & (pair.precipitation_trace.eq(True) | l.eq(.0254))
            lstate = [lcd_wind_state(None if pd.isna(d) else d,number(s))[0]
                      for d,s in zip(pair.wind_direction,pair.wind_speed_ms_lcd)]
            masks |= pd.Series(lstate,index=pair.index).ne(pair.wind_state.fillna('missing')) & pair.wind_direction.notna()
            gangle = pair.wind_direction_deg
            langle = pd.to_numeric(pair.wind_direction,errors='coerce')
            masks |= gangle.notna() & langle.notna() & ((gangle-langle+180)%360-180).abs().gt(.5)
            chosen = pair[masks]
            hours = [x.to_pydatetime() if hasattr(x,'to_pydatetime') else x for x in chosen.hour_utc]
            flags = {}
            if hours:
                cursor.execute('SELECT hour_utc,quality_flags FROM ghcnh_parallel.hourly_observations '
                    'WHERE dataset_version=%s AND station=%s AND hour_utc=ANY(%s)',(PRIMARY,station,hours))
                flags = dict(cursor.fetchall())
            for r in chosen.to_dict('records'):
                hour = r['hour_utc']
                gt = None if pd.isna(r['actual_time_gh']) else r['actual_time_gh']
                lt = None if pd.isna(r['actual_time_lcd']) else r['actual_time_lcd']
                raw = lookup.get(lt)
                metar = decode_metar(raw.get('REM',''),station,lt) if raw is not None else {}
                selected = {}
                for field,(raw_name,_,_,_) in FIELDS.items():
                    g,l = number(r[field+'_gh']),number(r[field+'_lcd'])
                    suspect = lcd_quality(raw,field,l) if l is not None else False
                    trace = raw is not None and raw.get('HourlyPrecipitation') == 'T'
                    original_lcd = l
                    if field == 'precipitation_reported_mm' and trace:
                        l = 0.  # Trace flag, never an invented positive amount.
                    gtrace = None if pd.isna(r['precipitation_trace']) else bool(r['precipitation_trace'])
                    d = resolve_number(field,g,l,gt,lt,flags.get(hour,{}).get(raw_name,{}),
                        lcd_suspect=suspect,metar=metar,gh_trace=gtrace,lcd_trace=trace if l is not None else None)
                    if d is not None:
                        if field == 'precipitation_reported_mm':
                            d['lcd_stored_trace_marker_or_amount_mm'] = original_lcd
                        selected[field] = d
                        counts[field+':'+d['reason']] += 1
                ls,la = lcd_wind_state(None if pd.isna(r['wind_direction']) else r['wind_direction'],number(r['wind_speed_ms_lcd']))
                if raw is None or str(raw.get('HourlyWindDirection','')).endswith('s') or str(raw.get('HourlyWindSpeed','')).endswith('s'):
                    ls,la = 'missing',None
                gs = 'missing' if pd.isna(r['wind_state']) else r['wind_state']
                d = resolve_wind(gs,number(r['wind_direction_deg']),ls,la,gt,lt,
                                 flags.get(hour,{}).get('wind_direction',{}),metar)
                if d is not None:
                    selected['wind_direction_deg'] = d
                    counts['wind_direction_deg:'+d['reason']] += 1
                if selected:
                    decisions.append((POLICY,station,hour,Json(selected)))
            previous = current
        print(f'Prepared {station}: {len(decisions):,} hours with explicit decisions',flush=True)
    if original_modern_hours != 873957:
        raise ValueError('LCD checked-minute hours changed since overlap verification')
    return decisions,evidence,counts


def policy_definition():
    files = [Path(__file__),ROOT/'analysis/observation_selection.py',ROOT/'sql/migrations/003_finalized_observations.sql']
    return {'primary_dataset_version':PRIMARY,'core_stations':sorted(STATIONS),
        'utc_scope':['2005-01-01T00:00Z','2025-01-01T00:00Z'],
        'precision_tolerances_and_global_bounds':FIELDS,'metar_match_tolerances':MATCH,
        'conflicts':'unresolved element NULL, never drop hour or delete inputs',
        'metar':'Exact station/time LCD-embedded report support, not independent sensor truth; no derived RH/station pressure',
        'fallback':'LCD raw evidence required, no suspect suffix or primary bad QC; exact report time unless entire primary hour absent',
        'precipitation':'Reported amount only; trace=0 plus flag; accumulation duration not certified',
        'code_hashes':{str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}}


def snapshot_sql():
    fields = list(FIELDS)+['sea_level_pressure_hpa','altimeter_hpa','wind_direction_deg']
    bounds = {f: spec[3] for f,spec in FIELDS.items()}
    bounds.update({'sea_level_pressure_hpa':(400,1100),'altimeter_hpa':(400,1100),'wind_direction_deg':(0,360)})
    values = []
    for field in fields:
        lo,hi = bounds[field]
        values.append(f"CASE WHEN d.decisions ? '{field}' THEN (d.decisions->'{field}'->>'value')::double precision "
                      f'ELSE CASE WHEN g.{field} BETWEEN {lo} AND {hi} THEN g.{field} END END')
    columns = ['policy_version','station','hour_utc','primary_observation_datetime_utc']+fields+['wind_state','precipitation_trace']
    return 'INSERT INTO metpipe_final.hourly_snapshots ('+','.join(columns)+') SELECT %s,stations.station,hours.hour_utc,g.observation_datetime_utc,'+','.join(values)+''',
        CASE WHEN d.decisions ? 'wind_direction_deg' THEN d.decisions->'wind_direction_deg'->>'state' ELSE COALESCE(g.wind_state,'missing') END,
        CASE WHEN d.decisions ? 'precipitation_reported_mm' THEN (d.decisions->'precipitation_reported_mm'->>'trace')::boolean ELSE g.precipitation_trace END
        FROM (SELECT unnest(%s::text[]) AS station) stations
        CROSS JOIN generate_series(TIMESTAMPTZ '2005-01-01 00:00+00',TIMESTAMPTZ '2024-12-31 23:00+00',interval '1 hour') hours(hour_utc)
        LEFT JOIN ghcnh_parallel.hourly_observations g ON g.station=stations.station AND g.hour_utc=hours.hour_utc AND g.dataset_version=%s
        LEFT JOIN metpipe_final.hour_decisions d ON d.station=stations.station AND d.hour_utc=hours.hour_utc AND d.policy_version=%s
        ORDER BY stations.station,hours.hour_utc'''


def run():
    OUT.mkdir(parents=True,exist_ok=True)
    definition = policy_definition()
    connection = connect()
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("SET LOCAL TIME ZONE 'UTC'")
                cursor.execute("SELECT pg_advisory_xact_lock(hashtext('metpipe-final-v1'))")
                cursor.execute('LOCK TABLE public.weather_observations,ghcnh_parallel.hourly_observations IN SHARE MODE')
                cursor.execute('SELECT count(*) FROM public.weather_observations')
                original_before = cursor.fetchone()[0]
                cursor.execute('SELECT count(*) FROM ghcnh_parallel.hourly_observations WHERE dataset_version=%s',(PRIMARY,))
                primary_before = cursor.fetchone()[0]
                cursor.execute('SELECT status FROM ghcnh_parallel.dataset_versions WHERE dataset_version=%s',(PRIMARY,))
                if cursor.fetchone() != ('complete',) or primary_before != 3497180:
                    raise ValueError('Expected complete immutable primary dataset')
                cursor.execute((ROOT/'sql/migrations/003_finalized_observations.sql').read_text())
                cursor.execute('SELECT policy,status FROM metpipe_final.policy_versions WHERE policy_version=%s',(POLICY,))
                previous = cursor.fetchone()
                if previous:
                    if previous[1] != 'complete' or previous[0] != json.loads(json.dumps(definition)):
                        raise ValueError('Existing policy version differs; publish a new reviewed version')
                    cursor.execute('SELECT source_path,source_sha256 FROM metpipe_final.evidence_files WHERE policy_version=%s',(POLICY,))
                    files = cursor.fetchall()
                    if len(files) != 100 or any(hashlib.sha256(Path(p).read_bytes()).hexdigest()!=sha for p,sha in files):
                        raise ValueError('LCD evidence changed')
                    counts = None
                else:
                    cursor.execute("INSERT INTO metpipe_final.policy_versions VALUES (%s,%s,'loading',now(),NULL)",(POLICY,Json(definition)))
                    decisions,evidence,counts = prepare_decisions(cursor)
                    execute_values(cursor,'INSERT INTO metpipe_final.evidence_files VALUES %s',
                        [(POLICY,e['station'],e['year'],e['path'],e['sha256']) for e in evidence])
                    if decisions:
                        execute_values(cursor,'INSERT INTO metpipe_final.hour_decisions VALUES %s',decisions,page_size=500)
                    print('Publishing expected-hour snapshot (sources unchanged)...',flush=True)
                    cursor.execute(snapshot_sql(),(POLICY,sorted(STATIONS),PRIMARY,POLICY))
                cursor.execute('SELECT count(*),count(DISTINCT station) FROM metpipe_final.hourly_snapshots WHERE policy_version=%s',(POLICY,))
                rows,stations = cursor.fetchone()
                if (rows,stations)!=(3506400,20):
                    raise ValueError('Incomplete expected-hour snapshot')
                cursor.execute('''SELECT count(*) FROM metpipe_final.hour_decisions d
                    JOIN metpipe_final.hourly_snapshots h USING(policy_version,station,hour_utc)
                    CROSS JOIN LATERAL jsonb_each(d.decisions) e
                    WHERE d.policy_version=%s AND e.value->>'reason'='conflict_unresolved'
                    AND (to_jsonb(h)->e.key) <> 'null'::jsonb''',(POLICY,))
                if cursor.fetchone()[0]:
                    raise ValueError('Unresolved conflict retained a finalized value')
                cursor.execute('SELECT count(*) FROM public.weather_observations')
                original_after = cursor.fetchone()[0]
                cursor.execute('SELECT count(*) FROM ghcnh_parallel.hourly_observations WHERE dataset_version=%s',(PRIMARY,))
                primary_after = cursor.fetchone()[0]
                if original_before!=original_after or primary_before!=primary_after:
                    raise ValueError('Input dataset changed')
                cursor.execute("UPDATE metpipe_final.policy_versions SET status='complete',completed_at=COALESCE(completed_at,now()) WHERE policy_version=%s",(POLICY,))
                cursor.execute('SELECT count(*) FROM metpipe_final.hour_decisions WHERE policy_version=%s',(POLICY,))
                decision_hours = cursor.fetchone()[0]
        result = {'policy_version':POLICY,'status':'complete','expected_hour_rows':rows,'core_stations':stations,
                  'hours_with_decisions':decision_hours,'original_rows':original_after,'primary_rows':primary_after,
                  'inputs_unchanged':True,'idempotent_rerun':bool(previous)}
        if counts is not None:
            result['decision_counts'] = dict(counts)
            (OUT/'initial_publication_summary.json').write_text(json.dumps(result,indent=2)+'\n')
        (OUT/'latest_publication_summary.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result,indent=2),flush=True)
        return result
    finally:
        connection.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish',action='store_true')
    if not parser.parse_args().publish:
        parser.error('Explicit --publish required; no default database writes')
    run()
