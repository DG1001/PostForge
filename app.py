import os
import secrets
import string
from flask import Flask
from app import create_app, db
from app.models import User, Post, Image

# Create Flask application
app = create_app(os.getenv('FLASK_CONFIG', 'default'))

# Shell context for flask shell command
@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Post': Post,
        'Image': Image
    }

if __name__ == '__main__':
    with app.app_context():
        # Run database migrations
        from app.utils.database_migrations import run_migrations, verify_database_schema
        
        print("🚀 Starting PostForge application...")
        
        # Run automatic database migrations
        if run_migrations():
            print("✅ Database migrations completed successfully")
        else:
            print("❌ Database migrations failed")
            exit(1)
            
        # Verify database schema (optional - don't fail if verification has issues)
        try:
            if verify_database_schema():
                print("✅ Database schema verification completed")
            else:
                print("⚠️  Database schema verification had issues, but continuing...")
        except Exception as e:
            print(f"⚠️  Database schema verification failed: {e}, but continuing...")
        
        # Create a default user if none exists
        if not User.query.first():
            # Get admin password from environment or generate random one
            admin_password = os.getenv('ADMIN_PASSWORD')
            if not admin_password:
                # Generate random password: 12 characters with letters, digits, and symbols
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
            
        print("🎉 PostForge application started successfully!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)