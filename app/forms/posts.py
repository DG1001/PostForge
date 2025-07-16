from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, DateField, SelectField, SubmitField, MultipleFileField
from wtforms.validators import DataRequired, Length, Optional

class PostForm(FlaskForm):
    title = StringField('Titel', validators=[
        DataRequired(message='Titel ist erforderlich'),
        Length(max=200, message='Titel darf maximal 200 Zeichen lang sein')
    ])
    content = TextAreaField('Inhalt', validators=[
        DataRequired(message='Inhalt ist erforderlich'),
        Length(max=3000, message='Inhalt darf maximal 3000 Zeichen lang sein')
    ])
    hashtags = StringField('Hashtags', validators=[
        Optional(),
        Length(max=500, message='Hashtags dürfen maximal 500 Zeichen lang sein')
    ])
    notes = TextAreaField('Notizen', validators=[
        Optional(),
        Length(max=1000, message='Notizen dürfen maximal 1000 Zeichen lang sein')
    ])
    scheduled_date = DateField('Geplantes Datum', validators=[Optional()])
    status = SelectField('Status', choices=[
        ('draft', 'Entwurf'),
        ('posted', 'Veröffentlicht'),
        ('imported', 'Importiert'),
        ('scheduled', 'Geplant')
    ], default='draft')
    submit = SubmitField('Speichern')

class ImageUploadForm(FlaskForm):
    images = MultipleFileField('Bilder', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Nur Bilddateien sind erlaubt')
    ])
    submit = SubmitField('Hochladen')

class PDFUploadForm(FlaskForm):
    pdf_file = FileField('PDF-Datei', validators=[
        FileRequired(message='PDF-Datei ist erforderlich'),
        FileAllowed(['pdf'], 'Nur PDF-Dateien sind erlaubt')
    ])
    submit = SubmitField('PDF hochladen')

class SearchForm(FlaskForm):
    query = StringField('Suche', validators=[Optional()])
    status_filter = SelectField('Status', choices=[
        ('all', 'Alle'),
        ('draft', 'Entwurf'),
        ('posted', 'Veröffentlicht'),
        ('imported', 'Importiert'),
        ('scheduled', 'Geplant')
    ], default='all')
    submit = SubmitField('Suchen')