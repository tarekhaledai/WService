from flask import Flask, request, jsonify
import psycopg2
from psycopg2 import pool
import os
from datetime import datetime

app = Flask(__name__)

# Configuration de la connexion PostgreSQL
def get_db_connection():
    """Crée une connexion à la base de données"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'db'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'wservice_db'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD')
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        raise

# Route de santé
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'OK',
        'message': 'API is running',
        'timestamp': datetime.now().isoformat()
    }), 200

# Route pour tester la connexion à la base de données
@app.route('/api/db/test', methods=['GET'])
def test_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT NOW() as current_time, version() as pg_version')
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Database connection successful',
            'data': {
                'current_time': str(result[0]),
                'pg_version': result[1]
            }
        }), 200
    except Exception as error:
        return jsonify({
            'success': False,
            'message': 'Database connection failed',
            'error': str(error)
        }), 500

# Route pour créer une table exemple (si elle n'existe pas)
@app.route('/api/db/init', methods=['POST'])
def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Table users created successfully'
        }), 200
    except Exception as error:
        return jsonify({
            'success': False,
            'message': 'Failed to create table',
            'error': str(error)
        }), 500

# Route pour créer un utilisateur
@app.route('/api/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        
        if not name or not email:
            return jsonify({
                'success': False,
                'message': 'Name and email are required'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id, name, email, created_at',
            (name, email)
        )
        result = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'User created successfully',
            'data': {
                'id': result[0],
                'name': result[1],
                'email': result[2],
                'created_at': str(result[3])
            }
        }), 201
    except psycopg2.IntegrityError as e:
        return jsonify({
            'success': False,
            'message': 'Email already exists',
            'error': str(e)
        }), 400
    except Exception as error:
        return jsonify({
            'success': False,
            'message': 'Failed to create user',
            'error': str(error)
        }), 500

# Route pour lister les utilisateurs
@app.route('/api/users', methods=['GET'])
def list_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, email, created_at FROM users ORDER BY created_at DESC')
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        users = []
        for row in results:
            users.append({
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'created_at': str(row[3])
            })
        
        return jsonify({
            'success': True,
            'count': len(users),
            'data': users
        }), 200
    except Exception as error:
        return jsonify({
            'success': False,
            'message': 'Failed to fetch users',
            'error': str(error)
        }), 500

if __name__ == '__main__':
    port = int(os.getenv('API_PORT', 3000))
    db_host = os.getenv('DB_HOST', 'db')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'wservice_db')
    
    print(f"🚀 API Server running on port {port}")
    print(f"📊 Database: {db_host}:{db_port}/{db_name}")
    
    app.run(host='0.0.0.0', port=port, debug=True)

