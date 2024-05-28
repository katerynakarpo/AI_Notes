import os
from sqlalchemy import create_engine, desc, select, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from db.db_tables import Base, Note, Embedding, SearchHistory, CntNotes
from datetime import datetime
import numpy as np

DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://')


def connect():
    try:
        engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        return Session
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        return error


Session = connect()
session = Session()
session.execute(text('CREATE EXTENSION IF NOT EXISTS vector'))


def get_all_notes_sorted_by_created_at_desc(user_id: int = 1):
    notes = session.query(Note).filter_by(is_deleted=False, user_id=user_id).order_by(desc(Note.created_at)).all()
    return [(note.note_id, note.text_note) for note in notes]


def add_note(note_text: str, embedding_text: list, user_id: int = 1):
    note_id = add_note_to_DB(note_text, user_id)
    add_embedding(np.array(embedding_text), note_id)
    return note_id


def add_note_to_DB(note_text: str, user_id: int = 1):
    new_note = Note(text_note=note_text, user_id=user_id)
    session.add(new_note)
    session.commit()
    return new_note.note_id


def add_embedding(embedding_text: list, note_id: int):
    new_embedding = Embedding(embedding_text=np.array(embedding_text), note_id=note_id)
    session.add(new_embedding)
    session.commit()


def update_note(note_id: int, new_text: str):
    note = session.query(Note).filter_by(note_id=note_id).first()
    if note and not note.is_deleted:
        note.text_note = new_text
        note.last_updated = datetime.utcnow()
        session.commit()


def delete_note(note_id: int):
    note = session.query(Note).filter_by(note_id=note_id).first()
    if note and not note.is_deleted:
        note.is_deleted = True
        note.last_updated = datetime.utcnow()
        session.commit()


def add_search_prompt(prompt: str, prompt_embedding: list, user_id: int = 1):
    new_prompt = SearchHistory(user_id=user_id, search_prompt=prompt, search_embedding=np.array(prompt_embedding))
    session.add(new_prompt)
    session.commit()


def get_notes_number(user_id: int = 1):
    notes_number = session.query(CntNotes).filter_by(user_id=user_id).first()
    return notes_number.cnt


def get_notes_limited(notes_limit: int, offset: int, user_id: int = 1):
    notes = session.query(Note).filter_by(is_deleted=False, user_id=user_id).order_by(desc(Note.created_at)).limit(
        notes_limit).offset(offset).all()
    return [(note.note_id, note.text_note) for note in notes]
    # return []


def get_notes_by_ids(ids_list: list):
    notes = session.query(Note).filter(Note.note_id.in_(ids_list)).all()
    return [(note.note_id, note.text_note) for note in notes]


def get_all_notes_embeddings(user_id: int = 1):
    embeddings = session.query(Embedding).join(Note).filter(Note.user_id == user_id).filter(
        Note.is_deleted == False)
    return [(embedding.note_id, embedding.embedding_text) for embedding in embeddings]


def get_max_note(max_note_id: int, user_id: int = 1):
    note = session.query(Note).filter_by(is_deleted=False, user_id=user_id).filter(Note.note_id < max_note_id).order_by(desc(Note.created_at)).first()
    if note:
        return (note.note_id, note.text_note)
    return None, None
