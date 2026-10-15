"""Read-only finalized station/year/element coverage, gaps and source reasons."""
import calendar
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy import text

from eda_utils import database_engine
from observation_selection import POLICY

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/audits/finalized_availability'
FIELDS = ['temperature_c','dewpoint_c','relative_humidity','station_pressure_hpa',
          'sea_level_pressure_hpa','altimeter_hpa','wind_speed_ms',
          'wind_direction_deg','wind_gust_ms','precipitation_reported_mm']
CORE = ['temperature_c','dewpoint_c','relative_humidity','station_pressure_hpa','wind_speed_ms']
GAP_FIELDS = CORE + ['precipitation_reported_mm']
START, END = pd.Timestamp('2005-01-01',tz='UTC'),pd.Timestamp('2025-01-01',tz='UTC')


def missing_runs(index, present):
    """Complete, ordered UTC calendar required; endpoints are [start,end)."""
    index = pd.DatetimeIndex(index)
    if index.tz is None or not index.equals(pd.date_range(index.min(),index.max(),freq='h')):
        raise ValueError('Complete ordered timezone-aware hourly scaffold required')
    missing = ~np.asarray(present,dtype=bool)
    starts = np.flatnonzero(missing & ~np.r_[False,missing[:-1]])
    ends = np.flatnonzero(missing & ~np.r_[missing[1:],False]) + 1
    return [{'start_utc':index[a].isoformat(),
             'end_utc_exclusive':pd.Timestamp(index[b-1].value+3_600_000_000_000,tz='UTC').isoformat(),
             'missing_hours':int(b-a),'within_72h_length_only':bool(b-a<=72),
             'touches_scope_boundary':bool(a==0 or b==len(index))}
            for a,b in zip(starts,ends)]


def annual_summary(frame, role):
    result = frame.drop(columns=['year']).groupby('station',sort=True).sum(numeric_only=True)
    count_columns = [f+'_hours' for f in FIELDS]+['wind_reported_state_hours','any_core_hours','all_core_hours','selected_report_hours']
    for column in count_columns:
        result[column.removesuffix('_hours')+'_pct'] = 100*result[column]/result.expected_hours
    result['role'] = role
    return result.reset_index()


def availability_query(table, version_column, version):
    fields = [f'count({f}) AS {f}_hours' for f in FIELDS]
    core_any = ' OR '.join(f'{f} IS NOT NULL' for f in CORE)
    core_all = ' AND '.join(f'{f} IS NOT NULL' for f in CORE)
    any_reported = ' OR '.join(f'{f} IS NOT NULL' for f in FIELDS) + " OR wind_state IN ('numeric','calm','variable')"
    report = 'primary_observation_datetime_utc' if table.endswith('hourly_snapshots') else 'observation_datetime_utc'
    return text('SELECT station,EXTRACT(YEAR FROM hour_utc AT TIME ZONE \'UTC\')::int AS year, '
                'count(*) AS stored_rows,'+','.join(fields)+', '
                "count(*) FILTER(WHERE wind_state IN ('numeric','calm','variable')) AS wind_reported_state_hours, "
                f'count(*) FILTER(WHERE {core_any}) AS any_core_hours, '
                f'count(*) FILTER(WHERE {core_all}) AS all_core_hours, '
                f'count(*) FILTER(WHERE {report} IS NOT NULL OR {any_reported}) AS selected_report_hours '
                f'FROM {table} WHERE {version_column}=:version GROUP BY station,year ORDER BY station,year'), {'version':version}


