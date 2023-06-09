from flask import Flask, render_template, flash, redirect, url_for, request
from forms import NewPacienteForm, RegistrationForm, LoginForm, ChangePasswordForm, ChangeProductPrice,NewEmployeeForm,NewOrderWarehouse,EditEmployeeForm, NewEmployeeSchedule, DeleteEmployee, NewCitasFrom,NewProductWarehouse
from flask_login import LoginManager
from flask_login import login_user, current_user, UserMixin, logout_user
from time import sleep
from datetime import date

import psycopg2



app = Flask(__name__)
login_manager = LoginManager(app)


def conector():
    conn=None
    try:
        #creamos conexión
        conn = psycopg2.connect(
        host="localhost",
        database="clinicaDental",
        user="armando",
        password="odoo",
        port="5434")
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
    formEmployee = NewEmployeeForm() 
    if current_user.is_authenticated:

        if current_user.is_admin:
            conn = conector()
            cur = conn.cursor()
            cur.execute("SELECT id_employee, emp_name, emp_surname, emp_salary, emp_user_id FROM employees")
            employees_data = cur.fetchall()
            print(employees_data)
            cur.close()
            conn.close()
            if request.form:
                conn = conector()
                cur = conn.cursor()
                emp_name = formEmployee.emp_name.data
                emp_surname = formEmployee.emp_surname.data
                emp_salary = formEmployee.emp_salary.data
                emp_user_id = 0
                cur.execute("INSERT INTO public.employees (emp_name, emp_surname, emp_salary) values (%s,%s,%s,%s)",(emp_name,emp_surname,emp_salary,emp_user_id))
                #flash(f'Cuenta creada para: {formEmployee.username.data}!', 'success')
                cur.close()
                conn.commit()
                conn.close()

                conn = conector()
                cur = conn.cursor()
                cur.execute("SELECT id_employee, emp_name, emp_surname, emp_salary, emp_user_id FROM employees")
                employees_data = cur.fetchall()
                cur.close()
                conn.close()
                # Procesar el formulario y crear un nuevo empleado
                # ...
                return render_template('gestion.html', formEmployee=formEmployee, employees_data = employees_data)
            else:
                flash_errors(formEmployee)
                return render_template('gestion.html', title='Empleados', formEmployee=formEmployee, employees_data = employees_data)
        else:
            return "<p>No puedes ver esto por falta de permisos</p>"
    else:
        return render_template('not_authenticated.html')


def obtain_users():
    conn = conector()
    cur = conn.cursor()
    cur.execute("SELECT id_user, username FROM users")
    users_data = cur.fetchall()
    cur.close()
    conn.close()
    return users_data

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
    if current_user.is_authenticated:
        return render_template('not_authenticated.html')
    conn = conector()
    form = RegistrationForm()
    if form.validate_on_submit():
        cur = conn.cursor()
        username = form.username.data
        password = form.password.data
        is_admin = form.is_admin.data
        cur.execute("INSERT INTO public.users (username, user_password, image_profile) VALUES(%s, %s,%s)",(username,password, is_admin))
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
    cur.execute("SELECT id_user, username, user_password, image_profile  FROM users WHERE id_user = %s", (user_id,))
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

