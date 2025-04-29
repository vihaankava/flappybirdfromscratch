import os
import json
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session

app = Flask(__name__)
app.secret_key = os.urandom(24)

DB_PATH = 'leaderboard.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS leaderboard (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        score INTEGER NOT NULL,
        date TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

def get_leaderboard():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM leaderboard ORDER BY score DESC LIMIT 10')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def add_score(name, score):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO leaderboard (name, score, date) VALUES (?, ?, ?)',
                  (name, score, current_time))
    conn.commit()
    conn.close()

init_db()

def import_existing_leaderboard():
    if os.path.exists('../leaderboard.json'):
        try:
            with open('../leaderboard.json', 'r') as f:
                scores = json.load(f)
                
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM leaderboard')
            count = cursor.fetchone()[0]
            
            if count == 0:  # Only import if leaderboard is empty
                for score in scores:
                    cursor.execute('INSERT INTO leaderboard (name, score, date) VALUES (?, ?, ?)',
                                  (score['name'], score['score'], score['date']))
                conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error importing leaderboard: {e}")

import_existing_leaderboard()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/game')
def game():
    return render_template('game.html')

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard_api():
    return jsonify(get_leaderboard())

@app.route('/api/score', methods=['POST'])
def add_score_api():
    data = request.json
    name = data.get('name')
    score = data.get('score')
    
    if not name or not score:
        return jsonify({'error': 'Name and score are required'}), 400
    
    add_score(name, score)
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
