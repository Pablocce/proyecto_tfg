from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from forms1 import PedidosForm
#from forms import NewPedidoForm

import psycopg2

app = Flask(__name__)
app.secret_key = "secret Key"

# app.config["SQLALCHEMY DATABASE_URI"]


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

@app.route('/')
def index(): 
    conn = conector()
    form = PedidosForm()

    cur = conn.cursor()
    
    cur.execute("SELECT id_pedido, precioTotalUnidad,id_empresa from pedidos")
    user_data = cur.fetchall()
    cur.close()
    conn.close()
    print(user_data)
    return render_template("index.html",pedidos=user_data)

if __name__=='__main__':
    app.run(debug=True)






