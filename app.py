from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sqlite3

app = Flask(__name__)

CORS(app, origins=[
    "https://sopan-rathod.github.io",
    "http://127.0.0.1:5500",
    "http://localhost:5500"
])

DB_NAME = "portfolio.db"


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


@app.route("/api/contact", methods=["POST"])
def contact():
    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    message = str(data.get("message", "")).strip()

    if not name or not email or not message:
        return jsonify({
            "error": "Please fill in all required fields."
        }), 400

    connection = sqlite3.connect(DB_NAME)
    connection.execute(
        "INSERT INTO messages (name, email, message) VALUES (?, ?, ?)",
        (name, email, message)
    )
    connection.commit()
    connection.close()

    return jsonify({
        "message": "Your message has been saved successfully!"
    }), 201


if __name__ == "__main__":
    create_database()
    app.run(debug=True, port=5000)
