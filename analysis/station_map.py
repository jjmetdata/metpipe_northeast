"""Build a self-contained Northeast station map from local NOAA CSVs."""

import csv
import html
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
BOUNDARIES_PATH = (
    PROJECT_ROOT / "analysis" / "assets" / "ne_50m_admin_1_states_provinces.geojson"
)
CANDIDATES_PATH = PROJECT_ROOT / "analysis" / "candidate_stations.csv"
OUTPUT_PATH = PROJECT_ROOT / "outputs" / "station_map.html"

WIDTH = 1100
HEIGHT = 800
WEST, EAST = -75.5, -68.4
SOUTH, NORTH = 39.9, 45.3

# Percentage of expected hours with an FM-15 report at the checked station
# minute, audited from the 2020–2024 LCDv1 CSVs (43,848 expected hours).
HOURLY_COVERAGE = {
    "BOS": 99.9, "ORH": 99.8, "PVC": 97.3, "PVD": 99.8,
    "BDL": 99.9, "BTV": 99.7, "MHT": 99.9, "PWM": 99.7,
    "ALB": 99.9, "JFK": 99.9, "EWB": 99.8, "HYA": 99.8,
    "MVY": 99.8, "UUU": 99.8, "HVN": 99.8, "PYM": 99.5,
    "BAF": 99.8, "DDH": 99.6, "LEB": 99.9, "AUG": 99.8,
}

LABEL_OFFSETS = {
    "ALB": (-12, -15),
    "BDL": (-12, 28),
    "BOS": (14, -15),
    "BTV": (14, -15),
    "JFK": (14, 27),
    "MHT": (14, -15),
    "ORH": (-13, -16),
    "PVC": (15, -15),
    "PVD": (-12, 29),
    "PWM": (14, -15),
    "EWB": (-12, 30),
    "HYA": (14, 19),
    "MVY": (14, 27),
    "UUU": (-12, 26),
    "HVN": (-12, 26),
    "PYM": (14, -15),
    "BAF": (-12, -15),
    "DDH": (-12, -15),
    "LEB": (14, -15),
    "AUG": (14, -15),
}


def station_from_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        if not {"LATITUDE", "LONGITUDE", "NAME"}.issubset(reader.fieldnames or []):
            return None
        for row in reader:
            if row.get("LATITUDE") and row.get("LONGITUDE") and row.get("NAME"):
                return {
                    "code": path.name.split("_", 1)[0].upper(),
                    "name": row["NAME"],
                    "latitude": float(row["LATITUDE"]),
                    "longitude": float(row["LONGITUDE"]),
                }
    return None


def load_stations():
    station_files = {}
    for path in sorted(RAW_DIR.glob("*/*_hourly_*.csv")):
        code = path.name.split("_", 1)[0].upper()
        station_files.setdefault(code, []).append(path)
    if not station_files:
        raise FileNotFoundError(f"No station-year CSVs found in {RAW_DIR}")

    stations = []
    for code in sorted(station_files):
        station = None
        for path in reversed(station_files[code]):
            station = station_from_csv(path)
            if station is not None:
                break
        if station is None:
            raise ValueError(f"No local raw CSV for {code} contains coordinates")
        stations.append(station)
    return stations


def load_candidates(current_codes):
    candidates = []
    seen = set()
    with CANDIDATES_PATH.open(newline="", encoding="utf-8-sig") as source:
        for row in csv.DictReader(source):
            code = row["code"].strip().upper()
            if code in seen:
                raise ValueError(f"Duplicate candidate station: {code}")
            seen.add(code)
            if code in current_codes:
                continue  # A downloaded station graduates from candidate to current.
            group = row["group"].strip()
            if group not in {"coastal", "regional"}:
                raise ValueError(f"Unknown candidate group for {code}: {group}")
            candidates.append({
                "code": code,
                "name": row["name"].strip(),
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
                "group": group,
            })
    return candidates


def project(point):
    longitude, latitude = point
    x = (longitude - WEST) / (EAST - WEST) * WIDTH
    y = (NORTH - latitude) / (NORTH - SOUTH) * HEIGHT
    return x, y


