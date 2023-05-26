from flask import Flask, render_template, flash, redirect, url_for, request
from forms import RegistrationForm, LoginForm, ChangePasswordForm, NewEmployeeForm, DeleteEmployee, EditEmployeeForm, NewEmployeeSchedule
from flask_login import LoginManager
from flask_login import login_user, current_user, UserMixin, logout_user
from time import sleep

import psycopg2

app = Flask(__name__)
login_manager = LoginManager(app)

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

#secret key for our aplication
app.config['SECRET_KEY'] = '898572ebbc3be7c4bbc0222472fbd928'

@app.route('/') 
#decoramos para indicar que se liga a la ruta raiz
def index():
    #render_template sirve para renderizar los hmtl
    return render_template('base.html')

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"Error en el campo {getattr(form, field).label.text}: {error}", "error")

@app.route('/gestion', methods=['GET','POST'])
def gestion():
    horarios = obtain_schedules()
    formEmployee = NewEmployeeForm() 
    if current_user.is_authenticated:
        if current_user.is_admin:
            conn = conector()
            cur = conn.cursor()
            cur.execute("SELECT id_employee, emp_name, emp_surname, emp_salary, emp_user_id FROM employees order by id_employee")
            employees_data = cur.fetchall()
            cur.close()
            conn.close()
            if request.form:
                conn = conector()
                cur = conn.cursor()
                emp_name = formEmployee.emp_name.data
                emp_surname = formEmployee.emp_surname.data
                emp_salary = formEmployee.emp_salary.data
                emp_user_id = 0
                cur.execute("INSERT INTO public.employees (emp_name, emp_surname, emp_salary) values (%s,%s,%s)",(emp_name,emp_surname,emp_salary))
                #flash(f'Cuenta creada para: {formEmployee.username.data}!', 'success')
                cur.close()
                conn.commit()
                conn.close()
                conn = conector()
                cur = conn.cursor()
                cur.execute("SELECT id_employee, emp_name, emp_surname, emp_salary FROM employees")
                employees_data = cur.fetchall()
                cur.close()
                conn.close()
                # Procesar el formulario y crear un nuevo empleado
                # ...
                return render_template('gestion.html', formEmployee=formEmployee, employees_data = employees_data, horarios = horarios)
            else:
                flash_errors(formEmployee)
                return render_template('gestion.html', title='Empleados', formEmployee=formEmployee, employees_data = employees_data, horarios = horarios)
        else:
            return "<p>No puedes ver esto por falta de permisos</p>"
    else:
        return render_template('not_authenticated.html')
    
def obtain_schedules():
    conn = conector()
    cur = conn.cursor()
    cur.execute("SELECT emp_schedule.schedule_id, emp_schedule.day, employees.emp_name, emp_schedule.start_time, emp_schedule.end_time FROM emp_schedule JOIN employees ON emp_schedule.id_employee = employees.id_employee ORDER BY CASE emp_schedule.day WHEN 'lunes' THEN 1 WHEN 'martes' THEN 2 WHEN 'miércoles' THEN 3 WHEN 'jueves' THEN 4 WHEN 'viernes' THEN 5 ELSE 6 END, TO_TIMESTAMP(emp_schedule.start_time, 'HH24:MI')")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def search_fields_employee(id):
    conn = conector()
    cur = conn.cursor()
    cur.execute("SELECT emp_name, emp_surname, emp_salary, emp_user_id FROM employees WHERE id_employee = %s", (id,))
    employee_data = cur.fetchone()
    cur.close()
    conn.close()
    return list(employee_data)

@app.route('/modifyemp/<id>', methods=['GET', 'POST'])
def modify_emp(id):
    formEmployee = EditEmployeeForm()
    datos_empleado = search_fields_employee(id)
    if current_user.is_authenticated:
        if current_user.is_admin:
            if request.form:
                conn = conector()
                cur = conn.cursor()
                emp_name = formEmployee.emp_name.data
                emp_surname = formEmployee.emp_surname.data
                emp_salary = formEmployee.emp_salary.data
                cur.execute("UPDATE employees set emp_name = %s, emp_surname = %s, emp_salary = %s where id_employee = %s",(emp_name, emp_surname, emp_salary, id))
                cur.close()
                conn.commit()
                conn.close()
                return redirect(url_for('gestion'))
        else:
            return "<p>No puedes ver esto por falta de permisos</p>"
    else:
        return render_template('not_authenticated.html')
    return render_template('modifyemp.html', id = id, datos_empleado = datos_empleado, formEmployee = formEmployee)

@app.route('/deleteemp/<id>', methods=['GET','POST'])
def delete_emp(id):
    conn = conector()
    cur = conn.cursor()
    cur.execute("DELETE FROM employees WHERE id_employee = %s", (id,))
    cur.close()
    conn.commit()
    conn.close()
    return redirect(url_for('gestion'))

