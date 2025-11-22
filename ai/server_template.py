# ai/server_template.py
# Universal Backend for NexaBuild Apps
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os
import uuid
import datetime

app = Flask(__name__, static_folder='.')
CORS(app)

# --- Database Setup ---
DB_FILE = "database.sqlite"


def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        # A generic table to store ANY kind of data (listings, todos, users)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS resources (
                id TEXT PRIMARY KEY,
                collection TEXT NOT NULL,  -- e.g., 'users', 'todos', 'houses'
                data JSON NOT NULL,        -- The actual data
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


init_db()


# --- Universal API Endpoints ---

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)


# 1. SAVE Data (Create or Update)
@app.route('/api/<collection>', methods=['POST'])
def save_item(collection):
    data = request.json
    item_id = data.get('id') or str(uuid.uuid4())
    data['id'] = item_id  # Ensure ID is in the data

    import json
    with get_db() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO resources (id, collection, data) VALUES (?, ?, ?)",
            (item_id, collection, json.dumps(data))
        )
        conn.commit()

    return jsonify({"status": "success", "id": item_id, "data": data})


# 2. LIST Data (Get all items in a collection)
@app.route('/api/<collection>', methods=['GET'])
def list_items(collection):
    import json
    items = []
    with get_db() as conn:
        cursor = conn.execute("SELECT data FROM resources WHERE collection = ? ORDER BY created_at DESC", (collection,))
        rows = cursor.fetchall()
        for row in rows:
            items.append(json.loads(row['data']))
    return jsonify(items)


# 3. DELETE Data
@app.route('/api/<collection>/<item_id>', methods=['DELETE'])
def delete_item(collection, item_id):
    with get_db() as conn:
        conn.execute("DELETE FROM resources WHERE collection = ? AND id = ?", (collection, item_id))
        conn.commit()
    return jsonify({"status": "deleted"})


if __name__ == '__main__':
    # Port is injected by main.py, defaulting to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)