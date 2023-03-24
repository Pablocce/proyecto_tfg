from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')  #decoramos para indicar que se liga a la ruta raiz
def index():
    return render_template("index.html")

if __name__=='__main__':
    app.run() #el atributo debug mode sirve para definir el tipo de depuración, si es true podremos modificar el código sin reiniciar el script