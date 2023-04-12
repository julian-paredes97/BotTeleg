from flask_sqlalchemy import SQLAlchemy #ORM para el manejo de la BD de PostgreSQL
from sqlalchemy.sql import func
from config import db
from modelos.ModeloPedido import Pedido
from modelos.ModeloOrden import Orden
import datetime
from datetime import datetime, timedelta

#Clase en la que guardaremos el texto con los datos del pedido del usuario
#que posteriormente se enviara al proveedor:
class TextoPedUsuario:
    def __init__(self, textoPedidoUsuario):
        self.textoPedidoUsuario = textoPedidoUsuario
        
#funcion que permite obtener la fecha actual:       
def fecha_actual():
    now = datetime.now()
    date_time = now.strftime("%y-%m-%d")
    fecha= date_time
    print("fecha:",fecha)
    print("tipo de la fecha:",type(fecha))
    return fecha

#funcion que permite obtener el dia siguiente de la fecha actual:  
def fecha_max_entrega():
    now = datetime.now()
    date_time = now.strftime("%y-%m-%d")
    fechapedido= date_time
    print("fechapedido:",fechapedido)
    fechamaxentrega= now + timedelta(days=1)
    fechamaxentrega= fechamaxentrega.strftime("%y-%m-%d")
    print("fechamaxentrega",fechamaxentrega)
    return fechamaxentrega

#funcion para calcular el maximo id de la tabla pedidos:
def max_id_pedidos():
    result = db.session.query(func.max(Pedido.idpedido)).scalar()
    return result

#funcion para calcular el maximo id de la tabla ordenes:
def max_id_ordenes():
    result = db.session.query(func.max(Orden.idorden)).scalar()
    return result