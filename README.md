# Bioworld - Open Source MMORPG

An open-source MMORPG where biotechnology meets economic strategy. Learn, Do, Teach.

## Overview

Bioworld is a highly dynamic, collaborative, and competitive ecosystem where scientific discovery is directly linked to massive economic and infrastructural development. Players solve real biotechnology challenges while building corporations and monetizing their discoveries.

## Core Model: Learn, Do, Teach

The game follows a proven pattern that allows players to monetize their scientific insights:
1. **Learn** - Master AI tools, understand protein structures, study genomics
2. **Do** - Predict protein folds, design therapeutics, run simulations
3. **Teach** - Create courses, expose APIs, build educational content

## Features

### Phase 1: Biotechnology Loop
- 🧬 **Protein Folding** - AlphaFold-inspired structure prediction
- 🔬 **Generative Design** - RF Diffusion-like protein design
- 🧪 **Wet Lab Validation** - Simulated laboratory experiments
- 📊 **Multi-Omics Data** - Genomics and proteomics integration

### Phase 2: Corporation & Economy
- 🏢 **Player Corporations** - Build your biotech empire
- 📡 **API Marketplace** - Monetize your AI models
- 📚 **Teaching Platform** - Create courses and guides
- 📈 **Market Trading** - Trade proteins, patents, and assets

## Website & API

The `website/` directory contains a Flask-based web application:

```bash
cd website
pip install -r requirements.txt
python app.py
```

Visit `http://localhost:5000` for the web interface.

### API Endpoints
- `/api/health` - Health check
- `/api/proteins` - Protein folding predictions
- `/api/proteins/design` - Generative protein design
- `/api/corporations` - Player corporation management
- `/api/player-apis` - Expose models as paid APIs
- `/api/market/orders` - Market trading system
- `/api/courses` - Educational course system

See [docs/API.md](docs/API.md) for full documentation.

## Technology

- **Game Engine**: Unreal Engine 5.x (Lumen, Nanite, PCG)
- **Backend**: Python Flask API with SQLite
- **AI Models**: AlphaFold-inspired, RF Diffusion-inspired (simulated)
- **Economics**: Game Theory, RL Trading, API Marketplace

## Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [API Documentation](docs/API.md)
- [Research Companion Spec](Bioworld_Research_Companion_Spec_v1.md)
- [Ultimate Playbook](Bioworld_Ultimate_Playbook_v1.md)

## License

MIT/Apache-2.0 dual license. Open source, open development.