@app.route('/schedule/<id>', methods=['GET','POST'])
def schedule_emp(id):
    formEmployee = NewEmployeeSchedule()
    conn = conector()
    cur = conn.cursor()
    cur.execute("SELECT emp_name from employees where id_employee = %s",(id,))
    employee_name = cur.fetchmany()
    employee_name = employee_name[0]
    cur.execute("SELECT schedule_id, id_employee, day, start_time, end_time FROM emp_schedule WHERE id_employee = %s ORDER BY CASE day WHEN 'lunes' THEN 1 WHEN 'martes' THEN 2 WHEN 'miércoles' THEN 3 WHEN 'jueves' THEN 4 WHEN 'viernes' THEN 5 ELSE 6 END", (id,))
    employee_schedule = cur.fetchall()  
    cur.close()
    conn.close()
    if request.form:
        conn = conector()
        cur = conn.cursor()
        day = formEmployee.schedule_day.data 
        entry = formEmployee.schedule_entry.data
        exit = formEmployee.schedule_exit.data
        cur.execute("INSERT INTO public.emp_schedule (id_employee, day, start_time, end_time) VALUES(%s,%s,%s,%s)",(id,day,entry,exit))
        cur.close()
        conn.commit()
        conn.close()
        return redirect(f'/schedule/{id}') 
    return render_template('schedule.html',formEmployee = formEmployee, employee_schedule = employee_schedule, employee_name = employee_name)

@app.route('/schedule_delete/<id>')
def schedule_delete(id):
    conn = conector()
    cur = conn.cursor()
    cur.execute("select id_employee from emp_schedule where schedule_id = %s",(id,))
    id_user = cur.fetchone
    cur.execute("delete from emp_schedule where schedule_id = %s",(id,))
    cur.close() 
    conn.commit()
    conn.close()
    return redirect('/gestion') 

@app.route('/register', methods=['GET', 'POST'])  #methods permite a flask ejecutar estos metodos desde las clases pertinentes
def register():
    if not current_user.is_authenticated:
        return render_template('not_authenticated.html')
    conn = conector()
    form = RegistrationForm()
    if form.validate_on_submit():
        cur = conn.cursor()
        username = form.username.data
        password = form.password.data
        is_admin = form.is_admin.data
        cur.execute("INSERT INTO public.users (username, user_password, is_admin) VALUES(%s, %s,%s)",(username,password, is_admin))
        flash(f'Cuenta creada para: {form.username.data}!', 'success')
        cur.close()
        conn.commit()
        conn.close()
        return redirect(url_for('register'))
    conn.close()
    return render_template('register.html', title='Register', form=form)

@app.route('/login',methods=['GET', 'POST'])
def login():
    conn = conector()
    form = LoginForm()
    if form.validate_on_submit():
        cur = conn.cursor()
        username = form.username.data
        password = form.password.data
        cur.execute("SELECT id_user, username, user_password FROM users WHERE username=%s and user_password=%s", (username,password))
        user_data = cur.fetchone()
        cur.close()
        conn.close()
        if user_data is not None:
            user = load_user(user_data[0])
            login_user(user, remember=form.remember.data)
            #flash(f'Bienvenido {form.username.data} , acceso exitoso redirigiendo al menu principal', 'success')
            sleep(2.5)
            return redirect(url_for('index'))
        else:
            flash(f'El nombre de usuario o la contraseña son incorrectos', 'danger')
    return render_template('login.html', title='Register', form=form)

@login_manager.user_loader
def load_user(user_id):
    conn = conector()
    cur = conn.cursor()
    cur.execute("SELECT id_user, username, user_password, is_admin FROM users WHERE id_user = %s", (user_id,))
    user_data = cur.fetchone()
    cur.close()
    conn.close()
    if not user_data:
        return None
    id_user, username, user_password, is_admin = user_data
    user = UserMixin()
    user.id = id_user
    user.username = username
    user.password = user_password
    user.is_admin = is_admin

    return user

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/account",methods=['GET', 'POST'])
def account():
    conn = conector()
    form = ChangePasswordForm()
    if form.validate_on_submit():
        cur = conn.cursor()
        name = current_user.username
        old_password = form.old_password.data
        new_password = form.new_password.data
        cur.execute("select * from users where username=%s and user_password=%s",(name,old_password))
        user_data = cur.fetchone()
        if user_data is not None:
            cur.execute("update users set user_password = %s where user_password = %s", (new_password, old_password))
        else:
            flash(f'Introduce correctamente la antigua contraseña', 'danger')
        cur.close()
        conn.commit()
        conn.close()
    return render_template('account.html', title='Account', form=form)

@app.route("/pedidos")
def warehouse():
    conn = conector()
    cur = conn.cursor()

    #select para mostrar los pedidos
    cur.execute("SELECT id_pedido,nombreProduc,precUnidad,cantidad,precioTotalUnidad,fecha,nombre_empresa from pedidos p join supplier su on p.id_empresa=su.id_empresa join product produ on p.id_producto=produ.id_producto")    
    user_data = cur.fetchall()

    # select para empresa   
    cur.execute("SELECT * from supplier")
    empresa=cur.fetchall()

    # select para productos
    cur.execute("SELECT * from product")
    productos=cur.fetchall()

    cur.close()
    conn.close()
    return render_template("warehouse.html",pedidos=user_data)

if __name__=='__main__':
    app.run(host='0.0.0.0')
