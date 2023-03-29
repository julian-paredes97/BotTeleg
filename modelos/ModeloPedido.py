#from app import db
#from ModeloProducto import Producto
from utils.db import db
from sqlalchemy import text

def max_id_pedidos():
    
    r = text("(SELECT MAX(idpedido) + 1 FROM pedidos)")
    # result = db.session.query(func.max(Pedido.idpedido)).scalar()
    # return (result + 1)
    return r

class Pedido(db.Model):  #pedidos
    
    __tablename__="pedidos"

    idpedido = db.Column(db.Integer, default= max_id_pedidos() , primary_key=True, autoincrement=True)
    identificacion = db.Column(db.String, nullable=False)#, db.ForeignKey("clientes.identificacion"), nullable=False) #, ondelete="CASCADE"
    nombres = db.Column(db.String)
    apellidos = db.Column(db.String)
    nombrenegocio = db.Column(db.String)
    direccion = db.Column(db.String)
    ciudad = db.Column(db.String)
    barrio = db.Column(db.String)
    correo = db.Column(db.String)
    celular = db.Column(db.String)
    fechapedido = db.Column(db.Date)
    fechamaxentrega = db.Column(db.Date)
    totalpagar = db.Column(db.Integer) 
    
    def __repr__(self):
        return f"Pedido: {self.identificacion,self.nombres,self.apellidos,self.nombrenegocio,self.direccion,self.ciudad,self.barrio,self.correo,self.celular,self.fechapedido,self.fechamaxentrega,self.totalpagar}"
        #return f"Pedido: {self.idpedido,self.identificacion,self.nombres,self.apellidos,self.nombrenegocio,self.direccion,self.ciudad,self.barrio,self.correo,self.celular,self.fechapedido,self.fechamaxentrega,self.totalpagar}"
    
    # def __init__(self,idpedido,identificacion,nombres,apellidos,nombrenegocio,direccion,ciudad,barrio,correo,celular,fechapedido,fechamaxentrega,totalpagar):
    #     self.idpedido=idpedido
    #     self.identificacion = identificacion
    #     self.nombres = nombres
    #     self.apellidos= apellidos
    #     self.nombrenegocio = nombrenegocio
    #     self.direccion=direccion
    #     self.ciudad=ciudad
    #     self.barrio=barrio
    #     self.correo=correo
    #     self.celular=celular
    #     self.fechapedido=fechapedido
    #     self.fechamaxentrega= fechamaxentrega
    #     self.totalpagar=totalpagar
   
def format_pedido(pedido):
    return{
        "idpedido":pedido.idpedido,
        "identificacion":pedido.identificacion,
        "nombres":pedido.nombres,
        "apellidos":pedido.apellidos,
        "nombrenegocio":pedido.nombrenegocio,
        "direccion":pedido.direccion,
        "ciudad":pedido.ciudad,
        "barrio":pedido.barrio,
        "correo":pedido.correo,
        "celular":pedido.celular,
        "fechapedido":pedido.fechapedido,
        "fechamaxentrega":pedido.fechamaxentrega,
        "totalpagar":pedido.totalpagar
    }