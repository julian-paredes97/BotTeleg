from config import db
from sqlalchemy import text

def max_id_pedidos():
    
    r = text("(SELECT MAX(idpedido) + 1 FROM pedidos)")
    return r

class Pedido(db.Model):  #pedidos
    
    __tablename__="pedidos"

    idpedido = db.Column(db.Integer, default= max_id_pedidos() , primary_key=True, autoincrement=True)
    identificacion = db.Column(db.String, nullable=False)#, db.ForeignKey("clientes.identificacion"), nullable=False) #, ondelete="CASCADE"
    fechapedido = db.Column(db.Date)
    fechamaxentrega = db.Column(db.Date)
    totalpagar = db.Column(db.Integer) 
    
    def __repr__(self):
        return f"Pedido: {self.identificacion,self.fechapedido,self.fechamaxentrega,self.totalpagar}"
        
   
def format_pedido(pedido):
    return{
        "idpedido":pedido.idpedido,
        "identificacion":pedido.identificacion,
        "fechapedido":pedido.fechapedido,
        "fechamaxentrega":pedido.fechamaxentrega,
        "totalpagar":pedido.totalpagar
    }