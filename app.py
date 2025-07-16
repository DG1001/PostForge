import os
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
        # Create database tables
        db.create_all()
        
        # Create a default user if none exists
        if not User.query.first():
            default_user = User(
                username='admin',
                email='admin@postforge.local'
            )
            default_user.set_password('admin123')
            db.session.add(default_user)
            db.session.commit()
            print("Default user created: admin / admin123")
    
    app.run(debug=True, host='0.0.0.0', port=5000)