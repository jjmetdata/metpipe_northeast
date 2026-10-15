# Frozen compatibility helpers

The pipeline's frozen GHCNh audit imports a few older shared helpers:
`audit_pvc_neighbors.py`, `weather_events.py`, `hourly_pair.py` and `eda_utils.py`.
They remain here to preserve the exact selection, timing and hash checks used
for the published dataset. They are dependencies, not additional ML or regional
research entrypoints in this repository.

New reconstruction work is in `metpipe-reconstruction`; current timing studies
are in `metpipe-regional-analysis`. The split did not change the database or
refit any model. Source hashes and ownership are recorded in
`split_provenance.json`. Public-facing docs were shortened; frozen scientific
Python was copied without style edits.

The pre-split working files are preserved locally outside the repositories.
Generated research caches still exist under the ignored `outputs/` directory;
their presence on a developer's disk does not make them part of this Git repo.
