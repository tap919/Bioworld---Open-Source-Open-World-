# Bioworld API Documentation

This document provides detailed documentation for the Bioworld MMORPG REST API.

## Base URL

Development: `http://localhost:5000/api`

## Authentication

Currently, the API operates without authentication for development purposes. 
Production deployments should implement appropriate authentication mechanisms.

## Endpoints Overview

### Core Endpoints
- Health Check
- Research Packets
- Simulation Adapters

### Phase 1: Biotechnology
- Protein Folding
- Protein Design
- Wet Lab Validation

### Phase 2: Economy
- Corporations
- Player APIs
- Market Orders
- Courses

---

## Health Check

### GET /api/health

Check the health status of the API.

**Response**

```json
{
    "status": "healthy",
    "timestamp": "2025-01-01T00:00:00.000000",
    "version": "1.0.0"
}
```

---

## Research Packets

Research packets are shareable bundles of research data, simulations, and results.

### GET /api/research-packets

List all research packets.

### POST /api/research-packets

Create a new research packet.

**Request Body**

```json
{
    "id": "packet-123",
    "title": "Protein Folding Analysis",
    "authors": "Research Team",
    "license": "MIT",
    "game_version": "0.1.0",
    "seed": "weekly-seed-001",
    "tags": ["protein", "simulation"]
}
```

### GET /api/research-packets/:packet_id

Get a specific research packet by ID.

---

## Protein Folding (Phase 1)

### GET /api/proteins

List all discovered proteins.

**Response**

```json
{
    "proteins": [
        {
            "id": "prot-abc123",
            "name": "MyProtein-001",
            "amino_acid_sequence": "MVLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHFDLSH",
            "predicted_structure": {...},
            "confidence_score": 0.92,
            "player_id": "player-001",
            "validation_status": "validated",
            "created_at": "2025-01-01 00:00:00"
        }
    ]
}
```

### POST /api/proteins

Submit an amino acid sequence for structure prediction using AlphaFold-inspired AI.

**Request Body**

```json
{
    "name": "MyProtein-001",
    "amino_acid_sequence": "MVLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHFDLSH",
    "player_id": "player-001"
}
```

**Response (201 Created)**

```json
{
    "message": "Protein structure predicted",
    "id": "prot-abc123",
    "confidence_score": 0.92,
    "validation_required": false
}
```

### POST /api/proteins/:protein_id/validate

Submit wet lab validation for a protein prediction.

**Response**

```json
{
    "protein_id": "prot-abc123",
    "validation_result": "success",
    "status": "validated",
    "message": "Wet lab validation completed"
}
```

### POST /api/proteins/design

Design a new protein using generative AI (RF Diffusion-inspired).

**Request Body**

```json
{
    "purpose": "antibody targeting cancer",
    "constraints": {
        "length": 200
    }
}
```

**Response**

```json
{
    "id": "designed-xyz789",
    "purpose": "antibody targeting cancer",
    "designed_sequence": "MKFLILLFNILCLFPVLAA...",
    "sequence_length": 200,
    "design_model": "bioworld-diffusion-v1",
    "estimated_stability": 0.85,
    "suggested_applications": [
        "Therapeutic targeting",
        "Diagnostic markers",
        "Immune modulation"
    ]
}
```

---

## Corporations (Phase 2)

### GET /api/corporations

List all player corporations.

**Response**

```json
{
    "corporations": [
        {
            "id": "corp-abc123",
            "name": "Isomorphic Labs Inc",
            "owner_id": "player-001",
            "description": "Leading biotech research corporation",
            "treasury": 50000.0,
            "reputation": 250,
            "specialization": "protein_design",
            "created_at": "2025-01-01 00:00:00"
        }
    ]
}
```

### POST /api/corporations

Create a new player corporation.

**Request Body**

```json
{
    "name": "Isomorphic Labs Inc",
    "owner_id": "player-001",
    "description": "Leading biotech research corporation",
    "specialization": "protein_design"
}
```

---

## Player APIs (Learn, Do, Teach Model)

### GET /api/player-apis

List all exposed player APIs.

### POST /api/player-apis

Create and expose a new player API.

**Request Body**

```json
{
    "name": "Cancer Marker Predictor",
    "owner_id": "player-001",
    "corporation_id": "corp-abc123",
    "endpoint_type": "genetic_marker",
    "description": "Predicts genetic markers for various cancers",
    "price_per_call": 5.0
}
```

**Supported Endpoint Types:**
- `drug_efficacy` - Predict drug effectiveness
- `genetic_marker` - Identify genetic markers
- `protein_prediction` - Protein structure analysis
- `market_analysis` - Trading recommendations
- `custom` - Custom analysis

### POST /api/player-apis/:api_id/call

Call a player-exposed API (charges caller, credits owner).

**Request Body**

```json
{
    "input": {
        "patient_data": {...}
    }
}
```

**Response**

