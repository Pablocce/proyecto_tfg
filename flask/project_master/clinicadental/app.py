from flask import Flask, render_template, flash, redirect, url_for, request
from forms import RegistrationForm, LoginForm, ChangePasswordForm, SearchPatientForm, NewApointmentForm, ChangeProductPrice,AddNewSupplier,  NewPatientForm, ChangeProductPrice,  NewEmployeeForm, DeleteEmployee, EditEmployeeForm, NewEmployeeSchedule, NewOrderWarehouse, NewProductWarehouse, ChangeProductStock
from forms import SearchApointmentForm, UpdateApointmentForm, UpdateResultsForm
from flask_login import LoginManager
from flask_login import login_user, current_user, UserMixin, logout_user
from time import sleep
from datetime import date
import ast
import datetime


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
    conn = conector()
    cur = conn.cursor()
    fecha_actual = datetime.date.today()
    cur.execute("""
        SELECT c.id_cita, p.paciente_nombre AS nombre_paciente, p.paciente_apellidos AS apellidos_paciente,
            e.emp_name AS nombre_medico, e.emp_surname AS apellido_medico,
            c.procedimiento, c.fecha, c.hora, c.notas
        FROM citas c
        JOIN pacientes p ON c.id_paciente = p.DNI
        JOIN employees e ON c.id_medico = e.id_employee
        WHERE c.fecha = %s
        ORDER BY c.fecha ASC, c.hora ASC
    """, (fecha_actual,))

    citas_data = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('base.html', citas_data = citas_data)

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
            users = obtain_users()
            if request.form:
                conn = conector()
                cur = conn.cursor()
                emp_name = formEmployee.emp_name.data
                emp_surname = formEmployee.emp_surname.data
                emp_salary = formEmployee.emp_salary.data
                emp_user_id = request.form.get('user')
                cur.execute("INSERT INTO public.employees (emp_name, emp_surname, emp_salary, emp_user_id) values (%s,%s,%s, %s)",(emp_name,emp_surname,emp_salary,emp_user_id))
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
                return render_template('gestion.html', formEmployee=formEmployee, employees_data = employees_data, horarios = horarios, users = users)
            else:
                flash_errors(formEmployee)
                return render_template('gestion.html', title='Empleados', formEmployee=formEmployee, employees_data = employees_data, horarios = horarios, users = users)
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
    if current_user.is_authenticated:
        conn = conector()
        cur = conn.cursor()
        cur.execute("DELETE FROM employees WHERE id_employee = %s", (id,))
        cur.close()
        conn.commit()
        conn.close()
        return redirect(url_for('gestion'))

@app.route('/deleteorder/<id>', methods=['GET','POST'])
def delete_order(id):
    if current_user.is_authenticated:
        conn = conector()
        cur = conn.cursor()
        cur.execute("DELETE FROM pedidos WHERE id_pedido = %s",(id,))
        cur.close()
        conn.commit()
        conn.close()
        return redirect(url_for('warehouse'))

@app.route('/schedule/<id>', methods=['GET','POST'])
def schedule_emp(id):
    if current_user.is_authenticated:
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
    if current_user.is_authenticated:
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
    if current_user.is_authenticated:
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
def warehouse():
    if current_user.is_authenticated:
        formNewOrder = NewOrderWarehouse()
        formNewProduct = NewProductWarehouse()
        formChangePrice = ChangeProductPrice()
        formNewSupplier = AddNewSupplier()
        conn = conector()
        cur = conn.cursor()

        #select para mostrar los pedidos
        cur.execute("SELECT id_pedido,nombreProduc,precUnidad,cantidad,precioTotalUnidad,fecha,nombre_empresa, (select emp_name from employees join pedidos on id_employee = employee_id group by emp_name) from pedidos p join supplier su on p.id_empresa=su.id_empresa join product produ on p.id_producto=produ.id_producto")    
        pedidos = cur.fetchall()

        # select para empresa   
        cur.execute("SELECT * from supplier")
        empresas_data=cur.fetchall()

        # select para productos
        cur.execute("SELECT product.id_producto,  product.precunidad,  product.nombreproduc,  product.id_empresa , product.stock ,supplier.nombre_empresa from product join supplier on supplier.id_empresa = product.id_empresa")
        productos=cur.fetchall()

        cur.close()
        conn.close()

        return render_template("warehouse.html",pedidos=pedidos,  productos = productos,formChangePrice = formChangePrice, empresas_data = empresas_data, formNewOrder = formNewOrder, NewProductWarehouse = formNewProduct , formNewSupplier = formNewSupplier)
    else:
        return "identificate"
    
