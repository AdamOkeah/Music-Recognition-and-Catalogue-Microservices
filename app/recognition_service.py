import os
import requests
import database
from flask import Flask, request, jsonify
from dotenv import load_dotenv


AUDD_KEY = os.environ.get("AUDD_KEY")
if not AUDD_KEY:
    raise ValueError("AUDD_KEY not set! Provide it via environment.")

print(AUDD_KEY)

app = Flask(__name__)

@app.route("/recognise", methods=["POST"])
def recognise_track():
    data = request.get_json()
    file_path = data.get("file_path")

    if not file_path:
        return jsonify({"error": "Missing 'file_path'"}), 400

    if not os.path.exists(file_path):
        return jsonify({"error": "Audio file does not exist at provided path"}), 400

    # Step 1: Read file bytes and send to Audd.io
    with open(file_path, "rb") as f:
        audio_bytes = f.read()

        audd_response = requests.post(
            "https://api.audd.io/",
            data={"api_token": AUDD_KEY},
            files={"file": ("fragment.wav", audio_bytes, "audio/wav")}
        )

    print("Audd.io API Response:", audd_response.text)
    audd_response.raise_for_status()
    audd_data = audd_response.json()
    
    if audd_data.get("status") != "success" or not audd_data.get("result"):
        return jsonify({"error": "Could not recognise track"}), 404

    recognised_artist = audd_data["result"].get("artist", "")
    recognised_title = audd_data["result"].get("title", "")

    if not recognised_artist or not recognised_title:
        return jsonify({"error": "Audd.io did not provide a valid artist/title"}), 404

    #Fetch the Base64-encoded data from the database
    track = database.get_track_by_title_artist(recognised_title, recognised_artist)

    if track and "file_data" in track:
        file_data_b64 = track["file_data"]

        return jsonify({
            "message": "Track found successfully",
            "title": recognised_title,
            "artist": recognised_artist,
            "file_data_b64": file_data_b64  # Returns valid Base64
        }), 200

    else:
        return jsonify({"error": f"Track '{recognised_title}' by '{recognised_artist}' not found"}), 405


if __name__ == "__main__":
    app.run(port=5003, debug=True)
