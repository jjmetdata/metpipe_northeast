-- October 12, 2026: the first backfill restored VRB from a measurement flag
-- after rejecting its numeric value. The adapter now checks QC before VRB.
-- Repair only historical GHCNh compatibility values; retain raw flags and
-- never touch the preserved LCDv1 data. Repeating this migration is harmless.
BEGIN;
UPDATE weather_observations
SET wind_direction = NULL
WHERE source_dataset = 'GHCNh'
  AND datetime >= '2005-01-01' AND datetime < '2020-01-01'
  AND wind_direction = 'VRB'
  AND (
    (source_metadata #>> '{fields,wind_direction,s}' IN
      ('220','221','222','223','347','348')
      AND source_metadata #>> '{fields,wind_direction,q}' IN ('2','3','5'))
    OR (source_metadata #>> '{fields,wind_direction,s}' IN
      ('313','314','315','322','335','343','344','346')
      AND source_metadata #>> '{fields,wind_direction,q}' IN ('2','3','6','7'))
    OR source_metadata #>> '{fields,wind_direction,q}' ~ '[a-z]'
    OR source_metadata #>> '{fields,wind_direction,r}' IN ('NSRDB','SOD','SOM')
  )
RETURNING station, datetime, source_metadata #> '{fields,wind_direction}' AS retained_raw_flags;
COMMIT;
