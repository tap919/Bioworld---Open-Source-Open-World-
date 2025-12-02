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

### Phase 3: NPCs and World Interaction
- NPCs (Randomized Fair Rewards)
- Bartering System
- Base Elements
- Tools
- Craftable Items (Jetpacks, Vehicles, Shelters)
- Shelters and Camps
- Disease Research Progress
- Loot Tables

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

---

## Phase 3: NPCs and World Interaction

### NPCs (Randomized but Mathematically Fair Rewards)

NPCs provide help, aid, information, tools, special files, NFTs, and coins through a mathematically balanced randomization system.

#### GET /api/npcs

List all NPCs with optional filtering.

**Query Parameters**
- `type` - Filter by NPC type (helper, merchant, information_giver, tool_giver, quest_giver, trainer, banker, researcher)
- `role` - Filter by role (aid, trade, information, tools, special_files, nfts, coins, crafting, research)
- `zone` - Filter by location zone

**Response**

```json
{
    "npcs": [
        {
            "id": "npc-abc123",
            "name": "Dr. Research Helper",
            "npc_type": "helper",
            "role": "aid",
            "location_zone": "lab_district",
            "description": "A helpful research assistant",
            "specialization": "protein_research",
            "rarity": "rare",
            "interaction_count": 42,
            "created_at": "2025-01-01 00:00:00"
        }
    ]
}
```

#### POST /api/npcs

Create a new NPC.

**Request Body**

```json
{
    "name": "Dr. Research Helper",
    "npc_type": "helper",
    "role": "aid",
    "location_zone": "lab_district",
    "description": "A helpful research assistant",
    "specialization": "protein_research",
    "rarity": "rare",
    "loot_table_id": "loot-abc123"
}
```

**Valid NPC Types:** helper, merchant, information_giver, tool_giver, quest_giver, trainer, banker, researcher

**Valid Roles:** aid, trade, information, tools, special_files, nfts, coins, crafting, research

**Valid Rarities:** common, uncommon, rare, epic, legendary

#### POST /api/npcs/:npc_id/interact

Interact with an NPC to receive randomized but fair rewards.

**Request Body**

```json
{
    "player_id": "player-001",
    "player_level": 5,
    "player_luck": 1.2
}
```

**Response**

```json
{
    "interaction_id": "int-xyz789",
    "npc": {
        "id": "npc-abc123",
        "name": "Dr. Research Helper",
        "type": "helper",
        "role": "aid"
    },
    "reward": {
        "type": "aid",
        "amount": 61.17,
        "item": "protection_buff",
        "item_id": "aid-86a1c8f4",
        "rarity": "rare"
    },
    "message": "Dr. Research Helper provides you with protection_buff. 'Use this wisely, researcher.'"
}
```

---

### Bartering System

Player-to-player and player-to-NPC trading through the bartering system.

#### POST /api/barter/create

Create a new barter transaction.

**Request Body**

```json
{
    "initiator_id": "player-001",
    "recipient_id": "player-002",
    "offered_items": [
        {"item_id": "elem-001", "quantity": 5}
    ],
    "requested_items": [
        {"item_id": "tool-001", "quantity": 1}
    ]
}
```

#### POST /api/barter/:barter_id/accept

Accept a pending barter transaction.

#### POST /api/barter/:barter_id/decline

Decline a pending barter transaction.

#### GET /api/barter

Get barter transactions for a player.

**Query Parameters**
- `player_id` - Filter by player
- `status` - Filter by status (pending, completed, declined)

---

### Base Elements

Building blocks for crafting and research.

#### GET /api/elements

Get all base elements.

**Response**

```json
{
    "elements": [
        {
            "id": "elem-abc123",
            "name": "Bio Carbon",
            "element_type": "organic",
            "rarity": "common",
            "description": "Basic organic building block",
            "properties": {"conductivity": 0.5},
            "research_contribution": 0.5
        }
    ]
}
```

#### POST /api/elements

Create a new base element.

**Request Body**

```json
{
    "name": "Bio Carbon",
    "element_type": "organic",
    "rarity": "common",
    "description": "Basic organic building block",
    "properties": {"conductivity": 0.5},
    "research_contribution": 0.5
}
```

**Valid Element Types:** organic, inorganic, synthetic, biological, energy, catalyst, compound

---

### Tools

Tools required for crafting advanced items.

