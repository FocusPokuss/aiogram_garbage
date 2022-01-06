from sqlalchemy import Integer, BigInteger, String, Boolean, DateTime, Column, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base
from db.base import Base


class RatingAssociation(Base):
    __tablename__ = 'rating_associations'
    user_id = Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    photo_id = Column('photo_id', Integer, ForeignKey('photos.id', ondelete='CASCADE'), primary_key=True)
    action = Column('action', Boolean, nullable=False)
    idx = Index(user_id, photo_id)


class User(Base):
    __tablename__ = 'users'
    id = Column(BigInteger, primary_key=True, autoincrement=False)
    name = Column(String)
    is_admin = Column(Boolean, default=False)
    uploaded_photos = relationship('Photo', cascade='all, delete-orphan')


class Photo(Base):
    __tablename__ = 'photos'
    id = Column(Integer, primary_key=True)
    user_id = Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'))
    title = Column(String, nullable=False, unique=True)
    data = Column(String, nullable=False)
    t_upload = Column('upload_t', DateTime)
    rsh = relationship('User', secondary='rating_associations', backref='photos')


class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, autoincrement=True)
    mes = Column(String)
