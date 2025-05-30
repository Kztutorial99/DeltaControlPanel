
#!/usr/bin/env python3
"""
Script untuk melihat informasi admin yang ada
"""

from app import app, db
from models import User

def get_admin_info():
    with app.app_context():
        admin_user = User.query.filter_by(username="deltapro_admin").first()
        
        if admin_user:
            print("=" * 50)
            print("INFORMASI ADMIN YANG ADA:")
            print("=" * 50)
            print(f"Username: {admin_user.username}")
            print(f"Email: {admin_user.email}")
            print(f"API Key: {admin_user.api_key}")
            print(f"Is Admin: {admin_user.is_admin}")
            print(f"Is Active: {admin_user.is_active}")
            print(f"Created: {admin_user.created_at}")
            print("=" * 50)
            print("CATATAN: Password tersimpan sebagai hash di database")
            print("=" * 50)
        else:
            print("Admin user tidak ditemukan!")
            print("Jalankan 'python create_admin.py' untuk membuat admin baru")

if __name__ == "__main__":
    get_admin_info()
