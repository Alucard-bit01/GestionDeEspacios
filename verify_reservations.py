from app import app, db
from model.models import Reservation, User, Classroom
from datetime import datetime, timedelta

def verify_logic():
    with app.app_context():
        print("Cleaning up old reservations for test...")
        Reservation.query.delete()
        db.session.commit()
        
        # Get a user and room
        user = User.query.first()
        room = Classroom.query.first()
        
        if not user or not room:
            print("Error: Need at least one user and one classroom.")
            return

        print(f"Testing with User: {user.username}, Room: {room.name}")
        
        # Scenario 1: Book 10:00 - 11:00
        start1 = datetime(2025, 1, 1, 10, 0)
        end1 = datetime(2025, 1, 1, 11, 0)
        
        res1 = Reservation(user_id=user.id, classroom_id=room.id, start_time=start1, end_time=end1)
        db.session.add(res1)
        db.session.commit()
        print("Created reservation 10:00-11:00 -> SUCCESS")
        
        # Scenario 2: Try overlapping book 10:30 - 11:30 (Should fail check)
        start2 = datetime(2025, 1, 1, 10, 30)
        end2 = datetime(2025, 1, 1, 11, 30)
        
        overlap = Reservation.query.filter(
            Reservation.classroom_id == room.id,
            Reservation.start_time < end2,
            Reservation.end_time > start2
        ).first()
        
        if overlap:
            print("Detected overlap for 10:30-11:30 -> SUCCESS (Expected overlap found)")
        else:
            print("Error: Failed to detect overlap!")
            
        # Scenario 3: Book non-overlapping 11:00 - 12:00 (Should succeed check)
        start3 = datetime(2025, 1, 1, 11, 0)
        end3 = datetime(2025, 1, 1, 12, 0)
        
        overlap_clean = Reservation.query.filter(
            Reservation.classroom_id == room.id,
            Reservation.start_time < end3,
            Reservation.end_time > start3
        ).first()
        
        if not overlap_clean:
             print("No overlap for 11:00-12:00 -> SUCCESS")
        else:
             print("Error: False positive overlap detected!")

if __name__ == '__main__':
    verify_logic()