#### GET /api/tools

Get all available tools.

**Response**

```json
{
    "tools": [
        {
            "id": "tool-abc123",
            "name": "Molecular Assembler",
            "tool_type": "crafting",
            "tier": 2,
            "description": "Advanced crafting tool",
            "required_elements": ["Bio Carbon", "Energy Cell"],
            "craft_time_seconds": 120,
            "durability": 100
        }
    ]
}
```

#### POST /api/tools

Create a new tool definition.

**Request Body**

```json
{
    "name": "Molecular Assembler",
    "tool_type": "crafting",
    "tier": 2,
    "description": "Advanced crafting tool",
    "required_elements": ["Bio Carbon", "Energy Cell"],
    "craft_time_seconds": 120,
    "durability": 100
}
```

**Valid Tool Types:** harvesting, crafting, research, construction, transport, defense, utility

---

### Craftable Items

Advanced items including jetpacks, vehicles, shelters, and equipment.

#### GET /api/craftables

Get all craftable items with optional category filter.

**Query Parameters**
- `category` - Filter by category (transport, shelter, equipment, weapon, utility, research)

**Response**

```json
{
    "craftables": [
        {
            "id": "craft-abc123",
            "name": "Basic Jetpack",
            "item_type": "jetpack",
            "category": "transport",
            "description": "A basic jetpack for short flights",
            "required_tools": ["Molecular Assembler"],
            "required_elements": ["Bio Carbon", "Energy Cell", "Propulsion Core"],
            "craft_time_seconds": 600,
            "effects": {"flight_duration": 30, "max_altitude": 100},
            "research_bonus": 0.15
        }
    ]
}
```

#### POST /api/craftables

Create a new craftable item definition.

**Request Body**

```json
{
    "name": "Basic Jetpack",
    "item_type": "jetpack",
    "category": "transport",
    "description": "A basic jetpack for short flights",
    "required_tools": ["Molecular Assembler"],
    "required_elements": ["Bio Carbon", "Energy Cell", "Propulsion Core"],
    "craft_time_seconds": 600,
    "effects": {"flight_duration": 30, "max_altitude": 100},
    "research_bonus": 0.15
}
```

**Valid Categories:** transport, shelter, equipment, weapon, utility, research

**Valid Item Types:** jetpack, flight_suit, car, motorcycle, boat, shelter, camp, outpost, lab_extension, armor, scanner, communicator, container

#### POST /api/craft

Craft an item using collected tools and elements.

**Request Body**

```json
{
    "player_id": "player-001",
    "craftable_id": "craft-abc123"
}
```

**Response**

```json
{
    "message": "Item crafted successfully",
    "player_item_id": "pitem-xyz789",
    "item": {
        "id": "craft-abc123",
        "name": "Basic Jetpack",
        "category": "transport",
        "effects": {"flight_duration": 30, "max_altitude": 100}
    },
    "craft_time_seconds": 600,
    "research_bonus": 0.15
}
```

---

### Shelters and Camps

Player-built structures providing research bonuses and storage.

#### GET /api/shelters

Get player shelters.

**Query Parameters**
- `player_id` - Filter by player

**Response**

```json
{
    "shelters": [
        {
            "id": "shelter-abc123",
            "player_id": "player-001",
            "name": "Research Outpost Alpha",
            "shelter_type": "research_station",
            "location": {"x": 100.0, "y": 200.0, "z": 50.0},
            "capacity": 4,
            "research_bonus": 0.3,
            "upgrades": [],
            "created_at": "2025-01-01 00:00:00"
        }
    ]
}
```

#### POST /api/shelters

Create a new shelter or camp.

**Request Body**

```json
{
    "player_id": "player-001",
    "name": "Research Outpost Alpha",
    "shelter_type": "research_station",
    "location": {"x": 100.0, "y": 200.0, "z": 50.0},
    "capacity": 6,
    "upgrades": []
}
```

**Valid Shelter Types:** tent, cabin, outpost, research_station, mobile_lab, underground_bunker, treehouse, floating_platform

**Research Bonuses by Type:**
- tent: 0.05
- cabin: 0.10
- outpost: 0.15
- research_station: 0.30
- mobile_lab: 0.25
- underground_bunker: 0.20
- treehouse: 0.10
- floating_platform: 0.15

---

### Disease Research Progress

