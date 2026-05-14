"""
Backend Flask - PHASE 7 - Architecture Complète
backend_app.py

Endpoints:
  - POST /api/auth/login - Authentification
  - POST /api/scraper/start - Lancer scraper
  - GET /api/scraper/status/{job_id} - Statut scraper
  - POST /api/dashboard/upload - Upload résultats
  - GET /api/dashboard/data - Récupérer données dashboard
  - GET /api/dashboard/stats/{role} - Stats par rôle
  - GET /api/health - Health check

Structure:
  Backend (Flask) ↔ Frontend (React)
         ↓
  Scraper (multi-source)
         ↓
  Database (JSON/SQLite)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json
import os
import uuid
import threading
import sqlite3
from typing import Dict, List, Optional
import logging

# ────────────────────────────────────────────────────────────
# SETUP
# ────────────────────────────────────────────────────────────

app = Flask(__name__)
CORS(app)

# Configuration
app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)

jwt = JWTManager(app)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database
DB_PATH = "analysis_platform.db"
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Job tracking
jobs = {}  # {job_id: {"status": "running|completed|failed", "progress": 0-100, ...}}


# ────────────────────────────────────────────────────────────
# DATABASE SETUP
# ────────────────────────────────────────────────────────────

def init_db():
    """Initialise la base de données."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Table utilisateurs
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        email TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Table analyses
    c.execute('''CREATE TABLE IF NOT EXISTS analyses (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        name TEXT NOT NULL,
        corpus_size INTEGER,
        topics_count INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        data_path TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    
    # Table jobs
    c.execute('''CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        type TEXT NOT NULL,
        status TEXT NOT NULL,
        progress INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP,
        result_path TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    
    conn.commit()
    conn.close()


def get_db():
    """Récupère connexion DB."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ────────────────────────────────────────────────────────────
# UTILISATEURS
# ────────────────────────────────────────────────────────────

def create_default_users():
    """Crée utilisateurs de test."""
    conn = get_db()
    c = conn.cursor()
    
    users = [
        {
            "id": str(uuid.uuid4()),
            "username": "analyst",
            "password": generate_password_hash("analyst123"),
            "role": "analyst",
            "email": "analyst@company.com"
        },
        {
            "id": str(uuid.uuid4()),
            "username": "decision_maker",
            "password": generate_password_hash("decision123"),
            "role": "decision_maker",
            "email": "decision@company.com"
        },
        {
            "id": str(uuid.uuid4()),
            "username": "admin",
            "password": generate_password_hash("admin123"),
            "role": "admin",
            "email": "admin@company.com"
        }
    ]
    
    for user in users:
        try:
            c.execute(
                'INSERT INTO users (id, username, password, role, email) VALUES (?, ?, ?, ?, ?)',
                (user["id"], user["username"], user["password"], user["role"], user["email"])
            )
        except sqlite3.IntegrityError:
            pass  # User exists
    
    conn.commit()
    conn.close()


# ────────────────────────────────────────────────────────────
# AUTH ENDPOINTS
# ────────────────────────────────────────────────────────────

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login utilisateur."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Missing credentials"}), 400
    
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    
    if not user or not check_password_hash(user['password'], password):
        return jsonify({"error": "Invalid credentials"}), 401
    
    access_token = create_access_token(
        identity={
            "id": user['id'],
            "username": user['username'],
            "role": user['role']
        }
    )
    
    return jsonify({
        "status": "success",
        "access_token": access_token,
        "user": {
            "id": user['id'],
            "username": user['username'],
            "role": user['role'],
            "email": user['email']
        }
    }), 200


@app.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout utilisateur."""
    return jsonify({"status": "logged out"}), 200


# ────────────────────────────────────────────────────────────
# SCRAPER ENDPOINTS
# ────────────────────────────────────────────────────────────

@app.route('/api/scraper/start', methods=['POST'])
@jwt_required()
def start_scraper():
    """Démarre un job de scraping."""
    user_identity = get_jwt_identity()
    user_id = user_identity['id']
    
    data = request.get_json()
    query = data.get('query', 'default')
    sources = data.get('sources', ['twitter', 'press', 'reddit'])
    
    job_id = str(uuid.uuid4())
    
    # Créer entry dans jobs
    conn = get_db()
    c = conn.cursor()
    c.execute(
        'INSERT INTO jobs (id, user_id, type, status, progress) VALUES (?, ?, ?, ?, ?)',
        (job_id, user_id, 'scraper', 'queued', 0)
    )
    conn.commit()
    conn.close()
    
    # Lancer scraper en thread
    thread = threading.Thread(
        target=run_scraper_job,
        args=(job_id, user_id, query, sources)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "status": "started",
        "job_id": job_id,
        "message": f"Scraper started for '{query}'"
    }), 202


