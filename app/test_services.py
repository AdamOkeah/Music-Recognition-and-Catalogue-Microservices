import unittest
import os
import base64
import database
from track_service import app as track_app
from recognition_service import app as recognition_app

class AddTrackTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize the database before running tests"""
        database.init_db()

    def setUp(self):
        """Reset database before each test"""
        database.reset_db()
        self.app = track_app.test_client()

    def test_add_track_happy_path(self):
        """Test adding a valid track"""
        # Create a dummy WAV file
        test_file_path = "test_audio.wav"
        with open(test_file_path, "wb") as f:
            f.write(os.urandom(1024))  

        response = self.app.post("/tracks", json={
            "title": "Test Song",
            "artist": "Test Artist",
            "file_path": test_file_path
        })
        
        os.remove(test_file_path)  # Cleanup after test
        self.assertEqual(response.status_code, 201)
        self.assertIn("Track added successfully", response.get_json()["message"])

    def test_add_track_missing_fields(self):
        """Test adding a track with missing fields"""
        response = self.app.post("/tracks", json={})  # No data provided
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing required fields", response.get_json()["error"])

    def test_add_track_invalid_path(self):
        """Test adding a track with an invalid file path"""
        response = self.app.post("/tracks", json={
            "title": "Test Song",
            "artist": "Test Artist",
            "file_path": "non_existent.wav"
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("Full track file does not exist", response.get_json()["error"])

    def test_add_track_file_encoding_failure(self):
        """Test adding a track where file encoding fails"""
        # Simulate file error by creating an empty directory instead of a file
        test_file_path = "test_audio.wav"
        os.mkdir(test_file_path)  # Create a directory instead of a file
        
        response = self.app.post("/tracks", json={
            "title": "Test Song",
            "artist": "Test Artist",
            "file_path": test_file_path
        })
        
        os.rmdir(test_file_path)  # Cleanup after test
        self.assertEqual(response.status_code, 500)
        self.assertIn("Failed to encode file", response.get_json()["error"])


class Delete_Track_Test(unittest.TestCase): 
    def setUp(self):
        """Reset database and set up test client"""
        self.app = track_app.test_client()
        database.reset_db()

        # Setup: Add a test track to the database
        wav_file_path = "/static/wavs/Blinding Lights.wav"

        
        database.add_track_to_db("Blinding Lights", "The Weeknd", wav_file_path)

    def tearDown(self):
        """Reset the database after each test"""
        database.reset_db()

    def test_delete_track_happy_path(self):
        """Test deleting an existing track"""
        response = self.app.delete("/tracks", json={
            "title": "Blinding Lights",
            "artist": "The Weeknd"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("deleted successfully", response.get_json()["message"])

    def test_delete_track_not_found(self):
        """Test deleting a non-existent track"""
        response = self.app.delete("/tracks", json={
            "title": "Nonexistent Song",
            "artist": "Unknown Artist"
        })
        self.assertEqual(response.status_code, 404)
        self.assertIn("not found", response.get_json()["error"])

    def test_delete_track_missing_fields(self):
        """Test deleting a track with missing required fields"""
        response = self.app.delete("/tracks", json={})  # Empty request
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing 'title' or 'artist'", response.get_json()["error"])

    def test_delete_track_database_error(self):
        """Test handling an unexpected database error"""
        # Simulate a database failure by renaming the database file
        os.rename("shamzam.db", "shamzam_backup.db")

        response = self.app.delete("/tracks", json={
            "title": "Blinding Lights",
            "artist": "The Weeknd"
        })

        self.assertEqual(response.status_code, 500)
        self.assertIn("Database error", response.get_json()["error"])

        # Restore the database file after test
        os.rename("shamzam_backup.db", "shamzam.db")

        
class List_Tracks_Test(unittest.TestCase): 
    def setUp(self):
        """Reset database and set up test client"""
        self.app = track_app.test_client()
        database.reset_db()
        
        database.add_track_to_db("Blinding Lights", "The Weeknd",  "static/wavs/Don't Look Back In Anger.wav")
        database.add_track_to_db("Blinding Lights", "The Weeknd", "static/wavs/Blinding Lights.wav")
        database.add_track_to_db("Blinding Lights", "The Weeknd", "static/wavs/Everybody Backstreet's Back) (Radio Edit).wav)")

        
    def tearDown(self):
        """Reset the database after each test"""
        database.reset_db()
        
        
    def test_list_tracks_happy(self):
        response = self.app.get("/tracks")
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
    def test_list_tracks_unhappy(self):

        """Test listing tracks when the database is unavailable"""
        os.rename("shamzam.db", "shamzam_backup.db")  # Simulate DB failure

        response = self.app.get("/tracks")

        self.assertEqual(response.status_code, 500)  # ✅ Should return an error
        data = response.get_json()

        self.assertIn("error", data)  # ✅ Should contain an error message
        self.assertIn("Database error", data["error"])

        os.rename("shamzam_backup.db", "shamzam.db")  # Restore DB after test
        
class TestRecognizeTrack(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        database.reset_db()

        # Create a dummy audio file
        self.test_audio_path = "test_audio.wav"
        with open(self.test_audio_path, "wb") as f:
            f.write(os.urandom(1024))  # Generate random bytes as mock audio data

            # Add a dummy track to the database
        self.test_title = "Test Song"
        self.test_artist = "Test Artist"
        encoded_file = base64.b64encode(b"dummy_data").decode("utf-8")
        database.add_track_to_db(self.test_title, self.test_artist, encoded_file)

    def tearDown(self):
        database.reset_db()
        os.remove(self.test_audio_path)

    def test_recognize_track_happy_path(self):
        """✅ Test recognizing a valid track"""
        response = self.app.post("/recognize", json={"file_path": self.test_audio_path})

        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertIn("message", data)
        self.assertIn("recognized_title", data)
        self.assertIn("recognized_artist", data)
        self.assertIn("file_data_b64", data)

        self.assertEqual(data["recognized_title"], self.test_title)
        self.assertEqual(data["recognized_artist"], self.test_artist)
        
    def test_recognize_track_missing_file_path(self):
        """❌ Test recognizing a track with a missing file path"""
        response = self.app.post("/recognize", json={})  # No file_path provided

        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("error", data)
        self.assertEqual(data["error"], "Missing 'file_path'")
        
    def test_recognize_track_missing_file_path(self):
        """❌ Test recognizing a track with a missing file path"""
        response = self.app.post("/recognize", json={})  # No file_path provided

        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("error", data)
        self.assertEqual(data["error"], "Missing 'file_path'")
        
        
        
    def test_recognize_track_audd_api_failure(self):
        """❌ Test Audd.io API failure"""
        os.rename("test_audio.wav", "test_audio_backup.wav")  # Temporarily remove the file to simulate failure

        response = self.app.post("/recognize", json={"file_path": "test_audio.wav"})

        self.assertIn(response.status_code, [500, 404])  # Expect either an API error (500) or "track not found" (404)
        data = response.get_json()
        self.assertIn("error", data)

        os.rename("test_audio_backup.wav", "test_audio.wav")  # Restore file



        
        
        
        
        
    

if __name__ == "__main__":
    unittest.main()    