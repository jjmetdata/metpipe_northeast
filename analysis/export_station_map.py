"""Generate the GitHub README's static SVG map without raw data or network."""
import html
from pathlib import Path

from station_map import WIDTH, HEIGHT, boundary_svg, load_network, project, LABEL_OFFSETS

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/assets/station_network.svg"


def build_svg():
    stations = load_network()
    markers = []
    for station in stations:
        code = html.escape(station["code"])
        name = html.escape(station["name"])
        x, y = project((station["longitude"], station["latitude"]))
        dx, dy = LABEL_OFFSETS.get(station["code"], (14, -15))
        anchor = "end" if dx < 0 else "start"
        markers.append(f'<g class="station" data-code="{code}"><title>{code}: {name}</title>'
                       f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8"/>'
                       f'<text x="{x+dx:.1f}" y="{y+dy:.1f}" text-anchor="{anchor}">{code}</text></g>')
    labels = []
    for name, lon, lat in [("NEW YORK",-74.5,43.1),("VERMONT",-72.8,44.8),
                           ("NEW HAMPSHIRE",-71.6,44.25),("MAINE",-69.25,44.6),
                           ("MASSACHUSETTS",-72.75,42.5),("CONNECTICUT",-73.2,41.55),
                           ("ATLANTIC OCEAN",-69.9,41.4)]:
        x,y = project((lon,lat))
        labels.append(f'<text class="region" x="{x:.1f}" y="{y:.1f}">{name}</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="950"
        viewBox="0 0 1100 950" role="img" aria-labelledby="title description">
  <title id="title">MetPipe Northeast: twenty-station observation network</title>
  <desc id="description">Twenty airport stations in Massachusetts, Rhode Island, Connecticut,
    Vermont, New Hampshire, Maine and New York. All stations use the same blue circle,
    including Provincetown. Historical database scope: 2005–2024; records have gaps.</desc>
  <style>
    text {{ font-family: Arial, Helvetica, sans-serif; fill: #17324d; }}
    .boundary {{ fill: #e6eddf; stroke: #9bb09b; stroke-width: 1.2; fill-rule: evenodd; }}
    .station circle {{ fill: #2784b9; stroke: #17324d; stroke-width: 2.3; }}
    .station text {{ font-size: 19px; font-weight: 700; stroke: #fff; stroke-width: 5; paint-order: stroke; }}
    .region {{ font-size: 15px; fill: #647b75; letter-spacing: 1.2px; }}
  </style>
  <rect width="1100" height="950" fill="#fff"/>
  <rect width="1100" height="94" fill="#17324d"/>
  <text x="28" y="40" style="fill:#fff;font-size:28px;font-weight:700">MetPipe Northeast</text>
  <text x="28" y="70" style="fill:#d2e6f5;font-size:18px">20 stations · Regional observation network · Historical scope: 2005–2024</text>
  <defs><clipPath id="map-clip"><rect width="{WIDTH}" height="{HEIGHT}"/></clipPath></defs>
  <g transform="translate(0 94)" clip-path="url(#map-clip)">
    <rect width="{WIDTH}" height="{HEIGHT}" fill="#dceef6"/>
    {boundary_svg()}
    {''.join(labels)}
    {''.join(markers)}
  </g>
  <circle cx="30" cy="923" r="7" fill="#2784b9" stroke="#17324d" stroke-width="2"/>
  <text x="47" y="928" style="font-size:15px">Core network · Missing hours/elements remain missing</text>
  <text x="1074" y="928" text-anchor="end" style="font-size:13px;fill:#547080">Coordinates: NOAA · Boundaries: Natural Earth (public domain)</text>
</svg>'''


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(build_svg(), encoding="utf-8")
    print(f"Exported twenty-station map -> {OUTPUT}")


if __name__ == "__main__":
    main()
