def register_blueprints(app):
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.posts import posts_bp
    from app.routes.upload import upload_bp
    from app.routes.admin import admin_bp
    from app.routes.export_import import export_import_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(export_import_bp)