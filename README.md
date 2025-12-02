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

### 🎓 Education Features (NEW)
Bioworld serves as a legitimate teaching aid, enabling science teachers to hold interactive classes in-game:

- **Virtual Classrooms** - Teachers can create classrooms with unique join codes
- **Interactive Science Demonstrations** - Visual simulations of:
  - 🔥 **Combustion reactions** with different fuels (methane, propane, hydrogen)
  - ⚗️ **Chemical reactions** and molecular structures
  - 🧬 **Cell division** (mitosis/meiosis) and DNA replication
  - ⚡ **Physics phenomena** (waves, particles, electromagnetic spectrum)
- **Lesson Builder** - Create structured lessons with objectives and demonstrations
- **Student Progress Tracking** - Monitor student completion and scores
- **Learning Center** - Students can explore and research independently

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

#### Education API Endpoints
- `/api/classrooms` - Create and manage virtual classrooms
- `/api/classrooms/join` - Join a classroom with a class code
- `/api/lessons` - Create and retrieve lessons
- `/api/lessons/<id>/progress` - Update student lesson progress
- `/api/students/<id>/progress` - Get student learning progress
- `/api/demonstrations` - Browse interactive science demonstrations
- `/api/demonstrations/<id>/simulate` - Run a science demonstration simulation

See [docs/API.md](docs/API.md) for full documentation.

## Technology

- **Game Engine**: Unreal Engine 5.x (Lumen, Nanite, PCG)
- **Backend**: Python Flask API with SQLite
- **AI Models**: AlphaFold-inspired, RF Diffusion-inspired (simulated)
- **Economics**: Game Theory, RL Trading, API Marketplace

## Contributing

Want to help build Bioworld? Check out our **[Contributing Guide](CONTRIBUTING.md)** with a skills-based update sheet to find where your abilities apply. Whether you're a programmer, artist, designer, or writer—there's a place for you!

We encourage creativity and welcome forks. Use Bioworld as a foundation to pivot into your own games.

## Documentation

- [**Contributing Guide**](CONTRIBUTING.md) - Skills update sheet and how to contribute
- [**Build Guide**](docs/BUILD_GUIDE.md) - Unreal Engine implementation guide with checklists
- [Architecture Overview](docs/ARCHITECTURE.md)
- [API Documentation](docs/API.md)
- [Research Companion Spec](Bioworld_Research_Companion_Spec_v1.md)
- [Ultimate Playbook](Bioworld_Ultimate_Playbook_v1.md)

## Unreal Engine Build Overview

The game is built using Unreal Engine 5.x with the following key systems:

| System | UE5 Feature | Purpose |
|--------|-------------|---------|
| Protein Folding | C++ Components + Data Tables | AI-driven structure prediction |
| Corporations | Component Hierarchy | Player organization holarchy |
| World Generation | PCG Framework + Nanite | Vast procedural landscapes |
| Economy | Replicated Actors | Multiplayer market sync |
| Visuals | Lumen + Niagara | Dynamic lighting and effects |

See [docs/BUILD_GUIDE.md](docs/BUILD_GUIDE.md) for detailed implementation instructions and build checklists.

## License

MIT/Apache-2.0 dual license. Open source, open development.
