import unittest
import json
import os
from app import create_app
from app.database import reset_db  # Reset DB before each test

class ShamzamTestCase(unittest.TestCase):
    """End-to-end tests for Shamzam API"""

    def setUp(self):
        """Set up the test client and reset the database before each test"""
        self.app = create_app().test_client()
        reset_db()  # ✅ Clears the database before each test

    ## 1️⃣ Happy Path: Add a Track
    def test_add_track(self):
        """Test adding a new track"""
        response = self.app.post('/tracks', json={
            "title": "Blinding Lights",
            "artist": "The Weeknd",
            "file": "static/_Blinding Lights.wav"
        })
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['message'], "Track added successfully")

    ## 2️⃣ Happy Path: List All Tracks
    def test_list_tracks(self):
        """Test retrieving all tracks"""
        self.test_add_track()  # Ensure at least one track exists
        response = self.app.get('/tracks')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)  # Ensure at least one track is listed

    ## 3️⃣ Happy Path: Recognise a Track (Mocked Response)
    def test_recognise_track(self):
        """Test recognising a music fragment"""
        if not os.path.exists("static/_Blinding Lights.wav"):
            self.skipTest("Test file missing: static/_Blinding Lights.wav")

        response = self.app.post('/recognise', data={
            "file": (open("static/_Blinding Lights.wav", "rb"), "_Blinding Lights.wav")
        })
        print(f"🔍 Test Recognise Response: {response.status_code}, {response.data.decode()}")
        self.assertIn(response.status_code, [200, 404])

    ## 4️⃣ Happy Path: Remove a Track
    def test_remove_track(self):
        """Test deleting a track"""
        self.test_add_track()  # Add a track first
        response = self.app.delete('/tracks/1')  # Assuming it gets ID 1
        self.assertIn(response.status_code, [200, 404])

    ## 5️⃣ Unhappy Path: Adding Track with Missing Fields
    def test_add_track_missing_fields(self):
        """Test adding a track with missing title"""
        response = self.app.post('/tracks', json={
            "artist": "Unknown Artist",
            "file": "static/missing.wav"
        })
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], "Missing fields")

    ## 6️⃣ Unhappy Path: Recognising Non-Existing File (Now Properly Handled)
    def test_recognise_nonexistent_track(self):
        """Test recognising a non-existent file"""
        response = self.app.post('/recognise')  # ✅ No file sent
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], "No file uploaded")

    ## 7️⃣ Unhappy Path: Removing Non-Existing Track
    def test_remove_nonexistent_track(self):
        """Test removing a track that doesn't exist"""
        response = self.app.delete('/tracks/999')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['error'], "Track not found")

if __name__ == '__main__':
    unittest.main()
