song_schema = {
    "type": "object",
    "properties": { 
        "file": {
            "type": "object", 
            "properties": {
                #"name": {"type" : "string"},
                "id": {"type" : "number"}
                            },
                },
            },
    "required": ["file"]
}

import os.path
import json

from flask import request, Response, url_for, send_from_directory
from werkzeug.utils import secure_filename
from jsonschema import validate, ValidationError

from . import models
from . import decorators
from . import app
from .database import session
from .utils import upload_path

@app.route("/api/songs", methods=["GET"])
@decorators.accept("application/json")
def songs_get():
    """ Get a list of songs """
    
    name_like = request.args.get("name_like")
    
    songs = session.query(models.Song)
    
    songs = songs.order_by(models.Song.id)
    
    data = json.dumps([song.as_dictionary() for song in songs])
    return Response(data, 200, mimetype="application/json")

@app.route("/api/songs", methods=["POST"])
@decorators.accept("application/json")
@decorators.require("application/json")
def songs_post():
    """ Post a song """
    data = request.json
    
    try:
        validate(data, song_schema)
    except ValidationError as error:
        data = {"message": error.message}
        return Response(json.dumps(data), 422, mimetype="application/json")
    
    song = models.Song()
    
    file = session.query(models.File).get(data["file"]["id"])
    song.file_id = file.id
    
    session.add(song)
    session.commit()
    
    data = json.dumps(song.as_dictionary())
    headers = {"Location": url_for("songs_get", id=song.id)}
    return Response(data, 201, headers=headers,
                    mimetype="application/json")
#PUT WIP
@app.route("/api/songs/<int:id>", methods=["PUT"])
@decorators.accept("application/json")
@decorators.require("application/json")
def songs_put(id):
    """ Update a song with PUT """
    
    data = request.json
    
    try:
        validate(data, song_schema)
    except ValidationError as error:
        data = {"message": error.message}
        return Response(json.dumps(data), 422, mimetype="application/json")
        
    song = session.query(models.Song).get(id)
    song.file_id = (data["file"]["id"])
    session.commit()
    
    data = json.dumps(song.as_dictionary())
    headers = {"Location": url_for("songs_get")}
    return Response(data, 201, headers=headers,
        mimetype="application/json")
    
@app.route("/api/songs/<int:id>", methods=["DELETE"])
@decorators.accept("application/json")
@decorators.require("application/json")
def songs_delete(id):
    """ Delete a song """
    
    song = session.query(models.Song).get(id)
    
    if not song:
        message = "Could not find song with id {}".format(id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")
        
    session.delete(song)
    session.commit()
    
    songs = session.query(models.Song).order_by(models.Song.id)
    
    data = json.dumps([song.as_dictionary() for song in songs])
    return Response(data, 200, mimetype="application.json")
    
@app.route("/uploads/<filename>", methods=["GET"])
def uploaded_file(filename):
    return send_from_directory(upload_path(), filename)
    
@app.route("/api/files", methods=["POST"])
@decorators.require("multipart/form-data")
@decorators.accept("application/json")
def file_post():
    file = request.files.get("file")
    if not file:
        data = {"message": "Could not find file data"}
        return Response(json.dumps(data), 422, mimetype="application/json")

    filename = secure_filename(file.filename)
    db_file = models.File(name=filename)
    session.add(db_file)
    session.commit()
    file.save(upload_path(filename))

    data = db_file.as_dictionary()
    return Response(json.dumps(data), 201, mimetype="application/json")
    
