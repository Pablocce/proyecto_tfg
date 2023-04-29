from flask import Flask, render_template, flash, redirect, url_for
from forms import RegistrationForm, LoginForm
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



@app.route('/empleados')
def empleados():
    if current_user.is_authenticated:
        return render_template('empleados.html')
    else:
        return render_template('not_authenticated.html')


@app.route('/register', methods=['GET', 'POST'])  #methods permite a flask ejecutar estos metodos desde las clases pertinentes
def register():
    if current_user.is_authenticated:
        return redirect(url_for('/'))
    conn = conector()
    form = RegistrationForm()
    if form.validate_on_submit():
        cur = conn.cursor()
        username = form.username.data
        password = form.password.data
        cur.execute("INSERT INTO public.users (username, user_password) VALUES(%s, %s)",(username,password))
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
            flash(f'Bienvenido {form.username.data} , acceso exitoso redirigiendo al menu principal', 'success')
            sleep(2.5)
            return redirect(url_for('index'))
        else:
            flash(f'El nombre de usuario o la contraseña son incorrectos', 'danger')
    return render_template('login.html', title='Register', form=form)

@login_manager.user_loader
def load_user(user_id):
    conn = conector()
    cur = conn.cursor()
    cur.execute("SELECT id_user, username, user_password FROM users WHERE id_user = %s", (user_id,))
    user_data = cur.fetchone()
    cur.close()
    conn.close()

    if not user_data:
        return None

    id_user, username, user_password = user_data

    user = UserMixin()
    user.id = id_user
    user.username = username
    user.password = user_password

    return user



@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/account")
def account():
    return render_template('account.html', title='Account')


if __name__=='__main__':
    app.run(host='0.0.0.0')

