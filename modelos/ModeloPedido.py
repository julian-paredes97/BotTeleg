#from app import db
#from ModeloProducto import Producto
from utils.db import db


class Pedido(db.Model):  #pedidos
    
    __tablename__="pedidos"

    idpedido = db.Column(db.Integer, primary_key=True)
    identificacion = db.Column(db.String, db.ForeignKey("clientes.identificacion"), nullable=False) #, ondelete="CASCADE"
    fechapedido = db.Column(db.Date)
    fechamaxentrega = db.Column(db.Date)
    totalpagar = db.Column(db.Integer) 
    
    def __repr__(self):
        return f"Orden: {self.idpedido,self.identificacion,self.fechapedido,self.fechamaxentrega,self.totalpagar}"
    
    def __init__(self,idpedido,identificacion,fechapedido,fechamaxentrega,totalpagar):
        self.idpedido=idpedido
        self.identificacion = identificacion
        self.fechapedido=fechapedido
        self.fechamaxentrega= fechamaxentrega
        self.totalpagar=totalpagar
   
def format_pedido(pedido):
    return{
        "idpedido":pedido.idpedido,
        "identificacion":pedido.identificacion,
        "fechapedido":pedido.fechapedido,
        "fechamaxentrega":pedido.fechamaxentrega,
        "totalpagar":pedido.totalpagar
    }