def feature_paths(feature):
    geometry = feature["geometry"]
    if geometry["type"] == "Polygon":
        polygons = [geometry["coordinates"]]
    elif geometry["type"] == "MultiPolygon":
        polygons = geometry["coordinates"]
    else:
        return []

    paths = []
    for polygon in polygons:
        for ring in polygon:
            if not ring:
                continue
            longitudes = [point[0] for point in ring]
            latitudes = [point[1] for point in ring]
            if (max(longitudes) < WEST or min(longitudes) > EAST or
                    max(latitudes) < SOUTH or min(latitudes) > NORTH):
                continue
            coordinates = [project(point) for point in ring]
            path = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in coordinates) + " Z"
            paths.append(path)
    return paths


def boundary_svg():
    features = json.loads(BOUNDARIES_PATH.read_text(encoding="utf-8"))["features"]
    shapes = []
    for feature in features:
        paths = feature_paths(feature)
        if paths:
            name = html.escape(feature["properties"].get("name", ""), quote=True)
            shapes.append(
                f'<path class="boundary" aria-label="{name}" d="{" ".join(paths)}"/>'
            )
    return "\n".join(shapes)


def station_svg(station, status):
    code = html.escape(station["code"], quote=True)
    name = html.escape(station["name"], quote=True)
    x, y = project((station["longitude"], station["latitude"]))
    dx, dy = LABEL_OFFSETS.get(station["code"], (13, -15))
    anchor = "end" if dx < 0 else "start"
    group_class = f' {station["group"]}' if status == "candidate" else ""
    if status == "candidate":
        mark = f'<rect x="{x - 6:.1f}" y="{y - 6:.1f}" width="12" height="12" '
        mark += f'transform="rotate(45 {x:.1f} {y:.1f})"/>'
    else:
        mark = f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9"/>'
    label = (
        f'<text x="{x + dx:.1f}" y="{y + dy:.1f}" '
        f'text-anchor="{anchor}">{code}</text>'
    )
    return (
        f'<g class="station {status}{group_class}" tabindex="0" data-code="{code}" '
        f'data-status="{status}" '
        f'data-group="{station.get("group", "")}" '
        f'data-coverage="{HOURLY_COVERAGE.get(station["code"], "")}" '
        f'data-name="{name}" data-lat="{station["latitude"]:.5f}" '
        f'data-lon="{station["longitude"]:.5f}" '
        f'aria-label="{code}: {name}">'
        f'<title>{code}: {name}</title>'
        f'{mark}{label}'
        '</g>'
    )


