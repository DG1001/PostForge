#!/usr/bin/env python3
"""
Reset admin password for PostForge
"""

import os
import sys
import secrets
import string
import getpass

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User

def reset_admin_password():
    """Reset the admin password"""
    
    app = create_app('development')
    
    with app.app_context():
        # Find admin user
        admin_user = User.query.filter_by(username='admin').first()
        
        if not admin_user:
            print("❌ Admin user not found!")
            return False
        
        # Ask for new password or generate one
        choice = input("Generate new password automatically? (y/n): ").lower().strip()
        
        if choice == 'y' or choice == 'yes' or choice == '':
            # Generate new password
            new_password = ''.join(secrets.choice(string.ascii_letters + string.digits + '!@#$%^&*') for _ in range(12))
            print(f"🔐 Generated new admin password: {new_password}")
        else:
            # Ask for password
            new_password = getpass.getpass("Enter new admin password: ")
            if not new_password:
                print("❌ Password cannot be empty!")
                return False
        
        # Update password
        admin_user.set_password(new_password)
        db.session.commit()
        
        print("✅ Admin password updated successfully!")
        print(f"Username: admin")
        print(f"Password: {new_password}")
        
        return True

if __name__ == '__main__':
    success = reset_admin_password()
    sys.exit(0 if success else 1)