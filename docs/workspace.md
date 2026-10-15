# Local workspace after the split

The existing `metpipe_phase2` checkout keeps the original Git history and
`jjmetdata/metpipe_northeast` remote. Two sibling directories are initialized as
independent local Git repositories:

```text
metpipe_phase2/             NOAA ETL and data quality
metpipe-reconstruction/     PVC pressure reconstruction
metpipe-regional-analysis/  Regional changes and timing
```

No new GitHub repository, commit or push was created during the split. The two
companions have no remote configured yet.

The original source, notebooks and documentation were copied and SHA-256 checked
into the sibling `.metpipe-workspace/archive-20261015` before files were separated.
That archive is local, outside all three repositories. It excludes credentials,
Git metadata and duplicated large caches.

Raw data, generated artifacts and the existing Python environment remain under
`metpipe_phase2`. The companions use ignored `data` and `outputs` symlinks to
those caches. Do not delete the ETL directory or the symlink targets to clean up
a companion. The short overview notebooks instead use committed report snapshots
and figures, so they work independently of those links.

Frozen Python/SQL and original scientific outputs were not rewritten. Public
READMEs and new walkthroughs provide the shorter project introductions; dated
technical reports retain the evidence behind the published versions.
