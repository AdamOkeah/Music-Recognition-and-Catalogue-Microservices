import os
import base64
import requests
import sqlite3
import database
from flask import Flask, request, jsonify

AUDD_API_KEY = os.environ.get("AUDD_API_KEY", "64f75deb9ba29f4211ebbb5913d2f52d")
DATABASE = "shamzam.db"

app = Flask(__name__)


import base64
from flask import Flask, request, jsonify

@app.route("/recognize", methods=["POST"])
def recognize_track():
    data = request.get_json()
    file_path = data.get("file_path")

    if not file_path:
        return jsonify({"error": "Missing 'file_path'"}), 400

    if not os.path.exists(file_path):
        return jsonify({"error": "Audio file does not exist at provided path"}), 400

    # Step 1: Read file bytes and send to Audd.io
    try:
        with open(file_path, "rb") as f:
            audio_bytes = f.read()

        audd_response = requests.post(
            "https://api.audd.io/",
            data={"api_token": AUDD_API_KEY},
            files={"file": ("fragment.wav", audio_bytes, "audio/wav")}
        )
        audd_response.raise_for_status()
        audd_data = audd_response.json()
    except requests.RequestException as e:
        return jsonify({"error": f"Audd.io API request failed: {e}"}), 500

    if audd_data.get("status") != "success" or not audd_data.get("result"):
        return jsonify({"error": "Could not recognize track"}), 404

    recognized_artist = audd_data["result"].get("artist", "")
    recognized_title = audd_data["result"].get("title", "")

    if not recognized_artist or not recognized_title:
        return jsonify({"error": "Audd.io did not provide a valid artist/title"}), 404

    # Step 2: Check local DB for (title, artist)
    track = database.get_track_by_title_artist(recognized_title, recognized_artist)

    if track:
        # Convert file_data (bytes) to a Base64 string
        file_data_b64 = base64.b64encode(track["file_data"]).decode("utf-8")

        return jsonify({
            "message": "Track recognized and found in the local database!",
            "recognized_title": recognized_title,
            "recognized_artist": recognized_artist,
            "file_format": "wav64",  # Indicating it's a wav64 file
            "file_data_b64": file_data_b64  # Base64 encoded audio
        }), 200
    else:
        return jsonify({"error": f"Track '{recognized_title}' by '{recognized_artist}' not found"}), 404





if __name__ == "__main__":
    app.run(port=5001, debug=True)
