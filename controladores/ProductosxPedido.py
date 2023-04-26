from modelos.ModeloProductosxPedido import ProductoxPedido, format_productosxpedido
from config import db
from flask import request, Blueprint

mainPxP = Blueprint('prodxped_blueprint', __name__)


@mainPxP.route('/prodxped')
def index():
    return "Endpoint productosxpedido"

#crear una orden / crea un producto por pedido
@mainPxP.route('/prodxpeds',methods=['POST'])
def crear_productoxpedido():
    idproductoxpedido = request.json['idproductoxpedido']
    idpedido = request.json['idpedido']
    codigo = request.json['codigo']
    precio = request.json['precio']
    cantidadped = request.json['cantidadped']
    precioxcantidadped = request.json['precioxcantidadped']
    prodxped = ProductoxPedido(idproductoxpedido=idproductoxpedido,idpedido=idpedido,codigo=codigo,precio=precio,cantidadped=cantidadped,precioxcantidadped=precioxcantidadped)
    db.session.add(prodxped)
    db.session.commit()
    
    return "productoxpedido agregado"

#traer todas las ordenes / trae todos los productos de todos los pedidos
@mainPxP.route('/prodxpeds',methods=['GET'])
def get_productosxpedidos():
    productosxpedidos = ProductoxPedido.query.order_by(ProductoxPedido.idorden.asc()).all()  
    pxp_lista=[]
    for pxp in productosxpedidos:
        pxp_lista.append(format_productosxpedido(pxp))
    return {'productosxpedidos':pxp_lista}

#traer una orden / trae el producto de un pedido
@mainPxP.route('/prodxpeds/<idproductoxpedido>',methods=['GET']) 
def get_productoxpedido(idproductoxpedido):
    productoxpedido = ProductoxPedido.query.filter_by(idproductoxpedido=idproductoxpedido).one()
    formatted_productosxpedido = format_productosxpedido(productoxpedido)
    return {'event':formatted_productosxpedido}

#borrar una orden / borra un producto por pedido 
@mainPxP.route('/prodxpeds/<idproductoxpedido>',methods=['DELETE'])
def delete_productoxpedido(idproductoxpedido):
    productoxpedido = ProductoxPedido.query.filter_by(idproductoxpedido=idproductoxpedido).one()
    db.session.delete(productoxpedido)
    db.session.commit()
    return f'Productoxpedido (idproductoxpedido: {idproductoxpedido}) Eliminado!'

#editar orden
@mainPxP.route('/prodxpeds/<idproductoxpedido>',methods=['PUT'])
def update_productoxpedido(idproductoxpedido):
    productoxpedido = ProductoxPedido.query.filter_by(idproductoxpedido = idproductoxpedido)
    idpedido = request.json['idpedido']
    codigo = request.json['codigo']
    precio = request.json['precio']
    cantidadped = request.json['cantidadped']
    precioxcantidadped= request.json['precioxcantidadped']
    
    ProductoxPedido.update(dict(idpedido=idpedido,codigo=codigo,precio=precio,cantidadped=cantidadped,precioxcantidadped=precioxcantidadped))
    db.session.commit()
    return {'event':format_productosxpedido(productoxpedido.one())}