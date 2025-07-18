from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import json
import zipfile
import tempfile
import shutil
from datetime import datetime
from app import db
from app.models.post import Post
from app.models.image import Image

export_import_bp = Blueprint('export_import', __name__, url_prefix='/export-import')

@export_import_bp.route('/')
@login_required
def index():
    """Export/Import dashboard"""
    user_posts_count = Post.query.filter_by(user_id=current_user.id).count()
    return render_template('export_import/index.html', posts_count=user_posts_count)

@export_import_bp.route('/export')
@login_required
def export_posts():
    """Export user's posts as ZIP file"""
    try:
        # Get user's posts
        posts = Post.query.filter_by(user_id=current_user.id).all()
        
        if not posts:
            flash('Sie haben keine Posts zum Exportieren.', 'info')
            return redirect(url_for('export_import.index'))
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, f'posts_export_{current_user.username}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip')
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Create posts data structure
            posts_data = []
            
            for post in posts:
                post_data = {
                    'id': post.id,
                    'title': post.title,
                    'content': post.content,
                    'hashtags': post.hashtags,
                    'notes': post.notes,
                    'status': post.status,
                    'scheduled_for': getattr(post, 'scheduled_for', None).isoformat() if getattr(post, 'scheduled_for', None) else None,
                    'created_at': post.created_at.isoformat(),
                    'updated_at': post.updated_at.isoformat(),
                    'engagement_stats': getattr(post, 'engagement_stats', None),
                    'images': []
                }
                
                # Add images
                for image in post.images:
                    image_data = {
                        'filename': image.filename,
                        'original_filename': getattr(image, 'original_filename', image.filename),
                        'file_path': getattr(image, 'file_path', ''),
                        'file_size': getattr(image, 'file_size', 0),
                        'mime_type': getattr(image, 'mime_type', 'image/jpeg'),
                        'uploaded_at': image.uploaded_at.isoformat()
                    }
                    post_data['images'].append(image_data)
                    
                    # Add image file to ZIP
                    image_path = os.path.join('app/static/uploads/images', image.filename)
                    if os.path.exists(image_path):
                        zipf.write(image_path, f'images/{image.filename}')
                
                posts_data.append(post_data)
            
            # Add posts.json to ZIP
            posts_json = json.dumps(posts_data, indent=2, ensure_ascii=False)
            zipf.writestr('posts.json', posts_json)
            
            # Add export metadata
            metadata = {
                'export_date': datetime.now().isoformat(),
                'username': current_user.username,
                'email': current_user.email,
                'total_posts': len(posts_data),
                'total_images': sum(len(post['images']) for post in posts_data),
                'postforge_version': '1.0.0'
            }
            zipf.writestr('export_metadata.json', json.dumps(metadata, indent=2))
        
        flash(f'✅ {len(posts)} Posts erfolgreich exportiert!', 'success')
        
        # Send file
        return send_file(
            zip_path,
            as_attachment=True,
            download_name=os.path.basename(zip_path),
            mimetype='application/zip'
        )
        
    except Exception as e:
        flash(f'❌ Fehler beim Exportieren: {str(e)}', 'error')
        return redirect(url_for('export_import.index'))

@export_import_bp.route('/import', methods=['GET', 'POST'])
@login_required
def import_posts():
    """Import posts from ZIP file"""
    if request.method == 'GET':
        return render_template('export_import/import.html')
    
    try:
        # Check if file was uploaded
        if 'zip_file' not in request.files:
            flash('Keine Datei ausgewählt.', 'error')
            return redirect(url_for('export_import.import_posts'))
        
        file = request.files['zip_file']
        if file.filename == '':
            flash('Keine Datei ausgewählt.', 'error')
            return redirect(url_for('export_import.import_posts'))
        
        if not file.filename.lower().endswith('.zip'):
            flash('Nur ZIP-Dateien sind erlaubt.', 'error')
            return redirect(url_for('export_import.import_posts'))
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, secure_filename(file.filename))
        file.save(zip_path)
        
        # Extract ZIP
        extract_dir = os.path.join(temp_dir, 'extracted')
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(extract_dir)
        
        # Read posts.json
        posts_json_path = os.path.join(extract_dir, 'posts.json')
        if not os.path.exists(posts_json_path):
            flash('Ungültige ZIP-Datei: posts.json nicht gefunden.', 'error')
            return redirect(url_for('export_import.import_posts'))
        
        with open(posts_json_path, 'r', encoding='utf-8') as f:
            posts_data = json.load(f)
        
        # Import posts
        imported_posts = 0
        imported_images = 0
        
        for post_data in posts_data:
            # Create new post
            new_post = Post(
                title=post_data['title'],
                content=post_data['content'],
                hashtags=post_data['hashtags'],
                notes=post_data['notes'],
                status='imported',  # Mark as imported
                user_id=current_user.id,
                engagement_stats=post_data.get('engagement_stats')
            )
            
            db.session.add(new_post)
            db.session.flush()  # Get the ID
            
            # Import images
            for image_data in post_data['images']:
                source_path = os.path.join(extract_dir, 'images', image_data['filename'])
                if os.path.exists(source_path):
                    # Create new filename to avoid conflicts
                    new_filename = f"imported_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{image_data['filename']}"
                    target_path = os.path.join('app/static/uploads/images', new_filename)
                    
                    # Copy image file
                    shutil.copy2(source_path, target_path)
                    
                    # Get file info
                    file_size = os.path.getsize(target_path)
                    
                    # Determine MIME type based on extension
                    if new_filename.lower().endswith(('.jpg', '.jpeg')):
                        mime_type = 'image/jpeg'
                    elif new_filename.lower().endswith('.png'):
                        mime_type = 'image/png'
                    elif new_filename.lower().endswith('.gif'):
                        mime_type = 'image/gif'
                    elif new_filename.lower().endswith('.webp'):
                        mime_type = 'image/webp'
                    else:
                        mime_type = 'image/jpeg'  # Default
                    
                    # Create image record
                    new_image = Image(
                        filename=new_filename,
                        original_filename=image_data.get('original_filename', image_data['filename']),
                        file_path=target_path,
                        file_size=file_size,
                        mime_type=mime_type,
                        post_id=new_post.id
                    )
                    db.session.add(new_image)
                    imported_images += 1
            
            imported_posts += 1
        
        db.session.commit()
        
        # Cleanup
        shutil.rmtree(temp_dir)
        
        flash(f'✅ {imported_posts} Posts und {imported_images} Bilder erfolgreich importiert!', 'success')
        return redirect(url_for('posts.index'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Fehler beim Importieren: {str(e)}', 'error')
        return redirect(url_for('export_import.import_posts'))