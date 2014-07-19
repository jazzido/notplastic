from flask_wtf import Form
from wtforms import TextField
from wtforms.validators import DataRequired

class DownloadCode(Form):
    download_code = TextField('download_code', validators=[DataRequired()])
