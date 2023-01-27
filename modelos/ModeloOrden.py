#from app import db
#from ModeloProducto import Producto
from utils.db import db


class Orden(db.Model):  #carrito
    
    __tablename__="ordenes"

    idorden = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String, db.ForeignKey("productos.codigo"), nullable=False) #, ondelete="CASCADE"
    idpedido = db.Column(db.Integer, db.ForeignKey("pedidos.idpedido"), nullable=False) #, ondelete="CASCADE"
    cantidad = db.Column(db.Integer)
    precioxcantidad=db.Column(db.String) 
    
    def __repr__(self):
        return f"Orden: {self.idorden,self.codigo,self.idpedido,self.cantidad,self.precioxcantidad}"
    
    def __init__(self,idorden,codigo,idpedido,cantidad,precioxcantidad):
        self.idorden=idorden
        self.codigo = codigo
        self.idpedido=idpedido
        self.cantidad=cantidad
        self.precioxcantidad=precioxcantidad
   
def format_orden(orden):
    return{
        "idorden":orden.idorden,
        "codigo":orden.codigo,
        "idpedido":orden.idpedido,
        "cantidad":orden.cantidad,
        "precioxcantidad":orden.precioxcantidad
    }