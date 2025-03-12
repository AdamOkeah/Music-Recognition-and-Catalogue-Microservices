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
RECOGNIZE_URL    = "http://127.0.0.1:5003/recognise"

class AddTrackTest(unittest.TestCase):
    def setUpClass():
        """Initialize DB once for this test class."""
        database.init_db()
    def setUp(self):
        """Reset DB before each test."""
        database.reset_db()

    def test_add_track_happy_path(self):
        database.reset_db()
   
        test_file_path = "./static/wavs/Blinding Lights.wav"
        

        json_data = {
            "title": "Test Song",
            "artist": "Test Artist",
            "file_path": test_file_path
        }
        rsp = requests.post(ADD_TRACK_URL, json=json_data)


        self.assertEqual(rsp.status_code, 200)


    def test_add_track_missing_fields(self):
        """Test adding a track with missing fields."""
        rsp = requests.post(ADD_TRACK_URL, json={})
        self.assertEqual(rsp.status_code, 400)


    def test_add_track_invalid_path(self):
        """Test adding a track with an invalid file path."""
        rsp = requests.post(ADD_TRACK_URL, json={
            "title": "Test Song",
            "artist": "Test Artist",
            "file_path": "non_existent.wav"
        })
        self.assertEqual(rsp.status_code, 400)


    def test_add_empty_audio_file(self):
        """
        Try to add an empty audio file (0 bytes),
        expecting the microservice to reject it.
        """
        empty_file_path = "empty_audio.wav"
        
        # Create an empty file
        open(empty_file_path, "wb").close()

        # Get absolute path
        abs_path = os.path.abspath(empty_file_path)

        rsp = requests.post(ADD_TRACK_URL, json={
            "title": "Empty Audio",
            "artist": "Silent Artist",
            "file_path": abs_path
        })

        # Cleanup
        os.remove(empty_file_path)

        #Expecting 400 Bad Request because the file is empty
        self.assertEqual(rsp.status_code, 400, f"Expected 400 but got {rsp.status_code}")
        self.assertIn("Audio file is empty", rsp.json()["error"])







class DeleteTrackTest(unittest.TestCase):
    def setUp(self):
        database.reset_db()
        # Insert track so it can be deleted
        # We'll insert directly via the DB for test setup
        database.add_track_to_db("Blinding Lights", "The Weeknd", "./static/wavs/Blinding Lights.wav")

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
        """Trigger a real database failure by locking the table"""
        conn = database.get_connection()
        cursor = conn.cursor()

        try:
            #Lock the table to prevent DELETE queries
            cursor.execute("BEGIN IMMEDIATE")
            cursor.execute("SELECT * FROM tracks")  # Locks the table

            #Now, send DELETE request while the table is locked
            rsp = requests.delete("http://127.0.0.1:5002/delete", json={
                "title": "Blinding Lights",
                "artist": "The Weeknd"
            })

            #Expect 500 since the database is locked
            self.assertEqual(rsp.status_code, 500)
            self.assertIn("Database error", rsp.json()["error"])

        finally:
            #Release the lock so future tests don't fail
            conn.rollback()
            conn.close()





class ListTracksTest(unittest.TestCase):
    def setUp(self):
        database.reset_db()
        # Insert some tracks
        database.add_track_to_db("Blinding Lights", "The Weeknd", "./static/wavs/Blinding Lights.wav")
        database.add_track_to_db("good 4 u", "Olivia Rodrigo", "./static/wavs/good 4 u.wav")

    def tearDown(self):
        database.reset_db()

    def test_list_tracks_happy(self):
        rsp = requests.get(LIST_TRACKS_URL)
        self.assertEqual(rsp.status_code, 200)
        data = rsp.json()
        self.assertIsInstance(data, list, "Should return a JSON list of tracks")
        self.assertGreaterEqual(len(data), 2)

    def test_list_tracks_database_error(self):
            """Simulate DB failure by corrupting the database schema"""
            database.reset_db()

            # Insert a corrupt SQL statement to break the database
            with database.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DROP TABLE tracks")  # Completely removes the table
                conn.commit()

            # Now the microservice should fail because the table is missing
            rsp = requests.get("http://127.0.0.1:5001/list")

            self.assertEqual(rsp.status_code, 500)
            self.assertIn("Database error", rsp.json()["error"])

            # Re-initialize the database so that further tests don't fail
            database.init_db()

   


class TestRecognizeTrack(unittest.TestCase):
    def setUp(self):
        database.reset_db()
        # Insert track so if recognized => found in DB
        database.add_track_to_db("Blinding Lights", "The Weeknd", "encodedstuff")

    def tearDown(self):
        database.reset_db()

    def test_recognize_track_happy_path(self):
        # e.g. a valid fragment
        frag_path = "./static/wavs/~Blinding Lights.wav"
        rsp = requests.post(RECOGNIZE_URL, json={"file_path": frag_path})
       
        self.assertEqual(rsp.status_code, 200)

    def test_fragment_not_recognized(self):
        davos_path = "./static/wavs/~Davos.wav"
        rsp = requests.post(RECOGNIZE_URL, json={"file_path": davos_path })
        self.assertEqual(rsp.status_code, 404)

    def test_full_track_not_in_db(self):
        # e.g. good4u => recognized but not in DB => 405
        good4u = "./static/wavs/~good 4 u.wav"
        rsp = requests.post(RECOGNIZE_URL, json={"file_path": good4u})
        self.assertEqual(rsp.status_code, 405)

    def test_recognize_track_missing_file_path(self):
        rsp = requests.post(RECOGNIZE_URL, json={})
        self.assertEqual(rsp.status_code, 400)
        data = rsp.json()
        self.assertIn("Missing 'file_path'", data["error"])


if __name__ == "__main__":
    unittest.main()
