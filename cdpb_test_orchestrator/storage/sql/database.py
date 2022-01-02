import logging

import sqlalchemy as sqla
from cdpb_test_orchestrator import settings
from sqlalchemy.orm import sessionmaker

from .models import Base

session_factory = None
logger = logging.getLogger("sqlalchemy")
logger.setLevel(logging.WARN)

if settings.db_type() == "sqlite":
    db_location = settings.db_location() + "/sqlite.db"
    logger.info(f"Opening SQLite DB at sqlite:///{db_location}")
    # echo=True means sqlalchemy keeps spamming the logs
    engine = sqla.create_engine(
        f"sqlite:///{db_location}",
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