@app.route("/add_product", methods=['POST'])
def add_product():
    if current_user.is_authenticated:
        formNewProduct = NewProductWarehouse()
        conn = conector()
        cur = conn.cursor()
        product_name = formNewProduct.product_name.data
        product_price = formNewProduct.product_price.data
        product_stock = formNewProduct.product_stock.data
        product_supplier = request.form.get('proveedor_producto')
        cur.execute("""INSERT INTO public.product
                    (nombreproduc, precunidad, id_empresa, stock)
                    VALUES( %s, %s, %s, %s);
                    """,(product_name, product_price, product_supplier, product_stock))
        cur.close()
        conn.commit()
        conn.close()
        return redirect(url_for('warehouse'))
    else:
        return "<p> va crack</p>"

@app.route('/deletesupplier/<id>', methods=['GET','POST'])
def delete_supplier(id):
    if current_user.is_authenticated:
        conn = conector()
        cur = conn.cursor()
        cur.execute("DELETE FROM supplier WHERE id_empresa = %s",(id,))
        cur.close()
        conn.commit()
        conn.close()
        return redirect(url_for('warehouse'))

@app.route("/add_supplier" , methods=['POST'])
def add_supplier():
    if current_user.is_authenticated:
        formNewSupplier = AddNewSupplier()
        conn = conector()
        cur = conn.cursor()
        supplier_name = formNewSupplier.supplier_name.data
        cur.execute("""INSERT INTO public.supplier
                    (nombre_empresa)
                    VALUES(%s);
                    """,(supplier_name,))
        cur.close()
        conn.commit()
        conn.close()
        return redirect(url_for('warehouse'))
    else:
        pass

@app.route("/add_order", methods=['POST'])
def add_order():
    if current_user.is_authenticated:
        formNewOrder = NewOrderWarehouse()
        conn = conector()
        cur = conn.cursor()
        proveedor_seleccionado = request.form.get('proveedor')
        producto_seleccionado = request.form.get('producto')
        cur.execute("select precunidad from product where id_producto = %s",(producto_seleccionado,))
        precio_unitario = cur.fetchone()[0]

        cur.execute("select id_employee from employees where emp_user_id = %s",(current_user.get_id()))
        id_employee = cur.fetchone()
        cur.execute("INSERT INTO public.pedidos (id_producto, cantidad, fecha, preciototalunidad, id_empresa, employee_id) VALUES (%s, %s, %s, %s, %s, %s);",(producto_seleccionado, formNewOrder.product_qty.data, date.today(), float(precio_unitario), proveedor_seleccionado, id_employee))
        cur.close()        
        conn.commit()
        conn.close()
        conn = conector()
        cur = conn.cursor()
        cur.execute("SELECT id_employee, emp_name, emp_surname, emp_salary FROM employees")
        employees_data = cur.fetchall()
        cur.close()
        conn.close()
        return redirect(url_for('warehouse'))
    else:
        return "<p> va crack</p>"
    
def buscar_producto(id):
    conn = conector()
    cur = conn.cursor()
    cur.execute("select nombreproduc from product where id_producto = %s",(id,))
    product_name = cur.fetchone()
    cur.close()
    conn.commit()
    conn.close()
    return product_name
    

@app.route("/actualizar_precio/<int:id>", methods=['GET', 'POST'])
def actualizar_precio(id):
    if current_user.is_authenticated:
        formChangePrice = ChangeProductPrice()
        product_name = buscar_producto(id)
        if request.form:
            new_product_price = formChangePrice.product_new_price.data
            conn = conector()
            cur = conn.cursor()
            cur.execute("UPDATE public.product SET precunidad=%s WHERE id_producto=%s",(new_product_price, id))
            cur.close()
            conn.commit()
            conn.close()
            return redirect(url_for('warehouse'))
        return render_template("update_product_price.html", ChangeProductPrice = formChangePrice, product_name = product_name[0])

@app.route("/actualizar_stock/<int:id>", methods=['GET', 'POST'])
def actualizar_stock(id):
    if current_user.is_authenticated:
        formChangeStock = ChangeProductStock()
        product_name = buscar_producto(id)
        if request.form:
            new_product_stock = formChangeStock.product_new_stock.data
            conn = conector()
            cur = conn.cursor()
            cur.execute("UPDATE public.product SET stock=%s WHERE id_producto=%s",(new_product_stock, id))
            cur.close()
            conn.commit()
            conn.close()
            return redirect(url_for('warehouse'))
        return render_template("update_product_stock.html", ChangeProductStock = formChangeStock, product_name = product_name[0])

