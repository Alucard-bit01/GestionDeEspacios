from app import app, db
from model.models import User

with app.app_context():
    print("Attempting to insert a test user...")
    try:
        # Check if user exists
        existing = User.query.filter_by(username='test_user').first()
        if existing:
            print("User 'test_user' already exists. Deleting...")
            db.session.delete(existing)
            db.session.commit()
        
        # Create new user
        new_user = User(username='test_user', password='hashed_password_example')
        db.session.add(new_user)
        db.session.commit()
        print("User committed to session.")
        
        # Verify
        check_user = User.query.filter_by(username='test_user').first()
        if check_user:
            print(f"Success! Found user: {check_user.username}")
        else:
            print("Error: User was committed but not found in query!")
            
    except Exception as e:
        print(f"An error occurred: {e}")
        db.session.rollback()