def run_scraper_job(job_id: str, user_id: str, query: str, sources: List[str]):
    """Exécute le scraper (simulé)."""
    conn = get_db()
    c = conn.cursor()
    
    try:
        # Mettre à jour statut
        c.execute(
            'UPDATE jobs SET status = ?, progress = ? WHERE id = ?',
            ('running', 10, job_id)
        )
        conn.commit()
        
        # Simuler scraping
        logger.info(f"Scraping {query} from {sources}")
        
        # Données simulées
        corpus = [
            {
                "text": f"Sample tweet about {query}",
                "origin": "twitter",
                "date": datetime.now().isoformat(),
                "likes": 10
            }
            for _ in range(100)
        ]
        
        # Sauvegarder résultats
        result_path = f"{UPLOAD_FOLDER}/{job_id}_corpus.json"
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(corpus, f)
        
        # Mettre à jour job
        c.execute(
            'UPDATE jobs SET status = ?, progress = ?, result_path = ?, updated_at = ? WHERE id = ?',
            ('completed', 100, result_path, datetime.now(), job_id)
        )
        conn.commit()
        
        logger.info(f"Job {job_id} completed")
        
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        c.execute(
            'UPDATE jobs SET status = ?, progress = ?, updated_at = ? WHERE id = ?',
            ('failed', 0, datetime.now(), job_id)
        )
        conn.commit()
    
    finally:
        conn.close()


@app.route('/api/scraper/status/<job_id>', methods=['GET'])
@jwt_required()
def get_scraper_status(job_id):
    """Récupère statut d'un job."""
    user_identity = get_jwt_identity()
    user_id = user_identity['id']
    
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM jobs WHERE id = ? AND user_id = ?', (job_id, user_id))
    job = c.fetchone()
    conn.close()
    
    if not job:
        return jsonify({"error": "Job not found"}), 404
    
    return jsonify({
        "job_id": job['id'],
        "status": job['status'],
        "progress": job['progress'],
        "created_at": job['created_at'],
        "updated_at": job['updated_at'],
        "result_path": job['result_path']
    }), 200


# ────────────────────────────────────────────────────────────
# DASHBOARD ENDPOINTS
# ────────────────────────────────────────────────────────────

@app.route('/api/dashboard/upload', methods=['POST'])
@jwt_required()
def upload_results():
    """Upload résultats de scraper vers dashboard."""
    user_identity = get_jwt_identity()
    user_id = user_identity['id']
    
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    analysis_name = request.form.get('name', 'Untitled Analysis')
    
    # Sauvegarder fichier
    filename = f"{user_id}_{uuid.uuid4()}_{file.filename}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    # Créer analyse en DB
    analysis_id = str(uuid.uuid4())
    conn = get_db()
    c = conn.cursor()
    c.execute(
        'INSERT INTO analyses (id, user_id, name, data_path) VALUES (?, ?, ?, ?)',
        (analysis_id, user_id, analysis_name, filepath)
    )
    conn.commit()
    conn.close()
    
    return jsonify({
        "status": "uploaded",
        "analysis_id": analysis_id,
        "name": analysis_name
    }), 201


@app.route('/api/dashboard/analyses', methods=['GET'])
@jwt_required()
def get_analyses():
    """Récupère analyses de l'utilisateur."""
    user_identity = get_jwt_identity()
    user_id = user_identity['id']
    
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM analyses WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
    analyses = c.fetchall()
    conn.close()
    
    return jsonify({
        "analyses": [dict(a) for a in analyses]
    }), 200


