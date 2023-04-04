from config import db

class Producto(db.Model):
    
    __tablename__="productos"
    
    codigo=db.Column(db.String, primary_key=True)
    categoria=db.Column(db.String)
    descripcion=db.Column(db.String)
    precio=db.Column(db.Integer)
    cantidad=db.Column(db.Integer)
    imagen= db.Column(db.String)
    
    def __repr__(self):
        return f"Producto: {self.codigo,self.categoria,self.descripcion,self.precio,self.cantidad,self.imagen}"
    
    def __init__(self,codigo,categoria,descripcion,precio,cantidad,imagen):
        self.codigo = codigo
        self.categoria = categoria
        self.descripcion = descripcion
        self.precio = precio
        self.cantidad = cantidad
        self.imagen = imagen
   
def format_producto(producto):
    return{
        "codigo":producto.codigo,
        "categoria":producto.categoria,
        "descripcion":producto.descripcion,
        "precio":producto.precio,
        "cantidad":producto.cantidad,
        "imagen":producto.imagen
    }
