from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp

class LoginForm(FlaskForm):
    username = StringField(
        label="Kullanıcı Adı",
        validators=[
            DataRequired(message="Kullanıcı adı boş bırakılamaz."),
            Length(max=32, message="Kullanıcı adı en fazla 32 karakter olabilir.")
        ]
    )
    password = PasswordField(
        label="Şifre",
        validators=[
            DataRequired(message="Şifre boş bırakılamaz.")
        ]
    )
    submit = SubmitField("Giriş Yap")


class RegisterForm(FlaskForm):
    username = StringField(
        label="Kullanıcı Adı",
        validators=[
            DataRequired(message="Kullanıcı adı boş bırakılamaz."),
            Length(min=4, max=32, message="Kullanıcı adı 4-32 karakter arası olmalıdır.")
        ]
    )
    password = PasswordField(
        label="Şifre",
        validators=[
            DataRequired(message="Şifre boş bırakılamaz."),
            Length(min=6, message="Şifre en az 6 karakter olmalıdır."),
            Regexp(
                r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$',
                message="Şifre en az 1 harf ve 1 rakam içermelidir."
            )
        ]
    )
    role = SelectField(
        label="Rol",
        choices=[
            ("admin", "Admin"),
            ("owner", "Anket Sahibi"),
            ("user", "Kullanıcı")
        ],
        validators=[
            DataRequired(message="Lütfen bir rol seçiniz.")
        ]
    )
    submit = SubmitField("Kayıt Ol")
