# PostForge - LinkedIn Post Manager

A comprehensive LinkedIn post management application designed as a local web application for creating, importing, and managing LinkedIn posts with PDF import functionality and image management.

## Features

### 📝 Post Management
- **Create & Edit Posts** - Full CRUD operations with rich text editing
- **Status Tracking** - Draft, Posted, Imported, Scheduled status management
- **Post Preview** - Real-time preview while editing
- **Search & Filter** - Find posts by content, hashtags, or status
- **Pagination** - Efficient browsing of large post collections

### 📄 PDF Import
- **LinkedIn PDF Import** - Import posts from LinkedIn data export PDFs
- **Intelligent Parsing** - Advanced pattern recognition for German LinkedIn exports
- **Content Cleaning** - Automatically removes LinkedIn UI elements and artifacts
- **Metadata Extraction** - Extracts author, company, engagement stats, and timestamps
- **Preview Before Import** - Review and select which posts to import

### 🖼️ Image Management
- **Multi-Image Upload** - Drag & drop or browse to upload multiple images
- **Image Gallery** - Visual management of post images
- **Thumbnail Generation** - Automatic thumbnail creation
- **File Validation** - Support for PNG, JPG, GIF, WEBP up to 10MB
- **Download for LinkedIn** - Easy download of images for LinkedIn posting

### 📋 LinkedIn Integration
- **Smart Copy Function** - Copy text to clipboard
- **Image Download Modal** - Download all post images with original filenames
- **Complete Workflow** - Text + images ready for LinkedIn posting

### 🔐 User Management
- **Secure Authentication** - User registration and login system
- **Personal Posts** - Each user manages their own posts
- **Session Management** - Secure session handling with Flask-Login

## Tech Stack

### Backend
- **Python 3.11+** - Modern Python with type hints
- **Flask 3.0** - Lightweight web framework
- **SQLAlchemy 2.0** - Modern ORM with async support
- **Flask-Login** - User session management
- **Flask-WTF** - Form handling and CSRF protection
- **Flask-Migrate** - Database migrations

### Frontend
- **Jinja2** - Server-side templating
- **TailwindCSS 3.x** - Utility-first CSS framework
- **Alpine.js 3.x** - Lightweight JavaScript framework
- **HTMX 1.9** - Modern web interactions

### Database
- **SQLite** - Development database
- **PostgreSQL Ready** - Production migration capability

### File Processing
- **pdfplumber** - Advanced PDF text extraction
- **PyPDF2** - Fallback PDF processing
- **Pillow** - Image processing and validation

## Installation

### Prerequisites
- Python 3.11 or higher
- Node.js (for TailwindCSS building)

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd PostForge
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows
```

3. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

4. **Install Node.js dependencies**
```bash
npm install
```

5. **Build TailwindCSS**
```bash
npm run build-css
```

6. **Initialize database**
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

7. **Run the application**
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage

### Getting Started
1. **Register** a new account or login
2. **Create your first post** using the "Neuen Post erstellen" button
3. **Upload images** by dragging and dropping files
4. **Import LinkedIn posts** from PDF exports

### LinkedIn PDF Import
1. Navigate to **Upload → PDF Import**
2. Upload your LinkedIn data export PDF
3. **Preview** the extracted posts
4. **Select** which posts to import
5. Posts are imported with "imported" status

### Copying for LinkedIn
1. Click **"Für LinkedIn kopieren"** on any post
2. Text is automatically copied to clipboard
3. If the post has images, a **download modal** appears
4. Download images and upload them to LinkedIn
5. Paste the text content

## Development

### Project Structure
```
PostForge/
├── app/
│   ├── models/          # Database models
│   ├── routes/          # Flask routes
│   ├── templates/       # Jinja2 templates
│   ├── static/          # CSS, JS, uploads
│   ├── utils/           # Utility modules
│   └── forms/           # WTForms
├── migrations/          # Database migrations
├── instance/            # Instance-specific files
├── requirements.txt     # Python dependencies
├── package.json         # Node.js dependencies
└── tailwind.config.js   # TailwindCSS configuration
```

### Development Commands

```bash
# Development server with auto-reload
python app.py

# Database operations
flask db migrate -m "Migration description"
flask db upgrade
flask db downgrade

# CSS development (watch mode)
npm run build-css

# CSS production build
npm run build-css-prod
```

### Configuration

The application supports different configurations:
- **Development**: Debug enabled, SQLite database
- **Production**: Optimized settings, PostgreSQL support

Environment variables:
- `SECRET_KEY` - Flask secret key
- `DATABASE_URL` - Database connection string
- `FLASK_CONFIG` - Configuration environment (default, development, production)

## Security Features

- **CSRF Protection** - All forms protected against CSRF attacks
- **File Upload Validation** - Secure file type and size validation
- **Session Security** - Secure cookie settings
- **Input Sanitization** - Protection against XSS attacks
- **User Isolation** - Users can only access their own posts

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Testing

The application includes comprehensive testing:
- Unit tests for models and utilities
- Integration tests for file upload and processing
- Frontend component tests for Alpine.js interactions

```bash
# Run tests (when implemented)
python -m pytest
```

## Deployment

### Production Setup
1. Use **Gunicorn** + **Nginx** for production
2. Set environment variables for security
3. Use **PostgreSQL** for production database
4. Enable SSL/HTTPS
5. Configure proper backup strategies

### Docker Support
Docker configuration available for containerized deployment.

## License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License - see the [LICENSE](LICENSE) file for details.

This means you are free to:
- Share: copy and redistribute the material in any medium or format
- Adapt: remix, transform, and build upon the material

Under the following terms:
- Attribution: You must give appropriate credit
- NonCommercial: You may not use the material for commercial purposes

## Acknowledgments

- Built with modern web technologies
- Inspired by the need for better LinkedIn content management
- Designed for content creators and social media managers

## Support

For support, please open an issue on the GitHub repository or contact the development team.

---

**PostForge** - Forge your LinkedIn presence with ease! 🔥