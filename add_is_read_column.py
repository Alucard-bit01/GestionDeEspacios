from app import app, db
from sqlalchemy import text

def add_is_read_column():
    with app.app_context():
        try:
            # Check if column exists
            result = db.session.execute(text("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'messages' 
                AND COLUMN_NAME = 'is_read'
            """))
            
            exists = result.scalar() > 0
            
            if not exists:
                print("Adding 'is_read' column to messages table...")
                db.session.execute(text("""
                    ALTER TABLE messages 
                    ADD is_read BIT NOT NULL DEFAULT 0
                """))
                db.session.commit()
                print("[OK] Column 'is_read' added successfully!")
            else:
                print("[OK] Column 'is_read' already exists.")
                
        except Exception as e:
            print(f"Error: {e}")
            db.session.rollback()

if __name__ == '__main__':
    add_is_read_column()
