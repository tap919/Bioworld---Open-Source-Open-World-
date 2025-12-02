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

## Education System

The Education System enables teachers to hold classes in-game with interactive science demonstrations.

### Classrooms

#### GET /api/classrooms

List all active classrooms.

**Response**

```json
{
    "classrooms": [
        {
            "id": "class-abc123",
            "name": "Biology 101",
            "teacher_id": "teacher-001",
            "subject": "biology",
            "description": "Introduction to Biology",
            "class_code": "ABC123",
            "max_students": 30,
            "current_students": 15,
            "is_active": true,
            "created_at": "2025-01-01 00:00:00"
        }
    ]
}
```

#### POST /api/classrooms

Create a new classroom.

**Request Body**

```json
{
    "name": "Biology 101",
    "teacher_id": "teacher-001",
    "subject": "biology",
    "description": "Introduction to Biology with interactive demonstrations",
    "max_students": 30
}
```

**Response (201 Created)**

```json
{
    "message": "Classroom created",
    "id": "class-abc123",
    "class_code": "ABC123"
}
```

#### POST /api/classrooms/join

Join a classroom using a class code.

**Request Body**

```json
{
    "class_code": "ABC123",
    "student_id": "student-001"
}
```

**Response (201 Created)**

```json
{
    "message": "Successfully joined classroom",
    "classroom_id": "class-abc123",
    "classroom_name": "Biology 101",
    "subject": "biology"
}
```

### Lessons

#### GET /api/lessons

List lessons, optionally filtered by classroom.

**Query Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| classroom_id | string | Filter lessons by classroom |

#### POST /api/lessons

Create a new lesson for a classroom.

**Request Body**

```json
{
    "classroom_id": "class-abc123",
    "title": "Introduction to Combustion",
    "subject_area": "combustion",
    "description": "Learn about the fire triangle and chemical reactions",
    "objectives": [
        "Understand the fire triangle",
        "Identify products of combustion"
    ],
    "materials": ["Safety goggles", "Lab notebook"],
    "demonstrations": ["demo-combustion-basic"],
    "estimated_duration": 45
}
```

#### POST /api/lessons/:lesson_id/progress

Update a student's progress on a lesson.

**Request Body**

```json
{
    "student_id": "student-001",
    "status": "completed",
    "score": 85,
    "notes": "Great understanding of combustion principles"
}
```

**Status Values:**
- `not_started` - Student hasn't begun the lesson
- `in_progress` - Student is working on the lesson
- `completed` - Student finished the lesson

### Student Progress

#### GET /api/students/:student_id/progress

Get all lesson progress for a student.

**Response**

```json
{
    "student_id": "student-001",
    "progress": [
        {
            "lesson_id": "lesson-xyz789",
            "lesson_title": "Introduction to Combustion",
            "subject_area": "combustion",
            "classroom_id": "class-abc123",
            "status": "completed",
            "score": 85,
            "completed_at": "2025-01-01 12:30:00",
            "notes": ""
        }
    ]
}
```

### Science Demonstrations

Interactive visualizations for teaching scientific concepts.

#### GET /api/demonstrations

List all available demonstrations.

**Query Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| category | string | Filter by category: `chemistry`, `physics`, `biology` |

**Response**

```json
{
    "demonstrations": [
        {
            "id": "demo-combustion-basic",
            "name": "Basic Combustion",
            "category": "chemistry",
            "description": "Demonstrates the combustion reaction with different fuels",
            "visualization_type": "combustion",
            "parameters": {
                "fuel": "methane",
                "oxygen_ratio": 2.0
            },
            "educational_notes": "Shows the fire triangle...",
            "safety_notes": "Virtual demonstration only"
        }
    ]
}
```

**Available Demonstrations:**

| ID | Name | Category | Description |
|----|------|----------|-------------|
| demo-combustion-basic | Basic Combustion | Chemistry | Fire triangle, fuel types, products |
| demo-acid-base | Acid-Base Neutralization | Chemistry | Neutralization reactions |
| demo-water-molecule | Water Molecule Structure | Chemistry | 3D molecular visualization |
| demo-light-waves | Light Wave Properties | Physics | Electromagnetic spectrum |
| demo-gas-particles | Gas Particle Motion | Physics | Kinetic theory visualization |
| demo-cell-mitosis | Cell Division (Mitosis) | Biology | Phases of cell division |
| demo-dna-replication | DNA Replication | Biology | DNA copying process |
| demo-protein-synthesis | Protein Synthesis | Biology | Transcription and translation |

#### POST /api/demonstrations/:demo_id/simulate

Run a science demonstration simulation.

**Request Body**

```json
{
    "custom_parameters": {
        "fuel": "propane",
        "initial_temperature": 25
    }
}
```

**Response (Combustion Example)**

```json
{
    "demonstration_id": "demo-combustion-basic",
    "name": "Basic Combustion",
    "category": "chemistry",
    "visualization_type": "combustion",
    "simulation_result": {
        "type": "combustion",
        "fuel": "propane",
        "chemical_equation": "C3H8 + 5O2 → 3CO2 + 4H2O",
        "energy_released_kj": 2220,
        "flame_color": "blue-yellow",
        "initial_temperature_c": 25,
        "final_temperature_c": 1000,
        "products": ["CO2", "H2O"],
        "learning_points": [
            "Combustion requires fuel, oxygen, and heat (fire triangle)",
            "Complete combustion produces CO2 and H2O",
            "Energy is released as heat and light",
            "Different fuels produce different flame colors"
        ],
        "visualization_frames": [...]
    },
    "educational_notes": "Shows the fire triangle...",
    "safety_notes": "Virtual demonstration only"
}
```

---

## Rate Limiting

Not implemented in development. Production deployments should implement 
appropriate rate limiting.

---

## Versioning

The API is currently at version 1.0.0. Version information is included in 
the health check response.