def main():
    stations = load_stations()
    candidates = load_candidates({station["code"] for station in stations})
    markers = "\n".join(
        [station_svg(station, "current") for station in stations]
        + [station_svg(station, "candidate") for station in candidates]
    )
    current_names = "\n".join(
        f'<li><b>{html.escape(station["code"])}</b> '
        f'{html.escape(station["name"])}</li>'
        for station in stations
    )
    def candidate_names(group):
        return "\n".join(
            f'<li><b>{html.escape(station["code"])}</b> '
            f'{html.escape(station["name"])}</li>'
            for station in candidates if station["group"] == group
        )

    coastal_count = sum(station["group"] == "coastal" for station in candidates)
    regional_count = sum(station["group"] == "regional" for station in candidates)
    candidate_legend = (
        '<span><i class="key candidate"></i>Proposed coastal</span>'
        '<span><i class="key candidate regional"></i>Proposed regional</span>'
        if candidates else ""
    )
    candidate_sections = "".join(
        f'<h3>Proposed {group} ({count})</h3><ul>{candidate_names(group)}</ul>'
        for group, count in [("coastal", coastal_count), ("regional", regional_count)]
        if count
    )
    candidate_note = (
        " Diamonds mark additions awaiting project ingestion." if candidates else ""
    )
    document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>MetPipe Northeast stations</title>
  <style>
    :root {{ color-scheme: light; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: system-ui, sans-serif; color: #17324d; background: #f3f7fa; }}
    header {{ padding: 18px 24px; background: #17324d; color: #fff; }}
    h1 {{ margin: 0; font-size: 1.45rem; }}
    header p {{ margin: 4px 0 0; color: #d2e6f5; }}
    main {{ display: grid; grid-template-columns: minmax(0, 1fr) 275px; gap: 18px;
            max-width: 1450px; margin: 20px auto; padding: 0 20px; }}
    .map-panel, aside {{ background: white; border: 1px solid #d7e2e8;
                         border-radius: 12px; overflow: hidden; }}
    svg {{ width: 100%; height: auto; display: block; background: #dceef6; }}
    .grid {{ stroke: #c0d9e4; stroke-width: 1; }}
    .boundary {{ fill: #e6eddf; stroke: #9bb09b; stroke-width: 1.4;
                 fill-rule: evenodd; }}
    .station {{ cursor: pointer; }}
    .station.current circle {{ fill: #2784b9; stroke: #17324d; stroke-width: 2.5; }}
    .station.candidate rect {{ fill: white; stroke-width: 3; }}
    .station.candidate.coastal rect {{ stroke: #64458b; }}
    .station.candidate.regional rect {{ stroke: #19785c; }}
    .station:hover circle, .station:focus circle,
    .station:hover rect, .station:focus rect {{ stroke: #e1a625; stroke-width: 5; }}
    .station text {{ font-size: 19px; font-weight: 750; fill: #17324d;
                     stroke: white; stroke-width: 5; paint-order: stroke; }}
    .legend {{ display: flex; gap: 16px; align-items: center; flex-wrap: wrap;
               padding: 10px 16px 0; font-size: .85rem; }}
    .legend span {{ display: inline-flex; align-items: center; gap: 7px; }}
    .key {{ display: inline-block; width: 13px; height: 13px; border-radius: 50%;
            background: #2784b9; border: 2px solid #17324d; }}
    .key.candidate {{ border-radius: 0; transform: rotate(45deg);
                      background: white; border-color: #64458b; width: 11px; height: 11px; }}
    .key.regional {{ border-color: #19785c; }}
    .caption {{ margin: 0; padding: 11px 16px; font-size: .8rem; color: #547080; }}
    aside {{ padding: 16px; }}
    aside h2 {{ margin: 0 0 12px; font-size: 1.1rem; }}
    aside h3 {{ margin: 17px 0 6px; font-size: .93rem; }}
    aside ul {{ padding-left: 20px; margin: 0; line-height: 1.55; font-size: .83rem; }}
    #selection {{ min-height: 52px; margin: 0 0 14px; padding: 10px;
                  background: #edf5f9; border-radius: 8px; font-size: .88rem;
                  white-space: pre-line; }}
    @media (max-width: 900px) {{ main {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <header><h1>MetPipe Northeast stations</h1>
    <p>{len(stations) + len(candidates)} stations · 2020–2024 availability checked · Click a marker for details</p></header>
  <main>
    <div class="map-panel">
      <svg viewBox="0 0 {WIDTH} {HEIGHT}" role="img"
           aria-label="Map of Northeast airport stations and proposed additions">
        <path class="grid" d="M0,400 H{WIDTH} M550,0 V{HEIGHT}"/>
        {boundary_svg()}
        {markers}
      </svg>
      <div class="legend" aria-label="Map legend">
        <span><i class="key"></i>Local data</span>
        {candidate_legend}
      </div>
      <p class="caption">All stations have reports in all 60 months of 2020–2024; individual hours and weather fields can be missing.{candidate_note} Coordinates: NOAA · Boundaries: Natural Earth (public domain)</p>
    </div>
    <aside><h2>Airport codes</h2>
      <p id="selection" aria-live="polite">Select a marker to see its location and hourly coverage.</p>
      <h3>With local data ({len(stations)})</h3><ul>{current_names}</ul>
      {candidate_sections}
    </aside>
  </main>
  <script>
    const selection = document.getElementById('selection');
    for (const marker of document.querySelectorAll('.station')) {{
      const show = () => {{
        const status = marker.dataset.status === 'candidate'
          ? `Proposed ${{marker.dataset.group}} — historical availability checked; awaiting ingestion`
          : 'Local 2020–2024 data';
        selection.textContent = `${{marker.dataset.code}} — ${{marker.dataset.name}}\n` +
          `${{marker.dataset.lat}}° N, ${{Math.abs(Number(marker.dataset.lon)).toFixed(5)}}° W\n` +
          `${{marker.dataset.coverage}}% scheduled hourly coverage (2020–2024)\n` + status +
          (marker.dataset.code === 'PVC' ? `\n2024 includes an October 17–25 reporting gap.` : '');
      }};
      marker.addEventListener('click', show);
      marker.addEventListener('keydown', event => {{
        if (event.key === 'Enter' || event.key === ' ') {{ event.preventDefault(); show(); }}
      }});
    }}
  </script>
</body>
</html>
"""
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(document, encoding="utf-8")
    print(f"Mapped {len(stations)} current and {len(candidates)} proposed stations -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
