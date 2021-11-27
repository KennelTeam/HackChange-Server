
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm.session import Session
from .images import Base

_SessionsManager: scoped_session = None


def _init_operating():
    user, pwd, host, port, dbname = input(
        'Enter database credentials:').split()

    engine = create_engine(f'mysql://{user}:{pwd}@{host}:{port}/{dbname}')
    Base.metadata.create_all(engine)

    global _SessionsManager
    session_factory = sessionmaker(bind=engine)
    _SessionsManager = scoped_session(session_factory)

    print('Database initialized')


def get_session() -> Session:
    return _SessionsManager()


def clear_session():
    _SessionsManager.remove()
