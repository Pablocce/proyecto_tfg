'''from __main__ import db

class User(db.Model):    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), db.ForeignKey('employee.username'), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password  = db.Column(db.String(60), nullable=False)

    #este método sirve para definir el formato cuando se printee la clase
    def __repr__(self):
        return f"User('{self.username}','{self.image_file}')"
    
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    surname = db.Column(db.String(120), unique=True, nullable=False)
    job = db.Column(db.String(50), unique=True, nullable=False)
    username = db.relationship('User', backref='username', lazy=True) #lazy carga los datos cuando son necesarios
    #este método sirve para definir el formato cuando se printee la clase
    def __repr__(self):
        return f"Employee('{self.name}','{self.surname}','{self.job}')"
    '''