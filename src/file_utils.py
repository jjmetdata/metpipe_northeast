"""Filename parsing and discovery for MetPipe station-year datasets."""

from dataclasses import dataclass
from pathlib import Path
import re
from typing import List


RAW_FILE_PATTERN = re.compile(
    r"^(?P<station>[a-z0-9]{3})_hourly_(?P<year>\d{4})\.csv$",
    re.IGNORECASE,
)
CLEANED_FILE_PATTERN = re.compile(
    r"^(?P<station>[a-z0-9]{3})_hourly_(?P<year>\d{4})_cleaned\.csv$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class WeatherDataFile:
    path: Path
    station: str
    year: int


def parse_weather_file(path: Path, *, cleaned: bool) -> WeatherDataFile:
    """Parse a station and year from a supported MetPipe CSV filename."""
    pattern = CLEANED_FILE_PATTERN if cleaned else RAW_FILE_PATTERN
    match = pattern.fullmatch(path.name)

    if match is None:
        kind = "cleaned" if cleaned else "raw"
        raise ValueError(f"Unsupported {kind} weather filename: {path.name}")

    return WeatherDataFile(
        path=path,
        station=match.group("station").upper(),
        year=int(match.group("year")),
    )


def discover_weather_files(directory: Path, *, cleaned: bool) -> List[WeatherDataFile]:
    """Find flat or year-organized files, rejecting ambiguous station-years."""
    glob_pattern = "*_hourly_*_cleaned.csv" if cleaned else "*_hourly_*.csv"
    discovered = []
    seen = {}

    for path in sorted(directory.rglob(glob_pattern)):
        try:
            weather_file = parse_weather_file(path, cleaned=cleaned)
        except ValueError:
            # Ignore unrelated CSVs that happen to match the broad glob.
            continue

        relative_parent = path.parent.relative_to(directory)
        if relative_parent != Path(".") and relative_parent != Path(str(weather_file.year)):
            raise ValueError(
                f"{path} must be directly in {directory} or its {weather_file.year}/ folder"
            )

        key = (weather_file.station, weather_file.year)
        if key in seen:
            raise ValueError(
                f"Duplicate {weather_file.station} {weather_file.year} files: "
                f"{seen[key]} and {path}"
            )
        seen[key] = path
        discovered.append(weather_file)

    return sorted(discovered, key=lambda item: (item.station, item.year))
