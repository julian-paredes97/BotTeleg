from config import db
from sqlalchemy import text

def max_id_ordenes():
    
    r = text("(SELECT MAX(idorden) + 1 FROM ordenes)")
    return r


class Orden(db.Model):  #carrito
    
    __tablename__="ordenes"

    idorden = db.Column(db.Integer, default = max_id_ordenes() , primary_key=True,autoincrement=True)
    idpedido = db.Column(db.Integer, nullable=False)#, db.ForeignKey("pedidos.idpedido"), nullable=False) #, ondelete="CASCADE"
    codigo = db.Column(db.String, nullable=False)# db.ForeignKey("productos.codigo"), nullable=False) #, ondelete="CASCADE"
    descripcion = db.Column(db.String)
    precio = db.Column(db.Integer)
    cantidad = db.Column(db.Integer)
    precioxcantidad=db.Column(db.Integer) 
    
    def __repr__(self):
        return f"Orden: {self.idpedido,self.codigo,self.descripcion,self.precio,self.cantidad,self.precioxcantidad}"
        
   
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