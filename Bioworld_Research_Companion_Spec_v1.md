# Bioworld Research Companion (BRC) — v1 Spec
Date: 2025-09-16

## 1) Purpose
A lightweight desktop companion that lets players:
- Import research files (PDF, CSV, images), annotate, and tag.
- Run simple validations and simulations, then compare results to known references.
- Package and share **Research Packets** with the community without needing game servers.
- Coordinate via low‑overhead channels so players stay engaged while coop servers are limited.

## 2) Non‑goals (v1)
- No hosted multiplayer or dedicated servers.
- No heavy knowledge graph or ML features.
- No real‑time P2P chat. We link out to community channels.

## 3) Users
- Players who tinker with systems and want structured experiments.
- Contributors who submit data or blueprints to the OSS repo.

## 4) Core workflows (MVP)
1) **Import**: Drop files → auto OCR (for PDFs) → store text + attachments in a local SQLite vault.
2) **Annotate**: Highlight, comment, tag by topic and world seed.
3) **Validate**: Choose a rule set → run checks (dimension/unit sanity, value ranges).
4) **Simulate**: Pick a **Sim Adapter** (Python script) → run with parameters → capture outputs.
5) **Compare**: Overlay sim results vs reference curves or tables → produce a one‑page summary.
6) **Package**: Generate a signed **Research Packet** (.brc.zip) with manifest.json, checksums, and license.
7) **Share**: One‑click export to folder or create a GitHub Issue/PR draft with attachments (if online).
8) **Consume**: Import others’ packets → see summary, trust score, and reproducibility checklist.

## 5) Data model
- `research_packet/manifest.json`:
  - id, title, authors, license, game_version, seed, tags
  - inputs (files + hashes), sim_adapter id@version, parameters
  - outputs (plots, tables + hashes), validation report, summary.md
  - trust: self‑certified steps + optional reviewer signatures
- Local vault: SQLite + file store. Backups are simple folder copies.

## 6) Integrations
- **Game** (UE5): Export **Blueprint Codes**, seeds, and logs to a watched folder. BRC can import and visualize.
- **GitHub** (optional): Personal token lets BRC create issues/PRs in the Bioworld repo with packet attachments.
- **Discord/Matrix** (optional): Read‑only webhook feed panel for announcements; links open externally.

## 7) Architecture (low risk)
- **App**: Tauri + React (small footprint, cross‑platform).
- **Store**: SQLite (bundled).
- **Sandboxed runner**: Python 3.x embedded for **Sim Adapters** with a tight whitelist (numpy, pandas, matplotlib). No network, capped CPU time.
- **Plugin API**: Sim Adapters are signed zip bundles with entrypoint, `schema.json`, and tests.
- **File I/O**: All in user space. No admin rights required.

## 8) Security, privacy, compliance
- Offline by default. Network calls only for GitHub/feeds when the user enables them.
- No PII stored except user‑provided author name.
- SPDX license picker for packets.
- Checksums for every file. Refuse unsigned or mal‑formed adapters.

## 9) Success metrics (MVP)
- 70% of new players export their first Research Packet within 30 minutes.
- 50+ packets merged to repo in first month post‑launch.
- <1% adapter sandbox escapes or crashes in the wild.

## 10) Delivery plan (8 weeks)
- W1: UX wireframes, manifest schema, adapter API.
- W2: Vault + import/OCR, basic viewer.
- W3: Validation rules engine + unit tests.
- W4: Python sandbox + first Sim Adapter (resource diffusion example).
- W5: Compare/plot view + summary generator.
- W6: Packet builder + signature + verify.
- W7: GitHub export + announcement feed panel.
- W8: Hardening, docs, sample packets, release builds.

## 11) Risks → mitigations
- Adapter security → Process isolation, timeouts, and no‑network policy.
- Scope creep → Only one official adapter in v1; community adds more later.
- Cross‑platform quirks → Tauri CI for Win/Linux, smoke tests per release.

## 12) Handoff checklist
- Source repo with MIT/Apache‑2.0 license.
- `/docs` with adapter authoring guide and manifest schema.
- CI: tag builds for Win64 and Linux AppImage.
- Signed sample packets and verification script.
