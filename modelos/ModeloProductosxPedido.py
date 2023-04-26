from config import db
from sqlalchemy import text

def max_id_productosxpedido():
    
    r = text("(SELECT MAX(idproductoxpedido) + 1 FROM productosxpedido)")
    return r


class ProductoxPedido(db.Model):  #carrito
    
    __tablename__="productosxpedido"

    idproductoxpedido = db.Column(db.Integer, default = max_id_productosxpedido() , primary_key=True,autoincrement=True)
    idpedido = db.Column(db.Integer, nullable=False)#, db.ForeignKey("pedidos.idpedido"), nullable=False) #, ondelete="CASCADE"
    codigo = db.Column(db.String, nullable=False)# db.ForeignKey("productos.codigo"), nullable=False) #, ondelete="CASCADE"
    precio = db.Column(db.Integer)
    cantidadped = db.Column(db.Integer)
    precioxcantidadped=db.Column(db.Integer) 
    
    def __repr__(self):
        return f"ProductosxPedido: {self.idpedido,self.codigo,self.precio,self.cantidadped,self.precioxcantidadped}"
        
   
def format_productosxpedido(prodxped):
    return{
        "idproductoxpedido":prodxped.idproductoxpedido,
        "idpedido":prodxped.idpedido,
        "codigo":prodxped.codigo,
        "precio":prodxped.precio,
        "cantidadped":prodxped.cantidadped,
        "precioxcantidadped":prodxped.precioxcantidadped
    }