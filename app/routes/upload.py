from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db, csrf
from app.models.post import Post
from app.models.image import Image
from app.forms.posts import PDFUploadForm, ImageUploadForm
from app.utils.pdf_parser import LinkedInPDFParser
from app.utils.image_processor import ImageProcessor
from app.utils.helpers import flash_errors
import os
import uuid

upload_bp = Blueprint('upload', __name__, url_prefix='/upload')

@upload_bp.route('/import', methods=['GET', 'POST'])
@login_required
def import_pdf():
    form = PDFUploadForm()
    if form.validate_on_submit():
        file = form.pdf_file.data
        
        # Save PDF temporarily
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join(current_app.config['PDF_UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        try:
            # Check file size
            file_size = os.path.getsize(filepath)
            if file_size > 10 * 1024 * 1024:  # 10MB limit
                raise ValueError("PDF-Datei ist zu groß (max. 10MB)")
            
            # Parse PDF with timeout protection
            parser = LinkedInPDFParser()
            posts_data = parser.parse_pdf(filepath)
            
            # Store parsed data in session for preview
            from flask import session
            session['parsed_posts'] = posts_data
            session['pdf_filename'] = filename
            
            flash(f'{len(posts_data)} Posts aus PDF extrahiert', 'success')
            return redirect(url_for('upload.preview_import'))
        
        except Exception as e:
            flash(f'Fehler beim Parsen der PDF: {str(e)}', 'error')
        finally:
            # Clean up temporary file
            if os.path.exists(filepath):
                os.remove(filepath)
    
    flash_errors(form)
    return render_template('upload/import.html', form=form)

@upload_bp.route('/preview')
@login_required
def preview_import():
    from flask import session
    posts_data = session.get('parsed_posts', [])
    pdf_filename = session.get('pdf_filename', '')
    
    if not posts_data:
        flash('Keine Posts zum Importieren gefunden.', 'warning')
        return redirect(url_for('upload.import_pdf'))
    
    return render_template('upload/preview.html', 
                         posts_data=posts_data, 
                         pdf_filename=pdf_filename)

@upload_bp.route('/confirm-import', methods=['POST'])
@login_required
def confirm_import():
    from flask import session
    posts_data = session.get('parsed_posts', [])
    selected_posts = request.form.getlist('selected_posts')
    
    if not posts_data or not selected_posts:
        flash('Keine Posts zum Importieren ausgewählt.', 'warning')
        return redirect(url_for('upload.import_pdf'))
    
    imported_count = 0
    
    try:
        for i, post_data in enumerate(posts_data):
            if str(i) in selected_posts:
                post = Post(
                    user_id=current_user.id,
                    title=post_data.get('title', 'Importierter Post'),
                    content=post_data.get('content', ''),
                    hashtags=post_data.get('hashtags', ''),
                    notes=post_data.get('notes', ''),
                    status='imported',
                    engagement_stats=post_data.get('engagement', '')
                )
                
                db.session.add(post)
                imported_count += 1
        
        db.session.commit()
        flash(f'{imported_count} Posts erfolgreich importiert!', 'success')
        
        # Clear session data
        session.pop('parsed_posts', None)
        session.pop('pdf_filename', None)
        
    except Exception as e:
        db.session.rollback()
        flash('Fehler beim Importieren der Posts.', 'error')
    
    return redirect(url_for('posts.index'))

@upload_bp.route('/images', methods=['POST'])
@login_required
@csrf.exempt
def upload_images():
    post_id = request.form.get('post_id')
    files = request.files.getlist('images')
    
    if not files:
        return jsonify({'error': 'Keine Dateien ausgewählt'}), 400
    
    # Verify post ownership if post_id is provided
    if post_id:
        post = Post.query.filter_by(id=post_id, user_id=current_user.id).first()
        if not post:
            return jsonify({'error': 'Post nicht gefunden'}), 404
    
    processor = ImageProcessor(current_app.config['IMAGE_UPLOAD_FOLDER'])
    uploaded_images = []
    
    for file in files:
        if file and file.filename:
            try:
                image_data = processor.process_image(file)
                
                # Save to database if post_id is provided
                if post_id:
                    image = Image(
                        post_id=post_id,
                        filename=image_data['filename'],
                        original_filename=image_data['original_filename'],
                        file_path=image_data['filepath'],
                        file_size=image_data['file_size'],
                        mime_type=image_data['mime_type']
                    )
                    
                    db.session.add(image)
                    db.session.commit()
                
                uploaded_images.append({
                    'filename': image_data['filename'],
                    'original_filename': image_data['original_filename'],
                    'size': image_data['file_size']
                })
                
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
            except Exception as e:
                return jsonify({'error': 'Fehler beim Hochladen der Datei'}), 500
    
    if post_id:
        # Return updated image gallery
        post = Post.query.get(post_id)
        from flask import render_template_string
        
        # Create template that calls the macro properly
        template = '''
        {% from "components/image_gallery.html" import image_gallery %}
        {{ image_gallery(images, editable=true) }}
        '''
        
        return render_template_string(template, images=post.images)
    
    return jsonify({'uploaded': uploaded_images})

@upload_bp.route('/images/<int:image_id>/delete', methods=['DELETE'])
@login_required
@csrf.exempt
def delete_image(image_id):
    image = Image.query.join(Post).filter(
        Image.id == image_id,
        Post.user_id == current_user.id
    ).first_or_404()
    
    try:
        # Delete file from filesystem
        processor = ImageProcessor(current_app.config['IMAGE_UPLOAD_FOLDER'])
        processor.delete_image(image.file_path)
        
        # Delete from database
        db.session.delete(image)
        db.session.commit()
        
        return '', 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Fehler beim Löschen des Bildes'}), 500