#!/usr/bin/env python3
"""
Script untuk membuat admin user
"""

from app import app, db
from models import User
import uuid

def create_admin_user():
    with app.app_context():
        try:
            # Check if admin user already exists
            admin_user = User.query.filter_by(username='deltapro_admin').first()

            if admin_user:
                print("Admin user already exists!")
                print(f"Username: {admin_user.username}")
                print(f"Email: {admin_user.email}")
                print(f"API Key: {admin_user.api_key}")
                return

            # Create new admin user
            admin = User()
            admin.username = 'deltapro_admin'
            admin.email = 'admin@deltapro.internal'
            admin.set_password('!tsMWiWeVuU$aC0xlJda')  # Password dari admin_info.py
            admin.is_admin = True
            admin.is_premium = True
            admin.is_active = True
            admin.balance = 1000.0
            admin.login_method = 'password'
            admin.api_key = 'ADMIN_FYW0A80GLMNJEEEX7I4TGHE6ZHLOZ6EPXGAGQAOL'  # API Key dari admin_info.py

            db.session.add(admin)
            db.session.commit()

            print("=" * 60)
            print("ADMIN USER CREATED SUCCESSFULLY!")
            print("=" * 60)
            print(f"Username: {admin.username}")
            print(f"Password: !tsMWiWeVuU$aC0xlJda")
            print(f"Email: {admin.email}")
            print(f"API Key: {admin.api_key}")
            print("=" * 60)
            print("Admin user created successfully!")

        except Exception as e:
            print(f"Error creating admin user: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    create_admin_user()