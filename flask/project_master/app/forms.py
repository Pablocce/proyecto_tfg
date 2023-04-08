from flask_wtf import FlaskForm
#tipo de dato y meter dominios dentro
from wtforms import StringField , PasswordField, SubmitField, BooleanField
#importamos validadores
from wtforms.validators import DataRequired, Length, Email, EqualTo
import email_validator
#formulario para el registro de usuarios
class RegistrationForm(FlaskForm):
    username = StringField('Username', 
                            validators=[DataRequired(), Length(min=5, max=20)]) #DataRequired() chequea que el field no este vacio
    
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Sing up')

#formulario para el login de usuarios
class LoginForm(FlaskForm):
    username = StringField('Username', 
                            validators=[DataRequired(), Length(min=5, max=20)]) #DataRequired() chequea que el field no este vacio
    
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')

    submit = SubmitField('Login')
