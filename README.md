# Business Gap Finder

**Global local-business intelligence + competitive mapping + public contact discovery + Blue Ocean opportunity analysis.**

A production-ready web application that allows users to select any city in the world, analyze real businesses operating there, enrich those businesses with publicly available contact information, compare business supply with similar cities, and identify potentially underserved industries.

## Features

- **City Selection**: Choose any country and city worldwide
- **Business Discovery**: Find actual businesses by category using open data sources
- **Contact Enrichment**: Extract emails, phones, and social profiles from official websites
- **Market Analysis**: Calculate businesses per capita, supply gaps, and opportunity scores
- **Peer City Comparison**: Compare your city against similar cities
- **Opportunity Discovery**: Automatically find underserved business categories
- **Export**: Download business data as CSV or JSON

## Data Sources (No Paid APIs Required)

- **Overture Maps Places**: Primary global POI source
- **OpenStreetMap**: Secondary verification and additional details
- **Official Business Websites**: Contact information extraction
- **Open Population/Boundary Datasets**: Demographics and boundaries

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Web UI    │────▶│  FastAPI    │────▶│ PostgreSQL  │
│  (Next.js)  │◀────│   Backend   │◀────│   +PostGIS  │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Workers   │
                    │  (Crawler)  │
                    └─────────────┘
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd business-gap-finder

# Copy environment configuration
cp .env.example .env

# Start all services
docker compose up --build
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **Adminer (Database UI)**: http://localhost:8080

## Project Structure

```
business-gap-finder/
├── apps/
│   ├── web/              # Next.js frontend
│   └── api/              # FastAPI backend
├── workers/
│   ├── geo-worker/       # Geographic data processing
│   └── crawler-worker/   # Website crawling & enrichment
├── packages/
│   ├── shared/           # Shared utilities
│   └── taxonomy/         # Business category taxonomy
├── infrastructure/       # Database migrations, scripts
├── docker/               # Docker configurations
├── docker-compose.yml
├── .env.example
└── README.md
```

## Usage

### Analyze a Market

1. Select a country (e.g., Georgia)
2. Select a city (e.g., Tbilisi)
3. Choose an industry (e.g., Pet Grooming)
4. Click "Analyze Market"

The application will:
- Resolve the city boundary
- Query Overture Maps for businesses
- Cross-check with OpenStreetMap
- Deduplicate and normalize records
- Display businesses on a map
- Calculate market statistics

### Discover Opportunities

1. Select a country and city
2. Click "Find Opportunities"

The system will automatically analyze multiple categories and identify underserved markets.

### Export Data

Filter businesses by contact availability and export to CSV or JSON.

## Configuration

See `.env.example` for available configuration options:

```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/business_gap_finder

# Application
NEXT_PUBLIC_API_URL=http://localhost:8000/api

# Crawler Settings
CRAWLER_MAX_CONCURRENCY=10
CRAWLER_TIMEOUT=30
```

## API Endpoints

- `GET /api/countries` - List countries
- `GET /api/cities/search?q=<query>` - Search cities
- `GET /api/categories` - List business categories
- `POST /api/cities/resolve` - Resolve city details
- `POST /api/cities/{id}/snapshot` - Create city snapshot
- `POST /api/markets/analyze` - Analyze market
- `POST /api/opportunities/discover` - Discover opportunities
- `GET /api/businesses` - List businesses
- `GET /api/exports/{analysisId}` - Export results

## Development

### Frontend

```bash
cd apps/web
npm install
npm run dev
```

### Backend

```bash
cd apps/api
pip install -r requirements.txt
uvicorn main:app --reload
```

### Running Tests

```bash
# Backend tests
cd apps/api
pytest

# Frontend tests
cd apps/web
npm test
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

---

Built with open data and open source technologies. No paid APIs required for core functionality.
