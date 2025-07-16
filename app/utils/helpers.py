from flask import flash, url_for
from functools import wraps
import os
import uuid

def flash_errors(form):
    """Flash form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text}: {error}", 'error')

def allowed_file(filename, allowed_extensions):
    """Check if filename has allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def generate_unique_filename(filename):
    """Generate unique filename while preserving extension"""
    name, ext = os.path.splitext(filename)
    return f"{uuid.uuid4()}{ext}"

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f} {size_names[i]}"

def truncate_text(text, max_length=100):
    """Truncate text to max_length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def get_post_status_badge_class(status):
    """Get CSS class for post status badge"""
    status_classes = {
        'draft': 'bg-gray-100 text-gray-800 border-gray-300',
        'posted': 'bg-green-100 text-green-800 border-green-300',
        'imported': 'bg-blue-100 text-blue-800 border-blue-300',
        'scheduled': 'bg-yellow-100 text-yellow-800 border-yellow-300'
    }
    return status_classes.get(status, 'bg-gray-100 text-gray-800 border-gray-300')

def admin_required(f):
    """Decorator for admin-only routes (for future use)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Add admin check logic here when needed
        return f(*args, **kwargs)
    return decorated_function