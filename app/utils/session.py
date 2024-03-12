import os
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

engine = create_engine(
    f"postgresql://{os.environ.get('DATABASE_USERNAME')}:"
    f"{os.environ.get('DATABASE_PASSWORD')}@{os.environ.get('DATABASE_HOST')}:"
    f"{os.environ.get('DATABASE_PORT')}/{os.environ.get('APP_DATABASE')}"
)

SessionFactory = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def create_session() -> Iterator[Session]:
    """Create new database session.

    Yields:
        Database session.
    """

    session = SessionFactory()

    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
