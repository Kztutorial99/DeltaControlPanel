
import logging
from app import app, db
from models import Notification, UserSettings, DailyClaim, SaldoTransaction

logging.basicConfig(level=logging.INFO)

def update_schema():
    """Update database schema with new tables"""
    with app.app_context():
        try:
            # Create all new tables
            db.create_all()
            logging.info("Database schema updated successfully!")
            
            # Check if tables exist
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            new_tables = ['notifications', 'user_settings', 'daily_claims', 'saldo_transactions']
            for table in new_tables:
                if table in tables:
                    logging.info(f"✓ Table '{table}' exists")
                else:
                    logging.warning(f"✗ Table '{table}' not found")
            
        except Exception as e:
            logging.error(f"Error updating schema: {e}")
            raise

if __name__ == "__main__":
    update_schema()
