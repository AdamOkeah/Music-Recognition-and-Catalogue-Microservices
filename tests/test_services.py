import unittest
import os
import base64
import requests

from app import database

# Define the base URLs for each microservice
# assuming each microservice is running on its own port:
ADD_TRACK_URL = "http://127.0.0.1:5000/tracks"
DELETE_TRACK_URL = "http://127.0.0.1:5002/delete"
LIST_TRACKS_URL  = "http://127.0.0.1:5001/list"
RECOGNIZE_URL    = "http://127.0.0.1:5003/recognize"

class AddTrackTest(unittest.TestCase):
    def setUpClass():
        """Initialize DB once for this test class."""
        database.init_db()
    def setUp(self):
        """Reset DB before each test."""
        database.reset_db()

    def test_add_track_happy_path(self):
        database.reset_db()
   
        test_file_path = "../static/wavs/Blinding Lights.wav"
        

        json_data = {
            "title": "Test Song",
            "artist": "Test Artist",
            "file_path": test_file_path
        }
        rsp = requests.post(ADD_TRACK_URL, json=json_data)


        self.assertEqual(rsp.status_code, 201)
        self.assertIn("Track added successfully", rsp.json()["message"])

    def test_add_track_missing_fields(self):
        """Test adding a track with missing fields."""
        rsp = requests.post(ADD_TRACK_URL, json={})
        self.assertEqual(rsp.status_code, 400)
        self.assertIn("Missing required fields", rsp.json()["error"])

    def test_add_track_invalid_path(self):
        """Test adding a track with an invalid file path."""
        rsp = requests.post(ADD_TRACK_URL, json={
            "title": "Test Song",
            "artist": "Test Artist",
            "file_path": "non_existent.wav"
        })
        self.assertEqual(rsp.status_code, 400)
        self.assertIn("Full track file does not exist", rsp.json()["error"])
        


    def test_file_encoding_failure(self):
        """
        Provide a directory path instead of a file, expecting the microservice
        to return 500 "Failed to encode file".
        """
        test_dir_path = "test_audio_dir"
        # Make a directory (not a file) => fail when reading
        os.mkdir(test_dir_path)

        # Construct an absolute path so microservice sees it
        abs_path = os.path.abspath(test_dir_path)

        rsp = requests.post(ADD_TRACK_URL, json={
            "title": "EncodingFail",
            "artist": "Test Artist",
            "file_path": abs_path
        })

        # Cleanup
        os.rmdir(test_dir_path)

        # We expect 500 if microservice is coded to treat directory => "Failed to encode file"
        self.assertEqual(rsp.status_code, 500,
            f"Expected 500 but got {rsp.status_code}")
        self.assertIn("Failed to encode file", rsp.json()["error"])




class DeleteTrackTest(unittest.TestCase):
    def setUp(self):
        database.reset_db()
        # Insert track so it can be deleted
        # We'll insert directly via the DB for test setup
        database.add_track_to_db("Blinding Lights", "The Weeknd", "../static/wavs/Blinding Lights.wav")

    def tearDown(self):
        database.reset_db()

    def test_delete_track_happy_path(self):
        rsp = requests.delete(DELETE_TRACK_URL, json={
            "title": "Blinding Lights",
            "artist": "The Weeknd"
        })
        self.assertEqual(rsp.status_code, 200)
        self.assertIn("deleted successfully", rsp.json()["message"])

    def test_delete_track_not_found(self):
        rsp = requests.delete(DELETE_TRACK_URL, json={
            "title": "Nonexistent Song",
            "artist": "Unknown Artist"
        })
        self.assertEqual(rsp.status_code, 404)
        self.assertIn("not found", rsp.json()["error"])

    def test_delete_track_missing_fields(self):
        rsp = requests.delete(DELETE_TRACK_URL, json={})
        self.assertEqual(rsp.status_code, 400)
        self.assertIn("Missing 'title' or 'artist'", rsp.json()["error"])

    def test_delete_track_database_error(self):
        # rename DB to simulate a failure
        os.rename("shamzam.db", "shamzam_backup.db")
        rsp = requests.delete(DELETE_TRACK_URL, json={
            "title": "Blinding Lights",
            "artist": "The Weeknd"
        })
        self.assertEqual(rsp.status_code, 500)
        self.assertIn("Database error", rsp.json()["error"])
        os.rename("shamzam_backup.db", "shamzam.db")


class ListTracksTest(unittest.TestCase):
    def setUp(self):
        database.reset_db()
        # Insert some tracks
        database.add_track_to_db("SongOne", "ArtistA", "static/wavs/SongOne.wav")
        database.add_track_to_db("SongTwo", "ArtistB", "static/wavs/SongTwo.wav")

    def tearDown(self):
        database.reset_db()

    def test_list_tracks_happy(self):
        rsp = requests.get(LIST_TRACKS_URL)
        self.assertEqual(rsp.status_code, 200)
        data = rsp.json()
        self.assertIsInstance(data, list, "Should return a JSON list of tracks")
        self.assertGreaterEqual(len(data), 2)

    def test_list_tracks_unhappy(self):
        # rename DB => break
        os.rename("shamzam.db", "shamzam_backup.db")
        rsp = requests.get(LIST_TRACKS_URL)
        self.assertEqual(rsp.status_code, 500)
        self.assertIn("Database error", rsp.json()["error"])
        os.rename("shamzam_backup.db", "shamzam.db")


class TestRecognizeTrack(unittest.TestCase):
    def setUp(self):
        database.reset_db()
        # Insert track so if recognized => found in DB
        database.add_track_to_db("Blinding Lights", "The Weeknd", "encodedstuff")

    def tearDown(self):
        database.reset_db()

    def test_recognize_track_happy_path(self):
        # e.g. a valid fragment
        frag_path = "../static/wavs/~Blinding Lights.wav"
        rsp = requests.post(RECOGNIZE_URL, json={"file_path": frag_path})
       
        self.assertEqual(rsp.status_code, 200)

    def test_fragment_not_recognized(self):
        davos_path = "../static/wavs/~Davos.wav"
        rsp = requests.post(RECOGNIZE_URL, json={"file_path": davos_path })
        self.assertEqual(rsp.status_code, 404)

    def test_full_track_not_in_db(self):
        # e.g. good4u => recognized but not in DB => 405
        good4u = "../static/wavs/~good 4 u.wav"
        rsp = requests.post(RECOGNIZE_URL, json={"file_path": good4u})
        self.assertEqual(rsp.status_code, 405)

    def test_recognize_track_missing_file_path(self):
        rsp = requests.post(RECOGNIZE_URL, json={})
        self.assertEqual(rsp.status_code, 400)
        data = rsp.json()
        self.assertIn("Missing 'file_path'", data["error"])


if __name__ == "__main__":
    unittest.main()
