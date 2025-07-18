from app import db
from datetime import datetime
import secrets
import string

class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    hashtags = db.Column(db.Text)
    notes = db.Column(db.Text)
    scheduled_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='draft')
    engagement_stats = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Review sharing fields
    share_token = db.Column(db.String(64), unique=True, nullable=True)
    is_shared = db.Column(db.Boolean, default=False)
    
    # Relationships
    images = db.relationship('Image', backref='post', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'hashtags': self.hashtags,
            'notes': self.notes,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'status': self.status,
            'engagement_stats': self.engagement_stats,
            'created_at': self.created_at.isoformat(),
            'images': [img.to_dict() for img in self.images]
        }
    
    @property
    def character_count(self):
        return len(self.content)
    
    @property
    def status_color(self):
        colors = {
            'draft': 'bg-gray-100 text-gray-800',
            'posted': 'bg-green-100 text-green-800',
            'imported': 'bg-blue-100 text-blue-800',
            'scheduled': 'bg-yellow-100 text-yellow-800'
        }
        return colors.get(self.status, 'bg-gray-100 text-gray-800')
    
    @property
    def status_display(self):
        displays = {
            'draft': 'Entwurf',
            'posted': 'Veröffentlicht',
            'imported': 'Importiert',
            'scheduled': 'Geplant'
        }
        return displays.get(self.status, 'Unbekannt')
    
    def generate_share_token(self):
        """Generate a unique share token for this post"""
        if not self.share_token:
            # Generate a 32-character random token
            self.share_token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        return self.share_token
    
    def enable_sharing(self):
        """Enable sharing for this post"""
        if not self.share_token:
            self.generate_share_token()
        self.is_shared = True
        from app import db
        db.session.commit()
    
    def disable_sharing(self):
        """Disable sharing for this post"""
        self.is_shared = False
        from app import db
        db.session.commit()
    
    @property
    def share_url(self):
        """Get the public share URL for this post"""
        if self.is_shared and self.share_token:
            from flask import url_for
            return url_for('posts.public_view', token=self.share_token, _external=True)
        return None
    
    def __repr__(self):
        return f'<Post {self.title}>'