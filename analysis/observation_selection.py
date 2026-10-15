"""Pure, conservative per-element source selection; never deletes source data."""
import math
import re
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from ghcnh_backfill import rejected

POLICY = 'observed_2005_2024_v1'
PRIMARY = 'GHCNh_2005_2024_routine_v1'
FIELDS = {
    'temperature_c': ('temperature', 'HourlyDryBulbTemperature', .06, (-90., 60.)),
    'dewpoint_c': ('dew_point_temperature', 'HourlyDewPointTemperature', .06, (-100., 60.)),
    'relative_humidity': ('relative_humidity', 'HourlyRelativeHumidity', 1., (0., 100.)),
    'station_pressure_hpa': ('station_level_pressure', 'HourlyStationPressure', .18, (400., 1100.)),
    'wind_speed_ms': ('wind_speed', 'HourlyWindSpeed', .25, (0., 100.)),
    'wind_gust_ms': ('wind_gust', 'HourlyWindGustSpeed', .25, (0., 150.)),
    'precipitation_reported_mm': ('precipitation', 'HourlyPrecipitation', .06, (0., 1000.)),
}
MATCH = {'temperature_c': (.06, .28), 'dewpoint_c': (.06, .28),
         'wind_speed_ms': (.10, .23), 'wind_gust_ms': (.10, .23),
         'precipitation_reported_mm': (.06, .001)}


def usable(value, bounds):
    return value is not None and math.isfinite(float(value)) and bounds[0] <= float(value) <= bounds[1]


def decode_metar(remark, station, timestamp):
    """Decode only explicitly reported elements with an exact station/time header.

    LCD-embedded text is supporting source evidence, NOT independent ground truth.
    No station pressure or RH is inferred from altimeter/SLP or temperature.
    """
    text = str(remark or '')
    # LCD REM often prefixes the bulletin with its MET### record-length tag.
    header = re.search(r'(?:^|\s|MET\d{3})METAR\s+(K[A-Z0-9]{3})\s+(\d{6})Z\b', text)
    if not header or header.group(1) != 'K' + station or header.group(2) != timestamp.strftime('%d%H%M'):
        return {}
    result = {'evidence_kind': 'LCD_embedded_METAR', 'remark': text,
              'station': station, 'observation_datetime_utc': timestamp.isoformat()}
    t = re.search(r'\bT([01])(\d{3})([01])(\d{3})\b', text)
    if t:
        result['temperature_c'] = int(t.group(2)) / 10 * (-1 if t.group(1) == '1' else 1)
        result['dewpoint_c'] = int(t.group(4)) / 10 * (-1 if t.group(3) == '1' else 1)
    p = re.search(r'\bP(\d{4})\b', text)
    if p:
        result['precipitation_reported_mm'] = int(p.group(1)) * .254
        result['precipitation_trace'] = p.group(1) == '0000'
    wind = re.search(r'\b(\d{3}|VRB)(\d{2,3})(?:G(\d{2,3}))?KT\b', text)
    if wind:
        result['wind_speed_ms'] = int(wind.group(2)) * .514444444444
        result['wind_state'] = 'calm' if int(wind.group(2)) == 0 else 'variable' if wind.group(1) == 'VRB' else 'numeric'
        result['wind_direction_deg'] = int(wind.group(1)) if result['wind_state'] == 'numeric' else None
        if wind.group(3):
            result['wind_gust_ms'] = int(wind.group(3)) * .514444444444
    return result


def decision(value, source, reason, when, gh, lcd, flags, metar=None, **extra):
    return {'value': value, 'source': source, 'reason': reason,
            'observation_datetime_utc': when.isoformat() if when is not None else None,
            'ghcnh_value': gh, 'lcd_value': lcd, 'ghcnh_flags': flags,
            'selected_qc': flags if source == 'GHCNh' else
                {'source_qc': 'unknown', 'raw_suspect_suffix': False} if source == 'LCDv1' else None,
            **({'metar_evidence': metar} if metar else {}), **extra}


