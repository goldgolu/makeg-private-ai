import os
import sys
import sqlite3
import uuid
import logging
import subprocess
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, g, redirect, url_for, send_from_directory
from textblob import TextBlob
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'supersecretkey')

DATABASE = 'app_data.db'
GENERATED_GAMES_FOLDER = 'generated_games'
GAME_TEMPLATES = ["airdrop", "3d", "cricket", "racing"]

# Ensure folders exist
if not os.path.exists(GENERATED_GAMES_FOLDER):
    os.makedirs(GENERATED_GAMES_FOLDER)
    logging.info(f"Created folder: {GENERATED_GAMES_FOLDER}")

# -------------------- Database Functions --------------------
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            sender TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_session TEXT,
            title TEXT,
            genre TEXT,
            description TEXT,
            story TEXT,
            game_file TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# -------------------- Authentication --------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username and password:
            session['user'] = username
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

@app.before_request
def ensure_session_and_db():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    init_db()

# -------------------- Game System --------------------
@app.route('/create_game', methods=['POST'])
def create_game():
    game_title = request.form.get('title')
    game_genre = request.form.get('genre')
    game_description = request.form.get('description')
    game_story = request.form.get('story')
    
    if not (game_title and game_genre and game_description and game_story):
        return jsonify({'message': 'Missing required fields'}), 400
    
    game_filename = f"{uuid.uuid4()}.html"
    game_filepath = os.path.join(GENERATED_GAMES_FOLDER, game_filename)
    
    game_code = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>{game_title}</title>
      <style>
        body {{ font-family: Arial; background: #f0f0f0; padding: 20px; }}
      </style>
    </head>
    <body>
      <h1>{game_title}</h1>
      <p>{game_description}</p>
      <p>{game_story}</p>
    </body>
    </html>
    """
    
    try:
        with open(game_filepath, 'w', encoding='utf-8') as f:
            f.write(game_code)
        conn = get_db()
        conn.execute("""
            INSERT INTO games (user_session, title, genre, description, story, game_file)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (session['session_id'], game_title, game_genre, game_description, game_story, game_filename))
        conn.commit()
        return jsonify({'message': 'Game created', 'link': url_for('serve_generated_game', filename=game_filename, _external=True)})
    except Exception as e:
        logging.error("Error creating game: %s", e)
        return jsonify({'message': 'Error creating game'}), 500

@app.route('/generated_games/<path:filename>')
def serve_generated_game(filename):
    return send_from_directory(GENERATED_GAMES_FOLDER, filename)

# -------------------- AI Chatbot --------------------
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.form.get('message')
    if user_message:
        polarity = TextBlob(user_message).sentiment.polarity
        if polarity > 0.3:
            bot_response = "That's great! Keep it up!"
        elif polarity < -0.3:
            bot_response = "I'm here if you need to talk. Stay strong!"
        else:
            bot_response = "Got it! Let me know more."
        return jsonify({'response': bot_response})
    return jsonify({'response': "I didn't quite catch that. Could you rephrase?"})

# -------------------- Main Menu Integration --------------------
def handle_text_commands():
    while True:
        cmd = input("\nMakeG> ")
        if "game" in cmd:
            game_type = input("Game type: ")
            if game_type in GAME_TEMPLATES:
                subprocess.run(["python", "generate_game.py", game_type])
        elif "delete" in cmd:
            target = cmd.split(" ")[1]
            os.remove(target)
        elif "website" in cmd:
            subprocess.run(["python", "utils/website_gen.py"])
        elif "exit" in cmd:
            break

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
