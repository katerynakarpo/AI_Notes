from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, LargeBinary
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import declarative_base, relationship, mapped_column
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    user_email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)

    notes = relationship('Note', back_populates='user')
    search_history = relationship('SearchHistory', back_populates='user')
    cnt_notes = relationship('CntNotes', back_populates='user')


class Note(Base):
    __tablename__ = 'notes'

    created_at = Column(DateTime, default=datetime.utcnow)
    note_id = Column(Integer, primary_key=True, autoincrement=True)
    text_note = Column(String, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    user = relationship('User', back_populates='notes')
    embedding = relationship('Embedding', back_populates='note')


class Embedding(Base):
    __tablename__ = 'notes_embeddings'
    created_at = Column(DateTime, default=datetime.utcnow)
    embedding_id = Column(Integer, primary_key=True, autoincrement=True)
    embedding_text = mapped_column(Vector(1536), nullable=False)
    note_id = Column(Integer, ForeignKey('notes.note_id'), nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow)
    note = relationship('Note', back_populates='embedding')


class SearchHistory(Base):
    __tablename__ = 'search_history'

    created_at = Column(DateTime, default=datetime.utcnow)
    search_id = Column(Integer, primary_key=True, autoincrement=True)
    search_prompt = Column(String, nullable=False)
    search_embedding = mapped_column(Vector(1536), nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)

    user = relationship('User', back_populates='search_history')


class CntNotes(Base):
    # MVP v.0.1 contain in this table only 1 number, in future versions can be used with users
    __tablename__ = 'cnt_notes'

    cnt_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    cnt = Column(Integer)

    user = relationship('User', back_populates='cnt_notes')
