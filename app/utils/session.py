import os
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv


Base = declarative_base()


load_dotenv()
engine = create_engine(
    f"postgresql://{os.getenv('DATABASE_USERNAME')}:"
    f"{os.getenv('DATABASE_PASSWORD')}@{os.getenv('DATABASE_HOST')}:"
    f"{os.getenv('DATABASE_PORT')}/{os.getenv('APP_DATABASE')}"
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
