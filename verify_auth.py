from app import app
from werkzeug.security import generate_password_hash, check_password_hash
from model.models import User, db

with app.app_context():
    print("Testing password hashing...")
    password = "mysecretpassword"
    hashed = generate_password_hash(password, method='scrypt')
    print(f"Hash length: {len(hashed)}")
    print(f"Hash: {hashed}")
    
    # Verify hash
    is_valid = check_password_hash(hashed, password)
    print(f"Password Check: {is_valid}")
    
    if not is_valid:
        print("ERROR: Password check failed immediately!")
    
    # Test DB roundtrip
    print("Testing DB roundtrip with hash...")
    try:
        user = User(username='hash_test_user', password=hashed)
        db.session.add(user)
        db.session.commit()
        
        # Retrieve
        retrieved = User.query.filter_by(username='hash_test_user').first()
        if retrieved:
            print(f"Retrieved Hash: {retrieved.password}")
            is_valid_db = check_password_hash(retrieved.password, password)
            print(f"DB Password Check: {is_valid_db}")
            
            # Clean up
            db.session.delete(retrieved)
            db.session.commit()
        else:
            print("ERROR: Could not retrieve user!")
            
    except Exception as e:
        print(f"DB Error: {e}")
