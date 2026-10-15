"""Render cached finalized availability and a source-safe analysis migration plan."""
import base64
import html
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from audit_finalized_availability import OUT, ROOT, CORE, FIELDS

LABELS = {'temperature_c':'Temperature','dewpoint_c':'Dew point','relative_humidity':'RH',
          'station_pressure_hpa':'Station pressure','sea_level_pressure_hpa':'Sea-level pressure',
          'altimeter_hpa':'Altimeter','wind_speed_ms':'Wind speed','wind_direction_deg':'Numeric wind bearing*',
          'wind_reported_state':'Reported wind state','wind_gust_ms':'Gust report*',
          'precipitation_reported_mm':'Reported precipitation*','any_core':'Any core element','all_core':'All five core elements'}
PLAN = [
    ('01_metpipe_eda.ipynb','Original public tables; fixed UTC−5 daily aggregation',
     'Create a new executed finalized-source version; declare UTC versus local-standard daily boundaries and pin policy version.'),
    ('02_hourly_station_relationships.ipynb','Original public temperature reports',
     'Rerun a new version using finalized temperature and its own selected timestamp; retain complete gap scaffold and old output.'),
    ('03_weather_event_case_studies.ipynb','Original public temperature/pressure; source-only event selection',
     'New version must rebuild references, source-only event selection, PC24 and responses with per-element actual times and source-switch diagnostics.'),
    ('04_pvc_neighbor_audit.ipynb / source availability audits','Explicit raw GHCNh/source-QC evidence',
     'Preserve original audits: they document source differences. Add a separate finalized-core plus auxiliary-CQX comparison if needed; do not erase source evidence.'),
    ('05_pvc_pressure_reconstruction.ipynb','LCDv1 pilot with failed publication guard',
     'Preserve failed pilot. New finalized-source pressure experiment needs fresh preparation, masking and validation; do not reuse its publisher/weights blindly.'),
    ('06_pvc_pressure_blocked_validation.ipynb','Consistent GHCNh historical blocked CV and all-data refit',
     'Preserve results. Rerun a separately named finalized-input experiment with annual blocked folds, timing controls and uncertainty calibration before any estimates.'),
    ('Frozen 2025 pressure holdout','Protocol frozen before prior one-time test',
     'Never rewrite or retune it retroactively. 2025 has been seen and cannot be called an untouched test for a new revision guided by those results.'),
    ('analysis/metanalysis.py','Legacy four-station flat cleaned-CSV plots',
     'Keep as legacy reference, not authoritative analysis. Replace with a new finalized-source notebook; rainfall summation needs separate duration validation.'),
]


def table(frame):
    return frame.to_html(index=False,border=0,float_format=lambda v:f'{v:.2f}',escape=True)


def image(path):
    return '<img alt="'+html.escape(path.stem)+'" src="data:image/png;base64,'+base64.b64encode(path.read_bytes()).decode()+'">'


def heatmap(frame, title, path):
    fig,ax=plt.subplots(figsize=(14,9))
    data=frame.to_numpy()
    display=ax.imshow(data,aspect='auto',cmap='RdYlGn',vmin=0,vmax=100)
    ax.set_xticks(range(len(frame.columns)),frame.columns,rotation=35,ha='right')
    ax.set_yticks(range(len(frame)),frame.index)
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            v=data[i,j]
            ax.text(j,i,f'{v:.1f}',ha='center',va='center',fontsize=7 if len(frame.columns)>10 else 8,
                    color='white' if v>80 or v<20 else '#173144')
    ax.set_title(title,pad=14,fontsize=13)
    fig.colorbar(display,ax=ax,fraction=.025,pad=.02).set_label('% of expected UTC hours')
    fig.tight_layout();fig.savefig(path,dpi=160);plt.close(fig)


