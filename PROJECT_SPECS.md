# LinkedIn Post Manager - Projekt Spezifikation

## 🎯 Projekt-Übersicht

Eine lokale Web-Anwendung zum Erstellen, Importieren und Verwalten von LinkedIn Posts mit PDF-Import-Funktionalität, Bilderverwaltung und internen Notizen.

Name der Applikation: PostForge

## 🛠️ Tech-Stack

### Backend
- **Python 3.11+**
- **Flask 3.0** (Web Framework)
- **SQLAlchemy 2.0** (ORM)
- **Flask-Login** (Session Authentication)
- **Flask-WTF** (Forms + CSRF)
- **Werkzeug** (File Upload)
- **PyPDF2** oder **pdfplumber** (PDF Processing)
- **Pillow** (Image Processing)

### Frontend
- **Jinja2** (Templates)
- **TailwindCSS 3.x** (Styling)
- **Alpine.js 3.x** (Reaktivität)
- **HTMX 1.9** (AJAX ohne JavaScript)

### Database
- **SQLite** (Lokal, später Migration zu PostgreSQL möglich)

### Deployment
- **Self-hosted** auf Linux Server
- **Gunicorn** (WSGI Server)
- **Nginx** (Reverse Proxy, Static Files)

## 📁 Projekt-Struktur

```
linkedin-post-manager/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── post.py
│   │   └── image.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── posts.py
│   │   ├── upload.py
│   │   └── main.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   └── register.html
│   │   ├── posts/
│   │   │   ├── index.html
│   │   │   ├── create.html
│   │   │   ├── edit.html
│   │   │   └── import.html
│   │   └── components/
│   │       ├── navbar.html
│   │       ├── post_card.html
│   │       └── image_gallery.html
│   ├── static/
│   │   ├── css/
│   │   │   └── app.css (TailwindCSS Output)
│   │   ├── js/
│   │   │   ├── alpine-components.js
│   │   │   └── pdf-upload.js
│   │   └── uploads/
│   │       ├── images/
│   │       └── pdfs/
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── pdf_parser.py
│   │   ├── image_processor.py
│   │   └── helpers.py
│   └── forms/
│       ├── __init__.py
│       ├── auth.py
│       └── posts.py
├── migrations/
├── instance/
│   └── app.db
├── requirements.txt
├── config.py
├── app.py
├── tailwind.config.js
├── package.json
├── .env.example
└── README.md
```

## 🗄️ Datenbank Schema

### Users Tabelle
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Posts Tabelle
```sql
CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    hashtags TEXT,
    notes TEXT,
    scheduled_date DATE,
    status VARCHAR(20) DEFAULT 'draft',
    engagement_stats TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

### Images Tabelle
```sql
CREATE TABLE images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE
);
```

## 🔗 API Endpoints / Routes

### Authentication
- `GET /login` - Login-Formular anzeigen
- `POST /login` - Login verarbeiten
- `GET /register` - Registrierung-Formular anzeigen
- `POST /register` - Registrierung verarbeiten
- `POST /logout` - Logout verarbeiten

### Posts Management
- `GET /` - Dashboard mit Post-Übersicht
- `GET /posts` - Alle Posts anzeigen (mit Filterung)
- `GET /posts/create` - Neuen Post erstellen (Formular)
- `POST /posts/create` - Neuen Post speichern
- `GET /posts/<id>/edit` - Post bearbeiten (Formular)
- `POST /posts/<id>/edit` - Post-Änderungen speichern
- `DELETE /posts/<id>` - Post löschen (HTMX)
- `POST /posts/<id>/copy` - Post in Zwischenablage kopieren

### File Upload & Processing
- `GET /import` - PDF Import-Seite anzeigen
- `POST /upload-pdf` - PDF hochladen und parsen
- `GET /pdf-preview/<upload_id>` - Vorschau der geparsten Posts (HTMX)
- `POST /import-posts` - Bestätigter Import der PDF-Posts
- `POST /upload-images` - Bilder hochladen (HTMX)
- `DELETE /images/<id>` - Bild löschen (HTMX)

### HTMX Partial Updates
- `GET /posts/<id>/preview` - Live Post-Vorschau
- `GET /posts/search` - Live-Suche durch Posts
- `GET /components/post-card/<id>` - Einzelne Post-Karte neu laden

## 🎨 Frontend-Komponenten

### Base Layout (base.html)
```html
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}LinkedIn Post Manager{% endblock %}</title>
    <link href="{{ url_for('static', filename='css/app.css') }}" rel="stylesheet">
    <script defer src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js"></script>
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
</head>
<body class="bg-gray-50">
    {% include 'components/navbar.html' %}
    
    <main class="container mx-auto px-4 py-8">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} mb-4">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        {% block content %}{% endblock %}
    </main>
    
    {% block scripts %}{% endblock %}
