from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import session

from .database import Base

class Song(Base):
    __tablename__ = 'songs'
    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    
    def as_dictionary(self):
        song_file_info = session.query(File).filter_by(id=self.file_id).first()
        song = {
            "id": self.id,
            "file": {
                "id": song_file_info.id,
                #"name": self.file.name
            }
        }
        return song
        
class File(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    song = relationship('Song', uselist=False, backref="song")
    
    def as_dictionary(self):
        file = {
            "id": self.id,
            "name": self.name
            }
        return file