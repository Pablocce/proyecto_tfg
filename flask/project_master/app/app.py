from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')  
#decoramos para indicar que se liga a la ruta raiz
def index():
    #render_template sirve para renderizar los hmtl
    return render_template('index.html')


if __name__=='__main__':
    app.run(host='0.0.0.0', port=8000) 
    #el atributo debug mode sirve para definir el tipo de depuración,
    #si es true podremos modificar el código sin reiniciar el script