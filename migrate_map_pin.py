from app import app, db
from sqlalchemy import text

def add_map_pin_column():
    with app.app_context():
        try:
            # Check if column exists
            result = db.session.execute(text("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'classrooms' 
                AND COLUMN_NAME = 'map_pin_id'
            """))
            
            exists = result.scalar() > 0
            
            if not exists:
                print("Adding 'map_pin_id' column to classrooms table...")
                db.session.execute(text("""
                    ALTER TABLE classrooms 
                    ADD map_pin_id INT NULL
                """))
                db.session.execute(text("""
                    ALTER TABLE classrooms
                    ADD CONSTRAINT FK_Classrooms_MapPins
                    FOREIGN KEY (map_pin_id) REFERENCES map_pins(id)
                """))
                db.session.commit()
                print("[OK] Column 'map_pin_id' and foreign key added successfully!")
            else:
                print("[OK] Column 'map_pin_id' already exists.")
                
        except Exception as e:
            print(f"Error: {e}")
            db.session.rollback()

if __name__ == '__main__':
    add_map_pin_column()
