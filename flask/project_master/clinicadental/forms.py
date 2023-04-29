from flask_wtf import FlaskForm
#tipo de dato y meter dominios dentro
from wtforms import StringField , PasswordField, SubmitField, BooleanField
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
#formulario para el registro de usuarios


class RegistrationForm(FlaskForm):
    username = StringField('Nombre usuario', validators=[DataRequired(), Length(min=5, max=20)])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar contraseña', validators=[DataRequired(), EqualTo('password')])
    codigo_admin = PasswordField('Código administrador', validators=[DataRequired()])

    #si queremos cambiar el codigo de admin debemos cambiar el string
    def validate_codigo_admin(self, codigo_admin):
        if codigo_admin.data != 'codigo':
            raise ValidationError('Código incorrecto')
        
    def validate_username(self, field):
        conn = conector()
        cur = conn.cursor()
        cur.execute("SELECT username FROM users WHERE username=%s", (str(self.username.data),))
        repeated_username = cur.fetchone()
        cur.close()
        conn.close()
        if repeated_username != None:
            raise ValidationError('Ya existe un usuario con este nombre, introduce otro nombre.')

    submit = SubmitField('Registrar usuario')

#formulario para el login de usuarios
class LoginForm(FlaskForm):
    username = StringField('Username', 
                            validators=[DataRequired(), Length(min=5, max=20)]) #DataRequired() chequea que el field no este vacio
    
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')

    submit = SubmitField('Acceder')
