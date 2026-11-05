from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
from functools import wraps

app = Flask(__name__)

CORS(app, origins=[
    "https://sopan-rathod.github.io",
    "http://127.0.0.1:5500",
    "http://localhost:5500"
])

DB_NAME = "portfolio.db"
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

def create_database():
    connection = sqlite3.connect(DB_NAME)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL
        )
    """)
    connection.commit()
    connection.close()
    create_database()

@app.route("/")
def home():
    return jsonify({
        "message": "Portfolio Backend is running!"
    })

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        password = request.headers.get("X-Admin-Password")

        if not ADMIN_PASSWORD:
            return jsonify({"error": "Admin password is not configured."}), 500

        if password != ADMIN_PASSWORD:
            return jsonify({"error": "Unauthorized access"}), 401

        return func(*args, **kwargs)
    return wrapper

@app.route("/api/admin/messages", methods=["GET"])
@admin_required
def get_messages():
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM messages ORDER BY id DESC")
    rows = cursor.fetchall()
    connection.close()
    messages = [dict(row) for row in rows]
    return jsonify(messages)

@app.route("/api/contact", methods=["POST"])
def contact():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    message = data.get("message")

    if not name or not email or not message:
        return jsonify({"error": "All fields are required"}), 400

    connection = sqlite3.connect(DB_NAME)
    connection.execute("INSERT INTO messages (name, email, message) VALUES (?, ?, ?)",
                       (name, email, message))
    connection.commit()
    connection.close()
    return jsonify({"success": True, "message": "Message saved"}), 200

if __name__ == "__main__":
    create_database()
    app.run(debug=True, port=5000)
