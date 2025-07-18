#!/usr/bin/env python3
"""
Database initialization script for PostForge
Run this script to initialize the database with all tables and migrations
"""

import os
import sys
import secrets
import string

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Post, Image, RegistrationToken
from app.utils.database_migrations import run_migrations

def init_database():
    """Initialize the database with all tables and migrations"""
    
    app = create_app('development')
    
    with app.app_context():
        print("🚀 Starting PostForge database initialization...")
        
        # Run migrations
        if run_migrations():
            print("✅ Database migrations completed successfully")
            
            # Create default admin user if none exists
            if not User.query.first():
                admin_password = os.getenv('ADMIN_PASSWORD')
                if not admin_password:
                    admin_password = ''.join(secrets.choice(string.ascii_letters + string.digits + '!@#$%^&*') for _ in range(12))
                    print(f"🔐 Generated admin password: {admin_password}")
                else:
                    print("🔐 Using provided admin password")
                
                default_user = User(
                    username='admin',
                    email='admin@postforge.local'
                )
                default_user.set_password(admin_password)
                db.session.add(default_user)
                db.session.commit()
                print("✅ Default admin user created: admin / (password shown above)")
            else:
                print("✅ Admin user already exists")
            
            print("🎉 Database initialization completed successfully!")
            return True
        else:
            print("❌ Database migrations failed")
            return False

if __name__ == '__main__':
    success = init_database()
    sys.exit(0 if success else 1)