@app.route('/api/dashboard/data/<analysis_id>', methods=['GET'])
@jwt_required()
def get_analysis_data(analysis_id):
    """Récupère données d'une analyse."""
    user_identity = get_jwt_identity()
    user_id = user_identity['id']
    
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM analyses WHERE id = ? AND user_id = ?', (analysis_id, user_id))
    analysis = c.fetchone()
    conn.close()
    
    if not analysis:
        return jsonify({"error": "Analysis not found"}), 404
    
    # Charger fichier
    try:
        with open(analysis['data_path'], 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return jsonify({
            "analysis_id": analysis['id'],
            "name": analysis['name'],
            "created_at": analysis['created_at'],
            "data": data
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/dashboard/stats/<role>', methods=['GET'])
@jwt_required()
def get_stats_by_role(role):
    """Récupère stats par rôle."""
    user_identity = get_jwt_identity()
    
    # Vérifier rôle
    if user_identity['role'] != role and user_identity['role'] != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    
    # Stats pour Analyste
    if role == 'analyst':
        stats = {
            "role": "analyst",
            "widgets": [
                {
                    "id": "topics",
                    "type": "chart",
                    "title": "Topics Distribution",
                    "description": "Top topics by document count"
                },
                {
                    "id": "temporal",
                    "type": "timeseries",
                    "title": "Activity Timeline",
                    "description": "Mentions over time"
                },
                {
                    "id": "metrics",
                    "type": "table",
                    "title": "Linguistic Metrics",
                    "description": "TTR, Coherence, Density, etc."
                },
                {
                    "id": "keywords",
                    "type": "wordcloud",
                    "title": "Top Keywords",
                    "description": "Most frequent terms"
                },
                {
                    "id": "convergence",
                    "type": "heatmap",
                    "title": "Lexical Convergence",
                    "description": "Vocabulary overlap by period"
                },
                {
                    "id": "reports",
                    "type": "document",
                    "title": "Generated Reports",
                    "description": "Semantic, Temporal, Cognitive summaries"
                }
            ]
        }
    
    # Stats pour Décideur
    elif role == 'decision_maker':
        stats = {
            "role": "decision_maker",
            "widgets": [
                {
                    "id": "executive_summary",
                    "type": "text",
                    "title": "Executive Summary",
                    "description": "One-page overview"
                },
                {
                    "id": "key_insights",
                    "type": "highlights",
                    "title": "Key Insights",
                    "description": "Top 5 findings"
                },
                {
                    "id": "risks",
                    "type": "alert",
                    "title": "Risk Assessment",
                    "description": "Critical issues and trends"
                },
                {
                    "id": "opportunities",
                    "type": "highlight",
                    "title": "Opportunities",
                    "description": "Positive trends and themes"
                },
                {
                    "id": "recommendations",
                    "type": "list",
                    "title": "Recommendations",
                    "description": "Actionable next steps"
                },
                {
                    "id": "metrics_summary",
                    "type": "kpi",
                    "title": "Key Metrics",
                    "description": "Overall health scores"
                }
            ]
        }
    else:
        stats = {"error": "Unknown role"}
    
    return jsonify(stats), 200


# ────────────────────────────────────────────────────────────
# HEALTH CHECK
# ────────────────────────────────────────────────────────────

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }), 200


# ────────────────────────────────────────────────────────────
# ERROR HANDLERS
# ────────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500


# ────────────────────────────────────────────────────────────
# MAIN
# ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Initialiser DB
    init_db()
    create_default_users()
    
    print("\n" + "="*70)
    print("BACKEND FLASK - ANALYSIS PLATFORM")
    print("="*70)
    print("\n✅ Database initialized")
    print("✅ Default users created:")
    print("   - analyst / analyst123")
    print("   - decision_maker / decision123")
    print("   - admin / admin123")
    print("\n🚀 Server starting on http://localhost:5000\n")
    
    app.run(debug=True, port=5000, host='0.0.0.0')