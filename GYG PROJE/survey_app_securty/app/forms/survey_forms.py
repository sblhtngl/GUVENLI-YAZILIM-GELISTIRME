from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class SurveyForm(FlaskForm):
    title = StringField("Başlık", validators=[
        DataRequired(message="Başlık boş bırakılamaz."),
        Length(min=3, max=100, message="Başlık 3-100 karakter arası olmalıdır.")
    ])

    question = StringField("Soru", validators=[
        DataRequired(message="Soru boş bırakılamaz."),
        Length(min=5, max=200, message="Soru 5-200 karakter arası olmalıdır.")
    ])

    option1 = StringField("Seçenek 1", validators=[
        DataRequired(message="En az 1 seçenek girilmelidir.")
    ])

    option2 = StringField("Seçenek 2")
    option3 = StringField("Seçenek 3")
    option4 = StringField("Seçenek 4")

    submit = SubmitField("Oluştur")
