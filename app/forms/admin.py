from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import Optional, NumberRange, Length

class CreateTokenForm(FlaskForm):
    expires_in_days = IntegerField('Gültigkeitsdauer (Tage)', validators=[
        Optional(),
        NumberRange(min=1, max=365, message='Gültigkeitsdauer muss zwischen 1 und 365 Tagen liegen')
    ])
    note = StringField('Notiz (optional)', validators=[
        Optional(),
        Length(max=200, message='Notiz darf maximal 200 Zeichen lang sein')
    ])
    submit = SubmitField('Token erstellen')

class DeactivateTokenForm(FlaskForm):
    submit = SubmitField('Deaktivieren')

class DeleteUserForm(FlaskForm):
    submit = SubmitField('Benutzer löschen')