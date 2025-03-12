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



@app.route("/delete", methods=["DELETE"])
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
    app.run(port=5002, debug=True)
