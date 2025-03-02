import sqlite3
from flask import Flask, request, jsonify
import os 
import database

app = Flask(__name__)
DATABASE = "shamzam.db"

@app.route("/list", methods=["GET"])
def list_tracks():
    """
    GET /tracks
    Returns a JSON array of {id, title, artist}.
    """
    try:
        tracks = database.get_all_tracks()  # use database helper
        return jsonify(tracks), 200
    except Exception as e:
        return jsonify({"error": f"Database error: {e}"}), 500
    
    
if __name__ == "__main__":
    app.run(port=5001, debug=True)