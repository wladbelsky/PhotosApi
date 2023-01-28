from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship


class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    datetime = Column(DateTime)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String)
    latitude = Column(String)
    longitude = Column(String)
    persons = relationship("Person", back_populates="photo")

    def __repr__(self):
        return f"Photo(title={self.name}, description={self.description}, filename={self.filename})"


class Person(Base):
    __tablename__ = "persons"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    photo_id = Column(Integer, ForeignKey("photos.id"))
    photo = relationship("Photo", back_populates="persons")

    def __repr__(self):
        return f"Person(name={self.name})"
