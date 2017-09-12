import unittest
import os
import shutil
import json
try: from urllib.parse import urlparse
except ImportError: from urlparse import urlparse # Py2 compatibility
from io import StringIO

import sys; print(list(sys.modules.keys()))
# Configure our app to use the testing databse
os.environ["CONFIG_PATH"] = "tuneful.config.TestingConfig"

from tuneful import app
from tuneful import models
from tuneful.utils import upload_path
from tuneful.database import Base, engine, session

class TestAPI(unittest.TestCase):
    """ Tests for the tuneful API """

    def setUp(self):
        """ Test setup """
        self.client = app.test_client()

        # Set up the tables in the database
        Base.metadata.create_all(engine)

        # Create folder for test uploads
        os.mkdir(upload_path())

    def tearDown(self):
        """ Test teardown """
        session.close()
        # Remove the tables and their data from the database
        Base.metadata.drop_all(engine)

        # Delete test upload folder
        shutil.rmtree(upload_path())

    def test_get_empty_songs(self):
        """ Getting songs from an empty database """
        response = self.client.get("/api/songs",
            headers=[("Accept", "application/json")]
            )
            
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        
        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(data, [])
        
    def test_get_songs(self):
        """ Getting songs from a populated database """

        songA = models.Song()
        songB = models.Song()
        
        fileA = models.File(name="fileA")
        fileB = models.File(name="fileB")
        
        session.add_all([fileA, fileB])
        session.commit()
        
        songA.file_id = fileA.id
        songB.file_id = fileB.id
        
        session.add_all([songA, songB])
        session.commit()
        
        response = self.client.get("/api/songs",
            headers=[("Accept", "application/json")]
            )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        
        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(len(data), 2)
        
        songAR = data[0]
        self.assertEqual(songAR, songA.as_dictionary())
        
        songBR = data[1]
        self.assertEqual(songBR, songB.as_dictionary())
        
    def test_post_song(self):
        """ Posting a song """
        file = models.File(name="fileA")
        session.add(file)
        session.commit()
        
        data = {
            "file": {"id": file.id}
        }
        
        response = self.client.post("/api/songs",
            data=json.dumps(data),
            content_type="application/json",
            headers=[("Accept", "application/json")]
        )
    
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(urlparse(response.headers.get("Location")).path,
                         "/api/songs")
                         
        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(data["id"], 1)
        
        songs = session.query(models.Song).all()
        self.assertEqual(len(songs), 1)
        
        
    def test_put_song(self):
        """ Updating a song """
         
        songA = models.Song()
         
        fileA = models.File(name="fileA")
        fileB = models.File(name="fileB")
        
        session.add_all([fileA, fileB])
        session.commit()
        
        songA.file_id = fileA.id
        
        session.add_all([songA])
        session.commit()
         
        data = {
            "file": {"id": fileB.id}
        }
        
        response = self.client.put("/api/songs/{}".format(songA.id),
            data=json.dumps(data),
            content_type="application/json",
            headers=[("Accept", "application/json")]
        )
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(urlparse(response.headers.get("Location")).path,
                         "/api/songs")
        
        songs = session.query(models.Song).all()
        self.assertEqual(len(songs), 1)
        
        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(data["file"]["id"], fileB.id)
        
        
    def test_delete_song(self):
        """ Delete a song """
        data = {
        }
        
        song = models.Song()
        file = models.File(name="file")
        
        session.add_all([file])
        session.commit()
        
        song.file_id = file.id
        
        session.add_all([song])
        session.commit()
        
        songs = session.query(models.Song).all()
        self.assertEqual(len(songs), 1)
        
        response = self.client.delete("/api/songs/{}".format(song.id),
            data=json.dumps(data),
            content_type="application/json",
            headers=[("Accept", "application/json")]
        )
        
        songs = session.query(models.Song).all()
        self.assertEqual(len(songs), 0)
        
        