</body>
</html>
```

### Post Editor Alpine.js Component
```javascript
function postEditor() {
    return {
        post: {
            title: '',
            content: '',
            hashtags: '',
            notes: '',
            scheduledDate: '',
            images: []
        },
        charCount: 0,
        maxChars: 3000,
        dragActive: false,
        
        init() {
            this.$watch('post.content', value => {
                this.charCount = value.length;
            });
        },
        
        handleDrop(event) {
            event.preventDefault();
            this.dragActive = false;
            const files = Array.from(event.dataTransfer.files);
            this.uploadImages(files);
        },
        
        uploadImages(files) {
            const formData = new FormData();
            files.forEach(file => formData.append('images', file));
            
            // HTMX Upload
            htmx.ajax('POST', '/upload-images', {
                values: formData,
                target: '#image-gallery'
            });
        },
        
        removeImage(imageId) {
            htmx.ajax('DELETE', `/images/${imageId}`, {
                target: '#image-gallery'
            });
        }
    }
}
```

### PDF Upload Component
```javascript
function pdfUpload() {
    return {
        dragActive: false,
        uploading: false,
        progress: 0,
        preview: [],
        
        handlePdfDrop(event) {
            event.preventDefault();
            this.dragActive = false;
            const files = Array.from(event.dataTransfer.files);
            const pdfFiles = files.filter(f => f.type === 'application/pdf');
            
            if (pdfFiles.length > 0) {
                this.uploadPdf(pdfFiles[0]);
            }
        },
        
        uploadPdf(file) {
            this.uploading = true;
            const formData = new FormData();
            formData.append('pdf', file);
            
            htmx.ajax('POST', '/upload-pdf', {
                values: formData,
                target: '#pdf-preview',
                indicator: '#upload-progress'
            }).then(() => {
                this.uploading = false;
            });
        }
    }
}
```

## 🔧 Kernfunktionalitäten

### 1. PDF-Parsing (utils/pdf_parser.py)
```python
import PyPDF2
import re
from datetime import datetime
from typing import List, Dict

class LinkedInPDFParser:
    def __init__(self):
        self.date_patterns = [
            r'\d{1,2}\.\d{1,2}\.\d{4}',
            r'\d{4}-\d{2}-\d{2}',
        ]
        self.hashtag_pattern = r'#\w+'
        self.engagement_pattern = r'(\d+)\s+(Likes?|Kommentare?|Comments?)'
    
    def parse_pdf(self, pdf_path: str) -> List[Dict]:
        """Parse LinkedIn PDF and extract posts"""
        posts = []
        
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            full_text = ""
            
            for page in reader.pages:
                full_text += page.extract_text()
        
        # Split into individual posts (customize based on LinkedIn PDF format)
        post_sections = self._split_into_posts(full_text)
        
        for section in post_sections:
            post_data = {
                'title': self._extract_title(section),
                'content': self._extract_content(section),
                'hashtags': self._extract_hashtags(section),
                'date': self._extract_date(section),
                'engagement': self._extract_engagement(section)
            }
            posts.append(post_data)
        
        return posts
    
    def _split_into_posts(self, text: str) -> List[str]:
        # Implement logic to split PDF text into individual posts
        # This depends on LinkedIn's PDF format structure
        pass
    
    def _extract_hashtags(self, text: str) -> str:
        hashtags = re.findall(self.hashtag_pattern, text)
        return ' '.join(hashtags)
    
    def _extract_engagement(self, text: str) -> str:
        matches = re.findall(self.engagement_pattern, text, re.IGNORECASE)
        if matches:
            return ', '.join([f"{count} {metric}" for count, metric in matches])
        return ""
```

### 2. Image Processing (utils/image_processor.py)
```python
from PIL import Image
import os
import uuid
from werkzeug.utils import secure_filename

class ImageProcessor:
    def __init__(self, upload_folder: str):
        self.upload_folder = upload_folder
        self.allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        self.max_size = 10 * 1024 * 1024  # 10MB
    
    def process_image(self, file) -> Dict:
        """Process uploaded image and return metadata"""
        if not self._allowed_file(file.filename):
            raise ValueError("Unsupported file type")
        
        if len(file.read()) > self.max_size:
            raise ValueError("File too large")
        file.seek(0)  # Reset file pointer
        
        # Generate unique filename
        filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
        filepath = os.path.join(self.upload_folder, filename)
        
        # Save original
        file.save(filepath)
        
        # Generate thumbnail if needed
        self._create_thumbnail(filepath)
        
        # Get image metadata
        with Image.open(filepath) as img:
            width, height = img.size
            format = img.format
        
        return {
            'filename': filename,
            'original_filename': file.filename,
            'filepath': filepath,
            'file_size': os.path.getsize(filepath),
            'mime_type': file.content_type,
            'width': width,
            'height': height,
            'format': format
        }
    
    def _allowed_file(self, filename: str) -> bool:
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def _create_thumbnail(self, filepath: str, size: tuple = (300, 300)):
        with Image.open(filepath) as img:
            img.thumbnail(size, Image.Resampling.LANCZOS)
            thumb_path = filepath.replace('.', '_thumb.')
            img.save(thumb_path, optimize=True, quality=85)
