from config import db

from modelos.ModeloCliente import Cliente , format_cliente
from flask import request, Blueprint

mainC = Blueprint('cliente_blueprint', __name__)

@mainC.route('/cliente')
def index():
    return "WEEEEEEEE"

#crear un cliente
@mainC.route('/clientes',methods=['GET', 'POST'])
def crear_cliente():
    if request.method == 'POST': 
        identificacion = request.json['identificacion']
        nombre1 = request.json['nombre1']
        nombre2 = request.json['nombre2']
        apellido1 = request.json['apellido1']
        apellido2 = request.json['apellido2']
        nombrenegocio = request.json['nombrenegocio']
        direccion = request.json['direccion']
        correo = request.json['correo']
        celular = request.json['celular']
        barrio = request.json['barrio']
        ciudad = request.json['ciudad']
        creacion = request.json['creacion']
        
        cliente = Cliente(identificacion = identificacion , nombre1 = nombre1, nombre2=nombre2, apellido1=apellido1,
                        apellido2=apellido2,nombrenegocio=nombrenegocio,direccion=direccion, correo=correo,
                        celular=celular,barrio=barrio,ciudad=ciudad,creacion=creacion)
        db.session.add(cliente)
        db.session.commit()
        
        return "cliente agregado"
    else:
        return "cliente no agregado"

#traer todos los clientes
@mainC.route('/clientes',methods=['GET'])
def get_clientes():
    clientes = Cliente.query.order_by(Cliente.identificacion.asc()).all()  #era id producto.id.asc
    cli_lista=[]
    for cl in clientes:
        cli_lista.append(format_cliente(cl))
    return {'clientes':cli_lista}

#traer un cliente
@mainC.route('/clientes/<identificacion>',methods=['GET'])
def get_cliente(identificacion):
    exists = db.session.query(db.exists().where(Cliente.identificacion == identificacion)).scalar()
    exists = str(exists)
    print("existe o no:",exists)
    if exists == "True":
        cliente = Cliente.query.filter_by(identificacion=identificacion).one()
        print("cliente en el back:",cliente)
        formatted_cliente = format_cliente(cliente)
        return {'event':formatted_cliente,'exists':exists}
    else:
        return {'exists':exists}

#borrar un cliente
@mainC.route('/clientes/<identificacion>',methods=['DELETE'])
def delete_cliente(identificacion):
    cliente = Cliente.query.filter_by(identificacion=identificacion).one()
    db.session.delete(cliente)
    db.session.commit()
    return f'Cliente (identificacion: {identificacion}) Eliminado!'

#editar cliente
@mainC.route('/clientes/<identificacion>',methods=['PUT'])
def update_cliente(identificacion):
    cliente=Cliente.query.filter_by(identificacion=identificacion)
    nombre1 = request.json['nombre1']
    nombre2 = request.json['nombre2']
    apellido1 = request.json['apellido1']
    apellido2 = request.json['apellido2']
    nombrenegocio = request.json['nombrenegocio']
    direccion = request.json['direccion']
    correo = request.json['correo']
    celular = request.json['celular']
    barrio = request.json['barrio']
    ciudad = request.json['ciudad']
    creacion = request.json['creacion']
    
    
    
    cliente.update(dict(identificacion = identificacion , nombre1 = nombre1, nombre2=nombre2, apellido1=apellido1,
                      apellido2=apellido2,nombrenegocio=nombrenegocio,direccion=direccion, correo=correo,
                      celular=celular,barrio=barrio,ciudad=ciudad,creacion=creacion))
    db.session.commit()
    return {'event':format_cliente(cliente.one())}

#funcion que permite traer los datos del cliente a partir de su id:
def datos_cliente(identificacion):
    cli = db.session.query(Cliente).filter(
        Cliente.identificacion == str(identificacion)
    ).first()
    return cli