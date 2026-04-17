from app import app, db
from model.models import MapPin

with app.app_context():
    try:
        db.create_all()
        print("Successfully created 'map_pins' table.")
    except Exception as e:
        print(f"Error creating table: {e}")
