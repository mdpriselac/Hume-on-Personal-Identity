from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange

class readingListForm(FlaskForm):
    searchSelect = SelectField(label='Search Type: strict or aggressive?', validators=[DataRequired()], choices=[('aggressive','Aggressive'), ('strict','Strict')])
    locationSelect = SelectField(label='Location Type: chapters or paragraphs?', validators=[DataRequired()], choices=[('paragraph','Paragraph'), ('chapter','Chapter')])
    numberLocations = IntegerField(label='How many locations should we display?', validators=[DataRequired()])
    submit = SubmitField(label='Generate a reading list')
