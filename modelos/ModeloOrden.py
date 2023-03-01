#from app import db
#from ModeloProducto import Producto
from utils.db import db


class Orden(db.Model):  #carrito
    
    __tablename__="ordenes"

    idorden = db.Column(db.Integer, primary_key=True)
    idpedido = db.Column(db.Integer, db.ForeignKey("pedidos.idpedido"), nullable=False) #, ondelete="CASCADE"
    codigo = db.Column(db.String, db.ForeignKey("productos.codigo"), nullable=False) #, ondelete="CASCADE"
    descripcion = db.Column(db.String)
    precio = db.Column(db.Integer)
    cantidad = db.Column(db.Integer)
    precioxcantidad=db.Column(db.Integer) 
    
    def __repr__(self):
        return f"Orden: {self.idorden,self.idpedido,self.codigo,self.descripcion,self.precio,self.cantidad,self.precioxcantidad}"
    
    def __init__(self,idorden,idpedido,codigo,descripcion,precio,cantidad,precioxcantidad):
        self.idorden = idorden
        self.idpedido = idpedido
        self.codigo = codigo
        self.descripcion = descripcion
        self.precio = precio
        self.cantidad = cantidad
        self.precioxcantidad = precioxcantidad
   
def format_orden(orden):
    return{
        "idorden":orden.idorden,
        "idpedido":orden.idpedido,
        "codigo":orden.codigo,
        "descripcion":orden.descripcion,
        "precio":orden.precio,
        "cantidad":orden.cantidad,
        "precioxcantidad":orden.precioxcantidad
    }