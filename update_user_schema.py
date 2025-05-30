
#!/usr/bin/env python3
"""
Script untuk update schema User table dengan kolom login_method dan facebook_id untuk PostgreSQL
"""

from app import app, db
from models import User
from sqlalchemy import text

def update_user_schema():
    with app.app_context():
        try:
            # Check if columns exist and add them if they don't (PostgreSQL version)
            with db.engine.connect() as conn:
                # Check for login_method column
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='users' AND column_name='login_method'
                """)).fetchall()
                
                if not result:
                    conn.execute(text("ALTER TABLE users ADD COLUMN login_method VARCHAR(20) DEFAULT 'password'"))
                    print("Added login_method column")
                else:
                    print("login_method column already exists")
                
                # Check for facebook_id column
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='users' AND column_name='facebook_id'
                """)).fetchall()
                
                if not result:
                    conn.execute(text("ALTER TABLE users ADD COLUMN facebook_id VARCHAR(50)"))
                    print("Added facebook_id column")
                else:
                    print("facebook_id column already exists")
                
                conn.commit()
            
            print("Database schema updated successfully!")
            
        except Exception as e:
            print(f"Error updating schema: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    update_user_schema()
