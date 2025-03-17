from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField, FileField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from flask_wtf.file import FileRequired, FileAllowed

class EntryForm(FlaskForm):
    class Meta:
        csrf = False  

    name = StringField("Nom", validators=[DataRequired(), Length(min=2, max=50)])
    amount = FloatField("Montant", validators=[DataRequired(), NumberRange(min=0)])
    category = StringField("Catégorie (optionnel)", validators=[Optional(), Length(max=50)])
    submit = SubmitField("Ajouter")

class DeleteForm(FlaskForm):
    class Meta:
        csrf = False 

    entry_id = StringField("ID de l'entrée", validators=[DataRequired()])
    submit = SubmitField("Supprimer")

class UpdateForm(FlaskForm):
    class Meta:
        csrf = False  

    entry_id = StringField("ID de l'entrée", validators=[DataRequired()])
    name = StringField("Nouveau Nom", validators=[Optional(), Length(min=2, max=50)])
    amount = FloatField("Nouveau Montant", validators=[Optional(), NumberRange(min=0)])
    category = StringField("Nouvelle Catégorie (optionnel)", validators=[Optional(), Length(max=50)])
    submit = SubmitField("Mettre à jour")

class ImportCSVForm(FlaskForm):
    file = FileField('Import CSV', validators=[FileRequired(), FileAllowed(['csv'], 'CSV files only!')])
    submit = SubmitField('Importer')