from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship


class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    date = Column(Date)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String)
    latitude = Column(String)
    longitude = Column(String)
    persons = relationship("Person", back_populates="photo")

    def __repr__(self):
        return f"Photo(title={self.name}, description={self.description}, filename={self.filename})"
