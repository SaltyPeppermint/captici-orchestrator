from storage.sql.models.base import Base
from sqlalchemy import Sequence, Column, Boolean, Integer, String, ForeignKey


class Commit(Base):
    __tablename__ = "commits"
    id = Column(Integer, Sequence("commit_id_seq"), primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    hash = Column(String(32), nullable=False)
    tested = Column(Boolean(), nullable=False)

    def __init__(self, project_id, hash, tested):
        self.project_id = project_id
        self.hash = hash
        self.tested = tested

    def __repr__(self):
        return f"<Commit(id='{self.id}', project_id='{self.project_id}', hash='{self.hash}', tested='{self.tested}')>"
