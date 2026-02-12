from app import app, db
from model.models import Classroom

def init_classrooms():
    with app.app_context():
        # Create table if it doesn't exist
        db.create_all()
        
        # Check if classrooms exist
        count = Classroom.query.count()
        if count == 0:
            print("Seeding 10 classrooms...")
            for i in range(1, 11):
                room = Classroom(name=f"Sala {i}")
                db.session.add(room)
            db.session.commit()
            print("Classrooms created successfully.")
        else:
            print(f"Classrooms already exist ({count}). Skipping seed.")

if __name__ == '__main__':
    init_classrooms()
