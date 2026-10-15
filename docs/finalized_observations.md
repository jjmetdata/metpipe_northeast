# Finalized observations and auxiliary Chatham data

Scope: core twenty stations, UTC 2005–2024. Source datasets are preserved.
This layer chooses existing reported observations; **it does not reconstruct,
model-fill or invent missing measurements**.

**Completed October 14, 2026:** finalized snapshot/view published with all
3,506,400 expected core station-hours. There are 1,844 hours with explicit
selection decisions, including 539 pressure fallbacks and 757 unresolved
element conflicts left NULL. Original 5,381,350 rows and the 3,497,180-row
GHCNh input remain unchanged. CQX auxiliary ingestion is also complete.
Both publication reruns verified existing versions without adding duplicates;
all 112 automated tests passed.

## Database layers

| Layer | PostgreSQL location | Purpose |
|---|---|---|
| Original | `public.weather_observations` and existing public views | Preserved mixed historical backfill/LCDv1 dataset |
| Consistent GHCNh | `ghcnh_parallel.hourly_observations` | Preserved GHCNh 2005–2024 core-20 version |
| Finalized | `metpipe_final.weather_hourly_utc` | Versioned per-element selection for reporting/research |
| Auxiliary | `metpipe_aux.hourly_observations` | CQX under its own identity; not automatically in core views/models |

The finalized view is backed by an immutable snapshot,
`observed_2005_2024_v1`. Every expected station-hour remains present, including
hours with no usable observations. **Unresolved conflicts produce SQL NULL for
only the affected element, not deletion of a source value, field or row.**
The expected calendar contains 3,506,400 rows. Completion is verified through
`metpipe_final.policy_versions.status` and the generated publication summary.

## Selection policy

1. Use the already source-QC-screened GHCNh routine-hour record as the default.
   Apply broad global physical bounds. Retain calculated/unmapped QC information;
   these flags are not promoted to independently certified sensor accuracy.
2. Compare LCDv1 only at the **same actual report timestamp**, not simply the
   same hourly bucket. Tiny precision-level differences retain GHCNh.
3. If a primary element is missing, use LCD only when its original CSV supports
   the stored value, no raw suspect `s` suffix is present, and report times match.
   A checked-minute LCD report can supply an entirely missing primary hour.
4. A primary known-bad QC rejection cannot be bypassed by reintroducing a value
   through LCD. Such fallback remains NULL pending review.
5. For a material same-time conflict, decode the LCD-embedded METAR only if its
   station identifier and UTC observation day/hour/minute match. Choose a source
   only when **exactly one** candidate matches the supported element at its
   reporting precision. Otherwise the finalized element remains NULL.
6. Two usable reports at different actual times are **not a same-instant
   conflict**. Retain GHCNh with `primary_different_report_times_not_compared`;
   do not silently mix an unmatched-time LCD fallback into another primary element.

Point agreement limits (not the earlier aggregate station-year gates):

| Element | Absolute difference allowed |
|---|---:|
| Temperature/dew point | 0.06°C |
| RH | 1 percentage point |
| Station pressure | 0.18 hPa |
| Wind speed/gust | 0.25 m/s |
| Reported precipitation | 0.06 mm, with consistent trace state |
| Numeric wind direction | 0.5°, circular difference |

These are explicit precision-based engineering rules, **not estimates of
meteorological measurement accuracy**. The policy stores thresholds, global
bounds, code hashes, input version and source CSV hashes. All policy decisions
are retained separately from the source observations.

## METAR support and its limits

The decoder handles the NOAA `MET###` REM prefix, validates the bulletin header,
and uses precise `T` temperature/dew-point remarks, wind groups and `P` reported
precipitation groups. It does **not** infer station pressure from altimeter/SLP,
derive reported RH from temperature/dew point, or adjudicate temperature using
only the coarser whole-degree body group.

