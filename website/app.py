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
    classrooms = db.execute(
        'SELECT id, name, teacher_id, subject, description, class_code, max_students, is_active, created_at '
        'FROM classrooms WHERE is_active = 1 ORDER BY created_at DESC'
    ).fetchall()
    
    result = []
    for classroom in classrooms:
        # Count enrolled students
        student_count = db.execute(
            'SELECT COUNT(*) FROM student_enrollments WHERE classroom_id = ?',
            (classroom['id'],)
        ).fetchone()[0]
        
        result.append({
            'id': classroom['id'],
            'name': classroom['name'],
            'teacher_id': classroom['teacher_id'],
            'subject': classroom['subject'],
            'description': classroom['description'],
            'class_code': classroom['class_code'],
            'max_students': classroom['max_students'],
            'current_students': student_count,
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
    
    classroom_id = f"class-{hashlib.sha256((data['name'] + data['teacher_id']).encode()).hexdigest()[:12]}"
    # Generate a unique 6-character class code
    class_code = hashlib.sha256((classroom_id + str(datetime.utcnow())).encode()).hexdigest()[:6].upper()
    
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
                data.get('max_students', 30)
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
    score = data.get('score')
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
    """Simulate particle motion for physics education."""
    particle_count = params.get('particle_count', 50)
    temperature = params.get('temperature', 300)
    
    # Calculate average velocity using kinetic theory of gases:
    # v_avg = sqrt(3 * k_B * T / m)
    # where k_B = 1.38e-23 J/K (Boltzmann constant)
    # and m = 1.67e-27 kg (approximate proton mass, used for hydrogen gas)
    boltzmann_constant = 1.38e-23  # J/K
    hydrogen_mass = 1.67e-27  # kg (proton mass approximation)
    average_velocity = (3 * boltzmann_constant * temperature / hydrogen_mass) ** 0.5
    
    return {
        'type': 'particle_motion',
        'particle_count': particle_count,
        'temperature_k': temperature,
        'average_velocity': average_velocity,
        'particles': [{'id': i, 'x': random.random(), 'y': random.random(), 
                       'vx': random.gauss(0, 1), 'vy': random.gauss(0, 1)} 
                      for i in range(min(particle_count, 100))]
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
        'direction': '5\' to 3\'',
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