```

### 3. Post Model (models/post.py)
```python
from app import db
from datetime import datetime
from sqlalchemy.orm import relationship

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
    
    # Relationships
    user = relationship("User", back_populates="posts")
    images = relationship("Image", back_populates="post", cascade="all, delete-orphan")
    
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
```

## 🎛️ Konfiguration

### config.py
```python
import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///linkedin_posts.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload Configuration
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file upload
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # PDF Processing
    PDF_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'pdfs')
    IMAGE_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'images')
    
class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
```

### requirements.txt
```
Flask==3.0.0
SQLAlchemy==2.0.23
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Flask-WTF==1.2.1
Flask-Migrate==4.0.5
WTForms==3.1.1
Werkzeug==3.0.1
PyPDF2==3.0.1
Pillow==10.1.0
python-dotenv==1.0.0
gunicorn==21.2.0
```

### package.json (für TailwindCSS)
```json
{
  "name": "linkedin-post-manager",
  "version": "1.0.0",
  "scripts": {
    "build-css": "tailwindcss -i ./app/static/css/input.css -o ./app/static/css/app.css --watch",
    "build-css-prod": "tailwindcss -i ./app/static/css/input.css -o ./app/static/css/app.css --minify"
  },
  "devDependencies": {
    "tailwindcss": "^3.3.6",
    "@tailwindcss/forms": "^0.5.7"
  }
}
```

### tailwind.config.js
```javascript
module.exports = {
  content: [
    "./app/templates/**/*.html",
    "./app/static/js/**/*.js"
  ],
  theme: {
    extend: {
      fontFamily: {
        'sans': ['Inter', 'system-ui', 'sans-serif']
      },
      colors: {
        'linkedin': '#0077B5'
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms')
  ],
}
```

## 📋 Entwicklungsschritte

### Phase 1: Grundsetup
1. **Projekt initialisieren**
   - Flask App Setup
   - Datenbank-Konfiguration
   - Basic Authentication
   - TailwindCSS Integration

2. **Basis-Templates erstellen**
   - base.html mit Navigation
   - Login/Register Seiten
   - Dashboard-Layout

### Phase 2: Post-Management
1. **Post CRUD Operations**
   - Erstellen, Bearbeiten, Löschen
   - Liste aller Posts
   - Status-Management

2. **Frontend-Interaktivität**
   - Alpine.js Komponenten
   - HTMX für Live-Updates
   - Responsive Design

### Phase 3: File Upload & Processing
1. **Bild-Upload**
   - Drag & Drop Interface
   - Multiple File Upload
   - Image Processing & Thumbnails

2. **PDF-Import**
   - PDF Upload & Parsing
   - Preview der erkannten Posts
   - Import-Bestätigung

### Phase 4: Advanced Features
1. **Erweiterte Funktionen**
   - Suche & Filter
   - Bulk-Operations
   - Export-Funktionen

2. **Performance & UX**
   - Caching
   - Pagination
   - Toast-Notifications

### Phase 5: Deployment
1. **Production Setup**
   - Gunicorn Configuration
   - Nginx Setup
   - SSL/HTTPS
   - Monitoring

## 🚀 Deployment-Anweisungen

### Systemctl Service (linkedin-posts.service)
```ini
[Unit]
Description=LinkedIn Post Manager
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/linkedin-post-manager
Environment=PATH=/var/www/linkedin-post-manager/venv/bin
Environment=FLASK_ENV=production
ExecStart=/var/www/linkedin-post-manager/venv/bin/gunicorn --bind unix:/var/www/linkedin-post-manager/app.sock -m 007 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/linkedin-post-manager/app.sock;
    }
    
    location /static {
        alias /var/www/linkedin-post-manager/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    client_max_body_size 16M;
}
```

## 🧪 Testing-Ansatz

### Unit Tests
- Model Tests (CRUD Operations)
- PDF Parser Tests
- Image Processor Tests

### Integration Tests
- Authentication Flow
- File Upload & Processing
- End-to-End User Journey

### Frontend Tests
- Alpine.js Component Tests
- HTMX Interaction Tests

## 📝 Zusätzliche Notizen

### Sicherheit
- CSRF Protection via Flask-WTF
- File Upload Validation
- Session Security
- Input Sanitization

### Performance
- Image Optimization
- Database Indexing
- Static File Caching
- Lazy Loading für große Listen

### Erweiterbarkeit
- Plugin-System für zusätzliche Social Platforms
- API für externe Tools
- Webhook-Support
- Multi-User Support (später)

---

**Hinweis für das agentic code tool**: Diese Spezifikation ist vollständig und implementation-ready. Beginne mit Phase 1 und arbeite dich systematisch durch die Phasen. Alle notwendigen Code-Snippets, Konfigurationen und Strukturen sind enthalten.