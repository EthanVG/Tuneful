song_schema = {
    "properties": {
        "file": {
            "name": {"type" : "string"}
        }
    },
    #"required": ["id",]
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
    
    if name_like:
        songs = songs.filter(models.Song.file.name.contains(name_like))
    
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
    
    #file = models.File(name=data["file.name"])
    file = models.File()
    song = models.Song()
    
    song.file = file
    
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
        
    song = models.Song.file(name=data["name"])
    session.query(models.Song).get(id).update(song)
    session.commit()
    
    data = json.dumps(song.as_dictionary())
    headers = {"Location": url_for("post_get")}
    return Response(data, 201, headers=headers,
        mimetype="application.json")
    
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
    
    