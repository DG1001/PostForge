from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models.post import Post
from app.models.user import User
from sqlalchemy import desc

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if not current_user.is_authenticated:
        return render_template('main/landing.html')
    
    # Get recent posts for dashboard
    recent_posts = Post.query.filter_by(user_id=current_user.id)\
                            .order_by(desc(Post.created_at))\
                            .limit(5).all()
    
    # Get statistics
    total_posts = Post.query.filter_by(user_id=current_user.id).count()
    draft_posts = Post.query.filter_by(user_id=current_user.id, status='draft').count()
    posted_posts = Post.query.filter_by(user_id=current_user.id, status='posted').count()
    scheduled_posts = Post.query.filter_by(user_id=current_user.id, status='scheduled').count()
    
    stats = {
        'total': total_posts,
        'draft': draft_posts,
        'posted': posted_posts,
        'scheduled': scheduled_posts
    }
    
    return render_template('main/dashboard.html', 
                         recent_posts=recent_posts, 
                         stats=stats)