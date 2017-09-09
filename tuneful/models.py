from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base

class Song(Base):
    __tablename__ = 'songs'
    id = Column(Integer, primary_key=True)
    file = relationship("File", uselist=False, backref="file")
    
    def as_dictionary(self):
        song = {
            "id": self.id,
            "file": {
                "id": self.file.id,
                "name": self.file.name
            }
        }
        return song
        
class File(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    song_id = Column(Integer, ForeignKey('songs.id'), nullable=False)
    
    def as_dictionary(self):
        file = {
            "id": self.id,
            "name": self.name
            }
        return file