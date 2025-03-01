import unittest
import json
import base64
from io import BytesIO
import app.track_service
import app.recognition_service

class TrackServiceTests(unittest.TestCase):
    def setUp(self):
        app.track_service.app.config['TESTING'] = True
        self.client = app.track_service.app.test_client()

    def test_add_track_json(self):
        file_data = base64.b64encode(b"dummy wav data").decode("utf-8")
        response = self.client.post("/tracks", json={
            "title": "Blinding Lights",
            "artist": "The Weeknd",
            "file_data": file_data
        })
        self.assertEqual(response.status_code, 201)

    def test_add_track_missing_field(self):
        response = self.client.post("/tracks", json={"artist": "The Weeknd"})
        self.assertEqual(response.status_code, 400)

class RecognitionServiceTests(unittest.TestCase):
    def setUp(self):
        app.recognition_service.app.config['TESTING'] = True
        self.client = recognition_service.app.test_client()

    def test_recognize_json(self):
        file_data = base64.b64encode(b"test wav data").decode("utf-8")
        response = self.client.post("/recognize", json={"file_data": file_data})
        self.assertIn(response.status_code, [200, 404])

    def test_recognize_missing_field(self):
        response = self.client.post("/recognize", json={})
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()