@app.route('/deleteproduct/<id>', methods=['GET','POST'])
def delete_product(id):
    if current_user.is_authenticated:
        conn = conector()
        cur = conn.cursor()
        cur.execute("DELETE FROM product WHERE id_producto = %s",(id,))
        cur.close()
        conn.commit()
        conn.close()
        return redirect(url_for('warehouse'))


@app.route("/citas", methods=['GET', 'POST'])
def citas(): 
    if current_user.is_authenticated:
        formNewApointment = NewApointmentForm()
        conn = conector()
        cur = conn.cursor()
        cur.execute("""SELECT c.id_cita, p.paciente_nombre AS nombre_paciente, p.paciente_apellidos AS apellidos_paciente,
                        e.emp_name AS nombre_medico, e.emp_surname AS apellido_medico,
                        c.procedimiento, c.fecha, c.hora, c.notas
                        FROM citas c
                        JOIN pacientes p ON c.id_paciente = p.DNI
                        JOIN employees e ON c.id_medico = e.id_employee
                        ORDER BY c.fecha ASC, c.hora ASC""")
        apointments = cur.fetchall()
        cur.close()
        conn.commit()
        conn.close()
        return render_template('apointments.html', apointments = apointments, patients_data = search_pacients(), doctors_data = search_doctors(), formNewApointment = formNewApointment)


@app.route("/update_apointment/<int:id>", methods=['GET', 'POST'])
def update_apointment(id):
    if current_user.is_authenticated:
        formUpdateApointment = UpdateApointmentForm()
        if formUpdateApointment.validate_on_submit():
            conn = conector()
            cur = conn.cursor()
            cur.execute("update citas set fecha = %s, hora = %s where id_cita = %s",
                        (formUpdateApointment.apointment_date.data, formUpdateApointment.apointment_hour.data, id))
            cur.close()
            conn.commit()
            conn.close()
            return redirect(url_for('citas'))  # Redirige a la página de citas
        return render_template('update_apointment.html', formUpdateApointment=formUpdateApointment)


@app.route("/add_apointment", methods=['GET', 'POST'])
def add_apointment():
    if current_user.is_authenticated:
        formNewApointment = NewApointmentForm()
        conn = conector()
        cur = conn.cursor()
        paciente_seleccionado = request.form.get('paciente')
        doctor_seleccionado = request.form.get('doctor')
        cur.execute("INSERT INTO public.citas (id_paciente, id_medico, procedimiento, fecha, hora, notas) VALUES(%s, %s, %s, %s, %s, %s);",
                    (paciente_seleccionado, doctor_seleccionado, formNewApointment.apointment_procedure.data,formNewApointment.apointment_date.data, formNewApointment.apointment_hour.data, formNewApointment.apointment_notes.data))
        cur.execute("INSERT INTO public.historial_clinico (diagnostico,pruebas_complementarias, tratamiento, notas, paciente_dni, fecha, hora) VALUES (%s,%s, %s, %s, %s, %s, %s)",
            ("sin establecer","sin establecer",formNewApointment.apointment_procedure.data, formNewApointment.apointment_notes.data, paciente_seleccionado, formNewApointment.apointment_date.data, formNewApointment.apointment_hour.data))
        cur.close()
        conn.commit()
        conn.close()
        return redirect(url_for('citas'))

@app.route('/deleteapointment/<id>', methods=['GET','POST'])
def delete_apointment(id):
    if current_user.is_authenticated:
        conn = conector()
        cur = conn.cursor()
        cur.execute("DELETE FROM citas WHERE id_cita = %s",(id,))
        cur.close()
        conn.commit()
        conn.close()
        return redirect(url_for('citas'))

