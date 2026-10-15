"""Render cached all-network availability results; no database or downloads."""
import base64
import html
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from audit_network_ghcnh import OUT, ROOT

LABELS = {"routine": "Routine report", "temperature_c": "Temperature", "dewpoint_c": "Dew point",
          "relative_humidity": "Relative humidity", "station_pressure_hpa": "Station pressure",
          "sea_level_pressure_hpa": "Sea-level pressure", "altimeter_hpa": "Altimeter",
          "wind_speed_ms": "Wind speed", "wind_direction_reported": "Wind direction/state",
          "wind_gust_ms": "Wind gust", "hourly_precipitation_mm": "Hourly precip*"}
CORE = ["routine", "temperature_c", "dewpoint_c", "relative_humidity", "station_pressure_hpa",
        "wind_speed_ms", "hourly_precipitation_mm"]


def heatmap(values, columns, title, path, delta=False):
    fig, ax = plt.subplots(figsize=(12, 9))
    data = values[columns].to_numpy()
    scale = np.max(np.abs(data)) if delta else 100
    display = ax.imshow(data, cmap="RdBu" if delta else "RdYlGn", vmin=-scale if delta else 0, vmax=scale, aspect="auto")
    ax.set_xticks(range(len(columns)), [LABELS[column] for column in columns], rotation=30, ha="right")
    ax.set_yticks(range(len(values)), values.index)
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            text = f"{data[i,j]:+.2f}" if delta else f"{data[i,j]:.1f}"
            color = "white" if (delta and abs(data[i,j]) > scale*.65) or (not delta and (data[i,j] < 20 or data[i,j] > 80)) else "#173144"
            ax.text(j, i, text, ha="center", va="center", fontsize=8, color=color)
    ax.set_title(title, pad=14, fontsize=13)
    bar = fig.colorbar(display, ax=ax, fraction=.03, pad=.025)
    bar.set_label("Percentage-point change" if delta else "% of expected UTC hours")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def table(frame):
    return frame.to_html(index=False, border=0, float_format=lambda value: f"{value:.2f}", escape=True)


def image(path):
    encoded = base64.b64encode(path.read_bytes()).decode()
    return f'<img src="data:image/png;base64,{encoded}" alt="{html.escape(path.stem.replace("_", " "))}">'