```json
{
    "api_id": "api-xyz789",
    "endpoint_type": "genetic_marker",
    "cost": 5.0,
    "result": {
        "markers_found": 3,
        "risk_assessment": "moderate",
        "recommended_tests": ["Panel A", "Sequence B"]
    }
}
```

---

## Market Orders (Trading System)

### GET /api/market/orders

Get all open market orders.

### POST /api/market/orders

Create a new market order (buy/sell).

**Request Body**

```json
{
    "order_type": "sell",
    "asset_type": "protein",
    "asset_id": "prot-abc123",
    "player_id": "player-001",
    "price": 1000.0,
    "quantity": 1
}
```

---

## Courses (Teaching Model)

### GET /api/courses

List all available courses.

### POST /api/courses

Create a new course.

**Request Body**

```json
{
    "title": "Introduction to Protein Folding",
    "instructor_id": "player-001",
    "corporation_id": "corp-abc123",
    "topic": "protein_folding",
    "price": 50.0,
    "content": {
        "modules": [...]
    }
}
```

### POST /api/courses/:course_id/enroll

Enroll in a course.

---

## Error Handling

All error responses follow this format:

```json
{
    "error": "Error message description"
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid input |
| 404 | Not Found - Resource doesn't exist |
| 409 | Conflict - Resource already exists |
| 500 | Internal Server Error |

---

## Community Spaces (Creative Building)

Community spaces allow players to collaboratively build and develop the ecosystem.

### GET /api/community-spaces

List all available community space presets.

**Response**

```json
{
    "spaces": [
        {
            "preset_id": "Env_School_A",
            "category": "community_space",
            "description": "Educational facility for player collaboration and learning",
            "max_occupancy": 100,
            "features": ["teaching_enabled", "collaborative"]
        }
    ]
}
```

### GET /api/community-spaces/:preset_id

Get details of a specific community space preset.

**Response**

```json
{
    "preset_id": "Env_School_A",
    "category": "community_space",
    "description": "Educational facility for player collaboration and learning",
    "budgets": {
        "tri_max": 6000000,
        "draw_calls_max": 1200,
        "tex_pool_mb": 900
    },
    "features": {
        "player_buildable": true,
        "collaborative": true,
        "teaching_enabled": true,
        "max_occupancy": 100
    }
}
```

### POST /api/community-spaces/place

Place a community space in the world.

**Request Body**

```json
{
    "preset_id": "Env_School_A",
    "player_id": "player-001",
    "location": {
        "x": 1000.0,
        "y": 2000.0,
        "z": 0.0
    },
    "rotation": 0.0
}
```

**Response (201 Created)**

```json
{
    "message": "Community space placed",
    "placement_id": "place-abc123",
    "preset_id": "Env_School_A",
    "owner_id": "player-001"
}
```

---

## Blueprints (Build Sharing)

Save and share player-created builds.

### GET /api/blueprints

List all public blueprints.

**Response**

```json
{
    "blueprints": [
        {
            "id": "bp-xyz789",
            "code": "BW-a1b2c3d4e5f6",
            "name": "Community Hub Alpha",
            "creator_id": "player-001",
            "category": "community_space",
            "downloads": 150,
            "created_at": "2025-01-01 00:00:00"
        }
    ]
}
```

### POST /api/blueprints

Create and save a new blueprint.

**Request Body**

```json
{
    "name": "My Awesome Build",
    "creator_id": "player-001",
    "category": "community_space",
    "build_data": {
        "assets": [...],
        "connections": [...]
    },
    "public": true
}
```

**Response (201 Created)**

```json
{
    "message": "Blueprint saved",
    "id": "bp-xyz789",
    "code": "BW-a1b2c3d4e5f6"
}
```

### GET /api/blueprints/:code

Get a blueprint by its share code.

**Response**

```json
{
    "id": "bp-xyz789",
    "code": "BW-a1b2c3d4e5f6",
    "name": "Community Hub Alpha",
    "creator_id": "player-001",
    "build_data": {...}
}
```

---

## Creative Building Elements

### GET /api/building-elements

List all creative building element presets (plants, trees, roads, lights).

**Response**

```json
{
    "elements": [
        {
            "preset_id": "Foliage_RealPlants_A",
            "category": "creative_building",
            "description": "Collection of real-world inspired plants",
            "item_count": 8
        },
        {
            "preset_id": "Foliage_RealTrees_A",
            "category": "creative_building",
            "description": "Collection of real-world inspired trees",
            "item_count": 8
        },
        {
            "preset_id": "Build_RoadBuilder_A",
            "category": "creative_building",
            "description": "Road construction toolkit",
            "item_count": 8
        },
        {
            "preset_id": "Build_LightFixtures_A",
            "category": "creative_building",
            "description": "Lighting toolkit",
            "item_count": 10
        }
    ]
}
```

### GET /api/building-elements/:preset_id

Get details of a specific building element preset.

---

## Rate Limiting

Not implemented in development. Production deployments should implement 
appropriate rate limiting.

---

## Versioning

The API is currently at version 1.0.0. Version information is included in 
the health check response.
