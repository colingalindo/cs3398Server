from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sqlalchemy
from contextlib import contextmanager

engine = None
Base = declarative_base()
Session = sessionmaker()

def set_engine(_engine):
    """
    Sets the database engine used by the model. For testing this should be an in-memory SQLite database, for production
    it should be something like MySQL.
    """
    global engine
    engine = _engine
    Base.metadata.bind = engine
    Session.configure(bind=engine)


def create_engine(uri, echo=True):
    """
    Sets the database engine from a database connection string.
    """
    set_engine(sqlalchemy.create_engine(uri, echo=echo))

def create_schema():
    Base.metadata.create_all(engine)

def teardown():
    """
    Unsets the database engine.
    """
    Session.remove()

@contextmanager
def session_scope():
    """
    Provide a transactional scope around a series of operations.

    This will automatically rollback the session on an exception, then re-raise the exception.

    On success it commits.

    On success or failure, it closes the session.
    """
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
