import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Exam, ExamEvent

# Setup paths (just in case)
sys.path.append(os.path.join(os.getcwd(), 'src'))

DB_URL = 'sqlite:///db.sqlite3'

def verify():
    engine = create_engine(DB_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        exam_count = session.query(Exam).count()
        event_count = session.query(ExamEvent).count()
        
        print(f"Total Exams: {exam_count}")
        print(f"Total Events: {event_count}")
        
        if exam_count > 0:
            print("\nSample Exams:")
            for exam in session.query(Exam).limit(5):
                print(f"- {exam.name} ({exam.organization})")
                
        if event_count > 0:
            print("\nSample Events:")
            for event in session.query(ExamEvent).limit(5):
                print(f"- {event.exam.name}: {event.event_type} ({event.year})")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    verify()
