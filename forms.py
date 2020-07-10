from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField, IntegerField, FloatField
from wtforms.validators import DataRequired, Length, Email, Regexp, NumberRange
from wtforms import ValidationError

class CoordsForm(FlaskForm):
    jour_naissance = IntegerField('Jour de naissance', validators = [NumberRange(min=1, max=31)])
    mois_naissance = IntegerField('Mois de naissance', validators = [NumberRange(min=1, max=12)])
    annee_naissance = IntegerField('Année de naissance', validators = [NumberRange(min=None, max=None)])
    heure_naissance = IntegerField('Heure (! en T.U.)', validators = [NumberRange(min=0, max=None)])
    min_naissance = IntegerField('Minutes', validators = [NumberRange(min=0, max=60)])
    latitude = FloatField('Latitude (6 ou 7 décimales)', validators = [NumberRange(min=0, max=None)])
    longitude = FloatField('Longitude (6 ou 7 décimales)', validators = [NumberRange(min=0, max=None)])
    submit = SubmitField('Envoyer')