Track player contributions to disease research with unique build bonuses.

#### GET /api/research-progress

Get disease research progress.

**Query Parameters**
- `disease_id` - Filter by disease
- `player_id` - Filter by player

**Response**

```json
{
    "progress": [
        {
            "id": "prog-abc123",
            "disease_id": "disease-001",
            "player_id": "player-001",
            "contribution_amount": 10.0,
            "contribution_type": "standard",
            "unique_build_bonus": 9.2,
            "created_at": "2025-01-01 00:00:00"
        }
    ],
    "total_contribution": 19.2
}
```

#### POST /api/research-progress

Add a research contribution with optional unique build bonus.

**Request Body**

```json
{
    "disease_id": "disease-001",
    "player_id": "player-001",
    "contribution_amount": 10.0,
    "contribution_type": "standard",
    "elements_used": ["organic", "catalyst", "biological"]
}
```

**Unique Build Bonus System:**

Creative combinations of base elements provide research bonuses:
- Using multiple elements provides base bonus (0.5 per element)
- Synergy combinations provide additional bonuses:
  - organic + catalyst: +2.0
  - biological + synthetic: +3.0
  - energy + compound: +2.5
  - organic + biological + catalyst: +5.0
  - synthetic + energy + compound: +4.0

---

### Loot Tables

Configure mathematically fair reward distributions.

#### GET /api/loot-tables

Get all loot tables.

**Response**

```json
{
    "loot_tables": [
        {
            "id": "loot-abc123",
            "name": "NPC Reward Table",
            "description": "Standard reward distribution",
            "entries": [
                {"item": "coins", "item_type": "currency", "weight": 50, "rarity": "common", "min_amount": 1, "max_amount": 10},
                {"item": "basic_tool", "item_type": "tool", "weight": 30, "rarity": "uncommon", "min_amount": 1, "max_amount": 1},
                {"item": "rare_element", "item_type": "element", "weight": 15, "rarity": "rare", "min_amount": 1, "max_amount": 3},
                {"item": "legendary_nft", "item_type": "nft", "weight": 5, "rarity": "legendary", "min_amount": 1, "max_amount": 1}
            ],
            "total_weight": 100,
            "created_at": "2025-01-01 00:00:00"
        }
    ]
}
```

#### POST /api/loot-tables

Create a new loot table.

**Request Body**

```json
{
    "name": "NPC Reward Table",
    "description": "Standard reward distribution",
    "entries": [
        {"item": "coins", "item_type": "currency", "weight": 50, "rarity": "common", "min_amount": 1, "max_amount": 10},
        {"item": "basic_tool", "item_type": "tool", "weight": 30, "rarity": "uncommon", "min_amount": 1, "max_amount": 1},
        {"item": "rare_element", "item_type": "element", "weight": 15, "rarity": "rare", "min_amount": 1, "max_amount": 3},
        {"item": "legendary_nft", "item_type": "nft", "weight": 5, "rarity": "legendary", "min_amount": 1, "max_amount": 1}
    ]
}
```

#### POST /api/loot-tables/:table_id/roll

Roll on a loot table to get a random but fair reward.

**Request Body**

```json
{
    "player_luck": 1.5
}
```

**Response**

```json
{
    "loot_table_id": "loot-abc123",
    "result": {
        "item": "rare_element",
        "item_type": "element",
        "rarity": "rare",
        "amount": 2
    },
    "message": "You received 2x rare_element (rare)"
}
```

---

## Mathematical Fairness System

The NPC reward system uses mathematically fair algorithms to ensure game balance:

### Weighted Random Selection
- Each item has a weight determining its probability
- Total weight is calculated as sum of all entry weights
- Selection probability = item_weight / total_weight

### Player Luck Modifier
- Base luck is 1.0
- Luck values above 1.0 increase the effective weight of rare+ items (capped at 2x)
- Luck has diminishing returns to prevent exploitation

### Reward Calculation Formula
```
base_reward = base_value × rarity_multiplier
variance = random(0.8, 1.2)
level_bonus = log(player_level + 1) × 0.5
final_reward = base_reward × variance × (1 + level_bonus)
```

### Rarity Multipliers
| Rarity | Multiplier |
|--------|------------|
| Common | 1.0× |
| Uncommon | 1.5× |
| Rare | 2.5× |
| Epic | 4.0× |
| Legendary | 7.5× |
