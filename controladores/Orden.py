#from app import db
from modelos.ModeloOrden import Orden, format_orden
from utils.db import db

#from modelos.ModeloProducto import Producto , format_producto
from flask import request, Blueprint

mainO = Blueprint('orden_blueprint', __name__)


@mainO.route('/orden')
def index():
    return "WEEEEEEEE puto"

#crear una orden
@mainO.route('/ordenes',methods=['POST'])
def crear_orden():
    idorden = request.json['idorden']
    codigo = request.json['codigo']
    idpedido = request.json['idpedido']
    cantidad = request.json['cantidad']
    precioxcantidad= request.json['precioxcantidad']
    orden = Orden(idorden=idorden,codigo=codigo,idpedido=idpedido,cantidad=cantidad,precioxcantidad=precioxcantidad)
    db.session.add(orden)
    db.session.commit()
    
    return "orden agregada"

#traer todas las ordenes
@mainO.route('/ordenes',methods=['GET'])
def get_ordenes():
    ordenes = Orden.query.order_by(Orden.idorden.asc()).all()  #era id producto.id.asc
    ord_lista=[]
    for orde in ordenes:
        ord_lista.append(format_orden(orde))
    return {'ordenes':ord_lista}

#traer una orden
@mainO.route('/ordenes/<idorden>',methods=['GET'])  #era id
def get_orden(idorden):
    orden = Orden.query.filter_by(idorden=idorden).one()
    formatted_orden = format_orden(orden)
    return {'event':formatted_orden}

#borrar una orden
@mainO.route('/ordenes/<idorden>',methods=['DELETE']) #era id
def delete_orden(idorden):
    orden = Orden.query.filter_by(idorden=idorden).one()
    db.session.delete(orden)
    db.session.commit()
    #return 'Event deleted!'
    return f'Orden (idorden: {idorden}) Eliminada!'

#editar orden
@mainO.route('/ordenes/<idorden>',methods=['PUT']) #era id
def update_orden(idorden):
    orden = Orden.query.filter_by(idorden = idorden)
    #idorden = request.json['idorden']
    codigo = request.json['codigo']
    idpedido = request.json['idpedido']
    cantidad = request.json['cantidad']
    precioxcantidad= request.json['precioxcantidad']
    
    orden.update(dict(codigo=codigo,idpedido=idpedido,cantidad=cantidad,precioxcantidad=precioxcantidad))
    db.session.commit()
    return {'event':format_orden(orden.one())}