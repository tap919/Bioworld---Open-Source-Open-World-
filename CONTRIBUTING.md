# Contributing to Bioworld

Welcome to the Bioworld open-source project! This is a collaborative MMORPG where biotechnology meets economic strategy. We encourage contributions from developers, artists, designers, and creative minds of all skill levels.

## 🎯 Skills Update Sheet

Find where your skills apply and how you can contribute:

### Programming

| Skill Level | Areas to Contribute | Files/Systems |
|-------------|---------------------|---------------|
| **Beginner** | Bug fixes, documentation, simple API endpoints | `website/app.py`, `docs/` |
| **Intermediate** | Flask API features, database schema, game logic | `website/`, API endpoints |
| **Advanced** | Unreal Engine C++, AI model integration, networking | Core game systems (see BUILD_GUIDE.md) |
| **Expert** | Distributed systems, security, blockchain/Biocoin | `BiocoinCore`, `SecurityCore` |

**Tech Stack:**
- Python (Flask) - Backend API
- Unreal Engine 5.x (C++/Blueprints) - Game client
- SQLite (dev) / Distributed DB (prod) - Data storage
- HTML5/CSS3/JavaScript - Web frontend

### Game Design

| Skill Level | Areas to Contribute | Resources |
|-------------|---------------------|-----------|
| **Beginner** | Balance suggestions, playtesting feedback | `game_design.csv` |
| **Intermediate** | Economy balancing, progression curves, mechanic design | `Bioworld_Ultimate_Playbook_v1.md` |
| **Advanced** | Core loop design, system interactions, holarchy architecture | `Bioworld_Concept_OnePager.md` |
| **Expert** | Game theory, RL trading algorithms, emergent systems | `docs/BUILD_GUIDE.md` |

**Design Philosophy:** Systems over scripts, player authorship, readable complexity.

### Art & Visual Design

| Skill Level | Areas to Contribute | Files/Systems |
|-------------|---------------------|---------------|
| **Beginner** | UI mockups, color palette suggestions | `ui_wireframe_*.png` |
| **Intermediate** | 2D UI assets, icons, marketing materials | `website/static/` |
| **Advanced** | 3D models, materials, environment art | `Env_*.json`, `Cloth_*.json` |
| **Expert** | Procedural generation, shaders, VFX | `VFX_Phenomena_A.json`, Niagara systems |

**Art Style:** Near-future sci-fi manga, photoreal with subtle shadow, dark theme with neon accents.

### Audio

| Skill Level | Areas to Contribute | Files |
|-------------|---------------------|-------|
| **Beginner** | Sound effect suggestions, audio feedback | |
| **Intermediate** | UI sounds, ambient audio | `click.wav`, `footstep.wav` |
| **Advanced** | Explosion effects, environmental audio | `explosion.wav` |
| **Expert** | Interactive music system, adaptive soundscapes | Music stems, state transitions |

### Writing & Documentation

| Skill Level | Areas to Contribute | Files |
|-------------|---------------------|-------|
| **Beginner** | Typo fixes, README improvements | `README.md`, `docs/` |
| **Intermediate** | API documentation, tutorials | `docs/API.md` |
| **Advanced** | Lore writing, in-game narrative | `Bioworld_Research_Companion_Spec_v1.md` |
| **Expert** | Technical specs, architecture docs | `docs/ARCHITECTURE.md` |

### Community & Outreach

| Area | How to Help |
|------|-------------|
| **Testing** | Playtest and report bugs |
| **Translation** | Localize documentation and UI |
| **Streaming** | Create content, tutorials |
| **Community** | Answer questions, welcome newcomers |

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
# Clone the main repository (or your fork)
git clone https://github.com/tap919/Bioworld---Open-Source-Open-World-.git
cd Bioworld---Open-Source-Open-World-
```

### 2. Set Up the Web API (Quick Start)

```bash
cd website
pip install -r requirements.txt
flask init-db
python app.py
```

Visit `http://localhost:5000` to see the website.

### 3. Choose Your First Task

1. **Check the Skills Update Sheet** above to find where your skills apply
2. **Look at open issues** for "good first issue" labels
3. **Read relevant documentation** in `docs/`
4. **Start small** - fix a typo, add a comment, improve docs

---

## 🎨 Room for Creativity

Bioworld is designed to be **remixable and extensible**. Here's how you can pivot into your own creations:

### Build Your Own Game

- **Fork the repo** and create your own variant
- **Use our systems** as a foundation for your game idea
- **Share Blueprint Codes** that work across forks
- **Keep or modify** the MIT/Apache-2.0 license

### Experiment Freely

| What You Can Do | How |
|-----------------|-----|
| Create new game modes | Modify core loop in `game_design.csv` |
| Design new biomes | Add entries to `Env_*.json` files |
| Invent new mechanics | Extend the API or game systems |
| Build standalone tools | Use the Research Companion spec |
| Make educational content | Create courses using the API |

### Community Forks Welcome

- Alternative art styles
- Different themes (fantasy, historical, space)
- Educational variants
- Single-player focused versions
- Mobile adaptations

---

## 📋 Current Project Status

### Phase 1: Biotechnology Loop (Active)
- [x] Protein folding API
- [x] Generative protein design
- [x] Wet lab validation
- [ ] Multi-omics integration
- [ ] AI model improvements

### Phase 2: Corporation & Economy (In Progress)
- [x] Corporation creation
- [x] Player API marketplace
- [x] Market trading system
- [ ] Biocoin implementation
- [ ] Governance voting

### Phase 3: World & Multiplayer (Planned)
- [ ] World partition system
- [ ] Procedural generation
- [ ] Multiplayer sync
- [ ] Mech challenges

---

## 🛠️ How to Contribute

### 1. Find an Issue

- Browse open issues on the GitHub repository
- Look for "good first issue", "help wanted" labels
- Or propose a new feature

### 2. Fork and Branch

```bash
git checkout -b feature/your-feature-name
```

### 3. Make Your Changes

- Follow existing code style
- Add tests if applicable
- Update documentation

### 4. Submit a Pull Request

- Describe what you changed and why
- Reference any related issues
- Be open to feedback

---

## 📚 Key Resources

| Resource | Description |
|----------|-------------|
| [README.md](README.md) | Project overview |
| [BUILD_GUIDE.md](docs/BUILD_GUIDE.md) | Unreal Engine implementation guide |
| [API.md](docs/API.md) | REST API documentation |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture |
| [Concept OnePager](Bioworld_Concept_OnePager.md) | Design vision |
| [Ultimate Playbook](Bioworld_Ultimate_Playbook_v1.md) | Detailed game design |

---

## 🤝 Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Give constructive feedback
- Collaborate, don't compete

---

## 📜 License

This project is dual-licensed under MIT and Apache-2.0. You are free to use, modify, and distribute the code. See the LICENSE file for details.

---

## 💡 Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions or ideas
- Check existing docs before asking

Thank you for contributing to Bioworld! 🧬🎮
