from flask_wtf import FlaskForm
#tipo de dato y meter dominios dentro
from wtforms import StringField , PasswordField, SubmitField, BooleanField, IntegerField
#importamos validadores
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
import email_validator
import psycopg2

def conector():
    conn=None
    try:
        #creamos conexión
        conn = psycopg2.connect(
        host="localhost",
        database="clinicadental",
        user="postgres",
        password="Curso2023")
        #creamos un cursor
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    return conn

class PedidosForm(FlaskForm):
    username = StringField('Nombre usuario', validators=[DataRequired(), Length(min=5, max=20)])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar contraseña', validators=[DataRequired(), EqualTo('password')])
    codigo_admin = PasswordField('Código administrador', validators=[DataRequired()])
    is_admin = BooleanField('Marcar como administrador?')