
import sqlalchemy as sqla
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from test_orchestrator.settings import config

from .models.base import Base
from .models.report import Report
from .models.config import Config
from .models.commit import Commit
from .models.project import Project


def init_db():
    Base.metadata.create_all(engine, checkfirst=True)


def get_session():
    return Session()


db_type = config["DB"]["type"]
db_location = config["NFS"]["mount"] + "/sqlite.db"
print(f"{db_type}://{db_location}")
engine = sqla.create_engine(f"{db_type}:///{db_location}", echo=True)
Session = sessionmaker(bind=engine)

if __name__ == "__main__":
    init_db()
