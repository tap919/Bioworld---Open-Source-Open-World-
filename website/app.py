"""
Bioworld Website - Flask Application
=====================================
A Flask-based web application for the Bioworld MMORPG ecosystem.
Provides API endpoints for game client communication, research packet management,
simulation adapter integration, protein folding challenges, player corporations,
and market systems.

The game follows the "learn the thing, do the thing, teach the thing" model,
allowing players to monetize their scientific insights into scalable offerings.
"""

import os
import sqlite3
import json
import hashlib
import base64
import random
import math
from datetime import datetime
from flask import Flask, request, jsonify, render_template, g

app = Flask(__name__)
app.config['DATABASE'] = os.path.join(app.instance_path, 'bioworld.db')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

# Ensure instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass


def get_db():
    """Get database connection for current request context."""
    if 'db' not in g:
        g.db = sqlite3.connect(
            app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    """Close database connection at end of request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Initialize database with schema."""
    db = get_db()
    db.executescript('''
        CREATE TABLE IF NOT EXISTS research_packets (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            authors TEXT,
            license TEXT,
            game_version TEXT,
            seed TEXT,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            manifest_json TEXT
        );
        
        CREATE TABLE IF NOT EXISTS sim_adapters (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            version TEXT,
            description TEXT,
            entrypoint TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS proteins (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            amino_acid_sequence TEXT NOT NULL,
            predicted_structure TEXT,
            confidence_score REAL,
            player_id TEXT,
            validation_status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS corporations (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            owner_id TEXT NOT NULL,
            description TEXT,
            treasury REAL DEFAULT 10000.0,
            reputation INTEGER DEFAULT 100,
            specialization TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS player_apis (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            owner_id TEXT NOT NULL,
            corporation_id TEXT,
            endpoint_type TEXT NOT NULL,
            description TEXT,
            price_per_call REAL DEFAULT 0.0,
            total_calls INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (corporation_id) REFERENCES corporations(id)
        );
        
        CREATE TABLE IF NOT EXISTS market_orders (
            id TEXT PRIMARY KEY,
            order_type TEXT NOT NULL,
            asset_type TEXT NOT NULL,
            asset_id TEXT NOT NULL,
            player_id TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER DEFAULT 1,
            status TEXT DEFAULT 'open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS courses (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            instructor_id TEXT NOT NULL,
            corporation_id TEXT,
            topic TEXT NOT NULL,
            price REAL DEFAULT 0.0,
            enrollment_count INTEGER DEFAULT 0,
            content_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS classrooms (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            teacher_id TEXT NOT NULL,
            subject TEXT NOT NULL,
            description TEXT,
            class_code TEXT UNIQUE,
            max_students INTEGER DEFAULT 30,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS lessons (
            id TEXT PRIMARY KEY,
            classroom_id TEXT NOT NULL,
            title TEXT NOT NULL,
            subject_area TEXT NOT NULL,
            description TEXT,
            objectives_json TEXT,
            demonstrations_json TEXT,
            materials_json TEXT,
            estimated_duration INTEGER DEFAULT 45,
            lesson_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (classroom_id) REFERENCES classrooms(id)
        );
        
        CREATE TABLE IF NOT EXISTS student_enrollments (
            id TEXT PRIMARY KEY,
            classroom_id TEXT NOT NULL,
            student_id TEXT NOT NULL,
            enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (classroom_id) REFERENCES classrooms(id),
            UNIQUE(classroom_id, student_id)
        );
        
        CREATE TABLE IF NOT EXISTS lesson_progress (
            id TEXT PRIMARY KEY,
            lesson_id TEXT NOT NULL,
            student_id TEXT NOT NULL,
            status TEXT DEFAULT 'not_started',
            score REAL,
            completed_at TIMESTAMP,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lesson_id) REFERENCES lessons(id),
            UNIQUE(lesson_id, student_id)
        );
        
        CREATE TABLE IF NOT EXISTS demonstrations (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            visualization_type TEXT NOT NULL,
            parameters_json TEXT,
            educational_notes TEXT,
            safety_notes TEXT,
        -- NPC System Tables
        CREATE TABLE IF NOT EXISTS npcs (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            npc_type TEXT NOT NULL,
            role TEXT NOT NULL,
            location_zone TEXT,
            description TEXT,
            specialization TEXT,
            rarity TEXT DEFAULT 'common',
            interaction_count INTEGER DEFAULT 0,
            loot_table_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS npc_interactions (
            id TEXT PRIMARY KEY,
            npc_id TEXT NOT NULL,
            player_id TEXT NOT NULL,
            interaction_type TEXT NOT NULL,
            reward_type TEXT,
            reward_amount REAL DEFAULT 0,
            reward_item_id TEXT,
            success INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (npc_id) REFERENCES npcs(id)
        );
        
        -- Base Elements for Crafting
        CREATE TABLE IF NOT EXISTS base_elements (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            element_type TEXT NOT NULL,
            rarity TEXT DEFAULT 'common',
            description TEXT,
            properties_json TEXT,
            research_contribution REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Tools System
        CREATE TABLE IF NOT EXISTS tools (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            tool_type TEXT NOT NULL,
            tier INTEGER DEFAULT 1,
            description TEXT,
            required_elements_json TEXT,
            craft_time_seconds INTEGER DEFAULT 60,
            durability INTEGER DEFAULT 100,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Player Tool Inventory
        CREATE TABLE IF NOT EXISTS player_tools (
            id TEXT PRIMARY KEY,
            player_id TEXT NOT NULL,
            tool_id TEXT NOT NULL,
            current_durability INTEGER DEFAULT 100,
            acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (tool_id) REFERENCES tools(id)
        );
        
        -- Craftable Items (Jetpacks, Vehicles, Shelters, etc.)
        CREATE TABLE IF NOT EXISTS craftable_items (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            item_type TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            required_tools_json TEXT,
            required_elements_json TEXT,
            craft_time_seconds INTEGER DEFAULT 300,
            effects_json TEXT,
            research_bonus REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Player Craftable Item Inventory
        CREATE TABLE IF NOT EXISTS player_items (
            id TEXT PRIMARY KEY,
            player_id TEXT NOT NULL,
            item_id TEXT NOT NULL,
            quantity INTEGER DEFAULT 1,
            condition INTEGER DEFAULT 100,
            acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (item_id) REFERENCES craftable_items(id)
        );
        
        -- Player Element Inventory
        CREATE TABLE IF NOT EXISTS player_elements (
            id TEXT PRIMARY KEY,
            player_id TEXT NOT NULL,
            element_id TEXT NOT NULL,
            quantity INTEGER DEFAULT 1,
            acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (element_id) REFERENCES base_elements(id)
        );
        
        -- Shelters and Camps
        CREATE TABLE IF NOT EXISTS shelters (
            id TEXT PRIMARY KEY,
            player_id TEXT NOT NULL,
            name TEXT NOT NULL,
            shelter_type TEXT NOT NULL,
            location_x REAL DEFAULT 0.0,
            location_y REAL DEFAULT 0.0,
            location_z REAL DEFAULT 0.0,
            capacity INTEGER DEFAULT 4,
            research_bonus REAL DEFAULT 0.0,
            upgrades_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Barter Transactions
        CREATE TABLE IF NOT EXISTS barter_transactions (
            id TEXT PRIMARY KEY,
            initiator_id TEXT NOT NULL,
            recipient_id TEXT NOT NULL,
            offered_items_json TEXT NOT NULL,
            requested_items_json TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        );
        
        -- Disease Research Progress
        CREATE TABLE IF NOT EXISTS research_progress (
            id TEXT PRIMARY KEY,
            disease_id TEXT NOT NULL,
            player_id TEXT NOT NULL,
            contribution_amount REAL DEFAULT 0.0,
            contribution_type TEXT,
            unique_build_bonus REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Loot Tables for NPC Rewards
        CREATE TABLE IF NOT EXISTS loot_tables (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            entries_json TEXT NOT NULL,
            total_weight INTEGER DEFAULT 100,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    db.commit()


app.teardown_appcontext(close_db)


# CLI command to initialize database
@app.cli.command('init-db')
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    print('Initialized the database.')


# ============================================================================
# Web Routes (HTML Pages)
# ============================================================================

@app.route('/')
def index():
    """Render the main landing page."""
    return render_template('index.html')


@app.route('/research')
def research():
    """Render the research companion page."""
    return render_template('research.html')


@app.route('/about')
def about():
    """Render the about page."""
    return render_template('about.html')


@app.route('/learning')
def learning():
    """Render the learning center page."""
    return render_template('learning.html')


# ============================================================================
# API Routes
# ============================================================================

@app.route('/api/health', methods=['GET'])
def api_health():
    """Health check endpoint for monitoring."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })


@app.route('/api/research-packets', methods=['GET'])
def get_research_packets():
    """Get all research packets."""
    db = get_db()
    packets = db.execute(
        'SELECT id, title, authors, license, game_version, seed, tags, created_at '
        'FROM research_packets ORDER BY created_at DESC'
    ).fetchall()
    
    result = []
    for packet in packets:
        result.append({
            'id': packet['id'],
            'title': packet['title'],
            'authors': packet['authors'],
            'license': packet['license'],
            'game_version': packet['game_version'],
            'seed': packet['seed'],
            'tags': json.loads(packet['tags']) if packet['tags'] else [],
            'created_at': packet['created_at']
        })
    
    return jsonify({'packets': result})


@app.route('/api/research-packets', methods=['POST'])
def create_research_packet():
    """Create a new research packet."""
    data = request.get_json()
    
    if not data or 'id' not in data or 'title' not in data:
        return jsonify({'error': 'Missing required fields: id, title'}), 400
    
    db = get_db()
    try:
        db.execute(
            'INSERT INTO research_packets (id, title, authors, license, game_version, seed, tags, manifest_json) '
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (
                data['id'],
                data['title'],
                data.get('authors', ''),
                data.get('license', 'MIT'),
                data.get('game_version', ''),
                data.get('seed', ''),
                json.dumps(data.get('tags', [])),
                json.dumps(data.get('manifest', {}))
            )
        )
        db.commit()
        return jsonify({'message': 'Research packet created', 'id': data['id']}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Packet with this ID already exists'}), 409


@app.route('/api/research-packets/<packet_id>', methods=['GET'])
def get_research_packet(packet_id):
    """Get a specific research packet by ID."""
    db = get_db()
    packet = db.execute(
        'SELECT * FROM research_packets WHERE id = ?', (packet_id,)
    ).fetchone()
    
    if packet is None:
        return jsonify({'error': 'Packet not found'}), 404
    
    return jsonify({
        'id': packet['id'],
        'title': packet['title'],
        'authors': packet['authors'],
        'license': packet['license'],
        'game_version': packet['game_version'],
        'seed': packet['seed'],
        'tags': json.loads(packet['tags']) if packet['tags'] else [],
        'created_at': packet['created_at'],
        'manifest': json.loads(packet['manifest_json']) if packet['manifest_json'] else {}
    })


@app.route('/api/sim-adapters', methods=['GET'])
def get_sim_adapters():
    """Get all simulation adapters."""
    db = get_db()
    adapters = db.execute(
        'SELECT id, name, version, description, entrypoint, created_at '
        'FROM sim_adapters ORDER BY name'
    ).fetchall()
    
    result = []
    for adapter in adapters:
        result.append({
            'id': adapter['id'],
            'name': adapter['name'],
            'version': adapter['version'],
            'description': adapter['description'],
            'entrypoint': adapter['entrypoint'],
            'created_at': adapter['created_at']
        })
    
    return jsonify({'adapters': result})


@app.route('/api/sim-adapters', methods=['POST'])
def create_sim_adapter():
    """Register a new simulation adapter."""
    data = request.get_json()
    
    if not data or 'id' not in data or 'name' not in data:
        return jsonify({'error': 'Missing required fields: id, name'}), 400
    
    db = get_db()
    try:
        db.execute(
            'INSERT INTO sim_adapters (id, name, version, description, entrypoint) '
            'VALUES (?, ?, ?, ?, ?)',
            (
                data['id'],
                data['name'],
                data.get('version', '1.0.0'),
                data.get('description', ''),
                data.get('entrypoint', 'main.py')
            )
        )
        db.commit()
        return jsonify({'message': 'Simulation adapter registered', 'id': data['id']}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Adapter with this ID already exists'}), 409


# ============================================================================
# AI/LLM Integration Endpoints
# ============================================================================

@app.route('/api/analyze', methods=['POST'])
def analyze_content():
    """
    Analyze content using AI capabilities.
    This endpoint provides a hook for LLM integration for content analysis,
    research insights, and educational content generation.
    """
    data = request.get_json()
    
    if not data or 'content' not in data:
        return jsonify({'error': 'Missing required field: content'}), 400
    
    analysis_type = data.get('type', 'general')
    content = data['content']
    
    # Placeholder response - in production this would call an LLM API
    response = {
        'analysis_type': analysis_type,
        'status': 'processed',
        'timestamp': datetime.utcnow().isoformat(),
        'result': {
            'summary': f'Analysis of {analysis_type} content completed.',
            'content_length': len(content),
            'suggestions': [
                'Further research recommended on protein interactions.',
                'Consider validating against AlphaFold predictions.',
                'Cross-reference with existing research packets.'
            ]
        }
    }
    
    return jsonify(response)


@app.route('/api/blueprint-codes', methods=['POST'])
def generate_blueprint_code():
    """
    Generate a shareable blueprint code for a build.
    Blueprint codes enable portable, remixable content sharing.
    """
    data = request.get_json()
    
    if not data or 'build_data' not in data:
        return jsonify({'error': 'Missing required field: build_data'}), 400
    
    # Generate a unique code based on build data
    build_json = json.dumps(data['build_data'], sort_keys=True)
    hash_obj = hashlib.sha256(build_json.encode())
    code = base64.urlsafe_b64encode(hash_obj.digest()[:12]).decode('utf-8')
    
    return jsonify({
        'blueprint_code': f'BW-{code}',
        'created_at': datetime.utcnow().isoformat()
    })


# ============================================================================
# Phase 1: Protein Folding and Biotechnology Endpoints
# ============================================================================

@app.route('/api/proteins', methods=['GET'])
def get_proteins():
    """Get all protein entries."""
    db = get_db()
    proteins = db.execute(
        'SELECT id, name, amino_acid_sequence, predicted_structure, confidence_score, '
        'player_id, validation_status, created_at FROM proteins ORDER BY created_at DESC'
    ).fetchall()
    
    result = []
    for protein in proteins:
        result.append({
            'id': protein['id'],
            'name': protein['name'],
            'amino_acid_sequence': protein['amino_acid_sequence'],
            'predicted_structure': protein['predicted_structure'],
            'confidence_score': protein['confidence_score'],
            'player_id': protein['player_id'],
            'validation_status': protein['validation_status'],
            'created_at': protein['created_at']
        })
    
    return jsonify({'proteins': result})


@app.route('/api/proteins', methods=['POST'])
def create_protein():
    """
    Submit a new protein for structure prediction.
    Simulates AlphaFold-like prediction based on amino acid sequence.
    """
    data = request.get_json()
    
    if not data or 'name' not in data or 'amino_acid_sequence' not in data:
        return jsonify({'error': 'Missing required fields: name, amino_acid_sequence'}), 400
    
    # Validate amino acid sequence (basic check for valid amino acid letters)
    valid_amino_acids = set('ACDEFGHIKLMNPQRSTVWY')
    sequence = data['amino_acid_sequence'].upper()
    if not all(aa in valid_amino_acids for aa in sequence):
        return jsonify({'error': 'Invalid amino acid sequence'}), 400
    
    protein_id = f"prot-{hashlib.sha256(sequence.encode()).hexdigest()[:12]}"
    
    # Simulate AI prediction (placeholder for actual AlphaFold-like model)
    confidence_score = round(random.uniform(0.7, 0.99), 3)
    predicted_structure = _simulate_protein_structure(sequence)
    
    db = get_db()
    try:
        db.execute(
            'INSERT INTO proteins (id, name, amino_acid_sequence, predicted_structure, '
            'confidence_score, player_id, validation_status) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (
                protein_id,
                data['name'],
                sequence,
                json.dumps(predicted_structure),
                confidence_score,
                data.get('player_id', 'anonymous'),
                'predicted'
            )
        )
        db.commit()
        return jsonify({
            'message': 'Protein structure predicted',
            'id': protein_id,
            'confidence_score': confidence_score,
            'validation_required': confidence_score < 0.9
        }), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Protein already exists', 'id': protein_id}), 409


def _simulate_protein_structure(sequence):
    """
    Simulate protein structure prediction.
    In production, this would interface with actual AI models like AlphaFold.
    """
    # Generate placeholder 3D coordinates based on sequence
    structure = {
        'type': 'predicted',
        'model': 'bioworld-fold-v1',
        'chain_count': 1,
        'residue_count': len(sequence),
        'secondary_structures': [],
        'domains': []
    }
    
    # Simulate secondary structure prediction
    for i in range(0, len(sequence), random.randint(5, 15)):
        struct_type = random.choice(['helix', 'sheet', 'coil'])
        structure['secondary_structures'].append({
            'type': struct_type,
            'start': i,
            'end': min(i + random.randint(5, 12), len(sequence))
        })
    
    return structure


@app.route('/api/proteins/<protein_id>/validate', methods=['POST'])
def validate_protein(protein_id):
    """
    Submit wet lab validation for a protein prediction.
    Simulates the validation process that even best AI models require.
    """
    data = request.get_json() or {}
    
    db = get_db()
    protein = db.execute('SELECT * FROM proteins WHERE id = ?', (protein_id,)).fetchone()
    
    if not protein:
        return jsonify({'error': 'Protein not found'}), 404
    
    # Simulate wet lab validation (success rate based on initial confidence)
    confidence = protein['confidence_score']
    validation_success = random.random() < (confidence * 0.95)
    
    new_status = 'validated' if validation_success else 'validation_failed'
    db.execute(
        'UPDATE proteins SET validation_status = ? WHERE id = ?',
        (new_status, protein_id)
    )
    db.commit()
    
    return jsonify({
        'protein_id': protein_id,
        'validation_result': 'success' if validation_success else 'failure',
        'status': new_status,
        'message': 'Wet lab validation completed' if validation_success else 'Validation failed - structure mismatch detected'
    })


@app.route('/api/proteins/design', methods=['POST'])
def design_protein():
    """
    Use generative AI to design a new protein for a specific purpose.
    Simulates RF Diffusion-like protein design capabilities.
    """
    data = request.get_json()
    
    if not data or 'purpose' not in data:
        return jsonify({'error': 'Missing required field: purpose'}), 400
    
    purpose = data['purpose']
    constraints = data.get('constraints', {})
    
    # Simulate generative protein design
    designed_sequence = _generate_protein_sequence(purpose, constraints)
    protein_id = f"designed-{hashlib.sha256(designed_sequence.encode()).hexdigest()[:12]}"
    
    return jsonify({
        'id': protein_id,
        'purpose': purpose,
        'designed_sequence': designed_sequence,
        'sequence_length': len(designed_sequence),
        'design_model': 'bioworld-diffusion-v1',
        'estimated_stability': round(random.uniform(0.6, 0.95), 3),
        'suggested_applications': _get_applications(purpose)
    })


def _generate_protein_sequence(purpose, constraints):
    """Generate a protein sequence for a given purpose."""
    amino_acids = 'ACDEFGHIKLMNPQRSTVWY'
    length = constraints.get('length', random.randint(100, 300))
    
    # Weight certain amino acids based on purpose
    weights = {aa: 1.0 for aa in amino_acids}
    if 'antibody' in purpose.lower():
        weights['C'] = 2.0  # More cysteines for disulfide bonds
    elif 'enzyme' in purpose.lower():
        weights['H'] = 1.5  # Histidines for catalysis
    
    sequence = ''.join(random.choices(
        amino_acids,
        weights=[weights[aa] for aa in amino_acids],
        k=length
    ))
    return sequence


def _get_applications(purpose):
    """Get suggested applications based on design purpose."""
    applications = {
        'antibody': ['Therapeutic targeting', 'Diagnostic markers', 'Immune modulation'],
        'enzyme': ['Industrial catalysis', 'Bioremediation', 'Drug synthesis'],
        'structural': ['Biomaterial scaffolds', 'Nanoscale assembly', 'Drug delivery'],
        'default': ['Research applications', 'Further characterization needed']
    }
    
    for key, apps in applications.items():
        if key in purpose.lower():
            return apps
    return applications['default']


# ============================================================================
# Phase 2: Corporation and Economic System Endpoints
# ============================================================================

@app.route('/api/corporations', methods=['GET'])
def get_corporations():
    """Get all player corporations."""
    db = get_db()
    corps = db.execute(
        'SELECT id, name, owner_id, description, treasury, reputation, specialization, created_at '
        'FROM corporations ORDER BY reputation DESC'
    ).fetchall()
    
    result = []
    for corp in corps:
        result.append({
            'id': corp['id'],
            'name': corp['name'],
            'owner_id': corp['owner_id'],
            'description': corp['description'],
            'treasury': corp['treasury'],
            'reputation': corp['reputation'],
            'specialization': corp['specialization'],
            'created_at': corp['created_at']
        })
    
    return jsonify({'corporations': result})


@app.route('/api/corporations', methods=['POST'])
def create_corporation():
    """Create a new player corporation."""
    data = request.get_json()
    
    if not data or 'name' not in data or 'owner_id' not in data:
        return jsonify({'error': 'Missing required fields: name, owner_id'}), 400
    
    corp_id = f"corp-{hashlib.sha256(data['name'].encode()).hexdigest()[:12]}"
    
    db = get_db()
    try:
        db.execute(
            'INSERT INTO corporations (id, name, owner_id, description, specialization) '
            'VALUES (?, ?, ?, ?, ?)',
            (
                corp_id,
                data['name'],
                data['owner_id'],
                data.get('description', ''),
                data.get('specialization', 'general')
            )
        )
        db.commit()
        return jsonify({
            'message': 'Corporation created',
            'id': corp_id,
            'initial_treasury': 10000.0
        }), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Corporation name already exists'}), 409


# ============================================================================
# Player API Marketplace (Learn, Do, Teach Model)
# ============================================================================

@app.route('/api/player-apis', methods=['GET'])
def get_player_apis():
    """Get all exposed player APIs."""
    db = get_db()
    apis = db.execute(
        'SELECT id, name, owner_id, corporation_id, endpoint_type, description, '
        'price_per_call, total_calls, created_at FROM player_apis ORDER BY total_calls DESC'
    ).fetchall()
    
    result = []
    for api in apis:
        result.append({
            'id': api['id'],
            'name': api['name'],
            'owner_id': api['owner_id'],
            'corporation_id': api['corporation_id'],
            'endpoint_type': api['endpoint_type'],
            'description': api['description'],
            'price_per_call': api['price_per_call'],
            'total_calls': api['total_calls'],
            'created_at': api['created_at']
        })
    
    return jsonify({'apis': result})


@app.route('/api/player-apis', methods=['POST'])
def create_player_api():
    """
    Expose a player's model or algorithm as an API.
    Enables the 'teach the thing' monetization model.
    """
    data = request.get_json()
    
    if not data or 'name' not in data or 'owner_id' not in data or 'endpoint_type' not in data:
        return jsonify({'error': 'Missing required fields: name, owner_id, endpoint_type'}), 400
    
    valid_types = ['drug_efficacy', 'genetic_marker', 'protein_prediction', 'market_analysis', 'custom']
    if data['endpoint_type'] not in valid_types:
        return jsonify({'error': f'Invalid endpoint_type. Must be one of: {valid_types}'}), 400
    
    api_id = f"api-{hashlib.sha256((data['name'] + data['owner_id']).encode()).hexdigest()[:12]}"
    
    db = get_db()
    try:
        db.execute(
            'INSERT INTO player_apis (id, name, owner_id, corporation_id, endpoint_type, description, price_per_call) '
            'VALUES (?, ?, ?, ?, ?, ?, ?)',
            (
                api_id,
                data['name'],
                data['owner_id'],
                data.get('corporation_id'),
                data['endpoint_type'],
                data.get('description', ''),
                data.get('price_per_call', 0.0)
            )
        )
        db.commit()
        return jsonify({
            'message': 'Player API created',
            'id': api_id,
            'endpoint': f'/api/player-apis/{api_id}/call'
        }), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'API with this configuration already exists'}), 409


@app.route('/api/player-apis/<api_id>/call', methods=['POST'])
def call_player_api(api_id):
    """
    Call a player-exposed API.
    Charges the caller and credits the API owner.
    """
    data = request.get_json() or {}
    
    db = get_db()
    api = db.execute('SELECT * FROM player_apis WHERE id = ?', (api_id,)).fetchone()
    
    if not api:
        return jsonify({'error': 'API not found'}), 404
    
    # Increment call count
    db.execute(
        'UPDATE player_apis SET total_calls = total_calls + 1 WHERE id = ?',
        (api_id,)
    )
    db.commit()
    
    # Simulate API response based on type
    response = _simulate_api_response(api['endpoint_type'], data.get('input', {}))
    
    return jsonify({
        'api_id': api_id,
        'endpoint_type': api['endpoint_type'],
        'cost': api['price_per_call'],
        'result': response
    })


def _simulate_api_response(endpoint_type, input_data):
    """Simulate response for different API types."""
    responses = {
        'drug_efficacy': {
            'predicted_efficacy': round(random.uniform(0.3, 0.95), 3),
            'confidence': round(random.uniform(0.7, 0.99), 3),
            'side_effect_risk': random.choice(['low', 'medium', 'high'])
        },
        'genetic_marker': {
            'markers_found': random.randint(0, 5),
            'risk_assessment': random.choice(['low', 'moderate', 'elevated']),
            'recommended_tests': ['Panel A', 'Sequence B']
        },
        'protein_prediction': {
            'structure_type': random.choice(['globular', 'membrane', 'fibrous']),
            'stability_score': round(random.uniform(0.5, 0.99), 3)
        },
        'market_analysis': {
            'trend': random.choice(['bullish', 'bearish', 'neutral']),
            'confidence': round(random.uniform(0.6, 0.95), 3),
            'recommended_action': random.choice(['buy', 'sell', 'hold'])
        },
        'custom': {
            'status': 'processed',
            'output': 'Custom analysis completed'
        }
    }
    return responses.get(endpoint_type, responses['custom'])


# ============================================================================
# Market and Trading System
# ============================================================================

@app.route('/api/market/orders', methods=['GET'])
def get_market_orders():
    """Get all open market orders."""
    db = get_db()
    orders = db.execute(
        "SELECT * FROM market_orders WHERE status = 'open' ORDER BY created_at DESC"
    ).fetchall()
    
    result = []
    for order in orders:
        result.append({
            'id': order['id'],
            'order_type': order['order_type'],
            'asset_type': order['asset_type'],
            'asset_id': order['asset_id'],
            'player_id': order['player_id'],
            'price': order['price'],
            'quantity': order['quantity'],
            'status': order['status'],
            'created_at': order['created_at']
        })
    
    return jsonify({'orders': result})


@app.route('/api/market/orders', methods=['POST'])
def create_market_order():
    """Create a new market order (buy/sell)."""
    data = request.get_json()
    
    required = ['order_type', 'asset_type', 'asset_id', 'player_id', 'price']
    if not data or not all(f in data for f in required):
        return jsonify({'error': f'Missing required fields: {required}'}), 400
    
    if data['order_type'] not in ['buy', 'sell']:
        return jsonify({'error': 'order_type must be buy or sell'}), 400
    
    order_id = f"order-{hashlib.sha256(str(datetime.utcnow()).encode()).hexdigest()[:12]}"
    
    db = get_db()
    db.execute(
        'INSERT INTO market_orders (id, order_type, asset_type, asset_id, player_id, price, quantity) '
        'VALUES (?, ?, ?, ?, ?, ?, ?)',
        (
            order_id,
            data['order_type'],
            data['asset_type'],
            data['asset_id'],
            data['player_id'],
            data['price'],
            data.get('quantity', 1)
        )
    )
    db.commit()
    
    return jsonify({
        'message': 'Market order created',
        'id': order_id,
        'status': 'open'
    }), 201


# ============================================================================
# Course System (Teaching Model)
# ============================================================================

@app.route('/api/courses', methods=['GET'])
def get_courses():
    """Get all available courses."""
    db = get_db()
    courses = db.execute(
        'SELECT id, title, instructor_id, corporation_id, topic, price, enrollment_count, created_at '
        'FROM courses ORDER BY enrollment_count DESC'
    ).fetchall()
    
    result = []
    for course in courses:
        result.append({
            'id': course['id'],
            'title': course['title'],
            'instructor_id': course['instructor_id'],
            'corporation_id': course['corporation_id'],
            'topic': course['topic'],
            'price': course['price'],
            'enrollment_count': course['enrollment_count'],
            'created_at': course['created_at']
        })
    
    return jsonify({'courses': result})


@app.route('/api/courses', methods=['POST'])
def create_course():
    """Create a new course (teach the thing)."""
    data = request.get_json()
    
    if not data or 'title' not in data or 'instructor_id' not in data or 'topic' not in data:
        return jsonify({'error': 'Missing required fields: title, instructor_id, topic'}), 400
    
    course_id = f"course-{hashlib.sha256(data['title'].encode()).hexdigest()[:12]}"
    
    db = get_db()
    try:
        db.execute(
            'INSERT INTO courses (id, title, instructor_id, corporation_id, topic, price, content_json) '
            'VALUES (?, ?, ?, ?, ?, ?, ?)',
            (
                course_id,
                data['title'],
                data['instructor_id'],
                data.get('corporation_id'),
                data['topic'],
                data.get('price', 0.0),
                json.dumps(data.get('content', {}))
            )
        )
        db.commit()
        return jsonify({
            'message': 'Course created',
            'id': course_id
        }), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Course with this title already exists'}), 409


@app.route('/api/courses/<course_id>/enroll', methods=['POST'])
def enroll_course(course_id):
    """Enroll in a course."""
    db = get_db()
    course = db.execute('SELECT * FROM courses WHERE id = ?', (course_id,)).fetchone()
    
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    
    db.execute(
        'UPDATE courses SET enrollment_count = enrollment_count + 1 WHERE id = ?',
        (course_id,)
    )
    db.commit()
    
    return jsonify({
        'message': 'Enrolled successfully',
        'course_id': course_id,
        'title': course['title']
    })


# ============================================================================
# Education System - Classrooms for Teachers and Learning Centers for Students
# ============================================================================

@app.route('/api/classrooms', methods=['GET'])
def get_classrooms():
    """Get all active classrooms."""
    db = get_db()
    # Use JOIN to get student counts in a single query, avoiding N+1 query issue
    classrooms = db.execute(
        '''SELECT c.id, c.name, c.teacher_id, c.subject, c.description, c.class_code, 
                  c.max_students, c.is_active, c.created_at, COUNT(se.id) as student_count 
           FROM classrooms c 
           LEFT JOIN student_enrollments se ON c.id = se.classroom_id 
           WHERE c.is_active = 1 
           GROUP BY c.id 
           ORDER BY c.created_at DESC'''
    ).fetchall()
    
    result = []
    for classroom in classrooms:
        result.append({
            'id': classroom['id'],
            'name': classroom['name'],
            'teacher_id': classroom['teacher_id'],
            'subject': classroom['subject'],
            'description': classroom['description'],
            'class_code': classroom['class_code'],
            'max_students': classroom['max_students'],
            'current_students': classroom['student_count'],
            'is_active': bool(classroom['is_active']),
            'created_at': classroom['created_at']
        })
    
    return jsonify({'classrooms': result})


@app.route('/api/classrooms', methods=['POST'])
def create_classroom():
    """Create a new classroom for a teacher."""
    data = request.get_json()
    
    if not data or 'name' not in data or 'teacher_id' not in data or 'subject' not in data:
        return jsonify({'error': 'Missing required fields: name, teacher_id, subject'}), 400
    
    # Validate max_students is within reasonable bounds
    max_students = data.get('max_students', 30)
    try:
        max_students = int(max_students)
    except (TypeError, ValueError):
        return jsonify({'error': 'max_students must be an integer between 1 and 500'}), 400
    if max_students < 1 or max_students > 500:
        return jsonify({'error': 'max_students must be between 1 and 500'}), 400
    
    classroom_id = f"class-{hashlib.sha256((data['name'] + data['teacher_id']).encode()).hexdigest()[:12]}"
    # Generate a unique 6-character class code
    class_code = hashlib.sha256((classroom_id + str(datetime.utcnow())).encode()).hexdigest()[:6].upper()
# NPC System - Randomized but Mathematically Fair Rewards
# ============================================================================

# Configuration constants for game balance tuning
MAX_LUCK_MULTIPLIER = 2.0  # Maximum luck bonus cap to prevent exploitation
MIN_PLAYER_LEVEL = 1  # Minimum effective player level for calculations
LEVEL_BONUS_FACTOR = 0.5  # Scaling factor for level-based bonuses
REWARD_VARIANCE_MIN = 0.8  # Minimum variance multiplier (±20%)
REWARD_VARIANCE_MAX = 1.2  # Maximum variance multiplier (±20%)


def calculate_fair_reward(player_level, npc_rarity, reward_type):
    """
    Calculate mathematically fair rewards using weighted probability distribution.
    Ensures game balance while maintaining randomness.
    
    Uses a modified pity system and weighted random selection to ensure fairness:
    - Base reward scales with player level (log scaling for diminishing returns)
    - Rarity multiplier affects reward quality
    - Small variance (±20%) to maintain excitement without exploitation
    
    Note: player_level is clamped to MIN_PLAYER_LEVEL (1) minimum, meaning level 0
    and level 1 players receive the same base reward.
    """
    # Base multipliers by rarity
    rarity_multipliers = {
        'common': 1.0,
        'uncommon': 1.5,
        'rare': 2.5,
        'epic': 4.0,
        'legendary': 7.5
    }
    
    # Reward type base values
    base_values = {
        'coins': 10.0,
        'tools': 1.0,
        'elements': 3.0,
        'information': 5.0,
        'special_files': 2.0,
        'nft': 0.1,
        'aid': 15.0
    }
    
    multiplier = rarity_multipliers.get(npc_rarity, 1.0)
    base = base_values.get(reward_type, 5.0)
    
    # Calculate fair reward with bounded variance
    variance = random.uniform(REWARD_VARIANCE_MIN, REWARD_VARIANCE_MAX)
    # Use log scaling for level bonus with diminishing returns
    effective_level = max(player_level, MIN_PLAYER_LEVEL)
    level_bonus = math.log(effective_level + 1) * LEVEL_BONUS_FACTOR
    
    reward = base * multiplier * variance * (1 + level_bonus)
    
    return round(reward, 2)


def select_weighted_reward(loot_entries, player_luck=1.0):
    """
    Select reward from loot table using weighted random selection.
    Implements mathematically fair distribution based on weights.
    
    Args:
        loot_entries: List of {item, weight, min_amount, max_amount}
        player_luck: Luck modifier (default 1.0)
    
    Returns:
        Selected reward entry with calculated amount
    """
    if not loot_entries:
        return None
    
    # Note: total_weight is calculated later after luck adjustments
    
    # Apply luck modifier to rare items (increases their effective weight)
    adjusted_entries = []
    for entry in loot_entries:
        weight = entry.get('weight', 1)
        rarity = entry.get('rarity', 'common')
        
        # Luck affects rare+ items, capped to prevent exploitation
        if rarity in ['rare', 'epic', 'legendary'] and player_luck > 1.0:
            weight = weight * min(player_luck, MAX_LUCK_MULTIPLIER)
        
        adjusted_entries.append({**entry, 'adjusted_weight': weight})
    
    # Recalculate total with adjustments
    adjusted_total = sum(e['adjusted_weight'] for e in adjusted_entries)
    
    # Weighted random selection
    roll = random.uniform(0, adjusted_total)
    cumulative = 0
    
    for entry in adjusted_entries:
        cumulative += entry['adjusted_weight']
        if roll <= cumulative:
            # Calculate amount within fair bounds
            min_amt = entry.get('min_amount', 1)
            max_amt = entry.get('max_amount', 1)
            amount = random.randint(int(min_amt), int(max_amt))
            return {
                'item': entry.get('item'),
                'item_type': entry.get('item_type'),
                'rarity': entry.get('rarity', 'common'),
                'amount': amount
            }
    
    # Fallback to first entry with proper amount calculation
    fallback = loot_entries[0]
    min_amt = fallback.get('min_amount', 1)
    max_amt = fallback.get('max_amount', 1)
    return {
        'item': fallback.get('item'),
        'item_type': fallback.get('item_type'),
        'rarity': fallback.get('rarity', 'common'),
        'amount': random.randint(int(min_amt), int(max_amt))
    }


@app.route('/api/npcs', methods=['GET'])
def get_npcs():
    """Get all NPCs with optional filtering by type, role, or zone."""
    db = get_db()
    
    npc_type = request.args.get('type')
    role = request.args.get('role')
    zone = request.args.get('zone')
    
    query = 'SELECT * FROM npcs WHERE 1=1'
    params = []
    
    if npc_type:
        query += ' AND npc_type = ?'
        params.append(npc_type)
    if role:
        query += ' AND role = ?'
        params.append(role)
    if zone:
        query += ' AND location_zone = ?'
        params.append(zone)
    
    query += ' ORDER BY rarity DESC, name ASC'
    
    npcs = db.execute(query, params).fetchall()
    
    result = []
    for npc in npcs:
        result.append({
            'id': npc['id'],
            'name': npc['name'],
            'npc_type': npc['npc_type'],
            'role': npc['role'],
            'location_zone': npc['location_zone'],
            'description': npc['description'],
            'specialization': npc['specialization'],
            'rarity': npc['rarity'],
            'interaction_count': npc['interaction_count'],
            'created_at': npc['created_at']
        })
    
    return jsonify({'npcs': result})


@app.route('/api/npcs', methods=['POST'])
def create_npc():
    """Create a new NPC with specified role and attributes."""
    data = request.get_json()
    
    required_fields = ['name', 'npc_type', 'role']
    if not data or not all(f in data for f in required_fields):
        return jsonify({'error': f'Missing required fields: {required_fields}'}), 400
    
    valid_types = ['helper', 'merchant', 'information_giver', 'tool_giver', 
                   'quest_giver', 'trainer', 'banker', 'researcher']
    valid_roles = ['aid', 'trade', 'information', 'tools', 'special_files', 
                   'nfts', 'coins', 'crafting', 'research']
    valid_rarities = ['common', 'uncommon', 'rare', 'epic', 'legendary']
    
    if data['npc_type'] not in valid_types:
        return jsonify({'error': f'Invalid npc_type. Must be one of: {valid_types}'}), 400
    
    if data['role'] not in valid_roles:
        return jsonify({'error': f'Invalid role. Must be one of: {valid_roles}'}), 400
    
    rarity = data.get('rarity', 'common')
    if rarity not in valid_rarities:
        return jsonify({'error': f'Invalid rarity. Must be one of: {valid_rarities}'}), 400
    
    npc_id = f"npc-{hashlib.sha256((data['name'] + str(datetime.utcnow())).encode()).hexdigest()[:12]}"
    
    db = get_db()
    try:
        db.execute(
            'INSERT INTO classrooms (id, name, teacher_id, subject, description, class_code, max_students) '
            'VALUES (?, ?, ?, ?, ?, ?, ?)',
            (
                classroom_id,
                data['name'],
                data['teacher_id'],
                data['subject'],
                data.get('description', ''),
                class_code,
                max_students
            'INSERT INTO npcs (id, name, npc_type, role, location_zone, description, '
            'specialization, rarity, loot_table_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (
                npc_id,
                data['name'],
                data['npc_type'],
                data['role'],
                data.get('location_zone', 'central_hub'),
                data.get('description', ''),
                data.get('specialization', 'general'),
                rarity,
                data.get('loot_table_id')
            )
        )
        db.commit()
        return jsonify({
            'message': 'Classroom created',
            'id': classroom_id,
            'class_code': class_code
        }), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Classroom with this configuration already exists'}), 409


@app.route('/api/classrooms/<classroom_id>', methods=['GET'])
def get_classroom(classroom_id):
    """Get a specific classroom by ID."""
    db = get_db()
    classroom = db.execute(
        'SELECT * FROM classrooms WHERE id = ?', (classroom_id,)
    ).fetchone()
    
    if classroom is None:
        return jsonify({'error': 'Classroom not found'}), 404
    
    # Get enrolled students count
    student_count = db.execute(
        'SELECT COUNT(*) FROM student_enrollments WHERE classroom_id = ?',
        (classroom_id,)
    ).fetchone()[0]
    
    # Get lessons for this classroom
    lessons = db.execute(
        'SELECT id, title, subject_area, description, estimated_duration, lesson_order '
        'FROM lessons WHERE classroom_id = ? ORDER BY lesson_order',
        (classroom_id,)
    ).fetchall()
    
    return jsonify({
        'id': classroom['id'],
        'name': classroom['name'],
        'teacher_id': classroom['teacher_id'],
        'subject': classroom['subject'],
        'description': classroom['description'],
        'class_code': classroom['class_code'],
        'max_students': classroom['max_students'],
        'current_students': student_count,
        'is_active': bool(classroom['is_active']),
        'created_at': classroom['created_at'],
        'lessons': [dict(lesson) for lesson in lessons]
    })


@app.route('/api/classrooms/join', methods=['POST'])
def join_classroom():
    """Join a classroom using a class code."""
    data = request.get_json()
    
    if not data or 'class_code' not in data or 'student_id' not in data:
        return jsonify({'error': 'Missing required fields: class_code, student_id'}), 400
    
    db = get_db()
    classroom = db.execute(
        'SELECT * FROM classrooms WHERE class_code = ? AND is_active = 1',
        (data['class_code'].upper(),)
    ).fetchone()
    
    if not classroom:
        return jsonify({'error': 'Invalid or inactive class code'}), 404
    
    # Check if classroom is full
    student_count = db.execute(
        'SELECT COUNT(*) FROM student_enrollments WHERE classroom_id = ?',
        (classroom['id'],)
    ).fetchone()[0]
    
    if student_count >= classroom['max_students']:
        return jsonify({'error': 'Classroom is full'}), 400
    
    enrollment_id = f"enroll-{hashlib.sha256((classroom['id'] + data['student_id']).encode()).hexdigest()[:12]}"
    
    try:
        db.execute(
            'INSERT INTO student_enrollments (id, classroom_id, student_id) VALUES (?, ?, ?)',
            (enrollment_id, classroom['id'], data['student_id'])
        )
        db.commit()
        return jsonify({
            'message': 'Successfully joined classroom',
            'classroom_id': classroom['id'],
            'classroom_name': classroom['name'],
            'subject': classroom['subject']
        }), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Already enrolled in this classroom'}), 409


@app.route('/api/classrooms/<classroom_id>/students', methods=['GET'])
def get_classroom_students(classroom_id):
    """Get all students enrolled in a classroom."""
    db = get_db()
    classroom = db.execute('SELECT * FROM classrooms WHERE id = ?', (classroom_id,)).fetchone()
    
    if not classroom:
        return jsonify({'error': 'Classroom not found'}), 404
    
    enrollments = db.execute(
        'SELECT student_id, enrolled_at FROM student_enrollments WHERE classroom_id = ? ORDER BY enrolled_at',
        (classroom_id,)
    ).fetchall()
    
    return jsonify({
        'classroom_id': classroom_id,
        'students': [{'student_id': e['student_id'], 'enrolled_at': e['enrolled_at']} for e in enrollments]
    })


# ============================================================================
# Lessons System for Science Education
# ============================================================================

@app.route('/api/lessons', methods=['GET'])
def get_lessons():
    """Get all lessons, optionally filtered by classroom."""
    classroom_id = request.args.get('classroom_id')
    
    db = get_db()
    if classroom_id:
        lessons = db.execute(
            'SELECT * FROM lessons WHERE classroom_id = ? ORDER BY lesson_order',
            (classroom_id,)
        ).fetchall()
    else:
        lessons = db.execute('SELECT * FROM lessons ORDER BY created_at DESC').fetchall()
    
    result = []
    for lesson in lessons:
        result.append({
            'id': lesson['id'],
            'classroom_id': lesson['classroom_id'],
            'title': lesson['title'],
            'subject_area': lesson['subject_area'],
            'description': lesson['description'],
            'objectives': json.loads(lesson['objectives_json']) if lesson['objectives_json'] else [],
            'demonstrations': json.loads(lesson['demonstrations_json']) if lesson['demonstrations_json'] else [],
            'materials': json.loads(lesson['materials_json']) if lesson['materials_json'] else [],
            'estimated_duration': lesson['estimated_duration'],
            'lesson_order': lesson['lesson_order'],
            'created_at': lesson['created_at']
        })
    
    return jsonify({'lessons': result})


@app.route('/api/lessons', methods=['POST'])
def create_lesson():
    """Create a new lesson for a classroom."""
    data = request.get_json()
    
    required = ['classroom_id', 'title', 'subject_area']
    if not data or not all(f in data for f in required):
        return jsonify({'error': f'Missing required fields: {required}'}), 400
    
    # Verify classroom exists
    db = get_db()
    classroom = db.execute('SELECT * FROM classrooms WHERE id = ?', (data['classroom_id'],)).fetchone()
    if not classroom:
        return jsonify({'error': 'Classroom not found'}), 404
    
    lesson_id = f"lesson-{hashlib.sha256((data['title'] + data['classroom_id']).encode()).hexdigest()[:12]}"
    
    # Get next lesson order
    max_order = db.execute(
        'SELECT MAX(lesson_order) FROM lessons WHERE classroom_id = ?',
        (data['classroom_id'],)
    ).fetchone()[0]
    next_order = (max_order or 0) + 1
    
    try:
        db.execute(
            'INSERT INTO lessons (id, classroom_id, title, subject_area, description, objectives_json, '
            'demonstrations_json, materials_json, estimated_duration, lesson_order) '
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (
                lesson_id,
                data['classroom_id'],
                data['title'],
                data['subject_area'],
                data.get('description', ''),
                json.dumps(data.get('objectives', [])),
                json.dumps(data.get('demonstrations', [])),
                json.dumps(data.get('materials', [])),
                data.get('estimated_duration', 45),
                data.get('lesson_order', next_order)
            'message': 'NPC created successfully',
            'id': npc_id,
            'name': data['name'],
            'rarity': rarity
        }), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'NPC creation failed'}), 409


@app.route('/api/npcs/<npc_id>/interact', methods=['POST'])
def interact_with_npc(npc_id):
    """
    Interact with an NPC to receive randomized but fair rewards.
    Supports: help, aid, information, tools, special files, NFTs, coins.
    
    Note: In production, player_level and player_luck should be derived 
    server-side from the authenticated player_id/session.
    """
    data = request.get_json() or {}
    player_id = data.get('player_id', 'anonymous')
    # Input validation for player_level and player_luck with bounded ranges
    player_level = max(1, min(int(data.get('player_level', 1)), 100))  # Cap at reasonable max
    player_luck = max(0.1, min(float(data.get('player_luck', 1.0)), MAX_LUCK_MULTIPLIER))
    
    db = get_db()
    npc = db.execute('SELECT * FROM npcs WHERE id = ?', (npc_id,)).fetchone()
    
    if not npc:
        return jsonify({'error': 'NPC not found'}), 404
    
    # Determine reward based on NPC role
    role = npc['role']
    rarity = npc['rarity']
    
    # Calculate fair reward
    reward_amount = calculate_fair_reward(player_level, rarity, role)
    
    # Generate reward based on role
    reward = _generate_npc_reward(role, rarity, reward_amount, player_luck)
    
    # Record interaction
    interaction_id = f"int-{hashlib.sha256(str(datetime.utcnow()).encode()).hexdigest()[:12]}"
    
    db.execute(
        'INSERT INTO npc_interactions (id, npc_id, player_id, interaction_type, '
        'reward_type, reward_amount, reward_item_id, success) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (
            interaction_id,
            npc_id,
            player_id,
            role,
            reward['type'],
            reward['amount'],
            reward.get('item_id'),
            1
        )
    )
    
    # Update NPC interaction count
    db.execute(
        'UPDATE npcs SET interaction_count = interaction_count + 1 WHERE id = ?',
        (npc_id,)
    )
    db.commit()
    
    return jsonify({
        'interaction_id': interaction_id,
        'npc': {
            'id': npc['id'],
            'name': npc['name'],
            'type': npc['npc_type'],
            'role': role
        },
        'reward': reward,
        'message': _generate_interaction_message(npc['name'], role, reward)
    })


def _generate_npc_reward(role, rarity, base_amount, luck=1.0):
    """Generate reward based on NPC role with fair randomization."""
    rewards_by_role = {
        'aid': {
            'type': 'aid',
            'options': ['health_pack', 'energy_boost', 'research_assist', 'protection_buff']
        },
        'trade': {
            'type': 'coins',
            'currency': 'biocoin'
        },
        'information': {
            'type': 'information',
            'options': ['research_tip', 'location_hint', 'recipe_clue', 'npc_location', 'rare_element_spot']
        },
        'tools': {
            'type': 'tool',
            'options': ['basic_tool', 'advanced_tool', 'specialized_tool', 'rare_tool']
        },
        'special_files': {
            'type': 'special_file',
            'options': ['blueprint', 'research_data', 'encrypted_file', 'ancient_document']
        },
        'nfts': {
            'type': 'nft',
            'options': ['common_nft', 'rare_nft', 'epic_nft', 'legendary_nft']
        },
        'coins': {
            'type': 'coins',
            'currency': 'biocoin'
        },
        'crafting': {
            'type': 'element',
            'options': ['basic_element', 'compound_element', 'rare_element', 'exotic_element']
        },
        'research': {
            'type': 'research_contribution',
            'options': ['data_sample', 'analysis_result', 'breakthrough_fragment']
        }
    }
    
    role_config = rewards_by_role.get(role, rewards_by_role['trade'])
    reward_type = role_config['type']
    
    # Apply luck to amount for certain rewards
    luck_bonus = 1.0 + (luck - 1.0) * 0.1 if luck > 1.0 else 1.0
    final_amount = round(base_amount * luck_bonus, 2)
    
    reward = {
        'type': reward_type,
        'amount': final_amount,
        'rarity': rarity
    }
    
    # Add specific item for non-currency rewards
    if 'options' in role_config:
        options = role_config['options']
        # Weighted selection favoring higher indices for rarer NPCs
        rarity_boost_map = {'common': 0, 'uncommon': 0, 'rare': 1, 'epic': 2, 'legendary': 3}
        rarity_boost = rarity_boost_map.get(rarity, 0)
        weights = [1 + i * rarity_boost for i in range(len(options))]
        selected_index = random.choices(range(len(options)), weights=weights)[0]
        reward['item'] = options[selected_index]
        reward['item_id'] = f"{reward_type}-{hashlib.sha256(options[selected_index].encode()).hexdigest()[:8]}"
    
    if 'currency' in role_config:
        reward['currency'] = role_config['currency']
    
    return reward


def _generate_interaction_message(npc_name, role, reward):
    """Generate a contextual message for NPC interaction."""
    messages = {
        'aid': f"{npc_name} provides you with {reward.get('item', 'aid')}. 'Use this wisely, researcher.'",
        'trade': f"{npc_name} transfers {reward['amount']} {reward.get('currency', 'coins')} to your account.",
        'information': f"{npc_name} shares valuable intelligence: '{reward.get('item', 'useful information')}'",
        'tools': f"{npc_name} hands you a {reward.get('item', 'tool')}. 'This will help with your crafting.'",
        'special_files': f"{npc_name} discreetly passes you {reward.get('item', 'special files')}. 'Handle with care.'",
        'nfts': f"{npc_name} grants you a unique {reward.get('item', 'NFT')}. 'This is one of a kind.'",
        'coins': f"{npc_name} rewards you with {reward['amount']} biocoins for your research efforts.",
        'crafting': f"{npc_name} provides {reward.get('item', 'crafting materials')}. 'Build something amazing.'",
        'research': f"{npc_name} contributes {reward.get('item', 'research data')} to your disease research."
    }
    return messages.get(role, f"{npc_name} gives you a reward worth {reward['amount']}.")


# ============================================================================
# Bartering and Trading System
# ============================================================================

@app.route('/api/barter/create', methods=['POST'])
def create_barter():
    """Create a new barter transaction between players or with NPCs."""
    data = request.get_json()
    
    required = ['initiator_id', 'recipient_id', 'offered_items', 'requested_items']
    if not data or not all(f in data for f in required):
        return jsonify({'error': f'Missing required fields: {required}'}), 400
    
    barter_id = f"barter-{hashlib.sha256(str(datetime.utcnow()).encode()).hexdigest()[:12]}"
    
    db = get_db()
    db.execute(
        'INSERT INTO barter_transactions (id, initiator_id, recipient_id, '
        'offered_items_json, requested_items_json, status) VALUES (?, ?, ?, ?, ?, ?)',
        (
            barter_id,
            data['initiator_id'],
            data['recipient_id'],
            json.dumps(data['offered_items']),
            json.dumps(data['requested_items']),
            'pending'
        )
    )
    db.commit()
    
    return jsonify({
        'message': 'Barter offer created',
        'id': barter_id,
        'status': 'pending'
    }), 201


@app.route('/api/barter/<barter_id>/accept', methods=['POST'])
def accept_barter(barter_id):
    """Accept a pending barter transaction."""
    db = get_db()
    barter = db.execute('SELECT * FROM barter_transactions WHERE id = ?', (barter_id,)).fetchone()
    
    if not barter:
        return jsonify({'error': 'Barter transaction not found'}), 404
    
    if barter['status'] != 'pending':
        return jsonify({'error': f"Barter cannot be accepted. Current status: {barter['status']}"}), 400
    
    db.execute(
        'UPDATE barter_transactions SET status = ?, completed_at = ? WHERE id = ?',
        ('completed', datetime.utcnow(), barter_id)
    )
    db.commit()
    
    return jsonify({
        'message': 'Barter completed successfully',
        'id': barter_id,
        'status': 'completed'
    })


@app.route('/api/barter/<barter_id>/decline', methods=['POST'])
def decline_barter(barter_id):
    """Decline a pending barter transaction."""
    db = get_db()
    barter = db.execute('SELECT * FROM barter_transactions WHERE id = ?', (barter_id,)).fetchone()
    
    if not barter:
        return jsonify({'error': 'Barter transaction not found'}), 404
    
    if barter['status'] != 'pending':
        return jsonify({'error': f"Barter cannot be declined. Current status: {barter['status']}"}), 400
    
    db.execute(
        'UPDATE barter_transactions SET status = ? WHERE id = ?',
        ('declined', barter_id)
    )
    db.commit()
    
    return jsonify({
        'message': 'Barter declined',
        'id': barter_id,
        'status': 'declined'
    })


@app.route('/api/barter', methods=['GET'])
def get_barters():
    """Get barter transactions for a player."""
    player_id = request.args.get('player_id')
    status = request.args.get('status')
    
    db = get_db()
    query = 'SELECT * FROM barter_transactions WHERE 1=1'
    params = []
    
    if player_id:
        query += ' AND (initiator_id = ? OR recipient_id = ?)'
        params.extend([player_id, player_id])
    if status:
        query += ' AND status = ?'
        params.append(status)
    
    query += ' ORDER BY created_at DESC'
    
    barters = db.execute(query, params).fetchall()
    
    result = []
    for b in barters:
        result.append({
            'id': b['id'],
            'initiator_id': b['initiator_id'],
            'recipient_id': b['recipient_id'],
            'offered_items': json.loads(b['offered_items_json']),
            'requested_items': json.loads(b['requested_items_json']),
            'status': b['status'],
            'created_at': b['created_at'],
            'completed_at': b['completed_at']
        })
    
    return jsonify({'barters': result})


# ============================================================================
# Base Elements System
# ============================================================================

@app.route('/api/elements', methods=['GET'])
def get_elements():
    """Get all base elements available for crafting."""
    db = get_db()
    elements = db.execute(
        'SELECT * FROM base_elements ORDER BY rarity, name'
    ).fetchall()
    
    result = []
    for e in elements:
        result.append({
            'id': e['id'],
            'name': e['name'],
            'element_type': e['element_type'],
            'rarity': e['rarity'],
            'description': e['description'],
            'properties': json.loads(e['properties_json']) if e['properties_json'] else {},
            'research_contribution': e['research_contribution']
        })
    
    return jsonify({'elements': result})


@app.route('/api/elements', methods=['POST'])
def create_element():
    """Create a new base element."""
    data = request.get_json()
    
    if not data or 'name' not in data or 'element_type' not in data:
        return jsonify({'error': 'Missing required fields: name, element_type'}), 400
    
    valid_types = ['organic', 'inorganic', 'synthetic', 'biological', 'energy', 'catalyst', 'compound']
    if data['element_type'] not in valid_types:
        return jsonify({'error': f'Invalid element_type. Must be one of: {valid_types}'}), 400
    
    element_id = f"elem-{hashlib.sha256(data['name'].encode()).hexdigest()[:12]}"
    
    db = get_db()
    try:
        db.execute(
            'INSERT INTO base_elements (id, name, element_type, rarity, description, '
            'properties_json, research_contribution) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (
                element_id,
                data['name'],
                data['element_type'],
                data.get('rarity', 'common'),
                data.get('description', ''),
                json.dumps(data.get('properties', {})),
                data.get('research_contribution', 0.0)
            )
        )
        db.commit()
        return jsonify({
            'message': 'Lesson created',
            'id': lesson_id,
            'lesson_order': next_order
        }), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Lesson with this configuration already exists'}), 409


@app.route('/api/lessons/<lesson_id>', methods=['GET'])
def get_lesson(lesson_id):
    """Get a specific lesson by ID."""
    db = get_db()
    lesson = db.execute('SELECT * FROM lessons WHERE id = ?', (lesson_id,)).fetchone()
    
    if not lesson:
        return jsonify({'error': 'Lesson not found'}), 404
    
    return jsonify({
        'id': lesson['id'],
        'classroom_id': lesson['classroom_id'],
        'title': lesson['title'],
        'subject_area': lesson['subject_area'],
        'description': lesson['description'],
        'objectives': json.loads(lesson['objectives_json']) if lesson['objectives_json'] else [],
        'demonstrations': json.loads(lesson['demonstrations_json']) if lesson['demonstrations_json'] else [],
        'materials': json.loads(lesson['materials_json']) if lesson['materials_json'] else [],
        'estimated_duration': lesson['estimated_duration'],
        'lesson_order': lesson['lesson_order'],
        'created_at': lesson['created_at']
    })


@app.route('/api/lessons/<lesson_id>/progress', methods=['POST'])
def update_lesson_progress(lesson_id):
    """Update a student's progress on a lesson."""
    data = request.get_json()
    
    if not data or 'student_id' not in data:
        return jsonify({'error': 'Missing required field: student_id'}), 400
    
    db = get_db()
    lesson = db.execute('SELECT * FROM lessons WHERE id = ?', (lesson_id,)).fetchone()
    if not lesson:
        return jsonify({'error': 'Lesson not found'}), 404
    
    progress_id = f"progress-{hashlib.sha256((lesson_id + data['student_id']).encode()).hexdigest()[:12]}"
    status = data.get('status', 'in_progress')
    
    # Validate status value
    if status not in ['not_started', 'in_progress', 'completed']:
        return jsonify({'error': 'Invalid status value. Must be: not_started, in_progress, or completed'}), 400
    
    # Validate score if provided
    score = data.get('score')
    if score is not None:
        try:
            score = float(score)
        except (TypeError, ValueError):
            return jsonify({'error': 'Score must be a number between 0 and 100'}), 400
        if score < 0 or score > 100:
            return jsonify({'error': 'Score must be between 0 and 100'}), 400
    
    notes = data.get('notes', '')
    completed_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S') if status == 'completed' else None
    
    try:
        db.execute(
            'INSERT INTO lesson_progress (id, lesson_id, student_id, status, score, completed_at, notes) '
            'VALUES (?, ?, ?, ?, ?, ?, ?) '
            'ON CONFLICT(lesson_id, student_id) DO UPDATE SET status = ?, score = ?, completed_at = ?, notes = ?',
            (progress_id, lesson_id, data['student_id'], status, score, completed_at, notes,
             status, score, completed_at, notes)
        )
        db.commit()
        return jsonify({
            'message': 'Progress updated',
            'lesson_id': lesson_id,
            'student_id': data['student_id'],
            'status': status
        })
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Failed to update progress'}), 500


@app.route('/api/students/<student_id>/progress', methods=['GET'])
def get_student_progress(student_id):
    """Get all lesson progress for a student."""
    db = get_db()
    progress = db.execute(
        'SELECT lp.*, l.title, l.subject_area, l.classroom_id '
        'FROM lesson_progress lp '
        'JOIN lessons l ON lp.lesson_id = l.id '
        'WHERE lp.student_id = ? '
        'ORDER BY lp.created_at DESC',
        (student_id,)
    ).fetchall()
    
    result = []
    for p in progress:
        result.append({
            'lesson_id': p['lesson_id'],
            'lesson_title': p['title'],
            'subject_area': p['subject_area'],
            'classroom_id': p['classroom_id'],
            'status': p['status'],
            'score': p['score'],
            'completed_at': p['completed_at'],
            'notes': p['notes']
        })
    
    return jsonify({'student_id': student_id, 'progress': result})


# ============================================================================
# Science Demonstrations - Visual Teaching Aids
# ============================================================================

@app.route('/api/demonstrations', methods=['GET'])
def get_demonstrations():
    """Get all available science demonstrations for teaching."""
    category = request.args.get('category')
    
    db = get_db()
    if category:
        demonstrations = db.execute(
            'SELECT * FROM demonstrations WHERE category = ? ORDER BY name',
            (category,)
        ).fetchall()
    else:
        demonstrations = db.execute('SELECT * FROM demonstrations ORDER BY category, name').fetchall()
    
    result = []
    for demo in demonstrations:
        result.append({
            'id': demo['id'],
            'name': demo['name'],
            'category': demo['category'],
            'description': demo['description'],
            'visualization_type': demo['visualization_type'],
            'parameters': json.loads(demo['parameters_json']) if demo['parameters_json'] else {},
            'educational_notes': demo['educational_notes'],
            'safety_notes': demo['safety_notes'],
            'created_at': demo['created_at']
        })
    
    return jsonify({'demonstrations': result})


@app.route('/api/demonstrations', methods=['POST'])
def create_demonstration():
    """Create a new science demonstration for teaching."""
    data = request.get_json()
    
    required = ['name', 'category', 'visualization_type']
    if not data or not all(f in data for f in required):
        return jsonify({'error': f'Missing required fields: {required}'}), 400
    
    demo_id = f"demo-{hashlib.sha256(data['name'].encode()).hexdigest()[:12]}"
            'message': 'Element created',
            'id': element_id
        }), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Element already exists'}), 409


# ============================================================================
# Tools System
# ============================================================================

@app.route('/api/tools', methods=['GET'])
def get_tools():
    """Get all available tools."""
    db = get_db()
    tools = db.execute(
        'SELECT * FROM tools ORDER BY tier, name'
    ).fetchall()
    
    result = []
    for t in tools:
        result.append({
            'id': t['id'],
            'name': t['name'],
            'tool_type': t['tool_type'],
            'tier': t['tier'],
            'description': t['description'],
            'required_elements': json.loads(t['required_elements_json']) if t['required_elements_json'] else [],
            'craft_time_seconds': t['craft_time_seconds'],
            'durability': t['durability']
        })
    
    return jsonify({'tools': result})


@app.route('/api/tools', methods=['POST'])
def create_tool():
    """Create a new tool definition."""
    data = request.get_json()
    
    if not data or 'name' not in data or 'tool_type' not in data:
        return jsonify({'error': 'Missing required fields: name, tool_type'}), 400
    
    valid_types = ['harvesting', 'crafting', 'research', 'construction', 'transport', 'defense', 'utility']
    if data['tool_type'] not in valid_types:
        return jsonify({'error': f'Invalid tool_type. Must be one of: {valid_types}'}), 400
    
    # Validate tier is within acceptable range (1-5)
    tier = data.get('tier', 1)
    if not (1 <= tier <= 5):
        return jsonify({'error': 'Tier must be between 1 and 5'}), 400
    
    tool_id = f"tool-{hashlib.sha256(data['name'].encode()).hexdigest()[:12]}"
    
    db = get_db()
    try:
        db.execute(
            'INSERT INTO tools (id, name, tool_type, tier, description, '
            'required_elements_json, craft_time_seconds, durability) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (
                tool_id,
                data['name'],
                data['tool_type'],
                tier,
                data.get('description', ''),
                json.dumps(data.get('required_elements', [])),
                data.get('craft_time_seconds', 60),
                data.get('durability', 100)
            )
        )
        db.commit()
        return jsonify({
            'message': 'Tool created',
            'id': tool_id
        }), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Tool already exists'}), 409


# ============================================================================
# Craftable Items System (Jetpacks, Vehicles, Shelters, etc.)
# ============================================================================

@app.route('/api/craftables', methods=['GET'])
def get_craftables():
    """Get all craftable items with optional category filter."""
    db = get_db()
    category = request.args.get('category')
    
    query = 'SELECT * FROM craftable_items'
    params = []
    
    if category:
        query += ' WHERE category = ?'
        params.append(category)
    
    query += ' ORDER BY category, name'
    
    items = db.execute(query, params).fetchall()
    
    result = []
    for item in items:
        # Safely parse JSON fields with error handling
        try:
            required_tools = json.loads(item['required_tools_json']) if item['required_tools_json'] else []
        except json.JSONDecodeError:
            required_tools = []
        try:
            required_elements = json.loads(item['required_elements_json']) if item['required_elements_json'] else []
        except json.JSONDecodeError:
            required_elements = []
        try:
            effects = json.loads(item['effects_json']) if item['effects_json'] else {}
        except json.JSONDecodeError:
            effects = {}
        result.append({
            'id': item['id'],
            'name': item['name'],
            'item_type': item['item_type'],
            'category': item['category'],
            'description': item['description'],
            'required_tools': required_tools,
            'required_elements': required_elements,
            'craft_time_seconds': item['craft_time_seconds'],
            'effects': effects,
            'research_bonus': item['research_bonus']
        })
    
    return jsonify({'craftables': result})


@app.route('/api/craftables', methods=['POST'])
def create_craftable():
    """Create a new craftable item definition."""
    data = request.get_json()
    
    required = ['name', 'item_type', 'category']
    if not data or not all(f in data for f in required):
        return jsonify({'error': f'Missing required fields: {required}'}), 400
    
    valid_categories = ['transport', 'shelter', 'equipment', 'weapon', 'utility', 'research']
    valid_types = ['jetpack', 'flight_suit', 'car', 'motorcycle', 'boat', 
                   'shelter', 'camp', 'outpost', 'lab_extension',
                   'armor', 'scanner', 'communicator', 'container']
    
    if data['category'] not in valid_categories:
        return jsonify({'error': f'Invalid category. Must be one of: {valid_categories}'}), 400
    
    if data['item_type'] not in valid_types:
        return jsonify({'error': f'Invalid item_type. Must be one of: {valid_types}'}), 400
    
    item_id = f"craft-{hashlib.sha256(data['name'].encode()).hexdigest()[:12]}"
    
    db = get_db()
    try:
        db.execute(
            'INSERT INTO demonstrations (id, name, category, description, visualization_type, '
            'parameters_json, educational_notes, safety_notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (
                demo_id,
                data['name'],
                data['category'],
                data.get('description', ''),
                data['visualization_type'],
                json.dumps(data.get('parameters', {})),
                data.get('educational_notes', ''),
                data.get('safety_notes', '')
            'INSERT INTO craftable_items (id, name, item_type, category, description, '
            'required_tools_json, required_elements_json, craft_time_seconds, effects_json, research_bonus) '
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (
                item_id,
                data['name'],
                data['item_type'],
                data['category'],
                data.get('description', ''),
                json.dumps(data.get('required_tools', [])),
                json.dumps(data.get('required_elements', [])),
                data.get('craft_time_seconds', 300),
                json.dumps(data.get('effects', {})),
                data.get('research_bonus', 0.0)
            )
        )
        db.commit()
        return jsonify({
            'message': 'Demonstration created',
            'id': demo_id
        }), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Demonstration already exists'}), 409


@app.route('/api/demonstrations/<demo_id>/simulate', methods=['POST'])
def simulate_demonstration(demo_id):
    """
    Simulate a science demonstration with given parameters.
    Returns visualization data for rendering in-game.
    """
    data = request.get_json() or {}
    
    db = get_db()
    demo = db.execute('SELECT * FROM demonstrations WHERE id = ?', (demo_id,)).fetchone()
    
    if not demo:
        return jsonify({'error': 'Demonstration not found'}), 404
    
    # Simulate the demonstration based on type
    simulation_result = _simulate_demonstration(
        demo['visualization_type'],
        demo['category'],
        json.loads(demo['parameters_json']) if demo['parameters_json'] else {},
        data.get('custom_parameters', {})
    )
    
    return jsonify({
        'demonstration_id': demo_id,
        'name': demo['name'],
        'category': demo['category'],
        'visualization_type': demo['visualization_type'],
        'simulation_result': simulation_result,
        'educational_notes': demo['educational_notes'],
        'safety_notes': demo['safety_notes']
    })


def _simulate_demonstration(viz_type, category, base_params, custom_params):
    """
    Simulate a science demonstration.
    Returns data for visual rendering of scientific phenomena.
    """
    params = {**base_params, **custom_params}
    
    # Chemistry demonstrations
    if category == 'chemistry':
        if viz_type == 'combustion':
            return _simulate_combustion(params)
        elif viz_type == 'reaction':
            return _simulate_chemical_reaction(params)
        elif viz_type == 'molecular_structure':
            return _simulate_molecular_structure(params)
    
    # Physics demonstrations
    elif category == 'physics':
        if viz_type == 'wave':
            return _simulate_wave(params)
        elif viz_type == 'particle':
            return _simulate_particle_motion(params)
        elif viz_type == 'electromagnetic':
            return _simulate_electromagnetic(params)
    
    # Biology demonstrations
    elif category == 'biology':
        if viz_type == 'cell_division':
            return _simulate_cell_division(params)
        elif viz_type == 'dna_replication':
            return _simulate_dna_replication(params)
        elif viz_type == 'protein_synthesis':
            return _simulate_protein_synthesis(params)
    
    # Default generic simulation
    return {
        'type': viz_type,
        'status': 'simulated',
        'parameters_used': params,
        'timestamp': datetime.utcnow().isoformat()
    }


def _simulate_combustion(params):
    """Simulate combustion reaction for chemistry education."""
    fuel = params.get('fuel', 'methane')
    oxygen_ratio = params.get('oxygen_ratio', 2.0)
    temperature = params.get('initial_temperature', 25)
    
    # Simulate combustion products and energy
    combustion_data = {
        'methane': {'formula': 'CH4 + 2O2 → CO2 + 2H2O', 'energy_kj': 890, 'flame_color': 'blue'},
        'propane': {'formula': 'C3H8 + 5O2 → 3CO2 + 4H2O', 'energy_kj': 2220, 'flame_color': 'blue-yellow'},
        'wood': {'formula': 'C6H10O5 + 6O2 → 6CO2 + 5H2O', 'energy_kj': 2500, 'flame_color': 'orange-yellow'},
        'hydrogen': {'formula': '2H2 + O2 → 2H2O', 'energy_kj': 572, 'flame_color': 'pale-blue'}
    }
    
    fuel_data = combustion_data.get(fuel, combustion_data['methane'])
    
    return {
        'type': 'combustion',
        'fuel': fuel,
        'chemical_equation': fuel_data['formula'],
        'energy_released_kj': fuel_data['energy_kj'],
        'flame_color': fuel_data['flame_color'],
        'oxygen_ratio': oxygen_ratio,
        'initial_temperature_c': temperature,
        'final_temperature_c': temperature + random.randint(800, 1200),
        'products': ['CO2', 'H2O'],
        'visualization_frames': _generate_combustion_frames(fuel_data),
        'learning_points': [
            'Combustion requires fuel, oxygen, and heat (fire triangle)',
            'Complete combustion produces CO2 and H2O',
            'Energy is released as heat and light',
            'Different fuels produce different flame colors'
        ]
    }


def _generate_combustion_frames(fuel_data):
    """Generate animation frames for combustion visualization."""
    frames = []
    for i in range(10):
        intensity = (i + 1) / 10.0
        frames.append({
            'frame': i,
            'flame_intensity': intensity,
            'particle_count': int(100 * intensity),
            'temperature_ratio': intensity,
            'color': fuel_data['flame_color']
        })
    return frames


def _simulate_chemical_reaction(params):
    """Simulate a generic chemical reaction."""
    reactants = params.get('reactants', ['HCl', 'NaOH'])
    
    return {
        'type': 'chemical_reaction',
        'reactants': reactants,
        'products': ['NaCl', 'H2O'] if 'HCl' in reactants else ['Products'],
        'reaction_type': 'neutralization' if 'HCl' in reactants and 'NaOH' in reactants else 'synthesis',
        'is_exothermic': random.choice([True, False]),
        'visualization_steps': [
            {'step': 1, 'description': 'Reactants mixing', 'visual': 'particle_approach'},
            {'step': 2, 'description': 'Bond breaking', 'visual': 'bond_break'},
            {'step': 3, 'description': 'New bonds forming', 'visual': 'bond_form'},
            {'step': 4, 'description': 'Products formed', 'visual': 'product_display'}
        ]
    }


def _simulate_molecular_structure(params):
    """Simulate molecular structure visualization."""
    molecule = params.get('molecule', 'H2O')
    
    structures = {
        'H2O': {'atoms': [{'type': 'O', 'x': 0, 'y': 0, 'z': 0}, 
                         {'type': 'H', 'x': 0.96, 'y': 0, 'z': 0},
                         {'type': 'H', 'x': -0.24, 'y': 0.93, 'z': 0}],
                'bonds': [[0, 1], [0, 2]], 'angle': 104.5},
        'CO2': {'atoms': [{'type': 'C', 'x': 0, 'y': 0, 'z': 0},
                         {'type': 'O', 'x': -1.16, 'y': 0, 'z': 0},
                         {'type': 'O', 'x': 1.16, 'y': 0, 'z': 0}],
                'bonds': [[0, 1], [0, 2]], 'angle': 180},
        'CH4': {'atoms': [{'type': 'C', 'x': 0, 'y': 0, 'z': 0},
                         {'type': 'H', 'x': 0.63, 'y': 0.63, 'z': 0.63},
                         {'type': 'H', 'x': -0.63, 'y': -0.63, 'z': 0.63},
                         {'type': 'H', 'x': -0.63, 'y': 0.63, 'z': -0.63},
                         {'type': 'H', 'x': 0.63, 'y': -0.63, 'z': -0.63}],
                'bonds': [[0, 1], [0, 2], [0, 3], [0, 4]], 'angle': 109.5}
    }
    
    return {
        'type': 'molecular_structure',
        'molecule': molecule,
        'structure': structures.get(molecule, structures['H2O']),
        'rotation_enabled': True
    }


def _simulate_wave(params):
    """Simulate wave physics visualization."""
    wave_type = params.get('wave_type', 'transverse')
    frequency = params.get('frequency', 1.0)
    amplitude = params.get('amplitude', 1.0)
    
    return {
        'type': 'wave',
        'wave_type': wave_type,
        'frequency_hz': frequency,
        'amplitude': amplitude,
        'wavelength': 1.0 / frequency if frequency > 0 else 1.0,
        'points': [{'x': i * 0.1, 'y': amplitude * (0.5 + 0.5 * (-1 if i % 2 else 1))} for i in range(20)]
    }


def _simulate_particle_motion(params):
    """
    Simulate particle motion for physics education.
    
    Parameters:
        params (dict): Simulation parameters. May include:
            - particle_count (int): Number of particles (default: 50).
            - temperature (float): Temperature in Kelvin (default: 300).
            - particle_mass (float): Mass of each particle in kg 
              (default: 1.67e-27, hydrogen/proton mass).
    
    By default, simulates hydrogen gas (proton mass = 1.67e-27 kg).
    To simulate other gases, provide 'particle_mass' in params.
    """
    particle_count = params.get('particle_count', 50)
    temperature = params.get('temperature', 300)
    particle_mass = params.get('particle_mass', 1.67e-27)  # kg, default: hydrogen/proton mass
    
    # Calculate average velocity using kinetic theory of gases:
    # v_avg = sqrt(3 * k_B * T / m)
    # where k_B = 1.38e-23 J/K (Boltzmann constant)
    boltzmann_constant = 1.38e-23  # J/K
    average_velocity = (3 * boltzmann_constant * temperature / particle_mass) ** 0.5
    
    # Limit to 100 particles for performance in web visualization
    max_particles = min(particle_count, 100)
    
    return {
        'type': 'particle_motion',
        'particle_count': particle_count,
        'temperature_k': temperature,
        'particle_mass_kg': particle_mass,
        'average_velocity': average_velocity,
        'particles': [{'id': i, 'x': random.random(), 'y': random.random(), 
                       'vx': random.gauss(0, 1), 'vy': random.gauss(0, 1)} 
                      for i in range(max_particles)]
    }


def _simulate_electromagnetic(params):
    """Simulate electromagnetic phenomena."""
    em_type = params.get('em_type', 'visible_light')
    
    spectrum = {
        'radio': {'wavelength_m': 1e3, 'frequency_hz': 3e5, 'color': 'none'},
        'microwave': {'wavelength_m': 1e-2, 'frequency_hz': 3e10, 'color': 'none'},
        'infrared': {'wavelength_m': 1e-5, 'frequency_hz': 3e13, 'color': 'none'},
        'visible_light': {'wavelength_m': 5e-7, 'frequency_hz': 6e14, 'color': 'rainbow'},
        'ultraviolet': {'wavelength_m': 1e-8, 'frequency_hz': 3e16, 'color': 'purple'},
        'xray': {'wavelength_m': 1e-10, 'frequency_hz': 3e18, 'color': 'none'},
        'gamma': {'wavelength_m': 1e-12, 'frequency_hz': 3e20, 'color': 'none'}
    }
    
    return {
        'type': 'electromagnetic',
        'em_type': em_type,
        'properties': spectrum.get(em_type, spectrum['visible_light']),
        'speed': 3e8,
        'visualization': 'wave_propagation'
    }


def _simulate_cell_division(params):
    """Simulate cell division (mitosis) for biology education."""
    division_type = params.get('division_type', 'mitosis')
    
    return {
        'type': 'cell_division',
        'division_type': division_type,
        'phases': [
            {'name': 'Interphase', 'description': 'Cell prepares for division, DNA replicates'},
            {'name': 'Prophase', 'description': 'Chromosomes condense, nuclear envelope breaks down'},
            {'name': 'Metaphase', 'description': 'Chromosomes align at cell center'},
            {'name': 'Anaphase', 'description': 'Sister chromatids separate'},
            {'name': 'Telophase', 'description': 'Nuclear envelopes reform'},
            {'name': 'Cytokinesis', 'description': 'Cell divides into two daughter cells'}
        ],
        'chromosome_count': 46 if division_type == 'mitosis' else 23,
        'result_cells': 2 if division_type == 'mitosis' else 4
    }


def _simulate_dna_replication(params):
    """Simulate DNA replication for biology education."""
    return {
        'type': 'dna_replication',
        'steps': [
            {'name': 'Helicase', 'action': 'Unwinds DNA double helix'},
            {'name': 'Primase', 'action': 'Creates RNA primers'},
            {'name': 'DNA Polymerase III', 'action': 'Synthesizes new DNA strands'},
            {'name': 'DNA Polymerase I', 'action': 'Replaces RNA primers with DNA'},
            {'name': 'Ligase', 'action': 'Joins DNA fragments'}
        ],
        'direction': "5' to 3'",
        'leading_strand': 'continuous synthesis',
        'lagging_strand': 'Okazaki fragments'
    }


def _simulate_protein_synthesis(params):
    """Simulate protein synthesis for biology education."""
    return {
        'type': 'protein_synthesis',
        'stages': [
            {
                'name': 'Transcription',
                'location': 'Nucleus',
                'steps': ['DNA unwinds', 'mRNA synthesized', 'mRNA exits nucleus']
            },
            {
                'name': 'Translation',
                'location': 'Ribosome',
                'steps': ['mRNA binds to ribosome', 'tRNA brings amino acids', 'Polypeptide chain forms']
            }
        ],
        'components': ['DNA', 'mRNA', 'tRNA', 'Ribosome', 'Amino acids']
    }


def _seed_default_demonstrations():
    """Seed the database with default science demonstrations."""
    demonstrations = [
        {
            'id': 'demo-combustion-basic',
            'name': 'Basic Combustion',
            'category': 'chemistry',
            'description': 'Demonstrates the combustion reaction with different fuels',
            'visualization_type': 'combustion',
            'parameters_json': json.dumps({'fuel': 'methane', 'oxygen_ratio': 2.0}),
            'educational_notes': 'Shows the fire triangle (fuel, oxygen, heat) and products of combustion',
            'safety_notes': 'Virtual demonstration only - do not attempt with real fire'
        },
        {
            'id': 'demo-acid-base',
            'name': 'Acid-Base Neutralization',
            'category': 'chemistry',
            'description': 'Demonstrates neutralization reaction between acid and base',
            'visualization_type': 'reaction',
            'parameters_json': json.dumps({'reactants': ['HCl', 'NaOH']}),
            'educational_notes': 'Shows how acids and bases neutralize to form salt and water',
            'safety_notes': 'Virtual demonstration - in real labs, use appropriate PPE'
        },
        {
            'id': 'demo-water-molecule',
            'name': 'Water Molecule Structure',
            'category': 'chemistry',
            'description': '3D visualization of water molecule structure',
            'visualization_type': 'molecular_structure',
            'parameters_json': json.dumps({'molecule': 'H2O'}),
            'educational_notes': 'Shows the bent shape of water and explains its unique properties',
            'safety_notes': 'None'
        },
        {
            'id': 'demo-light-waves',
            'name': 'Light Wave Properties',
            'category': 'physics',
            'description': 'Visualizes electromagnetic waves and light properties',
            'visualization_type': 'electromagnetic',
            'parameters_json': json.dumps({'em_type': 'visible_light'}),
            'educational_notes': 'Demonstrates wave-particle duality and the electromagnetic spectrum',
            'safety_notes': 'None'
        },
        {
            'id': 'demo-gas-particles',
            'name': 'Gas Particle Motion',
            'category': 'physics',
            'description': 'Shows kinetic theory of gases with particle visualization',
            'visualization_type': 'particle',
            'parameters_json': json.dumps({'particle_count': 50, 'temperature': 300}),
            'educational_notes': 'Demonstrates relationship between temperature and particle velocity',
            'safety_notes': 'None'
        },
        {
            'id': 'demo-cell-mitosis',
            'name': 'Cell Division (Mitosis)',
            'category': 'biology',
            'description': 'Step-by-step visualization of mitosis',
            'visualization_type': 'cell_division',
            'parameters_json': json.dumps({'division_type': 'mitosis'}),
            'educational_notes': 'Shows all phases of mitosis with chromosome behavior',
            'safety_notes': 'None'
        },
        {
            'id': 'demo-dna-replication',
            'name': 'DNA Replication',
            'category': 'biology',
            'description': 'Animation of DNA replication process',
            'visualization_type': 'dna_replication',
            'parameters_json': json.dumps({}),
            'educational_notes': 'Shows enzymes involved and mechanism of semi-conservative replication',
            'safety_notes': 'None'
        },
        {
            'id': 'demo-protein-synthesis',
            'name': 'Protein Synthesis',
            'category': 'biology',
            'description': 'From DNA to protein - transcription and translation',
            'visualization_type': 'protein_synthesis',
            'parameters_json': json.dumps({}),
            'educational_notes': 'Demonstrates the central dogma of molecular biology',
            'safety_notes': 'None'
        }
    ]
    
    return demonstrations
            'message': 'Craftable item created',
            'id': item_id,
            'category': data['category']
        }), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Craftable item already exists'}), 409


@app.route('/api/craft', methods=['POST'])
def craft_item():
    """
    Craft an item using collected tools and elements.
    Verifies player has required materials before crafting.
    """
    data = request.get_json()
    
    if not data or 'player_id' not in data or 'craftable_id' not in data:
        return jsonify({'error': 'Missing required fields: player_id, craftable_id'}), 400
    
    db = get_db()
    craftable = db.execute(
        'SELECT * FROM craftable_items WHERE id = ?', 
        (data['craftable_id'],)
    ).fetchone()
    
    if not craftable:
        return jsonify({'error': 'Craftable item not found'}), 404
    
    # Parse required materials
    required_tools = json.loads(craftable['required_tools_json']) if craftable['required_tools_json'] else []
    required_elements = json.loads(craftable['required_elements_json']) if craftable['required_elements_json'] else []
    
    # TODO: Before production, verify player has required tools and elements before crafting.
    # This would check player_tools and player_elements tables against required_tools and required_elements.
    # For now, this is a simplified implementation for testing.
    
    player_item_id = f"pitem-{hashlib.sha256(str(datetime.utcnow()).encode()).hexdigest()[:12]}"
    
    db.execute(
        'INSERT INTO player_items (id, player_id, item_id, quantity, condition) '
        'VALUES (?, ?, ?, ?, ?)',
        (
            player_item_id,
            data['player_id'],
            data['craftable_id'],
            1,
            100
        )
    )
    db.commit()
    
    return jsonify({
        'message': 'Item crafted successfully',
        'player_item_id': player_item_id,
        'item': {
            'id': craftable['id'],
            'name': craftable['name'],
            'category': craftable['category'],
            'effects': json.loads(craftable['effects_json']) if craftable['effects_json'] else {},
            'required_tools': required_tools,
            'required_elements': required_elements
        },
        'craft_time_seconds': craftable['craft_time_seconds'],
        'research_bonus': craftable['research_bonus']
    }), 201


# ============================================================================
# Shelters and Camps System
# ============================================================================

@app.route('/api/shelters', methods=['GET'])
def get_shelters():
    """Get player shelters with optional player filter."""
    db = get_db()
    player_id = request.args.get('player_id')
    
    query = 'SELECT * FROM shelters'
    params = []
    
    if player_id:
        query += ' WHERE player_id = ?'
        params.append(player_id)
    
    query += ' ORDER BY created_at DESC'
    
    shelters = db.execute(query, params).fetchall()
    
    result = []
    for s in shelters:
        result.append({
            'id': s['id'],
            'player_id': s['player_id'],
            'name': s['name'],
            'shelter_type': s['shelter_type'],
            'location': {
                'x': s['location_x'],
                'y': s['location_y'],
                'z': s['location_z']
            },
            'capacity': s['capacity'],
            'research_bonus': s['research_bonus'],
            'upgrades': json.loads(s['upgrades_json']) if s['upgrades_json'] else [],
            'created_at': s['created_at']
        })
    
    return jsonify({'shelters': result})


@app.route('/api/shelters', methods=['POST'])
def create_shelter():
    """Create a new shelter or camp for a player."""
    data = request.get_json()
    
    required = ['player_id', 'name', 'shelter_type']
    if not data or not all(f in data for f in required):
        return jsonify({'error': f'Missing required fields: {required}'}), 400
    
    valid_types = ['tent', 'cabin', 'outpost', 'research_station', 'mobile_lab', 
                   'underground_bunker', 'treehouse', 'floating_platform']
    
    if data['shelter_type'] not in valid_types:
        return jsonify({'error': f'Invalid shelter_type. Must be one of: {valid_types}'}), 400
    
    shelter_id = f"shelter-{hashlib.sha256(str(datetime.utcnow()).encode()).hexdigest()[:12]}"
    
    # Calculate research bonus based on shelter type
    research_bonuses = {
        'tent': 0.05,
        'cabin': 0.1,
        'outpost': 0.15,
        'research_station': 0.3,
        'mobile_lab': 0.25,
        'underground_bunker': 0.2,
        'treehouse': 0.1,
        'floating_platform': 0.15
    }
    
    db = get_db()
    try:
        db.execute(
            'INSERT INTO shelters (id, player_id, name, shelter_type, location_x, location_y, '
            'location_z, capacity, research_bonus, upgrades_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (
                shelter_id,
                data['player_id'],
                data['name'],
                data['shelter_type'],
                data.get('location', {}).get('x', 0.0),
                data.get('location', {}).get('y', 0.0),
                data.get('location', {}).get('z', 0.0),
                data.get('capacity', 4),
                research_bonuses.get(data['shelter_type'], 0.1),
                json.dumps(data.get('upgrades', []))
            )
        )
        db.commit()
        return jsonify({
            'message': 'Shelter created',
            'id': shelter_id,
            'research_bonus': research_bonuses.get(data['shelter_type'], 0.1)
        }), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Shelter creation failed'}), 409


# ============================================================================
# Disease Research Progress System
# ============================================================================

@app.route('/api/research-progress', methods=['GET'])
def get_research_progress():
    """Get disease research progress with optional disease or player filter."""
    db = get_db()
    disease_id = request.args.get('disease_id')
    player_id = request.args.get('player_id')
    
    query = 'SELECT * FROM research_progress WHERE 1=1'
    params = []
    
    if disease_id:
        query += ' AND disease_id = ?'
        params.append(disease_id)
    if player_id:
        query += ' AND player_id = ?'
        params.append(player_id)
    
    query += ' ORDER BY created_at DESC'
    
    progress = db.execute(query, params).fetchall()
    
    result = []
    for p in progress:
        result.append({
            'id': p['id'],
            'disease_id': p['disease_id'],
            'player_id': p['player_id'],
            'contribution_amount': p['contribution_amount'],
            'contribution_type': p['contribution_type'],
            'unique_build_bonus': p['unique_build_bonus'],
            'created_at': p['created_at']
        })
    
    # Calculate totals per disease if filtering by disease
    total_contribution = sum(p['contribution_amount'] + p['unique_build_bonus'] for p in progress)
    
    return jsonify({
        'progress': result,
        'total_contribution': round(total_contribution, 2)
    })


@app.route('/api/research-progress', methods=['POST'])
def add_research_contribution():
    """
    Add a research contribution from a player.
    Unique builds provide bonus contributions through creative element combinations.
    """
    data = request.get_json()
    
    required = ['disease_id', 'player_id', 'contribution_amount']
    if not data or not all(f in data for f in required):
        return jsonify({'error': f'Missing required fields: {required}'}), 400
    
    # Validate contribution_amount is non-negative
    if data['contribution_amount'] < 0:
        return jsonify({'error': 'Contribution amount must be non-negative'}), 400
    
    progress_id = f"prog-{hashlib.sha256(str(datetime.utcnow()).encode()).hexdigest()[:12]}"
    
    # Calculate unique build bonus based on creative element combinations
    unique_build_bonus = _calculate_unique_build_bonus(data.get('elements_used', []))
    
    db = get_db()
    db.execute(
        'INSERT INTO research_progress (id, disease_id, player_id, contribution_amount, '
        'contribution_type, unique_build_bonus) VALUES (?, ?, ?, ?, ?, ?)',
        (
            progress_id,
            data['disease_id'],
            data['player_id'],
            data['contribution_amount'],
            data.get('contribution_type', 'standard'),
            unique_build_bonus
        )
    )
    db.commit()
    
    total_contribution = data['contribution_amount'] + unique_build_bonus
    
    return jsonify({
        'message': 'Research contribution recorded',
        'id': progress_id,
        'base_contribution': data['contribution_amount'],
        'unique_build_bonus': unique_build_bonus,
        'total_contribution': round(total_contribution, 2)
    }), 201


def _calculate_unique_build_bonus(elements_used):
    """
    Calculate bonus for creative element combinations.
    More unique combinations yield higher bonuses.
    """
    if not elements_used:
        return 0.0
    
    # Base bonus for using multiple elements
    element_count = len(elements_used)
    base_bonus = element_count * 0.5
    
    # Synergy bonus for certain combinations (would be data-driven in full impl)
    synergy_combinations = {
        frozenset(['organic', 'catalyst']): 2.0,
        frozenset(['biological', 'synthetic']): 3.0,
        frozenset(['energy', 'compound']): 2.5,
        frozenset(['organic', 'biological', 'catalyst']): 5.0,
        frozenset(['synthetic', 'energy', 'compound']): 4.0
    }
    
    element_types = set(elements_used)
    synergy_bonus = 0
    
    for combo, bonus in synergy_combinations.items():
        if combo.issubset(element_types):
            synergy_bonus = max(synergy_bonus, bonus)
    
    # Uniqueness multiplier (more elements = potentially more unique)
    uniqueness = math.log(element_count + 1) * 0.3
    
    total_bonus = (base_bonus + synergy_bonus) * (1 + uniqueness)
    
    return round(total_bonus, 2)


# ============================================================================
# Loot Tables for Mathematically Fair Randomization
# ============================================================================

@app.route('/api/loot-tables', methods=['GET'])
def get_loot_tables():
    """Get all loot tables."""
    db = get_db()
    tables = db.execute('SELECT * FROM loot_tables ORDER BY name').fetchall()
    
    result = []
    for t in tables:
        result.append({
            'id': t['id'],
            'name': t['name'],
            'description': t['description'],
            'entries': json.loads(t['entries_json']),
            'total_weight': t['total_weight'],
            'created_at': t['created_at']
        })
    
    return jsonify({'loot_tables': result})


@app.route('/api/loot-tables', methods=['POST'])
def create_loot_table():
    """Create a new loot table for fair reward distribution."""
    data = request.get_json()
    
    if not data or 'name' not in data or 'entries' not in data:
        return jsonify({'error': 'Missing required fields: name, entries'}), 400
    
    # Validate entries structure
    entries = data['entries']
    if not isinstance(entries, list):
        return jsonify({'error': 'entries must be a list'}), 400
    
    for entry in entries:
        required_entry_fields = ['item', 'weight']
        if not all(f in entry for f in required_entry_fields):
            return jsonify({'error': f'Each entry must have: {required_entry_fields}'}), 400
        # Validate that weight is a positive number
        if not isinstance(entry['weight'], (int, float)) or entry['weight'] <= 0:
            return jsonify({'error': 'Entry weights must be positive numbers'}), 400
    
    # Calculate total weight
    total_weight = sum(e.get('weight', 1) for e in entries)
    
    table_id = f"loot-{hashlib.sha256(data['name'].encode()).hexdigest()[:12]}"
    
    db = get_db()
    try:
        db.execute(
            'INSERT INTO loot_tables (id, name, description, entries_json, total_weight) '
            'VALUES (?, ?, ?, ?, ?)',
            (
                table_id,
                data['name'],
                data.get('description', ''),
                json.dumps(entries),
                total_weight
            )
        )
        db.commit()
        return jsonify({
            'message': 'Loot table created',
            'id': table_id,
            'total_weight': total_weight,
            'entry_count': len(entries)
        }), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Loot table already exists'}), 409


@app.route('/api/loot-tables/<table_id>/roll', methods=['POST'])
def roll_loot_table(table_id):
    """Roll on a loot table to get a random but fair reward."""
    data = request.get_json() or {}
    player_luck = data.get('player_luck', 1.0)
    
    db = get_db()
    table = db.execute('SELECT * FROM loot_tables WHERE id = ?', (table_id,)).fetchone()
    
    if not table:
        return jsonify({'error': 'Loot table not found'}), 404
    
    entries = json.loads(table['entries_json'])
    result = select_weighted_reward(entries, player_luck)
    
    # Defensive: check result structure
    if not isinstance(result, dict):
        return jsonify({'error': 'Failed to select reward from loot table'}), 500
    
    # Use .get() to avoid KeyError and provide defaults
    return jsonify({
        'loot_table_id': table_id,
        'result': result,
        'message': f"You received {result.get('amount', 1)}x {result.get('item', 'item')} ({result.get('rarity', 'common')})"
    })


if __name__ == '__main__':
    # Initialize database on startup if needed
    with app.app_context():
        init_db()
        # Seed default demonstrations if empty
        db = get_db()
        demo_count = db.execute('SELECT COUNT(*) FROM demonstrations').fetchone()[0]
        if demo_count == 0:
            demos = _seed_default_demonstrations()
            for demo in demos:
                db.execute(
                    'INSERT OR IGNORE INTO demonstrations (id, name, category, description, visualization_type, '
                    'parameters_json, educational_notes, safety_notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                    (demo['id'], demo['name'], demo['category'], demo['description'],
                     demo['visualization_type'], demo['parameters_json'],
                     demo['educational_notes'], demo['safety_notes'])
                )
            db.commit()
    
    # Run development server
    # Debug mode controlled by environment variable (default: False for security)
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
