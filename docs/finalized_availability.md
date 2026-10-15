# Finalized station/year/element availability

Audit date: October 14, 2026. Policy: `observed_2005_2024_v1`.
**Read-only: no observation updates, reconstruction publication, station changes,
model refitting or notebook source switches.**

All **400 core station-years** (twenty stations, UTC 2005–2024) were assessed
for all ten numeric reported fields, wind state, any-core and complete-core
availability. CQX's twenty auxiliary GHCNh station-years are reported separately;
they are not part of the cross-archive finalized core view. All 3,506,400 expected
finalized station-hours remain present and unchanged.

## PVC remains the weakest-coverage core station

Each station has 175,320 expected UTC hours, including leap days and all absent
reports. Availability counts accepted finalized values, **not independent accuracy**.

| Core element | PVC availability | Missing hours | Lowest among core 20? |
|---|---:|---:|---|
| Temperature | 95.17% | 8,473 | Yes |
| Dew point | 94.62% | 9,438 | Yes |
| RH | 94.61% | 9,441 | Yes |
| Station pressure | 92.79% | 12,639 | Yes |
| Wind speed | 94.86% | 9,008 | Yes |

The next-lowest pressure availability is MVY at **98.82%**. PVC's weakest year
is 2006: pressure availability **61.75%**, temperature 62.76% and dew point/RH
about 59.82%. The full report includes every station/year and all elements;
twenty-year averages must not hide these weak periods.

Reconciliation recovered pressure values elsewhere in the network, but **PVC's
pressure count did not increase relative to the consistent GHCNh v1 dataset**.
Its missing pressure hours classify as:

- **7,192:** no selected primary routine report.
- **5,447:** the selected primary report lacks pressure.

These categories describe the selected source layer, not proof the station
never reported through any other feed or at any other time. None of these PVC
pressure gaps is classified as an unresolved cross-archive value conflict.

Gust report presence is conditional on gust reporting, not a demand for an hourly
gust value. Numeric wind bearings exclude calm/variable conditions, whose valid
states are counted separately. Precipitation remains reported-field presence,
not duration-validated rainfall totals; absence is not zero precipitation.

## Reconstruction should be selective, not a blanket fill

There are **2,010 missing-pressure runs**:

- **6,630 hours** occur in runs no longer than 72 hours.
- **6,009 hours** occur in longer runs.
- The longest run is **2,212 hours**, September 12, 2006 10:00 UTC through
  December 13, 2006 14:00 UTC (end exclusive), about 92 days.

The length screen alone does not establish reconstruction eligibility. Check
donor availability, source/actual-time alignment, boundary support, blocked
validation and regime-specific uncertainty. The previous pressure models used
different inputs and remain historical experiments, not approved publishers for
this new finalized version. Their <=72h publication guard cannot be silently
relaxed; occasional large errors and rapid-change uncertainty limitations remain.

The dataset is useful without complete reconstruction. If a continuous pressure
series is needed, start with pressure only, retain observed values as evaluation
truth, and keep estimates/model versions/uncertainty in a **separate layer**.
Never use estimated targets as their own validation truth or replace the
observed-only finalized dataset. Long gaps require a separately justified policy.

## Recover observations before modelling them

A secondary read-only scan of twenty audited raw PVC GHCNh files found **622
alternate FM-15 pressure reports spanning 428 currently missing finalized hours**.
They pass the same known-bad-QC/point-value screen, with unknown QC still explicit.
**All 428 hours have different report times from the selected routine record**;
the nearest alternatives differ by **1–55 minutes**.

The current coherent-row ranking prioritizes routine type, temperature/dew-point/
wind completeness and latest time. Thus another report in an hour can contain
pressure even when the selected record does not. These candidates are not
published, independently verified replacements or model estimates. Review
per-element timing, QC, station identity and source evidence before changing
the finalized sampling policy. Do not simply insert an earlier pressure reading
as if measured at the existing report time.

Recommended sequence: review these real-observation candidates first; then run
a new finalized-input pressure reconstruction experiment for the remaining
supported gaps, optionally assessing CQX as an additional predictor within the
training folds. The present finalized availability remains **92.79%**.

## Which previous analyses should change?

**Use finalized observations as the default for new current-dataset analyses,
but preserve previous outputs and rerun under new version names.**

| Analysis | Next action |
|---|---|
| Notebook 01: EDA/summary statistics | New finalized-source version; declare UTC versus fixed local-standard daily boundaries. |
| Notebook 02: hourly temperature relationships | Rerun with selected temperature timestamps, source provenance and complete gap scaffold. |
| Notebook 03: events/pressure/PC24 | Rebuild reference climatological samples, source-only event selection and tendencies with each element's own actual timestamp; flag source changes. |
| Notebook 04 and source/history/availability audits | Preserve original-source evidence. Add a separately labelled finalized/auxiliary comparison; do not make source comparison circular by replacing its inputs. |
| Notebook 05: failed LCD pressure pilot | Preserve its failure and guard. A new input dataset requires a new experiment, not silent weight/publisher reuse. |
| Notebook 06: GHCNh blocked pressure validation | New finalized-input experiment/folds and uncertainty validation. Keep original scores/source-specific results unchanged. |
| Frozen 2025 holdout | Preserve the historical protocol and result. It has been inspected and is not an untouched test set for revisions guided by it. |
| Legacy `analysis/metanalysis.py` | Keep as legacy; use new finalized-source notebooks instead. Its simple rainfall summation is not an authoritative rainfall analysis. |

A **blind table-name replacement is unsafe**. Existing loaders expect a single
observation timestamp and source per row, while finalized selections can differ
by element; some also reject missing report timestamps or filter specifically
for LCDv1. New loaders must handle selected per-element timestamps, unresolved
NULLs, UTC calendars and explicit policy versions without altering frozen helpers.

No old notebook/helper/model was changed by this audit. The next implementation
step is a new finalized-source EDA/relationship analysis, followed by a separately
validated pressure reconstruction experiment—not automatic filling of all gaps.

## Outputs and reproduction

```bash
.venv/bin/python analysis/audit_finalized_availability.py
.venv/bin/python analysis/audit_pvc_pressure_recovery.py
MPLBACKEND=Agg .venv/bin/python analysis/report_finalized_availability.py
.venv/bin/python -m unittest discover -s tests
```

Generated report and evidence: `outputs/audits/finalized_availability/`.

- `finalized_availability.html`: heatmaps, all station/year/element tables and migration plan.
- `core_station_year_availability.csv`: all 400 core station-years, counts and percentages.
- `auxiliary_cqx_year_availability.csv`: twenty separately labelled auxiliary years.
- `core_missing_runs.csv` / `gap_summary.csv`: full-period runs across year boundaries.
- `pressure_missing_reason_hours.csv` / `pressure_missing_reasons.csv`: missing-pressure classifications.
- `pvc_unselected_pressure_report_candidates.csv`: all 622 unpublished alternate reports.
- `pvc_raw_pressure_recovery_summary.json`: timing/QC/checksum evidence for 428 candidate hours.
- `analysis_source_migration_plan.csv`: inspected notebook/helper source inventory and recommendations.

The audit computes percentages against the full expected UTC calendar and uses
the finalized snapshot backing the published view. No model estimates enter
availability counts. Reproducible policy/code hashes are retained in JSON.
