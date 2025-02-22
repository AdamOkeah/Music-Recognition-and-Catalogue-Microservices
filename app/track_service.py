import base64
import sqlite3
from flask import Flask, request, jsonify

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

@app.route("/tracks", methods=["POST"])
def add_track():
    """
    POST /tracks  (multipart/form-data)
    Fields required:
      - title: text
      - artist: text
      - file: the uploaded WAV file
    The server encodes the WAV in base64 and stores it in 'file_data'.
    """
    # 1) Check for missing fields
    if "title" not in request.form or "artist" not in request.form or "file" not in request.files:
        return jsonify({"error": "Missing 'title', 'artist' or 'file'"}), 400

    title = request.form["title"]
    artist = request.form["artist"]
    file_ = request.files["file"]  # The WAV file

    try:
        # 2) Read raw bytes from the uploaded file
        raw_bytes = file_.read()
    except Exception as e:
        # If reading the file fails
        return jsonify({"error": f"Error reading uploaded file: {e}"}), 400

    try:
        # 3) Encode the WAV data to base64
        encoded_wav = base64.b64encode(raw_bytes).decode("utf-8")
    except Exception as e:
        return jsonify({"error": f"Error base64-encoding file: {e}"}), 500

    # 4) Store the base64-encoded data in the database
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tracks (title, artist, file_data)
                VALUES (?, ?, ?)
            """, (title, artist, encoded_wav))
            conn.commit()
            track_id = cursor.lastrowid
    except Exception as e:
        return jsonify({"error": f"Database error: {e}"}), 500

    # 5) Success
    return jsonify({"message": "Track added successfully", "track_id": track_id}), 200


@app.route("/tracks", methods=["GET"])
def list_tracks():
    """
    GET /tracks
    Returns a JSON array of {id, title, artist}.
    """
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, artist FROM tracks")
            rows = cursor.fetchall()
    except Exception as e:
        return jsonify({"error": f"Database error: {e}"}), 500

    result = [{"id": r[0], "title": r[1], "artist": r[2]} for r in rows]
    return jsonify(result), 200



@app.route("/tracks/<int:track_id>", methods=["DELETE"])
def delete_track(track_id):
    """
    DELETE /tracks/<track_id>
    Removes a track from the catalogue (by database ID).
    Returns 200 if removed, or 404 if not found.
    """
    # Connect to DB, attempt to delete
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tracks WHERE id = ?", (track_id,))
        rows_affected = cursor.rowcount
        conn.commit()

    # rows_affected will be 0 if the track ID didn't exist
    if rows_affected == 0:
        return jsonify({"error": f"Track ID {track_id} not found"}), 404
    else:
        return jsonify({"message": f"Track ID {track_id} deleted successfully"}), 200



if __name__ == "__main__":
    init_db()
    app.run(port=5000, debug=True)
