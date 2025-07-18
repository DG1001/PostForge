from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models.user import User
from app.models.registration_token import RegistrationToken

class LoginForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    remember_me = BooleanField('Angemeldet bleiben')
    submit = SubmitField('Anmelden')

class RegisterForm(FlaskForm):
    registration_token = StringField('Registrierungs-Token', validators=[
        DataRequired(message='Registrierungs-Token ist erforderlich')
    ])
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
    
    def validate_registration_token(self, registration_token):
        token = RegistrationToken.query.filter_by(token=registration_token.data).first()
        if not token:
            raise ValidationError('Ungültiger Registrierungs-Token')
        if not token.is_valid:
            if token.used_at:
                raise ValidationError('Dieser Token wurde bereits verwendet')
            elif token.is_expired:
                raise ValidationError('Dieser Token ist abgelaufen')
            else:
                raise ValidationError('Dieser Token ist nicht mehr gültig')