def run():
    audit=json.loads((OUT/'audit_summary.json').read_text())
    annual=pd.read_csv(OUT/'core_station_year_availability.csv')
    summary=pd.read_csv(OUT/'core_station_summary.csv')
    aux=pd.read_csv(OUT/'auxiliary_cqx_summary.csv')
    aux_annual=pd.read_csv(OUT/'auxiliary_cqx_year_availability.csv')
    gaps=pd.read_csv(OUT/'gap_summary.csv')
    pvc_gaps=pd.DataFrame(audit['pvc_longest_pressure_gaps'])
    plan=pd.DataFrame(PLAN,columns=['Analysis','Current source','Recommended action'])
    plan.to_csv(OUT/'analysis_source_migration_plan.csv',index=False)
    pressure=annual.pivot(index='station',columns='year',values='station_pressure_hpa_pct')
    heatmap(pressure,'Finalized station-pressure availability: each station and year',OUT/'pressure_by_station_year.png')
    overall=summary.set_index('station')[[f+'_pct' for f in CORE+['precipitation_reported_mm']]].copy()
    overall.columns=[LABELS[f] for f in CORE+['precipitation_reported_mm']]
    heatmap(overall,'Finalized 2005–2024 availability: reported values, not sensor accuracy',OUT/'overall_availability.png')
    cols=['station']+[f+'_pct' for f in FIELDS+['wind_reported_state','any_core','all_core']]
    rename={'station':'Station',**{f+'_pct':LABELS[f]+' %' for f in FIELDS+['wind_reported_state','any_core','all_core']}}
    full=summary[cols].rename(columns=rename)
    aux_full=aux[cols].rename(columns=rename)
    yearly_cols=['station','year']+[f+'_pct' for f in FIELDS+['wind_reported_state','all_core']]
    pvc=annual[annual.station.eq('PVC')][yearly_cols]
    rank=pd.DataFrame([{'Element':LABELS[k],'PVC availability %':v['coverage_pct'],
                       'Missing hours':v['missing_hours'],'Rank (lowest first)':v['rank_lowest_first'],
                       'Next-lowest station':v['next_lowest_station'],'Next-lowest %':v['next_lowest_pct']}
                      for k,v in audit['pvc_core_ranking'].items()])
    pressure_gap=audit['pvc_pressure_gaps'][0]
    recovery_path=OUT/'pvc_raw_pressure_recovery_summary.json'
    recovery=json.loads(recovery_path.read_text()) if recovery_path.exists() else None
    body='''<!doctype html><html><head><meta charset="utf-8"><title>MetPipe finalized availability</title>
    <style>body{font:16px system-ui,sans-serif;background:#f3f7fa;color:#203b4e;margin:0}header{background:#18354b;color:white;padding:28px 5%}main{max-width:1380px;margin:auto;padding:24px}section{background:white;padding:24px;margin:20px 0;border-radius:10px}p,li{line-height:1.55}img{width:100%;height:auto}table{border-collapse:collapse;width:100%;font-size:12px}th,td{padding:7px;border-bottom:1px solid #dce5eb;text-align:right;vertical-align:top}th:first-child,td:first-child{text-align:left}.scroll{overflow-x:auto}.note{padding:15px;background:#fff2d8;border-left:4px solid #d38a27}summary{cursor:pointer;font-weight:600}h2{margin-top:0}</style></head><body>
    <header><h1>MetPipe Northeast — finalized availability</h1><p>2005–2024 UTC · 400 core station-years · CQX shown separately · policy observed_2005_2024_v1</p></header><main>'''
    body+='<section><h2>What remains missing?</h2><p>PVC remains the lowest-availability core station for all five core elements. Its pressure coverage is <strong>92.79%</strong>, compared with 98.82% at the next-lowest station (MVY). Source reconciliation did not recover additional PVC pressure hours.</p>'
    body+='<div class="scroll">'+table(rank)+'</div><p class="note">Availability is not independent measurement accuracy. The final layer contains no reconstructed values. Gusts are conditional reports; absent gusts are not automatically missing measurements. Precipitation presence is not validated one-hour rainfall coverage, and blanks are not dry hours.</p></section>'
    body+='<section><h2>All core stations: full-period availability</h2>'+image(OUT/'overall_availability.png')+'<div class="scroll">'+table(full)+'</div><p>*Numeric wind bearing excludes valid calm/variable states. Reported wind-state coverage is shown separately. Gust and precipitation report presence should not be ranked as if required every hour.</p></section>'
    body+='<section><h2>Station pressure, every year</h2>'+image(OUT/'pressure_by_station_year.png')+'<p>Percentages use every expected hour, including leap days and fully absent reports—not only rows containing observations.</p></section>'
    body+='<section><h2>PVC annual detail</h2><div class="scroll">'+table(pvc.rename(columns=rename))+'</div></section>'
    body+='<section><h2>PVC pressure reconstruction planning</h2><p>There are '+f"{pressure_gap['missing_hours']:,} missing pressure hours in {pressure_gap['missing_runs']:,} runs. "
    body+=f"{pressure_gap['hours_in_runs_le_72h_length_only']:,} hours lie in runs of at most 72 hours; {pressure_gap['hours_in_runs_gt_72h']:,} lie in longer runs. "
    body+='The longest run is 2,212 hours (about 92 days), from September 12 to December 13, 2006.</p><p class="note">Length alone does not establish model eligibility. Donor availability, actual report-time alignment, temporal validation, rapid-change performance and uncertainty still require checks. The existing publication policy does not authorize filling a three-month gap. Keep all estimates separate from finalized observations.</p><div class="scroll">'+table(pvc_gaps)+'</div><h3>Pressure-gap reasons</h3>'+table(pd.DataFrame(audit['pvc_pressure_missing_reasons']))
    if recovery:
        body+=f'<h3>Observation recovery before ML</h3><p>A separate scan of all twenty raw PVC files found <strong>{recovery["candidate_reports"]} accepted alternate FM-15 pressure reports in {recovery["unique_missing_hours_with_candidate"]} currently missing finalized hours</strong>. All are at different actual times from the selected routine record; the nearest alternatives differ by 1–55 minutes. These are unpublished observation-recovery candidates, not reconstructed data or validated replacements. Review their timing, QC and provenance before revising the finalized sampling policy. The 92.79% current coverage is unchanged.</p>'
    body+='</section>'
    body+='<section><h2>CQX auxiliary: not part of the finalized core-20 view</h2><p>These are separately QC-screened GHCNh auxiliary observations, not cross-archive finalized values. No reconstruction model has automatically gained CQX as a predictor.</p><div class="scroll">'+table(aux_full)+'</div><details><summary>All CQX years and elements</summary><div class="scroll">'+table(aux_annual[yearly_cols].rename(columns=rename))+'</div></details></section>'
    body+='<section><h2>Analysis migration: new versions, not overwritten evidence</h2><div class="scroll">'+table(plan)+'</div><p>Finalized values can have different actual timestamps and source provenance by element. A blind table-name replacement or a single shared observation-time column is unsafe. Aggregations also need an explicit UTC versus local-standard-time calendar choice. Observed-only finalized targets—not reconstructed estimates—must remain evaluation truth.</p><p>No existing notebook, frozen model or held-out protocol was changed by this availability audit.</p></section>'
    body+='<section><h2>Complete station-year tables and audit files</h2><details><summary>All 400 core station-years and all reported elements</summary><div class="scroll">'+table(annual[yearly_cols].rename(columns=rename))+'</div></details><p>CSV exports include all annual counts/percentages, missing-run inventories for five core fields and reported precipitation, pressure missing reasons, source-selection decisions, change from GHCNh v1 and the analysis migration plan. Database read-only checks passed; all 3,506,400 final scaffold rows are unchanged.</p></section></main></body></html>'
    (OUT/'finalized_availability.html').write_text(body)
    print(OUT/'finalized_availability.html')


if __name__=='__main__':
    run()
