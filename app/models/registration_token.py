from datetime import datetime, timedelta
from app import db
import secrets
import string

class RegistrationToken(db.Model):
    __tablename__ = 'registration_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)  # None = never expires
    used_at = db.Column(db.DateTime, nullable=True)
    used_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    note = db.Column(db.String(200), nullable=True)  # Optional note about the token
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_tokens')
    user = db.relationship('User', foreign_keys=[used_by], backref='used_tokens')
    
    def __init__(self, created_by, expires_in_days=None, note=None):
        self.token = self.generate_token()
        self.created_by = created_by
        self.note = note
        if expires_in_days:
            self.expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
    
    @staticmethod
    def generate_token():
        """Generate a secure random token"""
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
    
    @property
    def is_valid(self):
        """Check if token is valid for use"""
        if not self.is_active:
            return False
        if self.used_at is not None:
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True
    
    @property
    def is_expired(self):
        """Check if token has expired"""
        return self.expires_at and datetime.utcnow() > self.expires_at
    
    def use_token(self, user_id):
        """Mark token as used"""
        self.used_at = datetime.utcnow()
        self.used_by = user_id
        self.is_active = False
        db.session.commit()
    
    def deactivate(self):
        """Deactivate token"""
        self.is_active = False
        db.session.commit()
    
    def __repr__(self):
        return f'<RegistrationToken {self.token[:8]}...>'