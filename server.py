# ==============================================================
# server.py — BACKEND LAYER (Python)
# Edit this file to change game logic and database rules.
# This file does NOT control the look or feel of the site.
#
# To run: pip install flask flask-cors && python server.py
# ==============================================================

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import hashlib
import os

app = Flask(__name__)
CORS(app)  # Allows the HTML page to talk to this server


# ==============================================================
# CONFIG — Edit these settings without touching game logic below
# ==============================================================
DATABASE_FILE   = "economy.db"     # Where all data is stored
STARTING_BALANCE = 1000.00         # Money each new player starts with
MIN_USERNAME_LEN = 3
MAX_USERNAME_LEN = 20


# ==============================================================
# DATABASE SETUP — Runs once to create tables if they don't exist
# Add new tables here as you build more game features
# ==============================================================
def init_db():
    with sqlite3.connect(DATABASE_FILE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                username  TEXT    UNIQUE NOT NULL,
                password  TEXT    NOT NULL,
                balance   REAL    DEFAULT 0,
                created   TEXT    DEFAULT (datetime('now'))
            )
        """)
        # Future tables go here — e.g. companies, jobs, transactions
        conn.commit()


# ==============================================================
# HELPER FUNCTIONS — Reusable utilities
# ==============================================================
def hash_password(password: str) -> str:
    """One-way encrypt a password before storing it."""
    return hashlib.sha256(password.encode()).hexdigest()

def get_db():
    """Open a database connection. Use inside a 'with' block."""
    return sqlite3.connect(DATABASE_FILE)


# ==============================================================
# ROUTES — Each function below is a URL the frontend can call
# To add a new feature, add a new @app.route block here
# ==============================================================

@app.route("/register", methods=["POST"])
def register():
    """
    Called when a user submits the signup form.
    Expects JSON: { "username": "...", "password": "..." }
    Returns:  200 OK with success message, or 400/409 with error
    """
    data = request.get_json()

    # --- Input validation ---
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "")

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    if len(username) < MIN_USERNAME_LEN or len(username) > MAX_USERNAME_LEN:
        return jsonify({"error": f"Username must be {MIN_USERNAME_LEN}–{MAX_USERNAME_LEN} characters."}), 400

    if not username.isalnum() and "_" not in username:
        return jsonify({"error": "Username can only contain letters, numbers, and underscores."}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters."}), 400

    # --- Save to database ---
    try:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO users (username, password, balance) VALUES (?, ?, ?)",
                (username, hash_password(password), STARTING_BALANCE)
            )
            conn.commit()

        return jsonify({"message": f"Welcome, {username}! Your account is ready."}), 200

    except sqlite3.IntegrityError:
        # Username already taken (UNIQUE constraint failed)
        return jsonify({"error": "That username is already taken."}), 409

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "")

    with get_db() as conn:
        user = conn.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, hash_password(password))
        ).fetchone()

    if user:
        return jsonify({"message": "ok", "username": username}), 200
    else:
        return jsonify({"error": "Wrong username or password."}), 401


@app.route("/stats", methods=["GET"])
def stats():
    """
    Called by the landing page to show live economy numbers.
    Returns: player count, company count, total wealth in the game
    """
    with get_db() as conn:
        player_count  = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        total_wealth  = conn.execute("SELECT SUM(balance) FROM users").fetchone()[0] or 0

        # TODO: replace 0 with real company count once that table exists
        company_count = 0

    return jsonify({
        "players":      player_count,
        "companies":    company_count,
        "total_wealth": round(total_wealth, 2)
    })


# ==============================================================
# START THE SERVER
# ==============================================================
if __name__ == "__main__":
    init_db()  # Make sure tables exist before accepting requests
    print("Server running at http://localhost:5000")
    app.run(debug=True, port=5000)  # Set debug=False when you deploy
