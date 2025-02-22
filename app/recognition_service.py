# recognition_service.py

import os
import base64
import requests
import sqlite3

from flask import Flask, request, jsonify

# If you have a config file or an .env for your Audd.io API key, import or read it here.
# For demo, let's read from an environment variable named AUDD_API_KEY.
AUDD_API_KEY = os.environ.get("AUDD_API_KEY", "YOUR_AUDD_API_KEY")

DATABASE = "shamzam.db"

app = Flask(__name__)

def init_db():
    """
    Optional: Ensure the `tracks` table exists.
    If your track_service already does this, you can omit it here.
    """
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tracks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                artist TEXT NOT NULL,
                file_data BLOB NOT NULL
            )
        ''')
        conn.commit()

@app.route("/recognize", methods=["POST"])
def recognize_track():
    """
    POST /recognize
    
    Expects a WAV file in multipart/form-data under the key "file".
    Example cURL:
        curl -X POST -F "file=@path/to/clip.wav" http://127.0.0.1:5001/recognize

    1) Reads the uploaded file bytes and sends to Audd.io.
    2) If recognized, checks local DB for (title, artist).
    3) If found, returns success + base64-encoded WAV from DB.
       If not found, returns 404 "Track not found".
    """
    # 1) Validate file
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    fragment_file = request.files["file"]
    fragment_bytes = fragment_file.read()
    
    if not fragment_bytes:
        return jsonify({"error": "Uploaded file is empty"}), 400

    # 2) Send audio fragment to Audd.io
    try:
        audd_response = requests.post(
            "https://api.audd.io/",
            data={"api_token": AUDD_API_KEY},
            files={"file": ("fragment.wav", fragment_bytes, "audio/wav")}
        )
        audd_response.raise_for_status()  # Raise exception if 4xx/5xx
    except requests.RequestException as e:
        return jsonify({"error": f"Audd.io API request failed: {e}"}), 500

    audd_data = audd_response.json()
    # Expected shape:
    # {
    #   "status": "success",
    #   "result": {
    #       "artist": "The Weeknd",
    #       "title": "Blinding Lights",
    #       ...
    #   }
    # }
    if audd_data.get("status") != "success" or not audd_data.get("result"):
        return jsonify({"error": "Could not recognize track"}), 404

    recognized_artist = audd_data["result"].get("artist", "")
    recognized_title = audd_data["result"].get("title", "")

    if not recognized_artist or not recognized_title:
        return jsonify({"error": "Audd.io did not provide a valid artist/title"}), 404

    # 3) Look up recognized track in local DB
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, file_data FROM tracks WHERE title = ? AND artist = ?",
            (recognized_title, recognized_artist)
        )
        row = cursor.fetchone()

    if not row:
        return jsonify({
            "message": f"Track '{recognized_title}' by '{recognized_artist}' not found in DB."
        }), 404

    track_id = row[0]
    raw_bytes = row[1]  # BLOB (raw WAV bytes) from DB

    # 4) Convert raw bytes => base64 string for JSON
    file_data_b64 = base64.b64encode(raw_bytes).decode("utf-8")

    # 5) Return success with recognized info + the base64 file
    return jsonify({
        "message": "Track recognized and found in the local database!",
        "recognized_title": recognized_title,
        "recognized_artist": recognized_artist,
        "track_id": track_id,
        "file_data_b64": file_data_b64
    }), 200

if __name__ == "__main__":
    # Optionally init the DB if needed (only if your track_service.py doesn't do it).
    init_db()

    # Run this recognition service on port 5001
    app.run(host="127.0.0.1", port=5001, debug=True)
