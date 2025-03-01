import base64
import sqlite3
from flask import Flask, request, jsonify
import os 
import database

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
    """
    Add a full track to the catalogue.
    Reads the file, encodes it in Base64, and stores the track.
    """
    data = request.get_json()
    title = data.get('title')
    artist = data.get('artist')
    file_path = data.get('file_path')

    if not title or not artist or not file_path:
        return jsonify({"error": "Missing required fields"}), 400

    if not os.path.exists(file_path):
        return jsonify({"error": "Full track file does not exist at provided path"}), 400

    try:
        with open(file_path, "rb") as f:
            raw_data = f.read()
            encoded_file = base64.b64encode(raw_data).decode("ascii")
    except Exception as e:
        return jsonify({"error": "Failed to encode file", "details": str(e)}), 500

    # Corrected call to your provided database function
    track_id = database.add_track_to_db(title, artist, encoded_file)
    return jsonify({"message": "Track added successfully", "track_id": track_id}), 201

@app.route("/tracks", methods=["GET"])
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


@app.route("/tracks", methods=["DELETE"])
def delete_track():
    """
    DELETE /tracks (JSON)
    {
        "title": "Song Title",
        "artist": "Artist Name"
    }
    Removes a track from the database by title and artist.
    """
    data = request.get_json()
    title = data.get('title')
    artist = data.get('artist')

    if not title or not artist:
        return jsonify({"error": "Missing 'title' or 'artist'"}), 400

    try:
        success = database.remove_track_from_db(title, artist)

        if success:
            return jsonify({"message": f"Track '{title}' by '{artist}' deleted successfully"}), 200
        else:
            return jsonify({"error": f"Track '{title}' by '{artist}' not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Database error: {e}"}), 500



if __name__ == "__main__":
    init_db()
    app.run(port=5000, debug=True)