Evidence is labelled `LCD_embedded_METAR`, not independent ground truth. It is
another representation within the same preserved source file, not a separately
retrieved complete corrected-bulletin history. Conflicting duplicate raw rows
cannot serve as adjudication evidence. Resolving archive representation
differences does not establish which sensor reading was physically accurate.

Precipitation remains `precipitation_reported_mm`, **not a certified one-hour
rainfall accumulation**. The legacy cleaner stored trace as 0.001 inch; the final
layer represents trace as numerical zero plus `precipitation_trace=true`, without
changing that legacy source value. Missing, trace and explicit zero remain distinct.
Do not sum reported amounts as rainfall totals without duration-aware validation.

Calm/variable winds have NULL numeric bearings and explicit states. No calm/VRB
placeholder becomes a north-pointing wind vector. Pressure/PC24 model experiments
and frozen 2025 protocols are unchanged; source selection is not a new model fit.

## Provenance and usage

`element_provenance` contains the selected source, reason, actual observation time
and selected QC information for every element. Non-default decisions also retain
both candidate values, source flags and any METAR support. LCD absence of a suspect
suffix is not full QC certification. `primary_quality_flags` always refers to the
GHCNh input, not necessarily the selected fallback.

Example: inspect one station/year without dropping missing hours:

```sql
SET TIME ZONE 'UTC';
SELECT station, hour_utc, temperature_c, station_pressure_hpa,
       element_provenance -> 'temperature_c' ->> 'source' AS temperature_source,
       element_provenance -> 'temperature_c' ->> 'reason' AS temperature_reason
FROM metpipe_final.weather_hourly_utc
WHERE station = 'BOS'
  AND hour_utc >= TIMESTAMPTZ '2024-01-01 00:00+00'
  AND hour_utc < TIMESTAMPTZ '2025-01-01 00:00+00'
ORDER BY hour_utc;
```

These timestamp columns are `TIMESTAMPTZ` (absolute instants). DataGrip/PostgreSQL
may display them in the session's local time zone unless it is set to UTC. The
actual report minute is in the per-element provenance; `hour_utc` is the hour bucket.

For model development, record the policy version and input snapshot. A missing
target can exclude that sample from that particular model, but must not erase the
database hour or unrelated elements. New notebook experiments must explicitly
choose this view; existing notebooks/public views and frozen models are unchanged.

## Chatham: auxiliary, not a relabelled substitute

CQX, **CHATHAM MUNICIPAL AIRPORT (MA)**, canonical NOAA ID **USW00094624**, is
ingested separately for 2005–2024: **175,089 selected routine-hour records** from
twenty audited raw files. Accepted station-pressure availability is **99.63%**;
temperature 99.52% and wind speed 99.35%.

The core network remains twenty stations. CQX is an auxiliary observation source,
not a replacement, not a PVC measurement and not automatically an input to the
existing pressure models. The map still depicts the core twenty. Future use as
a reconstruction predictor requires separate validation of its incremental value.
The auxiliary dataset has source-aware QC/availability checks, not independent
measurement-accuracy certification or an LCD-overlap audit.

```sql
SELECT * FROM metpipe_aux.hourly_observations
WHERE station = 'CQX'
  AND hour_utc >= TIMESTAMPTZ '2024-01-01 00:00+00'
  AND hour_utc < TIMESTAMPTZ '2025-01-01 00:00+00'
ORDER BY hour_utc;
```

## Reproduce and guardrails

```bash
.venv/bin/python -m unittest discover -s tests
.venv/bin/python analysis/publish_final_observations.py --publish
.venv/bin/python analysis/ingest_auxiliary_cqx.py --publish
```

Both scripts require explicit publication. Each import is transactional and
checks that original data/core membership remain unchanged. A completed policy
cannot be silently rewritten: changed code/evidence requires a newly reviewed
version. Immediate reruns should verify existing rows instead of duplicating them.
Generated evidence/results are under ignored `outputs/finalized_observations/`
and `outputs/auxiliary_cqx/`. Do not remove referenced raw source files.
