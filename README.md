# SANBI Ecosystem Risk Profiler

A Streamlit web application for ecosystem-level risk assessment based on the **2018 National Biodiversity Assessment (NBA)** data from the South African National Biodiversity Institute (SANBI). It analyses ecosystem threat status, habitat transformation risk, and biodiversity vulnerability across South Africa's 10 biomes.

---

## Features

- **Overview Dashboard** — national-level risk summary with threat level metrics (CR/EN/VU/NT/LC) and biome-wide charts
- **Biome Explorer** — interactive three-level filtering (Biome → Bioregion → Ecosystem) with trend analysis and comparison against national averages
- **Risk Categories** — deep dive into four risk factors: habitat transformation, biodiversity threat status, vegetation vulnerability, and protection gaps

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web framework | Streamlit ≥ 1.28 |
| Visualisation | Plotly, Altair, Folium, Matplotlib, Seaborn |
| Database | PostgreSQL + PostGIS |
| ORM / DB adapter | SQLAlchemy ≥ 2.0, psycopg2 |
| Geospatial | GeoPandas ≥ 0.14, Shapely ≥ 2.0 |
| Data | pandas ≥ 2.1, NumPy, SciPy |
| Config | python-dotenv, Pydantic ≥ 2.0 |
| Runtime | Python 3.12, Docker |

---

## Prerequisites

- Python 3.12+
- PostgreSQL with PostGIS extension (NBA 2018 data loaded)
- Docker & Docker Compose (for containerised setup)

---

## Local Setup (without Docker)

```bash
# 1. Clone the repository
git clone https://github.com/SAEON/sanbi-ecosystem-risk-atlas.git
cd sanbi-ecosystem-risk-atlas

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env with your database credentials (see Environment Variables below)

# 5. (Optional) Test the database connection
python scripts/test_database.py

# 6. Run the app
streamlit run main.py
```

App will be available at `http://localhost:8501`.

---

## Docker Setup

```bash
# Build and start
TAG=latest docker compose up -d --build

# Check status
docker compose ps
docker logs sanbi-ecosystem
```

App will be available at `http://localhost:8503`.

---

## Environment Variables

Copy `.env.example` to `.env` and fill in the values:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ecosystem_risk_db
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_SCHEMA=sdgs
DB_TABLE=environmental_risk_data

# Application Settings
APP_DEBUG=False
APP_LOG_LEVEL=INFO

# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Cache Settings
CACHE_TTL=3600
MAX_CACHE_ENTRIES=1000

# Security (for production deployment)
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=localhost,127.0.0.1

# Performance Monitoring (optional)
# SENTRY_DSN=your_sentry_dsn_here
```

The database must contain a PostGIS-enabled table at `<DB_SCHEMA>.<DB_TABLE>` with the NBA 2018 ecosystem data. Key columns include `biome_18`, `bioregion_`, `rlev5` (Red List level), `pcnat2014`, `prcdelyear`, `pl_2018`, and `geometry`.

---

## Project Structure

```
sanbi-ecosystem-risk-atlas/
├── main.py                    # App entry point
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── app/
│   └── config.py             # App config, risk thresholds, constants
├── pages/
│   ├── Overview.py
│   ├── Biome_Explorer.py
│   └── Risk_Categories.py
├── components/
│   ├── geographic_filter.py  # Biome → Bioregion → Ecosystem filter
│   ├── comparison_metrics.py
│   ├── risk_summary_panel.py
│   └── trend_charts.py
├── utils/
│   └── risk_calculations.py
├── data/
│   ├── database.py           # DatabaseManager, connection pooling
│   ├── cache_manager.py      # Streamlit cache wrappers
│   └── queries.py            # SQL query builders
└── scripts/
    └── test_database.py      # DB connectivity test
```

---

## Data Source

> **2018 Marine Ecosystem Threat Status and Protection Level**
> Layer containing threat status and protection level assessments of marine ecosystems evaluated for the National Biodiversity Assessment 2018. Vector format, national coverage (South Africa).
>
> **Author:** Kerry Sink ([K.Sink@sanbi.org.za](mailto:K.Sink@sanbi.org.za)) — SANBI, Kirstenbosch Research Centre
> **Contact:** SANBI BGIS — [bgishelp@sanbi.org.za](mailto:bgishelp@sanbi.org.za) · +27 21 799 8738
> **Publisher:** South African National Biodiversity Institute (SANBI), 2019 — via [SARVA / SAEON](https://catalogue.saeon.ac.za/records/10.15493/SARVA.251120-11)
> **License:** [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)
> **DOI:** [10.15493/SARVA.251120-11](https://catalogue.saeon.ac.za/records/10.15493/SARVA.251120-11)
> **More info:** [bgis.sanbi.org/SpatialDataset/Detail/2682](https://bgis.sanbi.org/SpatialDataset/Detail/2682)
>
> **Citation:** South African National Biodiversity Institute. *2018 Marine ecosystem threat status and protection level* [Vector]. 2018.

All ecological data is sourced from the **South African National Biodiversity Assessment 2018 (NBA 2018)**, published by SANBI and made available through the SAEON data catalogue. The dataset covers ecosystem threat status, habitat transformation, vegetation vulnerability, and protected area coverage across South African biomes.

---

## License

See [LICENSE](LICENSE).
