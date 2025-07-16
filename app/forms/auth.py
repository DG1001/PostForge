from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models.user import User

class LoginForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    remember_me = BooleanField('Angemeldet bleiben')
    submit = SubmitField('Anmelden')

class RegisterForm(FlaskForm):
    username = StringField('Benutzername', validators=[
        DataRequired(),
        Length(min=4, max=20, message='Benutzername muss zwischen 4 und 20 Zeichen lang sein')
    ])
    email = StringField('E-Mail', validators=[
        DataRequired(),
        Email(message='Geben Sie eine gültige E-Mail-Adresse ein')
    ])
    password = PasswordField('Passwort', validators=[
        DataRequired(),
        Length(min=6, message='Passwort muss mindestens 6 Zeichen lang sein')
    ])
    password2 = PasswordField('Passwort bestätigen', validators=[
        DataRequired(),
        EqualTo('password', message='Passwörter müssen übereinstimmen')
    ])
    submit = SubmitField('Registrieren')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Benutzername ist bereits vergeben')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('E-Mail-Adresse ist bereits registriert')