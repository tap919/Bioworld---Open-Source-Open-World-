# Bioworld Website Infrastructure

This document describes the website and API infrastructure for the Bioworld open-source MMORPG ecosystem.

## Overview

The Bioworld website provides:
- Public-facing landing page for the MMORPG
- Research Lab interface for protein folding and design
- REST API for game client communication
- Phase 1: Biotechnology loop (protein prediction, design, validation)
- Phase 2: Corporation economy (player APIs, market trading, courses)

## The Core Model: Learn, Do, Teach

Bioworld follows the "learn the thing, do the thing, teach the thing" pattern:
1. **Learn** - Master AI tools, understand protein structures
2. **Do** - Predict protein folds, design therapeutics, run simulations
3. **Teach** - Create courses, expose APIs, build educational content

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend Layer                          │
│                  (HTML5, CSS3, JavaScript)                   │
├─────────────────────────────────────────────────────────────┤
│                       API Layer                              │
│              (Flask REST API + Player APIs)                  │
├─────────────────────────────────────────────────────────────┤
│                     Game Logic                               │
│       (AI Models, Market Engine, Corporation System)         │
├─────────────────────────────────────────────────────────────┤
│                   Distributed Backend                        │
│            (SQLite Dev → Distributed DB Prod)                │
├─────────────────────────────────────────────────────────────┤
│                     Game Engine                              │
│           (Unreal Engine 5.x - Lumen, Nanite, PCG)           │
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Frontend
- **HTML5** - Semantic markup for accessibility
- **CSS3** - Modern styling with CSS variables, dark theme, neon accents
- **JavaScript** - Vanilla ES6+ for interactivity

### Backend
- **Python 3.x** - Server-side programming
- **Flask** - Web framework for routing and API
- **SQLite** - Embedded database (development), distributed-ready

### AI Models (Simulated)
- **Bioworld-Fold-v1** - AlphaFold-inspired protein structure prediction
- **Bioworld-Diffusion-v1** - RF Diffusion-inspired protein design

### Design System
- Near-future, sci-fi manga aesthetic
- Dark theme with neon accents
- Photoreal with subtle shadow for dystopian vibe

## Directory Structure

```
website/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── static/
│   ├── css/
│   │   └── style.css      # Main stylesheet
│   └── js/
│       ├── main.js        # Core JavaScript
│       └── research.js    # Research page (protein folding)
└── templates/
    ├── index.html         # Landing page
    ├── research.html      # Research Lab
    └── about.html         # About page
```

## Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

```bash
cd website
pip install -r requirements.txt
```

### Initialize Database

```bash
flask init-db
```

### Run Development Server

```bash
python app.py
```

The website will be available at `http://localhost:5000`

## API Endpoints

See [API.md](API.md) for complete API documentation.

### Phase 1: Biotechnology
- `POST /api/proteins` - Predict protein structure from sequence
- `POST /api/proteins/design` - Design new proteins for specific purposes
- `POST /api/proteins/:id/validate` - Wet lab validation

### Phase 2: Economy
- `POST /api/corporations` - Create player corporations
- `POST /api/player-apis` - Expose models as paid APIs
- `POST /api/market/orders` - Create buy/sell orders
- `POST /api/courses` - Create educational courses

## Game Phases

### Phase 1: Biotechnology Loop
The initial gameplay centers around foundational biotechnology:
- **Protein Folding** - Use AlphaFold-inspired AI to predict structures
- **Generative Design** - Create novel proteins using RF Diffusion-like AI
- **Wet Lab Validation** - Validate predictions with simulated experiments
- **Multi-Omics Data** - Integrate genomics and proteomics data

### Phase 2: Corporation & Economy
The "Grand Theft" style emerges through strategic deployment:
- **Player Corporations** - Build biotech empires
- **API Marketplace** - Monetize your AI models
- **Teaching Platform** - Create courses and guides
- **Market Trading** - Trade proteins, patents, and assets

## Distributed System Design

Bioworld operates as a distributed system (holarchy):

### Scalability
- Partitioning divides workload across nodes
- "Think globally, act locally" design pattern
- Stateless API design for easy replication

### Reliability
- Data replication across nodes
- Graceful degradation on failures
- Health check monitoring

### Consensus
- Distributed consensus for coordinated state
- Blueprint code verification
- Research packet integrity checks

## Security

- CORS protection
- Input validation (amino acid sequences validated)
- SQL injection prevention via parameterized queries
- XSS protection via HTML escaping

## Development

### Code Style
- PEP 8 for Python
- ES6+ JavaScript standards

### Testing
```bash
python -c "from app import app; ..."  # Integration tests
```

## Deployment

### Production Checklist
1. Set `SECRET_KEY` environment variable
2. Use a production WSGI server (gunicorn, uWSGI)
3. Configure reverse proxy (nginx)
4. Enable HTTPS
5. Set up database backups
6. Configure distributed database

### Example Production Command
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## Contributing

See the main repository for contribution guidelines.

## License

MIT/Apache-2.0 dual license.
