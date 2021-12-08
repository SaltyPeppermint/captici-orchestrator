from storage.sql.models.base import Base
from sqlalchemy import Sequence, Column, Integer, String, ForeignKey


class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, Sequence("config_id_seq"), primary_key=True)
    config_id = Column(Integer, ForeignKey("configs.id"), nullable=False)
    commit_id = Column(Integer, ForeignKey("commits.id"), nullable=False)
    content = Column(String(65536), nullable=False)

    def __init__(self, config_id, commit_id, content):
        self.config_id = config_id
        self.commit_id = commit_id
        self.content = content

    def __repr__(self):
        return f"<Config(id='{self.id}', config_id='{self.config_id}', commit_id='{self.commit_id}', content='{self.content}')>"
