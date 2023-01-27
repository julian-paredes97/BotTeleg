#from app import db
from modelos.ModeloPedido import Pedido , format_pedido
from utils.db import db
import json

#from modelos.ModeloProducto import Producto , format_producto
from flask import request, Blueprint

mainPet = Blueprint('peticion_blueprint', __name__)


@mainPet.route('/peticion')
def index():
    return "WEEEEEEEE puto"



#recibir pedido que llega desde el front:
@mainPet.route('/recibePedido',methods=['GET', 'POST'])
def recibePedido():
    
    if request.method == 'POST':
       print("WEEEEEE")
       #pedidos = request.data
       req = request.get_json(silent=True, force=True) #ensayar con esto
       res = json.dumps(req, indent=4)
       print(res)
       aber = json.loads(res)
       
       total=0
       
       for i in aber:
           cantidad = i["cantidad"]
           precio = i["precio"]
           precioxCantidad = cantidad * precio
           total = total + precioxCantidad
           #print(i["cantidad"])
           print(precioxCantidad)
       print(total)
       #cantidad = req.get('responseId')
           
       #temp = json.dumps(pedidos)
       #print("pedido:",pedidos)
       #print("pedidos:",temp)
       #pedido=[]
       #for p in pedidos:
       #    pedido.append(p)
       #print("PEDIDO;",pedido)
    
       
    else :
        print("F")
    # idpedido = request.json['idpedido']
    # identificacion = request.json['identificacion']
    # fechapedido = request.json['fechapedido']
    # fechamaxentrega = request.json['fechamaxentrega']
    # totalpagar= request.json['totalpagar']
    
    
    #pedido = Pedido(idpedido=idpedido,identificacion=identificacion,fechapedido=fechapedido,fechamaxentrega=fechamaxentrega,totalpagar=totalpagar)
    #db.session.add(pedido)
    #db.session.commit()
    
    return "pedido recibido"