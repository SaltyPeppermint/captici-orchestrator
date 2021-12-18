import sqlalchemy as sqla
from cdpb_test_orchestrator.settings import get_config
from sqlalchemy.orm import sessionmaker

from .models import Base

session_factory = None


config = get_config()
db_type = config["DB"]["type"]
db_location = config["NFS"]["mount"] + "/sqlite.db"
print(f"{db_type}://{db_location}")
engine = sqla.create_engine(
    f"{db_type}:///{db_location}",
    echo=True,
    connect_args={"check_same_thread": False},
)
session_factory = sessionmaker(bind=engine, future=True)


def init_db():
    Base.metadata.create_all(engine, checkfirst=True)


def get_db():
    db = session_factory()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
