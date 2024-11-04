import sqlite3
import sqlalchemy
import datetime

from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def init_db(engine: sqlalchemy.Engine):
    Base.metadata.create_all(bind=engine, checkfirst=True)


class Config(Base):
    __tablename__ = "config"
    key = Column(String, primary_key=True, unique=True)
    value = Column(String)
    last_update = Column(DateTime, default=datetime.datetime.utcnow)


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    num = Column(Integer)
    name = Column(String, index=True)
    description = Column(String)
    content = Column(String)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)


class SnailBet(Base):
    __tablename__ = "snailbet"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    user_id = Column(Integer)
    result = Column(Integer)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    def to_dict_for_insert(self):
        return {
            "user_id": self.user_id,
            "result": self.result
        }


class SnailVote(Base):
    __tablename__ = "snailvote"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    xeet_poster = Column(String)
    is_snail = Column(Integer)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)


class SnailStateCache(Base):
    __tablename__ = "snailstate"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    tweet_id = Column(String)
    initial_poster_name = Column(String)
    initial_jump_url = Column(String)
    initial_post_time = Column(DateTime)
    post_count = Column(Integer)

class FishScore(Base):
    __tablename__ = "fishscore"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    user_id = Column(Integer)
    fish_caught = Column(Integer)
    fish_missed = Column(Integer)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)


class FishResult(Base):
    __tablename__ = "fishresult"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    user_name = Column(String)
    fish_weight = Column(Integer)
    fish_fed = Column(Integer)
    caught_at = Column(DateTime, default=datetime.datetime.utcnow)
