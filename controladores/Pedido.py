from modelos.ModeloPedido import Pedido , format_pedido
from config import db
import json
from flask import request, Blueprint, make_response

mainPe = Blueprint('pedido_blueprint', __name__)


@mainPe.route('/pedido')
def index():
    return "Endpoint pedido"

#crear un pedido
@mainPe.route('/pedidos',methods=['POST'])
def crear_pedido():
    idpedido = request.json['idpedido']
    identificacion = request.json['identificacion']
    fechapedido = request.json['fechapedido']
    fechamaxentrega = request.json['fechamaxentrega']
    totalpagar= request.json['totalpagar']
    pedido = Pedido(idpedido=idpedido,identificacion=identificacion,fechapedido=fechapedido,fechamaxentrega=fechamaxentrega,totalpagar=totalpagar)
    db.session.add(pedido)
    db.session.commit()
    
    return "pedido agregado"

#traer todos los pedidos
@mainPe.route('/pedidos',methods=['GET'])
def get_pedidos():
    pedidos=Pedido.query.order_by(Pedido.idpedido.asc()).all()
    ped_lista=[]
    for ped in pedidos:
        ped_lista.append(format_pedido(ped))
    return {'pedidos':ped_lista}

#traer un pedido
@mainPe.route('/pedidos/<idpedido>',methods=['GET'])
def get_pedido(idpedido):
    pedido = Pedido.query.filter_by(idpedido=idpedido).one()
    formatted_pedido = format_pedido(pedido)
    return {'event':formatted_pedido}

#borrar un pedido
@mainPe.route('/pedidos/<idpedido>',methods=['DELETE'])
def delete_pedido(idpedido):
    pedido = Pedido.query.filter_by(idpedido=idpedido).one()
    db.session.delete(pedido)
    db.session.commit()
    return f'Pedido (idpedido: {idpedido}) Eliminado!'

#editar pedido
@mainPe.route('/pedidos/<idpedido>',methods=['PUT'])
def update_pedido(idpedido):
    pedido = Pedido.query.filter_by(idpedido=idpedido)
    identificacion = request.json['identificacion']
    fechapedido = request.json['fechapedido']
    fechamaxentrega = request.json['fechamaxentrega']
    totalpagar= request.json['totalpagar']
    
    pedido.update(dict(identificacion=identificacion,fechapedido=fechapedido,fechamaxentrega=fechamaxentrega,totalpagar=totalpagar))
    db.session.commit()
    return {'event':format_pedido(pedido.one())}