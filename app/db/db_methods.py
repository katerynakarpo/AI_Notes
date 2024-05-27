from db.config_db import DATABASE_URL
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from db.db_tables import Base, Note, SearchHistory, CntNotes
from datetime import datetime

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


def get_all_notes_sorted_by_created_at_desc(user_id=1):
    notes = session.query(Note).filter_by(is_deleted=False, user_id=user_id).order_by(desc(Note.created_at)).all()
    return [(note.note_id, note.text_note) for note in notes]


def add_note(note_text, user_id=1):
    new_note = Note(text_note=note_text, user_id=user_id)
    session.add(new_note)
    session.commit()
    return new_note.note_id


def update_note(note_id, new_text):
    note = session.query(Note).filter_by(note_id=note_id).first()
    if note and not note.is_deleted:
        note.text_note = new_text
        note.last_updated = datetime.utcnow()
        session.commit()


def delete_note(note_id):
    note = session.query(Note).filter_by(note_id=note_id).first()
    if note and not note.is_deleted:
        note.is_deleted = True
        note.last_updated = datetime.utcnow()
        session.commit()


def add_search_prompt(prompt):
    new_prompt = SearchHistory(search_prompt=prompt)
    session.add(new_prompt)
    session.commit()


def get_notes_number(user_id=1):
    notes_number = session.query(CntNotes).filter_by(user_id=user_id).first()
    return notes_number.cnt

# min max limit 10 ofset 90 (витягнути 10 після 90)

