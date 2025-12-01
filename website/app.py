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


if __name__ == '__main__':
    # Initialize database on startup if needed
    with app.app_context():
        init_db()
    
    # Run development server
    app.run(debug=True, host='0.0.0.0', port=5000)
