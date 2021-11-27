from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *

Base = declarative_base()


class Investor(Base):
    __tablename__ = 'investors'

    id = Column(Integer, primary_key=True, autoincrement=True)
    google_user_id = Column(String(32))
    access_token = Column(String(64))

    nickname = Column(String(16))
    avatar_link = Column(String(100))

    def __init__(self, google_user_id: int, access_token: str) -> None:
        super().__init__()
        self.google_user_id = google_user_id
        self.access_token = access_token


class Instrument(Base):
    __tablename__ = 'instruments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30))
    details = Column(String(100))

    def __init__(self, name: str, details: str) -> None:
        super().__init__()
        self.name = name
        self.details = details

class Topic(Base):
    __tablename__ = 'topics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    instrument_id = Column(Integer)
    title = Column(String(32))

    def __init__(self, instrument_id: int, title: str) -> None:
        super().__init__()
        self.instrument_id = instrument_id
        self.title = title

class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    author_id = Column(Integer)
    topic_id = Column(Integer)
    text = Column(Text)

    def __init__(self, author_id: int, topic_id: int, text: str) -> None:
        super().__init__()
        self.author_id = author_id
        self.topic_id = topic_id
        self.text = text


class Subscription(Base):
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    subscriber_id = Column(Integer)
    blogger_id = Column(Integer)

    def __init__(self, subscriber_id: int, blogger_id: int) -> None:
        super().__init__()
        self.subscriber_id = subscriber_id
        self.blogger_id = blogger_id


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    post_id = Column(Integer)
    commenter_id = Column(Integer)
    text = Column(Text)

    def __init__(self, post_id: int, commenter_id: int, text: str) -> None:
        super().__init__()
        self.post_id = post_id
        self.commenter_id = commenter_id
        self.text = text