def run():
    OUT.mkdir(parents=True,exist_ok=True)
    engine = database_engine()
    gaps, annual, auxiliary = [], None, None
    with engine.connect().execution_options(isolation_level='REPEATABLE READ') as connection:
        if connection.execute(text('SHOW transaction_read_only')).scalar()!='on':
            raise ValueError('Read-only connection required')
        connection.execute(text("SET LOCAL TIME ZONE 'UTC'"))
        status = connection.execute(text('SELECT status,policy FROM metpipe_final.policy_versions WHERE policy_version=:v'),{'v':POLICY}).one()
        if status.status!='complete':
            raise ValueError('Final policy is not complete')
        stations = sorted(status.policy['core_stations'])
        before = connection.execute(text('SELECT count(*) FROM metpipe_final.hourly_snapshots WHERE policy_version=:v'),{'v':POLICY}).scalar()
        query,params = availability_query('metpipe_final.hourly_snapshots','policy_version',POLICY)
        annual = pd.read_sql_query(query,connection,params=params)
        annual['expected_hours'] = annual.year.map(lambda y:(366 if calendar.isleap(y) else 365)*24)
        annual['role'] = 'core_finalized'
        if len(annual)!=400 or not annual.stored_rows.eq(annual.expected_hours).all() or set(annual.station)!=set(stations):
            raise ValueError('Expected complete 20-station x 20-year final scaffold')
        for field in FIELDS+['wind_reported_state','any_core','all_core','selected_report']:
            annual[field+'_pct'] = annual[field+'_hours']/annual.expected_hours*100
        query,params = availability_query('metpipe_aux.hourly_observations','dataset_version','CQX_GHCNh_2005_2024_auxiliary_v1')
        auxiliary = pd.read_sql_query(query,connection,params=params)
        auxiliary['expected_hours'] = auxiliary.year.map(lambda y:(366 if calendar.isleap(y) else 365)*24)
        auxiliary['role'] = 'auxiliary_GHCNh_not_finalized'
        if len(auxiliary)!=20 or set(auxiliary.station)!={'CQX'}:
            raise ValueError('Expected separately labelled CQX twenty-year series')
        for field in FIELDS+['wind_reported_state','any_core','all_core','selected_report']:
            auxiliary[field+'_pct'] = auxiliary[field+'_hours']/auxiliary.expected_hours*100
        # All core missing runs, full-period not reset on New Year's Day.
        for i,station in enumerate(stations,1):
            columns = ','.join(f'{f} IS NOT NULL AS {f}' for f in GAP_FIELDS)
            frame = pd.read_sql_query(text('SELECT hour_utc,'+columns+' FROM metpipe_final.hourly_snapshots '
                'WHERE policy_version=:v AND station=:s ORDER BY hour_utc'),connection,params={'v':POLICY,'s':station})
            frame['hour_utc'] = pd.to_datetime(frame.hour_utc,utc=True)
            if not pd.DatetimeIndex(frame.hour_utc).equals(pd.date_range(START,END,freq='h',inclusive='left')):
                raise ValueError('Gap inventory lacks expected hours')
            for field in GAP_FIELDS:
                for gap in missing_runs(frame.hour_utc,frame[field]):
                    gaps.append({'station':station,'element':field,**gap})
            if i%5==0:
                print(f'Inventoried gaps for {i}/20 core stations',flush=True)
        decisions = pd.read_sql_query(text('''SELECT d.station,d.hour_utc,e.key AS element,
            e.value->>'source' AS selected_source,e.value->>'reason' AS reason,
            e.value->>'value' AS selected_value FROM metpipe_final.hour_decisions d
            CROSS JOIN LATERAL jsonb_each(d.decisions) e WHERE policy_version=:v'''),connection,params={'v':POLICY})
        pressure = pd.read_sql_query(text('''SELECT h.station,h.hour_utc,
            h.primary_observation_datetime_utc,g.quality_flags->'station_level_pressure' AS flags
            FROM metpipe_final.hourly_snapshots h LEFT JOIN ghcnh_parallel.hourly_observations g
            ON g.dataset_version=:g AND g.station=h.station AND g.hour_utc=h.hour_utc
            WHERE h.policy_version=:v AND h.station_pressure_hpa IS NULL
            ORDER BY h.station,h.hour_utc'''),connection,params={'v':POLICY,'g':status.policy['primary_dataset_version']})
        after = connection.execute(text('SELECT count(*) FROM metpipe_final.hourly_snapshots WHERE policy_version=:v'),{'v':POLICY}).scalar()
        if before!=after or before!=3506400:
            raise ValueError('Final input changed during read-only audit')
    engine.dispose()
    annual.to_csv(OUT/'core_station_year_availability.csv',index=False)
    auxiliary.to_csv(OUT/'auxiliary_cqx_year_availability.csv',index=False)
    summary = annual_summary(annual,'core_finalized')
    aux_summary = annual_summary(auxiliary,'auxiliary_GHCNh_not_finalized')
    summary.to_csv(OUT/'core_station_summary.csv',index=False)
    aux_summary.to_csv(OUT/'auxiliary_cqx_summary.csv',index=False)
    inventory = pd.DataFrame(gaps)
    inventory.to_csv(OUT/'core_missing_runs.csv',index=False)
    decisions.to_csv(OUT/'selection_decisions.csv',index=False)
    # Distinguish absent reports/elements, known bad flags and selection conflicts.
    from ghcnh_backfill import rejected
    pressure['hour_utc'] = pd.to_datetime(pressure.hour_utc,utc=True)
    lookup = {(r.station,pd.Timestamp(r.hour_utc)):r.reason for r in decisions[decisions.element.eq('station_pressure_hpa')].itertuples()}
    def reason(r):
        explicit = lookup.get((r.station,r.hour_utc))
        if explicit:
            return explicit
        if pd.isna(r.primary_observation_datetime_utc):
            return 'no_primary_routine_report'
        flags = r.flags or {}
        if rejected('station_level_pressure',flags):
            return 'primary_bad_qc'
        if flags.get('raw') is None:
            return 'primary_pressure_not_reported'
        return 'primary_pressure_unusable_or_range_screened'
    pressure['missing_reason'] = [reason(r) for r in pressure.itertuples()]
    pressure[['station','hour_utc','missing_reason']].to_csv(OUT/'pressure_missing_reason_hours.csv',index=False)
    reason_counts = pressure.groupby(['station','missing_reason']).size().rename('missing_hours').reset_index()
    reason_counts.to_csv(OUT/'pressure_missing_reasons.csv',index=False)
    gap_summary = inventory.groupby(['station','element']).agg(missing_hours=('missing_hours','sum'),
        missing_runs=('missing_hours','size'),longest_run_hours=('missing_hours','max')).reset_index()
    short = inventory[inventory.within_72h_length_only].groupby(['station','element']).missing_hours.sum()
    gap_summary['hours_in_runs_le_72h_length_only'] = [int(short.get((r.station,r.element),0)) for r in gap_summary.itertuples()]
    gap_summary['hours_in_runs_gt_72h'] = gap_summary.missing_hours-gap_summary.hours_in_runs_le_72h_length_only
    gap_summary.to_csv(OUT/'gap_summary.csv',index=False)
    pvc = summary[summary.station.eq('PVC')].iloc[0]
    ranks = {}
    for field in CORE:
        ranks[field] = {'coverage_pct':float(pvc[field+'_pct']),
            'missing_hours':int(pvc.expected_hours-pvc[field+'_hours']),
            'rank_lowest_first':int(summary[field+'_pct'].rank(method='min').loc[pvc.name]),
            'next_lowest_station':summary[summary.station.ne('PVC')].sort_values(field+'_pct').iloc[0].station,
            'next_lowest_pct':float(summary[summary.station.ne('PVC')][field+'_pct'].min())}
    weak = annual.melt(id_vars=['station','year','expected_hours'],value_vars=[f+'_pct' for f in CORE],
                       var_name='element',value_name='coverage_pct')
    weak[weak.coverage_pct.lt(95)].sort_values(['station','year','element']).to_csv(OUT/'core_year_elements_below_95pct.csv',index=False)
    prior_path = ROOT/'outputs/audits/network_ghcnh/annual_availability.csv'
    prior = pd.read_csv(prior_path)
    mappings = {f:f for f in FIELDS}
    mappings.update({'wind_direction_deg':None,'precipitation_reported_mm':'hourly_precipitation_mm'})
    changes = []
    for r in summary.to_dict('records'):
        old = prior[(prior.station==r['station']) & prior.year.between(2005,2024)]
        for field,old_field in mappings.items():
            if old_field:
                baseline = int(old[old_field+'_hours'].sum())
                changes.append({'station':r['station'],'element':field,'ghcnh_hours':baseline,
                    'finalized_hours':r[field+'_hours'],'change_hours':r[field+'_hours']-baseline})
    pd.DataFrame(changes).to_csv(OUT/'change_from_ghcnh_v1.csv',index=False)
    result = {'policy_version':POLICY,'core_station_years':len(annual),'auxiliary_station_years':len(auxiliary),
        'core_rows_before':int(before),'core_rows_after':int(after),'database_writes':False,
        'pvc_core_ranking':ranks,'pvc_pressure_gaps':gap_summary[(gap_summary.station=='PVC') & (gap_summary.element=='station_pressure_hpa')].to_dict('records'),
        'pvc_longest_pressure_gaps':inventory[(inventory.station=='PVC') & (inventory.element=='station_pressure_hpa')].nlargest(10,'missing_hours').to_dict('records'),
        'pvc_pressure_missing_reasons':reason_counts[reason_counts.station.eq('PVC')].to_dict('records'),
        'source_policy':status.policy,'audit_code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (OUT/'audit_summary.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in {'source_policy','pvc_longest_pressure_gaps'}},indent=2),flush=True)
    return result


if __name__=='__main__':
    run()
