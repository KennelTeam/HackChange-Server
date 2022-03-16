from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *

Base = declarative_base()


class Investor(Base):
    __tablename__ = 'investors'

    id = Column(Integer, primary_key=True, autoincrement=True)
    access_token = Column(String(64))

    nickname = Column(String(32))
    password = Column(String(32))

    avatar_link = Column(String(64))

    def __init__(self, nickname: str, password: str) -> None:
        super().__init__()
        self.nickname = nickname
        self.password = password


class Instrument(Base):
    __tablename__ = 'instruments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30))
    details = Column(String(200))

    def __init__(self, name: str, details: str) -> None:
        super().__init__()
        self.name = name
        self.details = details


class Topic(Base):
    __tablename__ = 'topics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    instrument_id = Column(Integer)
    title = Column(String(96))

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


class PostVoting(Base):
    __tablename__ = 'postsvotings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer)
    investor_id = Column(Integer)
    up_voted = Column(Boolean)

    def __init__(self, post_id: int, investor_id: int, up_voted: bool) -> None:
        super().__init__()
        self.post_id = post_id
        self.investor_id = investor_id
        self.up_voted = up_voted


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
