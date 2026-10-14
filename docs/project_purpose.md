# MetPipe Northeast: purpose and research direction

Updated October 13, 2026.

## General purpose

Build a reliable, traceable regional observation dataset that connects
historical weather analysis with future near-real-time monitoring and
observation-supported nowcasting in the northeastern United States.

The pipeline is the infrastructure, not the final forecast product. It makes
weather observations comparable and queryable while preserving their source,
quality flags, actual observation times and limitations. The scientific aim is
to characterize regional weather patterns, temporal trends, seasonal variability
and short-term changes; learn which signals help explain—and potentially
anticipate—local weather evolution; and test those relationships on unseen events.

The intended prediction workflow combines observations with global and mesoscale
NWP outputs, supporting statistical and machine-learning-assisted forecast
refinement and nowcasting. NWP integration and machine-learning prediction
components remain development goals, not current capabilities.

## Present scope

The original twenty airport stations are retained across MA, RI, CT, VT, NH,
ME and NY. The local database covers 2005–2024 with 5,381,350 point observations
and 3,495,851 selected routine hours. See the
[network map](assets/station_network.svg) and
[validated ingestion report](ingestion_2005_2024.md).

Implemented: historical acquisition/cleaning, source-aware conversion,
incremental database ingestion, provenance, hourly selection, summary views and
coverage auditing. Not implemented: live ingestion, pressure-index products,
lead/lag prediction models, radar/NWP ingestion or operational nowcasting.

The network supports regional analysis and multiple downstream applications
without designating a particular station as a special target.

## Questions this foundation should support

- What temporal trends, seasonal patterns and short-term tendencies are present,
  after accounting for gaps, archive changes and station/instrument history?
- How do temperature, moisture, wind and pressure evolve across coastal and
  inland stations during fronts, sea-breeze transitions and other weather regimes?
- Does a change at one station consistently precede a change elsewhere?
  How does any lead time depend on wind direction, system type and season?
- Can short-term tendencies or upstream observations outperform a simple
  persistence forecast at a target station?
- Which pressure diagnostics provide useful information beyond local pressure
  alone, and when do they fail?
- Can observations help identify, quantify or correct short-range model errors?

These are research questions, not conclusions already established by ingestion.
An airport seeing a change does not mean the same change must reach another
airport: systems evolve, and terrain, coastlines and local circulations matter.

## Pressure diagnostics: useful idea, careful definitions

A starting point is same-station pressure tendency over explicitly defined
time intervals. Regional differences and gradients are another potential
feature family, once compatible pressure measurements are available.

HKO's DP972 is a pressure difference between Hong Kong and Chenzhou (station
57972), used alongside other regional indices in wind-prediction research.
It is a geographically defined index, not a universal formula or a 972 hPa
threshold. [HKO research paper, section 2](https://www.hko.gov.hk/en/publica/reprint/files/r1832.pdf).

Our proposed direction is to test Northeast-specific, physically motivated
indices, not copy that station pair or assume the same forecast skill. An
experimental coastal–inland or north–south difference would need a declared
station pair, subtraction order, units, pressure reference, valid-time alignment
and missing-data policy, followed by independent evaluation.

**Current limitation:** the compatibility table stores station pressure, not
a verified, consistently defined mean-sea-level-pressure field. Station pressure
depends on elevation; altimeter setting and mean sea-level pressure are also
distinct definitions. Raw interstation subtraction can therefore reflect site
elevation rather than the intended weather signal. Before computing regional
gradients, extend the adapters to preserve and qualify the appropriate pressure
fields and site metadata. [NWS pressure definitions](https://www.weather.gov/bou/pressure_definitions).

## Development sequence

1. **Historical analysis and baselines.** Build reproducible event-based
   analyses, element-specific availability screens and simple tendency/lag
   features. Begin with persistence and short-term trend baselines.
2. **Live-observation adapters.** Start with a well-defined airport feed, then
   evaluate mesonets, coastal/marine observations and other sensors as distinct
   sources. Preserve sensor identity and siting; do not silently merge unlike
   instruments into a single station-time value. Track observation time,
   receipt time, latency, revisions, outages and stale-data status.
3. **Experimental nowcasts.** Evaluate target-specific lead/lag and regional
   diagnostics against baselines. More sources or a more complex model do not
   by themselves establish better forecasts.
4. **Model and spatial context.** Evaluate HRRR, GFS and ECMWF integration where
   access permits; retain initialization, valid time and lead time. Radar and
   other spatial observations would be separate adapters, not inferred from
   airport observations alone.

## Evaluation and operational boundaries

- Use chronological and event-held-out evaluation, not random adjacent-hour
  splits. Compare against persistence/trend and relevant model baselines.
- Only use information available at the forecast issue time. A historical
  observation timestamp is not proof that a live feed delivered it immediately.
- Report skill by target, variable, lead time, season/regime and availability;
  verify uncertainty and failure cases as well as average error.
- Use actual UTC observation times for lag/model joins. Hourly bucket times
  must not imply that a later observation was already available at the hour's start.
- Keep gaps and source-dependent flags visible. PVC rainfall remains sparse;
  an absent amount is not automatically a dry hour. Coded cloud data is not yet
  a fully normalized cloud product.
- Assess the archive/selection-policy change at 2020 and station/instrument
  changes before attributing trends or training a model.

MetPipe is an early-stage weather-data engineering and research project. It does
not currently issue validated forecasts, operational warnings or safety guidance.
