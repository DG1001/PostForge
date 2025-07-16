from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.post import Post
from app.forms.posts import PostForm, SearchForm
from app.utils.helpers import flash_errors
from sqlalchemy import desc, or_

posts_bp = Blueprint('posts', __name__, url_prefix='/posts')

@posts_bp.route('/')
@login_required
def index():
    search_form = SearchForm()
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Base query
    query = Post.query.filter_by(user_id=current_user.id)
    
    # Apply search filter
    search_query = request.args.get('query', '')
    if search_query:
        query = query.filter(
            or_(
                Post.title.contains(search_query),
                Post.content.contains(search_query),
                Post.hashtags.contains(search_query)
            )
        )
    
    # Apply status filter
    status_filter = request.args.get('status_filter', 'all')
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    # Order by creation date
    query = query.order_by(desc(Post.created_at))
    
    # Paginate
    posts = query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    return render_template('posts/index.html', 
                         posts=posts, 
                         search_form=search_form,
                         search_query=search_query,
                         status_filter=status_filter)

@posts_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            user_id=current_user.id,
            title=form.title.data,
            content=form.content.data,
            hashtags=form.hashtags.data,
            notes=form.notes.data,
            scheduled_date=form.scheduled_date.data,
            status=form.status.data
        )
        
        try:
            db.session.add(post)
            db.session.commit()
            flash('Post erfolgreich erstellt!', 'success')
            return redirect(url_for('posts.edit', id=post.id))
        except Exception as e:
            db.session.rollback()
            flash('Fehler beim Erstellen des Posts.', 'error')
    
    flash_errors(form)
    return render_template('posts/create.html', form=form)

@posts_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = PostForm(obj=post)
    
    if form.validate_on_submit():
        form.populate_obj(post)
        
        try:
            db.session.commit()
            flash('Post erfolgreich aktualisiert!', 'success')
            return redirect(url_for('posts.edit', id=post.id))
        except Exception as e:
            db.session.rollback()
            flash('Fehler beim Aktualisieren des Posts.', 'error')
    
    flash_errors(form)
    return render_template('posts/edit.html', form=form, post=post)

@posts_bp.route('/<int:id>/delete', methods=['DELETE'])
@login_required
def delete(id):
    post = Post.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    try:
        db.session.delete(post)
        db.session.commit()
        # Return empty content to replace the post card
        return '', 200
    except Exception as e:
        db.session.rollback()
        return '<div class="text-red-600 text-sm p-2">Fehler beim Löschen des Posts</div>', 500

@posts_bp.route('/<int:id>/copy', methods=['POST'])
@login_required
def copy(id):
    post = Post.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    new_post = Post(
        user_id=current_user.id,
        title=f"Kopie von {post.title}",
        content=post.content,
        hashtags=post.hashtags,
        notes=post.notes,
        status='draft'
    )
    
    try:
        db.session.add(new_post)
        db.session.commit()
        flash('Post erfolgreich kopiert!', 'success')
        return redirect(url_for('posts.edit', id=new_post.id))
    except Exception as e:
        db.session.rollback()
        flash('Fehler beim Kopieren des Posts.', 'error')
        return redirect(url_for('posts.index'))

@posts_bp.route('/<int:id>/preview')
@login_required
def preview(id):
    post = Post.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    return render_template('posts/preview.html', post=post)

@posts_bp.route('/search')
@login_required
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    posts = Post.query.filter_by(user_id=current_user.id)\
                     .filter(
                         or_(
                             Post.title.contains(query),
                             Post.content.contains(query),
                             Post.hashtags.contains(query)
                         )
                     ).limit(10).all()
    
    return jsonify([{
        'id': post.id,
        'title': post.title,
        'content': post.content[:100] + '...' if len(post.content) > 100 else post.content,
        'status': post.status_display
    } for post in posts])