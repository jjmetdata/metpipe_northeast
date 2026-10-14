# MetPipe working data scope

Decision date: October 12, 2026.

## Working window

Use **2005–2024** as the current historical hourly analysis and expansion target.
Keep the 1995–2024 and 1990–2024 audits as context for optional future backfill,
not mandatory eligibility criteria for the current network.

The full selected 94-location assessment found 41 sites passing the conservative
hourly core screen in every year of 2005–2024. The screen covers temperature,
dew point and wind speed, not every weather element. Thirteen original stations
pass all 20 recent years; several others narrowly miss in particular years.
These are source/QC availability findings, not complete station certifications.

Prioritize geographic usefulness and element quality within the working window.
Do not discard modern coastal stations solely because pre-2005 coverage is weaker.
PVC can remain a local-target exception with its gaps explicitly documented.

## State and next steps

- The finalized network retains all original 20 stations. PSF, VSF and BDR
  remain backups, not replacements.
- The 2005–2019 GHCNh backfill supplements existing 2020–2024 LCDv1 data.
  Ingestion is complete and validated: 5,381,350 point observations and
  3,495,851 selected routine hours across all 400 station-year combinations.
  See [ingestion report](ingestion_2005_2024.md) for completion and verified counts.
- Preserve historical report types, source/QC flags and time semantics. GHCNh
  uses routine-report ranking rather than modern fixed-minute selection.
- Qualify precipitation, pressure and clouds separately for each application;
  core-hour availability does not establish all-element completeness.
- Ingest independently by station-year, with missing periods preserved and
  chronological validation rather than random adjacent-hour train/test splits.

Evidence: [all-94 three-window audit](all94_history_three_windows.md).
