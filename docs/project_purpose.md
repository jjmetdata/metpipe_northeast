# Scope

MetPipe turns annual NOAA station archives into a consistent, traceable
PostgreSQL observation layer. Its responsibilities are ingestion, transformation,
source selection, provenance and availability checks.

Reconstruction and regional weather analysis consume that layer in separate
projects. Live ingestion, NWP integration and ISO New England load forecasting
are possible extensions, not current pipeline capabilities.

The original twenty stations cover coastal and inland locations in MA, RI, CT,
VT, NH, ME and NY. The working historical window is 2005–2024.
