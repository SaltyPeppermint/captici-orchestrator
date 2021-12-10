from .base import Base
from sqlalchemy import Sequence, Column, Integer, String, ForeignKey


class Config(Base):
    __tablename__ = "configs"
    id = Column(Integer, Sequence("config_id_seq"), primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    content = Column(String(65536), nullable=False)

    def __init__(self, project_id, content):
        self.project_id = project_id
        self.content = content

    def __repr__(self):
        return f"<Config(id='{self.id}', project_id='{self.project_id}', content='{self.content}')>"
