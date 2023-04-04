from config import db

class Cliente(db.Model):
    
    __tablename__="clientes"
    
    identificacion=db.Column(db.String, primary_key=True)
    nombre1=db.Column(db.String)
    nombre2=db.Column(db.String)
    apellido1=db.Column(db.String)
    apellido2=db.Column(db.String)
    nombrenegocio=db.Column(db.String)
    direccion=db.Column(db.String)
    correo=db.Column(db.String)
    celular=db.Column(db.String)
    barrio=db.Column(db.String)
    ciudad=db.Column(db.String)
    creacion= db.Column(db.String)
    
    def __repr__(self):
        return f"Cliente: {self.identificacion,self.nombre1,self.nombre2,self.apellido1,self.apellido2,self.nombrenegocio,self.direccion,self.correo,self.celular,self.barrio,self.ciudad,self.creacion}"
    
    def __init__(self,identificacion,nombre1,nombre2,apellido1,apellido2,nombrenegocio,direccion,correo,celular,barrio,ciudad,creacion):
        
        self.identificacion = identificacion
        self.nombre1 = nombre1
        self.nombre2 = nombre2
        self.apellido1 = apellido1
        self.apellido2 = apellido2
        self.nombrenegocio = nombrenegocio
        self.direccion = direccion
        self.correo = correo
        self.celular = celular
        self.barrio = barrio
        self.ciudad = ciudad
        self.creacion = creacion
   
def format_cliente(cliente):
    return{
        "identificacion":cliente.identificacion,
        "nombre1":cliente.nombre1,
        "nombre2":cliente.nombre2,
        "apellido1":cliente.apellido1,
        "apellido2":cliente.apellido2,
        "nombrenegocio":cliente.nombrenegocio,
        "direccion":cliente.direccion,
        "correo":cliente.correo,
        "celular":cliente.celular,
        "barrio":cliente.barrio,
        "ciudad":cliente.ciudad,
        "creacion":cliente.creacion
    }