@app.route("/pedidos", methods=['GET', 'POST'])
def pedidos(): 
    if current_user.is_authenticated:
        conn = conector()
        formNewOrder = NewOrderWarehouse()
        formNewProduct = NewProductWarehouse()
        formChangePrice = ChangeProductPrice()

        cur = conn.cursor()


        #select para mostrar los pedidos
        cur.execute("SELECT id_pedido,nombreProduc,precUnidad,p.cantidad,precioTotalUnidad,fecha,nombre_empresa, (select emp_name from employees e join Users u on e.emp_user_id= u.id_user join pedidos p on p.id_usuario=u.id_user ) from pedidos p join supplier su on p.id_empresa=su.id_empresa join product produ on p.id_producto=produ.id_producto")
        user_data = cur.fetchall()
        


        # select para empresa
        cur.execute("SELECT * from supplier")
        empresas_data=cur.fetchall()
        

        # select para productos
        cur.execute("SELECT product.id_producto,  product.precUnidad,  product.nombreProduc,  product.id_empresa,product.cantidad, supplier.nombre_empresa from product join supplier on supplier.id_empresa = product.id_empresa")
        productos=cur.fetchall()
  
        cur.close()
        conn.close()
        if request.method == 'POST':
            conn = conector()
            cur = conn.cursor()
            proveedor_seleccionado = request.form.get('proveedor')
            producto_seleccionado = request.form.get('producto')
            cur.execute("select precUnidad from product where id_producto = %s",(producto_seleccionado,))
            precio_unitario = cur.fetchone()[0]

            cur.execute("select id_employee from employees where emp_user_id = %s",(current_user.get_id()))
            id_employee = cur.fetchone()
            print(id_employee)
            cur.execute("INSERT INTO pedidos (id_producto, cantidad, fecha, preciototalunidad, id_empresa, employee_id) VALUES (%s, %s, %s, %s, %s, %s);",(producto_seleccionado, formNewOrder.product_qty.data, date.today(), float(precio_unitario), proveedor_seleccionado, id_employee))
            #flash(f'Cuenta creada para: {formEmployee.username.data}!', 'success')
            cur.close()
            conn.commit()
            conn.close()
        return render_template("pedidos.html",title ='Pedidos',pedidos=user_data, productos = productos, empresas_data = empresas_data, formNewOrder = formNewOrder,NewProductWarehouse = formNewProduct,formChangePrice = formChangePrice)
    else:
        return "identificate"


@app.route("/citas", methods=['GET', 'POST'])
def citas(): 
    if current_user.is_authenticated:
        conn = conector()
        formNewOrder = NewCitasFrom()

        cur = conn.cursor()


        #select para mostrar citas
        cur.execute("SELECT c.id_cita,c.fecha, c.descripcion,p.dni,p.nombre,p.apellido1 from pacientes p join cita c on p.dni=c.id_paciente order by fecha;")

        user_data = cur.fetchall()
        print (user_data)

        cur.close()
        conn.commit()
        conn.close()
        return render_template('citas.html', title='Cita', citas=user_data, formNewOrder=formNewOrder)

@app.route("/pacientes", methods=['GET', 'POST'])
def pacientes(): 
    if current_user.is_authenticated:
        conn = conector()
        formNewOrder = NewPacienteForm()

        cur = conn.cursor()


        #select para mostrar citas
        cur.execute("SELECT p.dni,p.nombre,p.apellido1,p.apellido2, p.id_cita from pacientes p")
        user_data = cur.fetchall()
        print (user_data)

        cur.close()
        conn.commit()
        conn.close()
        return render_template('pacientes.html', title='Pacientes', pacientes=user_data, formNewOrder=formNewOrder)




if __name__=='__main__':
    app.run(host='0.0.0.0')



@app.route("/citas", methods=['GET', 'POST'])
def citas(): 
    # Verifica si el usuario actual está autenticado
    if current_user.is_authenticated:
        # Conexión a la base de datos
        conn = conector()

        # Creación del formulario para una nueva cita
        formNewOrder = NewCitasFrom()

        # Creación del cursor para ejecutar consultas SQL
        cur = conn.cursor()

        # Consulta SQL para obtener los datos de las citas y los pacientes
        cur.execute("SELECT c.id_cita, c.fecha, c.descripcion, p.dni, p.nombre, p.apellido1 FROM pacientes p JOIN cita c ON p.dni = c.id_paciente ORDER BY fecha;")
        
        # Obtiene todos los datos de las citas y los pacientes
        user_data = cur.fetchall()

        # Imprime los datos obtenidos en la consola (para propósitos de depuración)
        print(user_data)

        # Cierra el cursor
        cur.close()

        # Guarda los cambios en la base de datos
        conn.commit()

        # Cierra la conexión a la base de datos
        conn.close()

        # Renderiza la plantilla 'citas.html' y pasa los datos de las citas, el formulario y el título como argumentos
        return render_template('citas.html', title='Cita', citas=user_data, formNewOrder=formNewOrder)