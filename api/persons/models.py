from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship


class Person(Base):
    __tablename__ = "persons"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    photo_id = Column(Integer, ForeignKey("photos.id"))
    photo = relationship("Photo", back_populates="persons")

    def __repr__(self):
        return f"Person(name={self.name})"
