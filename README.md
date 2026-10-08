# Geospatial Measurement API

A lightweight FastAPI service built for Aereo's technical assessment. It accepts `.zip` (Shapefiles) and `.kml` spatial files, extracts feature details, re-projects geographic coordinates to appropriate projected CRS, and computes geometry measurements (Area for Polygons, Length for LineStrings).

---

##  Tech Stack

- **FastAPI** & **Uvicorn** - API routing and server execution
- **GeoPandas** & **PyOgrio** - Spatial file reading and vector processing
- **Shapely** & **PyProj** - Geometric computations and Coordinate Reference System (CRS) transformations

---

##  Repository Structure

```text
aereo-project/
├── app/
│   ├── __init__.py
│   ├── main.py          # Route definitions & file handlers
│   └── services.py      # Spatial data extraction & measurement logic
├── .gitignore
├── README.md
└── requirements.txt