def resolve_number(field, gh, lcd, gh_time, lcd_time, flags=None,
                   lcd_suspect=False, metar=None, gh_trace=None, lcd_trace=None):
    """Return an explicit override, including NULL, or None for unchanged primary.

    Only exact-time values are compared. A whole-hour LCD fallback is allowed if
    there is no primary report; otherwise fallback also requires exact report time.
    """
    flags = flags or {}
    raw_name, _, tolerance, bounds = FIELDS[field]
    bad = rejected(raw_name, flags)
    g_ok = usable(gh, bounds) and not bad
    l_ok = usable(lcd, bounds) and not lcd_suspect
    def choose(value, source, reason, when, **kwargs):
        if field == 'precipitation_reported_mm' and 'trace' not in kwargs:
            kwargs['trace'] = gh_trace if source == 'GHCNh' else lcd_trace if source == 'LCDv1' else None
        return decision(value, source, reason, when, gh, lcd, flags, **kwargs)
    if bad or (gh is not None and not usable(gh, bounds)):
        return choose(None, None, 'blocked_primary_bad_qc_or_range', None)
    if not g_ok:
        if not l_ok:
            return choose(None, None, 'lcd_suspect_or_invalid', None) if lcd is not None else None
        if gh_time is not None and gh_time != lcd_time:
            return choose(None, None, 'fallback_unverified_report_time', None)
        extra = {'trace': lcd_trace} if field == 'precipitation_reported_mm' else {}
        return choose(lcd, 'LCDv1', 'fallback_missing_GHCNh', lcd_time, **extra)
    if not l_ok:
        return choose(gh, 'GHCNh', 'primary_LCD_suspect_or_invalid', gh_time) if lcd is not None else None
    if gh_time != lcd_time:
        return choose(gh, 'GHCNh', 'primary_different_report_times_not_compared', gh_time,
                      lcd_observation_datetime_utc=lcd_time.isoformat())
    trace_conflict = field == 'precipitation_reported_mm' and gh_trace != lcd_trace
    if abs(gh - lcd) <= tolerance + 1e-10 and not trace_conflict:
        return None
    evidence = metar or {}
    if field in MATCH and field in evidence:
        g_tol, l_tol = MATCH[field]
        g_match = abs(gh - evidence[field]) <= g_tol + 1e-10
        l_match = abs(lcd - evidence[field]) <= l_tol + 1e-10
        if field == 'precipitation_reported_mm':
            g_match &= gh_trace == evidence.get('precipitation_trace')
            l_match &= lcd_trace == evidence.get('precipitation_trace')
        if g_match != l_match:
            value, source, when = (gh, 'GHCNh', gh_time) if g_match else (lcd, 'LCDv1', lcd_time)
            extra = {'trace': gh_trace if g_match else lcd_trace} if field == 'precipitation_reported_mm' else {}
            return choose(value, source, 'conflict_supported_by_LCD_embedded_METAR', when,
                          metar=evidence, **extra)
    return choose(None, None, 'conflict_unresolved', None, metar=evidence)


def lcd_wind_state(direction, speed):
    if direction is None:
        return 'missing', None
    if str(direction).upper() == 'VRB':
        return 'variable', None
    try:
        angle = float(direction)
    except (ValueError, TypeError):
        return 'missing', None
    if not 0 <= angle <= 360:
        return 'missing', None
    if speed == 0:
        return 'calm', None
    return 'numeric', angle


def resolve_wind(gh_state, gh_angle, lcd_state, lcd_angle, gh_time, lcd_time, flags, metar):
    g_ok, l_ok = gh_state in {'numeric', 'calm', 'variable'}, lcd_state in {'numeric', 'calm', 'variable'}
    if rejected('wind_direction', flags or {}):
        return decision(None, None, 'blocked_primary_bad_qc_or_range', None, gh_angle, lcd_angle, flags, state='conflict')
    if not g_ok and l_ok:
        if gh_time is not None and gh_time != lcd_time:
            return decision(None, None, 'fallback_unverified_report_time', None, gh_angle, lcd_angle, flags, state='conflict')
        return decision(lcd_angle, 'LCDv1', 'fallback_missing_GHCNh', lcd_time, gh_angle, lcd_angle, flags, state=lcd_state)
    if not g_ok or not l_ok:
        return None
    if gh_time != lcd_time:
        return decision(gh_angle, 'GHCNh', 'primary_different_report_times_not_compared', gh_time,
                        gh_angle, lcd_angle, flags, state=gh_state)
    agree = gh_state == lcd_state
    if agree and gh_state == 'numeric':
        agree = abs((gh_angle - lcd_angle + 180) % 360 - 180) <= .5
    if agree:
        return None
    e_state = (metar or {}).get('wind_state')
    def matches(state, angle):
        return state == e_state and (state != 'numeric' or abs((angle - metar['wind_direction_deg'] + 180) % 360 - 180) <= .5)
    gm, lm = matches(gh_state, gh_angle), matches(lcd_state, lcd_angle)
    if gm != lm:
        value, source, when, state = (gh_angle, 'GHCNh', gh_time, gh_state) if gm else (lcd_angle, 'LCDv1', lcd_time, lcd_state)
        return decision(value, source, 'conflict_supported_by_LCD_embedded_METAR', when,
                        gh_angle, lcd_angle, flags, metar, state=state)
    return decision(None, None, 'conflict_unresolved', None, gh_angle, lcd_angle, flags, metar, state='conflict')