@app.route('/search_apointments', methods=['GET', 'POST'])
def search_apointments():
    if current_user.is_authenticated:
        formSearchApointment = SearchApointmentForm()
        conn = conector()
        cur = conn.cursor()
        cur.execute("""
                        SELECT c.id_cita, p.paciente_nombre AS nombre_paciente, p.paciente_apellidos AS apellidos_paciente,
                            e.emp_name AS nombre_medico, e.emp_surname AS apellido_medico,
                            c.procedimiento, c.fecha, c.hora, c.notas
                        FROM citas c
                        JOIN pacientes p ON c.id_paciente = p.DNI
                        JOIN employees e ON c.id_medico = e.id_employee
                        WHERE c.id_paciente = %s
                        ORDER BY c.fecha ASC, c.hora ASC
                    """, (request.form.get('paciente'),))
        pacient_data = cur.fetchall()
        cur.close()
        conn.commit()
        conn.close()
        return render_template('search_apointments.html', title='Pacientes', pacient_data = pacient_data, formSearchApointment = formSearchApointment)

def search_pacients():
    conn = conector()
    cur = conn.cursor()
    cur.execute("SELECT * from pacientes")
    pacient_data = cur.fetchall()
    cur.close()
    conn.commit()
    conn.close()
    return pacient_data

def search_doctors():
    conn = conector()
    cur = conn.cursor()
    cur.execute("SELECT id_employee, emp_name, emp_surname from employees")
    doctors_data = cur.fetchall()
    cur.close()
    conn.commit()
    conn.close()
    return doctors_data

@app.route("/pacientes", methods=['GET', 'POST'])
def patients(): 
    if current_user.is_authenticated:
        formNewPatient = NewPatientForm()
        conn = conector()
        cur = conn.cursor()
        cur.execute("SELECT DNI, paciente_nombre, paciente_apellidos from pacientes")
        patients_data = cur.fetchall()
        cur.close()
        conn.commit()
        conn.close()
        return render_template('patients.html', title='Pacientes', formNewPatient = formNewPatient, patients_data = patients_data)
    
@app.route("/add_patient", methods=['GET', 'POST'])
def add_patient():
    if current_user.is_authenticated:
        formNewPatient = NewPatientForm()
        conn = conector()
        cur = conn.cursor()
        cur.execute("INSERT INTO public.pacientes (dni, paciente_nombre, paciente_apellidos)VALUES(%s, %s, %s)",
                    (formNewPatient.patient_dni.data,formNewPatient.patient_name.data, formNewPatient.patient_surname.data))
        cur.close()
        conn.commit()
        conn.close()
        return redirect(url_for('patients'))

@app.route('/deletepatient/<id>', methods=['GET','POST'])
def delete_patient(id):
    if current_user.is_authenticated:
        conn = conector()
        cur = conn.cursor()
        cur.execute("DELETE FROM pacientes WHERE dni = %s",(id,))
        cur.close()
        conn.commit()
        conn.close()
        return redirect(url_for('patients'))

@app.route('/search_pacient', methods=['POST'])
def search_patient():
    if current_user.is_authenticated:
        formSearchPatient = SearchPatientForm()
        conn = conector()
        cur = conn.cursor()
        cur.execute("SELECT * FROM pacientes WHERE dni = %s", (formSearchPatient.patient_dni.data,))
        patient_dni = cur.fetchone()
        cur.close()
        conn.commit()
        conn.close()

        if patient_dni is None:
            flash("No existe ese paciente", "error")
            return redirect(url_for('patients'))
        else:
            # Realiza alguna acción con los datos del paciente encontrado
            # y muestra la respuesta en la página correspondiente
            #return render_template('patients_history.html', id=patient_dni, form=formSearchPatient)
            return redirect(url_for('patients_history', id=patient_dni))

@app.route('/patients_history<id>', methods=['GET', 'POST'])
def patients_history(id):
    if current_user.is_authenticated:
        conn = conector()
        cur = conn.cursor()
        lista = ast.literal_eval(id)
        cur.execute("SELECT * FROM historial_clinico WHERE paciente_dni = %s", (lista[0],))
        patients_history = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('patients_history.html', id=id, patients_history = patients_history)


@app.route('/modifyhistory/<id>', methods=['GET', 'POST'])
def añadir_diagnostico(id):
    if current_user.is_authenticated:
        NewUpdateResultsForm = UpdateResultsForm()
        if request.form:
            conn = conector()
            cur = conn.cursor()
            cur.execute("UPDATE historial_clinico SET diagnostico = %s WHERE id = %s", (NewUpdateResultsForm.results.data, id,))
            cur.close()
            conn.commit()
            conn.close()
            print("prueba")
            return redirect(url_for('patients'))
    return render_template('modifyhistory.html', NewUpdateResultsForm=NewUpdateResultsForm)






if __name__=='__main__':
    app.run(host='0.0.0.0')
