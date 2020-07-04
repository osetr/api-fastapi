from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "User"

    login = Column(String(30), primary_key=True)
    hashed_password = Column(Text)


class Post(Base):
    __tablename__ = "Post"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(30))
    post = Column(Text)
    date_time = Column(DateTime, default=datetime.utcnow)


class Love(Base):
    __tablename__ = "Love"

    lover = Column(String(30), primary_key=True)
    loved = Column(String(30))
    post_id = Column(Integer, primary_key=True)
    date_time = Column(DateTime, default=datetime.utcnow)


class Login(Base):
    __tablename__ = "Login"

    login = Column(String(30), primary_key=True)
    date_time = Column(DateTime, default=datetime.utcnow)
