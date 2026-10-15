"""Plot the committed finalized-observation availability tables; no DB query."""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FIELDS = {'temperature_c_pct': 'Temperature', 'dewpoint_c_pct': 'Dew point',
          'relative_humidity_pct': 'Relative humidity', 'station_pressure_hpa_pct': 'Station pressure',
          'wind_speed_ms_pct': 'Wind speed'}


def load_reports():
    stations = pd.read_csv(ROOT / 'reports/data_availability.csv').sort_values('station')
    years = pd.read_csv(ROOT / 'reports/station_year_availability.csv')
    if len(stations) != 20 or len(years) != 400 or stations.expected_hours.sum() != 3506400:
        raise ValueError('Unexpected core-20 / 2005–2024 coverage scope')
    if years.duplicated(['station', 'year']).any():
        raise ValueError('Duplicate station-year')
    for column in FIELDS:
        hours = column.removesuffix('_pct') + '_hours'
        np.testing.assert_allclose(stations[column], 100 * stations[hours] / stations.expected_hours, atol=1e-8)
        if not stations[column].between(0, 100).all():
            raise ValueError('Invalid availability')
    return stations, years


def main():
    stations, years = load_reports()
    assets = ROOT / 'docs/assets'
    assets.mkdir(exist_ok=True)
    matrix = stations.set_index('station')[list(FIELDS)]
    fig, ax = plt.subplots(figsize=(8.4, 8.5))
    image = ax.imshow(matrix, cmap='Blues', vmin=90, vmax=100, aspect='auto')
    ax.set_xticks(range(len(FIELDS)), list(FIELDS.values()), fontsize=10)
    ax.xaxis.tick_top()
    ax.tick_params(axis='x', length=0, pad=9)
    ax.set_yticks(range(20), matrix.index, fontsize=10)
    ax.tick_params(axis='y', length=0)
    for i in range(len(matrix)):
        for j in range(len(FIELDS)):
            value = matrix.iloc[i, j]
            ax.text(j, i, f'{value:.1f}%', ha='center', va='center', fontsize=10,
                    color='white' if value >= 96 else '#17324d')
    fig.colorbar(image, ax=ax, fraction=.045, pad=.04, label='Expected UTC hours with observed value (%)')
    fig.suptitle('MetPipe Northeast · Observed data availability', fontsize=16, fontweight='bold', y=.98)
    fig.text(.09, .025, '2005–2024 · 20 stations · Finalized observed-only policy\nRounded to 0.1 percentage point; 100.0% can include small gaps.\nCoverage, not independent accuracy. No reconstructed values are counted.', fontsize=10)
    fig.tight_layout(rect=(0, .1, 1, .93))
    fig.savefig(assets / 'data_availability.png', dpi=170, facecolor='white')
    plt.close(fig)

    annual = years.pivot(index='station', columns='year', values='station_pressure_hpa_pct').sort_index()
    if annual.isna().any().any() or annual.shape != (20, 20):
        raise ValueError('Expected complete station/year audit, including zero coverage if absent')
    fig, ax = plt.subplots(figsize=(12.5, 7.2))
    image = ax.imshow(annual, cmap='Blues', vmin=60, vmax=100, aspect='auto')
    ax.set_yticks(range(20), annual.index)
    ax.set_xticks(range(20), annual.columns, rotation=45, ha='right')
    ax.set_xlabel('UTC year')
    ax.set_title('Observed station-pressure availability by year', fontsize=15, fontweight='bold', pad=14)
    fig.colorbar(image, ax=ax, fraction=.035, pad=.02, label='Expected hours with observed pressure (%)')
    row, col = np.unravel_index(np.argmin(annual.to_numpy()), annual.shape)
    ax.text(col, row, f'{annual.iloc[row, col]:.1f}', ha='center', va='center', color='#17324d', fontsize=9)
    fig.text(.07, .025, 'Finalized observed-only policy · Each cell uses its calendar-year denominator, including leap days.\nThe full-precision station/year/element counts are included in reports/.', fontsize=10)
    fig.tight_layout(rect=(0, .07, 1, 1))
    fig.savefig(assets / 'pressure_availability_by_year.png', dpi=170, facecolor='white')
    plt.close(fig)
    print('Exported two observed-only availability charts.')


if __name__ == '__main__':
    main()
