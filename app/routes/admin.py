from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.registration_token import RegistrationToken
from app.models.user import User
from app.forms.admin import CreateTokenForm, DeactivateTokenForm, DeleteUserForm
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.username != 'admin':
            flash('Admin-Berechtigung erforderlich.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def index():
    """Admin dashboard"""
    # Get token statistics
    total_tokens = RegistrationToken.query.count()
    active_tokens = RegistrationToken.query.filter_by(is_active=True, used_at=None).count()
    used_tokens = RegistrationToken.query.filter(RegistrationToken.used_at.isnot(None)).count()
    
    # Get recent tokens
    recent_tokens = RegistrationToken.query.order_by(RegistrationToken.created_at.desc()).limit(10).all()
    
    return render_template('admin/index.html', 
                         total_tokens=total_tokens,
                         active_tokens=active_tokens, 
                         used_tokens=used_tokens,
                         recent_tokens=recent_tokens)

@admin_bp.route('/tokens')
@login_required
@admin_required
def tokens():
    """List all registration tokens"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    tokens = RegistrationToken.query.order_by(RegistrationToken.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    form = CreateTokenForm()
    return render_template('admin/tokens.html', tokens=tokens, form=form)

@admin_bp.route('/tokens/create', methods=['POST'])
@login_required
@admin_required
def create_token():
    """Create a new registration token"""
    form = CreateTokenForm()
    
    if form.validate_on_submit():
        expires_in_days = form.expires_in_days.data
        note = form.note.data
        
        if expires_in_days is not None and expires_in_days <= 0:
            expires_in_days = None
        
        token = RegistrationToken(
            created_by=current_user.id,
            expires_in_days=expires_in_days,
            note=note or None
        )
        
        db.session.add(token)
        db.session.commit()
        
        flash(f'Registrierungs-Token erstellt: {token.token}', 'success')
        return redirect(url_for('admin.tokens'))
    
    # If form validation fails, redirect back with errors
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    tokens = RegistrationToken.query.order_by(RegistrationToken.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/tokens.html', tokens=tokens, form=form)

@admin_bp.route('/tokens/<int:token_id>/deactivate', methods=['POST'])
@login_required
@admin_required
def deactivate_token(token_id):
    """Deactivate a registration token"""
    token = RegistrationToken.query.get_or_404(token_id)
    token.deactivate()
    
    flash('Token wurde deaktiviert.', 'success')
    return redirect(url_for('admin.tokens'))

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """List all users"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    users = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user (except admin themselves)"""
    user = User.query.get_or_404(user_id)
    
    # Prevent admin from deleting themselves
    if user.id == current_user.id:
        flash('Sie können sich nicht selbst löschen.', 'error')
        return redirect(url_for('admin.users'))
    
    # Additional protection: prevent deleting the admin user
    if user.username == 'admin' and current_user.username == 'admin':
        flash('Der Admin-Benutzer kann nicht gelöscht werden.', 'error')
        return redirect(url_for('admin.users'))
    
    try:
        username = user.username
        user_posts_count = len(user.posts)
        
        # Delete user (posts will be deleted due to cascade)
        db.session.delete(user)
        db.session.commit()
        
        flash(f'Benutzer "{username}" wurde erfolgreich gelöscht ({user_posts_count} Posts ebenfalls gelöscht).', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Fehler beim Löschen des Benutzers: {str(e)}', 'error')
    
    return redirect(url_for('admin.users'))