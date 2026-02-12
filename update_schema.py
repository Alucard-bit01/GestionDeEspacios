from app import app, db
from model.models import Classroom
from sqlalchemy import text

def update_schema():
    with app.app_context():
        print("Dropping old tables to enforce schema change...")
        try:
            db.session.execute(text("DROP TABLE reservations")) # In case it exists
        except:
            pass
            
        try:
            db.session.execute(text("DROP TABLE classrooms"))
        except:
            pass
            
        db.session.commit()
        
        print("Creating new tables...")
        db.create_all()
        
        print("Reseeding classrooms...")
        for i in range(1, 11):
            room = Classroom(name=f"Sala {i}")
            db.session.add(room)
        db.session.commit()
        print("Schema updated and seeded.")

if __name__ == '__main__':
    update_schema()
