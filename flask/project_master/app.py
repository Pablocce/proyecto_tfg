from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')  
#decoramos para indicar que se liga a la ruta raiz
def index():
    #render_template sirve para renderizar los hmtl
    return render_template("index.html")


@app.route('/agenda')
def agenda():
    return "<p> Diego tonto <p>"

@app.route('/pacientes')
def servicios():
    datos = pacientesCargarTabla()
    print(datos[1])
    return render_template("servicios.html", cabeceras = datos[0], data = datos[1])

def pacientesCargarTabla():
    cabeceras = ("Nombre", "Empleo", "Salario")
    data = (
        ("Pablo", "Jefe", "4000"),
        ("Marcuelo", "Jefe", "3000"),
        ("Armando", "Jefe", "2000")
    )
    datos = [cabeceras, data]
    return datos




if __name__=='__main__':
    app.run(host='0.0.0.0', port=8000) 
    #el atributo debug mode sirve para definir el tipo de depuración,
    #si es true podremos modificar el código sin reiniciar el script