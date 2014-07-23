from flask_wtf import Form
from wtforms import TextField
from wtforms.fields.html5 import IntegerRangeField
from wtforms.validators import DataRequired, NumberRange

class DownloadCode(Form):
    download_code = TextField('download_code', validators=[DataRequired()])

class Payment(Form):
    amount = IntegerRangeField('amount', validators=[DataRequired()])
