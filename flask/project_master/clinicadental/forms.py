from flask_wtf import FlaskForm
#tipo de dato y meter dominios dentro
from wtforms import StringField , PasswordField, SubmitField, BooleanField, IntegerField, DecimalField, DateField, TimeField, TextAreaField
#importamos validadores
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, AnyOf, Regexp
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
    is_admin = BooleanField('Marcar como administrador?')

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
    username = StringField('Nombre de usuario', 
                            validators=[DataRequired(), Length(min=5, max=20)]) #DataRequired() chequea que el field no este vacio
    
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember = BooleanField('Remember Me')

    submit = SubmitField('Acceder')

class ChangePasswordForm(FlaskForm): 
    old_password = PasswordField('Contraseña antigua', validators=[DataRequired()])
    new_password = PasswordField('Nueva contraseña', validators=[DataRequired()])
    confirm_new_password = PasswordField('Repite la nueva contraseña', validators=[DataRequired(),EqualTo('new_password')])

    submit = SubmitField('Cambiar contraseña')

class NewEmployeeForm(FlaskForm):
    emp_name = StringField('Nombre empleado', validators=[DataRequired(), Length(max=20)])
    emp_surname = StringField('Apellidos empleado', validators=[DataRequired(), Length(max=35)])
    emp_salary = IntegerField('Salario empleado', validators=[DataRequired()])
    emp_user_id = IntegerField('ID usuario', validators=[])

    submit = SubmitField('Añadir empleado')

class EditEmployeeForm(FlaskForm):
    emp_name = StringField('Nombre empleado', validators=[DataRequired(), Length(max=20)])
    emp_surname = StringField('Apellidos empleado', validators=[DataRequired(), Length(max=35)])
    emp_salary = IntegerField('Salario empleado', validators=[DataRequired()])
    emp_user_id = IntegerField('ID usuario', validators=[])

    submit = SubmitField('Añadir empleado')

class DeleteEmployee(FlaskForm):
    emp_id = IntegerField('ID empleado', validators=[DataRequired()])
    
    delete = SubmitField('Borrar empleado')

class NewEmployeeSchedule(FlaskForm):
    schedule_day = StringField('Día de la semana', validators=[DataRequired(),AnyOf(['lunes', 'martes', 'miércoles', 'jueves', 'viernes'],
                                                message='El día debe ser lunes, martes, miércoles, jueves o viernes.')])
    
    schedule_entry = StringField('Hora de entrada', validators=[DataRequired()])
    schedule_exit = StringField('Hora de salida', validators=[DataRequired()])

    submit = SubmitField('Añadir horario')

class NewProductWarehouse(FlaskForm):
    product_name = StringField('Nombre del producto', validators=[DataRequired()])
    product_price = DecimalField('Precio del producto', validators=[DataRequired()])
    product_stock = IntegerField('Stock del producto', validators=[DataRequired()])
    submit = SubmitField('Añadir producto')


class ChangeProductPrice(FlaskForm):
    product_new_price = DecimalField('Nuevo precio del producto', validators=[DataRequired()])

#form warehouse
class NewOrderWarehouse(FlaskForm):
    product_qty = IntegerField('Cantidad del producto', validators=[DataRequired()])
    submit = SubmitField('Crear pedido')

class ChangeProductPrice(FlaskForm):
    product_new_price = DecimalField('Nuevo precio', validators=[DataRequired()])
    submit = SubmitField('Cambiar precio')

class ChangeProductStock(FlaskForm):
    product_new_stock = IntegerField('Nuevo stock del producto', validators=[DataRequired()])
    submit = SubmitField('Cambiar stock')

class AddNewSupplier(FlaskForm):
    supplier_name = StringField('Nombre de la empresa', validators=[DataRequired()])
    submit = SubmitField('Cambiar stock')


class NewAppointmentFrom(FlaskForm):
    related_doctor=StringField('Nombre del doctor', validators=[DataRequired()])
    pacient_name =StringField('Nombre del paciente', validators=[DataRequired()])
    pacient_surname =StringField("Primer apellido",validators=[DataRequired()])
    description= StringField('Descripcion de la cita', validators=[DataRequired()])
    date=StringField('Fecha de la cita', validators=[DataRequired()])

    submit = SubmitField('Cita creada')


class NewPatientForm(FlaskForm):
    patient_dni=StringField("Dni del paciente",validators=[DataRequired()])
    patient_name=StringField("Nombre del paciente",validators=[DataRequired()])
    patient_surname=StringField("Apellidos",validators=[DataRequired()])

    submit = SubmitField('Paciente registrado')

class SearchPatientForm(FlaskForm):
    patient_dni=StringField("Dni del paciente",validators=[DataRequired()])

    submit = SubmitField('Paciente registrado')


class NewApointmentForm(FlaskForm):
    apointment_procedure = TextAreaField('Procedimiento',validators=[DataRequired()])
    apointment_date = DateField('Fecha de la cita',validators=[DataRequired()])
    apointment_hour = TimeField('Hora de la cita', validators=[DataRequired()])
    apointment_notes = TextAreaField('Notas',validators=[DataRequired()])
    submit = SubmitField('Añadir cita')

class SearchApointmentForm(FlaskForm):
    patient_dni =StringField("Dni del paciente",validators=[DataRequired()])
    submit = SubmitField('Buscar')

class UpdateApointmentForm(FlaskForm):
    apointment_date = DateField('Nueva fecha de la cita',validators=[DataRequired()])
    apointment_hour = TimeField('Nueva hora de la cita', validators=[DataRequired()])

    submit = SubmitField('Modificar cita')

class UpdateResultsForm(FlaskForm):
    results = TextAreaField('Diagnóstico del paciente', validators=[DataRequired()])
    submit = SubmitField('Añadir diagnóstico')