import base64
import os
import sqlite3
from flask import Flask, request, jsonify
import database
import mimetypes

app = Flask(__name__)
DATABASE = "shamzam.db"

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tracks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                artist TEXT NOT NULL,
                file_data TEXT NOT NULL
            )
        """)
        conn.commit()

@app.route('/tracks', methods=['POST'])
def add_track():
    """Reads, encodes, and stores an audio file as Base64"""
    data = request.get_json()
    title = data.get('title')
    artist = data.get('artist')
    file_path = data.get('file_path')

    if not title or not artist or not file_path:
        return jsonify({"error": "Missing required fields"}), 400

    if not os.path.exists(file_path):
        return jsonify({"error": "Audio file does not exist at provided path"}), 400

    try:
        #Ensure the file is readable and not empty
        if os.stat(file_path).st_size == 0:
            return jsonify({"error": "Audio file is empty"}), 400

        #  Open file correctly
        with open(file_path, "rb") as f:
            raw_data = f.read()
        
        if not raw_data:
            return jsonify({"error": "File read error, empty data"}), 400

        # Convert to Base64 properly
        encoded_file = base64.b64encode(raw_data).decode("utf-8")

    except Exception as e:
        print("Encoding error:", e)  # Debugging
        return jsonify({"error": "Failed to encode file", "details": str(e)}), 500

    #Store Base64 string in database
    track_id = database.add_track_to_db(title, artist, encoded_file)

    return jsonify({"message": "Track added successfully", "track_id": track_id}), 200



if __name__ == "__main__":
    init_db()
    app.run(port=5000, debug=True)
