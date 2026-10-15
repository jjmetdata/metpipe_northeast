# MetPipe: pipeline maintenance

This repository owns NOAA ingestion, transformation, source reconciliation and
data-quality reporting. ML reconstruction and regional diagnostics live in the
sibling `metpipe-reconstruction` and `metpipe-regional-analysis` repositories.

## Keep these contracts

- Preserve raw observations, source/QC flags, report times and file hashes.
- Keep the core twenty stations and the agreed 2005–2024 scope unchanged unless
  the user requests a new data version. CQX remains auxiliary.
- Retain every expected hour. Missing values are not zero; gust reporting is
  conditional, and calm/variable wind states are not numeric directions.
- LCDv1 legacy fields use customary units and fixed UTC−5; the finalized view is
  UTC/SI. Historical reporting minutes and source IDs can change.
- Finalized `observed_2005_2024_v1` is observed-only. Do not fill it with model
  output. Known-bad primary data needs verified fallback evidence; unresolved
  conflicts blank only that element.
- Database changes must be additive, versioned and explicitly authorized. Never
  drop/reset an existing dataset to simplify a rerun.
- Do not edit hash-bound source/selection helpers to change their style. New
  scientific behavior requires a new version. See `docs/compatibility.md`.

## Working style

Write concise, direct documentation with correct grammar. Keep public descriptions
regional and product-neutral. Put detailed audit evidence in reference reports,
not the main README. Preserve unrelated local changes and never commit or push
without the user's request.

Tests: `python -m unittest discover -s tests -v`.
Local datasets and generated output caches stay outside Git.
The pre-split working tree is preserved in the sibling
`.metpipe-workspace/archive-20261015`; do not delete it as cleanup.
