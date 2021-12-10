from .base import Base
from sqlalchemy import Sequence, Column, Integer, String


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, Sequence("project_id_seq"), primary_key=True)
    name = Column(String(256), nullable=False)

    def __repr__(self):
        return f"<Project(id='{self.id}', name='{self.name}')>"
