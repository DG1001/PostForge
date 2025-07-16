# PostForge - LinkedIn Post Manager

Eine lokale Web-Anwendung zum Erstellen, Importieren und Verwalten von LinkedIn Posts mit PDF-Import-Funktionalität, Bilderverwaltung und internen Notizen.

## Features

- **Post-Management**: Erstellen, bearbeiten und organisieren Sie LinkedIn Posts
- **PDF-Import**: Importieren Sie vorhandene Posts aus LinkedIn PDF-Exporten
- **Bilderverwaltung**: Hochladen und Verwalten mehrerer Bilder pro Post
- **Status-Tracking**: Verfolgen Sie den Status Ihrer Posts (Entwurf, Veröffentlicht, Geplant)
- **Interaktive UI**: Moderne Benutzeroberfläche mit Alpine.js und HTMX
- **Drag & Drop**: Einfache Datei-Uploads per Drag & Drop

## Tech Stack

- **Backend**: Flask 3.0, SQLAlchemy 2.0, Python 3.11+
- **Frontend**: TailwindCSS 3.x, Alpine.js 3.x, HTMX 1.9
- **Database**: SQLite (migrierbar zu PostgreSQL)
- **Authentication**: Flask-Login
- **File Processing**: PyPDF2, Pillow

## Installation

### 1. Repository klonen
```bash
git clone <repository-url>
cd PostForge
```

### 2. Virtual Environment erstellen
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate     # Windows
```

### 3. Dependencies installieren
```bash
pip install -r requirements.txt
```

### 4. Node.js Dependencies installieren
```bash
npm install
```

### 5. TailwindCSS kompilieren
```bash
npm run build-css
```

### 6. Umgebungsvariablen konfigurieren
```bash
cp .env.example .env
# .env Datei nach Bedarf anpassen
```

### 7. Anwendung starten
```bash
python app.py
```

Die Anwendung ist dann unter `http://localhost:5000` verfügbar.

## Standard-Benutzer

Bei der ersten Ausführung wird automatisch ein Standard-Benutzer erstellt:
- **Benutzername**: admin
- **Passwort**: admin123

**Wichtig**: Ändern Sie das Passwort nach der ersten Anmeldung!

## Verwendung

### Posts erstellen
1. Klicken Sie auf "Neuen Post erstellen"
2. Geben Sie Titel und Inhalt ein
3. Fügen Sie optional Hashtags und Notizen hinzu
4. Laden Sie Bilder hoch (Drag & Drop unterstützt)
5. Wählen Sie den Status und speichern Sie

### PDF-Import
1. Gehen Sie zu "PDF Import"
2. Laden Sie eine LinkedIn PDF-Datei hoch
3. Überprüfen Sie die erkannten Posts
4. Wählen Sie die zu importierenden Posts aus
5. Bestätigen Sie den Import

### Bilderverwaltung
- Drag & Drop von Bildern direkt in den Editor
- Unterstützte Formate: PNG, JPG, JPEG, GIF, WEBP
- Automatische Thumbnail-Generierung
- Bildlöschung mit einem Klick

## Entwicklung

### TailwindCSS Development
```bash
npm run build-css  # Watch mode für Entwicklung
npm run build-css-prod  # Production Build
```

### Database Migrations
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Projektstruktur
```
PostForge/
├── app/                    # Hauptanwendung
│   ├── models/            # SQLAlchemy Models
│   ├── routes/            # Flask Routes
│   ├── templates/         # Jinja2 Templates
│   ├── static/           # Statische Dateien
│   ├── utils/            # Utility-Module
│   └── forms/            # WTForms
├── migrations/           # Database Migrations
├── instance/            # Instance-spezifische Dateien
└── requirements.txt     # Python Dependencies
```

## Deployment

### Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Nginx (Beispiel-Konfiguration)
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static {
        alias /path/to/PostForge/app/static;
    }
}
```

## Konfiguration

### Environment Variables
- `SECRET_KEY`: Flask Secret Key
- `DATABASE_URL`: Database Connection String
- `FLASK_CONFIG`: Konfigurationsmodus (development/production)

### Upload-Limits
- **Bilder**: 10MB pro Datei
- **PDFs**: 16MB pro Datei
- **Unterstützte Bildformate**: PNG, JPG, JPEG, GIF, WEBP

## Sicherheit

- CSRF-Protection durch Flask-WTF
- Datei-Upload-Validierung
- Session-Sicherheit
- Input-Sanitization

## Lizenz

MIT License - siehe LICENSE-Datei für Details.

## Support

Bei Problemen oder Fragen erstellen Sie bitte ein Issue im Repository.