def main():
    audit = json.loads((OUT / "audit_summary.json").read_text())
    if audit["successful_files"] != 420 or audit["historical_successful_files"] != 400:
        raise ValueError("Audit incomplete")
    historical = pd.read_csv(OUT / "station_summary_2005_2024.csv").set_index("station")
    annual = pd.read_csv(OUT / "annual_availability.csv")
    monthly = pd.read_csv(OUT / "monthly_availability.csv")
    comparison = pd.read_csv(OUT / "source_coverage_comparison.csv")
    values = historical[[field + "_pct" for field in CORE]].rename(columns=lambda name: name.removesuffix("_pct"))
    heatmap(values, CORE, "GHCNh 2005–2024: availability, not independent sensor accuracy", OUT / "historical_availability.png")
    modern = comparison[comparison.period.eq("2020–2024")].pivot(index="station", columns="element", values="change_percentage_points")
    fields = ["temperature_c", "dewpoint_c", "relative_humidity", "station_pressure_hpa", "wind_speed_ms", "hourly_precipitation_mm"]
    heatmap(modern, fields, "2020–2024 coverage change: GHCNh minus current production", OUT / "modern_coverage_change.png", delta=True)
    pressure25 = monthly[monthly.year.eq(2025)].copy()
    pressure25["pct"] = pressure25.station_pressure_hpa_hours / pressure25.expected_hours * 100
    pressure25 = pressure25.pivot(index="station", columns="month", values="pct")
    fig, ax = plt.subplots(figsize=(12, 9))
    plot = ax.imshow(pressure25, cmap="RdYlGn", vmin=0, vmax=100, aspect="auto")
    ax.set_xticks(range(12), ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"])
    ax.set_yticks(range(20), pressure25.index)
    for i in range(20):
        for j in range(12):
            value = pressure25.iloc[i,j]
            ax.text(j,i,f"{value:.1f}",ha="center",va="center",fontsize=7,color="white" if value<20 or value>80 else "#173144")
    ax.set_title("2025 readiness: station pressure nearly absent after August",pad=14)
    fig.colorbar(plot,ax=ax,fraction=.03,pad=.025).set_label("% of expected UTC hours")
    fig.tight_layout(); fig.savefig(OUT / "pressure_2025_monthly.png",dpi=150); plt.close(fig)
    core_fields = ["temperature_c", "dewpoint_c", "relative_humidity", "station_pressure_hpa", "wind_speed_ms"]
    low = []
    for _, row in annual[annual.year.le(2024)].iterrows():
        for field in core_fields:
            pct = row[field + "_hours"] / row.expected_hours * 100
            if pct < 95:
                low.append({"Station": row.station, "Year": int(row.year), "Element": LABELS[field], "Availability %": pct})
    lows = pd.DataFrame(low)
    lows.to_csv(OUT / "core_station_years_below_95.csv",index=False)
    full = historical.reset_index()[["station"]+[field+"_pct" for field in LABELS]]
    full = full.rename(columns={"station":"Station", **{field+"_pct":label+" %" for field,label in LABELS.items()}})
    modern_table = comparison[comparison.period.eq("2020–2024")].copy()
    modern_table["element"] = modern_table.element.map(LABELS)
    unknown = annual[annual.year.le(2024)].groupby("station")[[field+"_unmapped_qc_hours" for field in LABELS if field!="routine"]].sum().reset_index()
    body = """<!doctype html><html><head><meta charset="utf-8"><title>MetPipe: GHCNh network availability</title>
    <style>body{font:16px system-ui,sans-serif;color:#203b4e;background:#f5f8fa;margin:0}header{background:#18354b;color:white;padding:28px 5%}main{max-width:1280px;margin:auto;padding:24px}section{background:white;padding:24px;margin:20px 0;border-radius:10px}img{width:100%;height:auto}table{border-collapse:collapse;font-size:12px;width:100%}th,td{padding:7px;border-bottom:1px solid #dde6ec;text-align:right}th:first-child,td:first-child{text-align:left}.scroll{overflow-x:auto}h2{margin-top:0}p{line-height:1.55}.note{background:#fff1d4;padding:14px;border-left:4px solid #d38a27}details{margin:14px 0}summary{cursor:pointer;font-weight:600}</style></head><body>
    <header><h1>MetPipe Northeast: all-network GHCNh availability</h1><p>20 stations · 400 historical files read · 20 additional 2025 files · October 14, 2026</p></header><main>
    <section><h2>Decision summary</h2><p>GHCNh is available for all twenty stations throughout 2005–2024. Nineteen stations have at least 98.6% aggregate availability for temperature, dew point, relative humidity, station pressure and wind speed. Annual and element-specific weaknesses remain; file existence is not complete hourly coverage or sensor accuracy.</p>
    <p class="note">No database migration or overwrite occurred. PVC remains the main historical coverage exception: pressure 92.79%, hourly-compatibility precipitation 10.61%, sea-level pressure 42.65%. Routine reports are absent in October/November 2006.</p></section>"""
    body += '<section><h2>Historical availability: 2005–2024</h2>' + image(OUT / "historical_availability.png")
    body += '<p>One coherent routine record per hour; known-bad flags filtered under the existing adapter policy. Unknown/calculated quality is retained and counted, not certified. All expected UTC hours remain in denominators. Gusts are event-dependent. Reported wind direction/state includes calm and variable codes; numeric-bearing availability is recorded separately.</p>'
    body += '<p>*Precipitation is compatible selected FM15 data, not independently validated hourly totals. Explicit recorded zero and flagged trace count as available; missing values never become zero. Frequent-report running totals still need duration-aware aggregation before rainfall analysis.</p><div class="scroll">' + table(full) + '</div></section>'
    body += '<section><h2>Compare with current production: 2020–2024</h2>' + image(OUT / "modern_coverage_change.png")
    body += '<p>Current production preserves LCDv1 in this period, with a few boundary GHCNh records. Selection and QC differ, so this measures operational availability, not proof that one source is more accurate. Gains are generally modest; pressure and precipitation are slightly worse at some stations.</p><details><summary>Full comparison by station and element</summary><div class="scroll">'+table(modern_table[['station','element','production_pct','ghcnh_pct','change_percentage_points']])+'</div></details></section>'
    body += '<section><h2>Annual weaknesses are not hidden by twenty-year averages</h2><p>The 95% screen is an advisory flag, not a station-replacement rule. Some failures concern only one year or element.</p><div class="scroll">'+table(lows)+'</div></section>'
    body += '<section><h2>2025 readiness is a separate problem</h2>'+image(OUT / "pressure_2025_monthly.png")
    body += '<p>All twenty 2025 files exist, but the selected archives contain only 32 routine station-pressure values across the entire network in September–December (58,560 expected station-hours). Temperature and altimeter generally continue. Do not infer airport sensor shutdown, and do not silently substitute altimeter for station pressure.</p></section>'
    body += '<section><h2>Quality and reproducibility</h2><p>Unknown quality mappings, gross-check-only pressure, source precision, sensor spikes and changing schedules still need quality work. Relative humidity may be calculated rather than directly measured. No claim of homogenized climatology or forecast skill is made.</p><details><summary>Values retained without a mapped strict QC tier (not automatically erroneous)</summary><div class="scroll">'+table(unknown)+'</div></details>'
    body += '<p>Audit code: analysis/audit_network_ghcnh.py. CSV/JSON exports retain annual/monthly counts, raw-file SHA256, per-element source/quality distributions, trace/calm/variable counts and source comparison. Raw observations and the network were not changed.</p><p><a href="https://www.ncei.noaa.gov/products/global-historical-climatology-network-hourly">NOAA GHCNh product information</a> · <a href="https://www.ncei.noaa.gov/oa/global-historical-climatology-network/hourly/doc/ghcnh_DOCUMENTATION.pdf">NOAA coding documentation</a></p></section></main></body></html>'
    (OUT / "network_ghcnh_availability.html").write_text(body)
    print("Rendered all-network availability tables and three figures.")


if __name__ == "__main__":
    main()
