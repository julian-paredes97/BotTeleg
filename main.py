from flask import Flask, request, Blueprint #para crear el servidor web
from config import *
import telebot # libreria para manejar la api de telegram
from telebot.types import ReplyKeyboardMarkup #para crear botones
from telebot.types import ForceReply #para citar un mensaje
from telebot.types import ReplyKeyboardRemove # para eliminar botones
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton , KeyboardButton #para los botones para abrir la webapp
from telebot.types import MenuButtonWebApp, WebAppInfo #para los botones para abrir la webapp
import time
import requests
import json
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy #ORM para el manejo de la BD de PostgreSQL
from controladores.Producto import mainP
from controladores.Orden import mainO
from controladores.Pedido import mainPe
from controladores.Cliente import mainC
from modelos.ModeloPedido import Pedido
from modelos.ModeloOrden import Orden
from modelos.ModeloCliente import Cliente , format_cliente
from controladores.Helpers import max_id_pedidos, max_id_ordenes , datos_cliente , TextoPedUsuario , fecha_actual, fecha_max_entrega


#instanciamos el bot de telegram
bot = telebot.TeleBot(TELEGRAM_TOKEN)

#instanciamos el servidor web de flask:
web_server= Flask(__name__)

#Se configura el ORM sqlalchemy con las credenciales de la base de datos que se encuentra en AWS:
web_server.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:root123456@postgresdb.cadpgx7qqz5d.us-east-1.rds.amazonaws.com/postgres"
web_server.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db=SQLAlchemy(web_server)

CORS(web_server)


webURL= localtunnel     #variable que almacena la URL en la que se establecera el webhook

#Clase en la que guardaremos el texto con los datos del pedido del usuario
#que posteriormente se enviara al proveedor:
TextoPedUsuario.textoPedidoUsuario = '<u><b>Datos Pedido:</b></u> \n'

#variable global en la que guardaremos los datos de los usuarios que se van a registrar:
usuarios = {}

#variable global en la que guardaremos los datos de los usuarios activos y validados:
usuariosAct = {}

#posibles saludos por parte del usuario:
saludo=["hola","ola","hey","buenas","buen dia","buenos dias",
        "buena tarde","buenas tardes","buena noche","buenas noches",
        "quisiera hacer un pedido","como esta","saludos"]


#Gestiona las peticiones o actualizaciones POST enviadas al webhook
#del bot en el servidor web y las procesa:
@web_server.route('/', methods=['POST'])
def webhook():
    #si el post recibido es un JSON:
    if request.headers.get("content-type") == "application/json":
        update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
        bot.process_new_updates([update])
        return "OK",200


#responde al comando /start :
@bot.message_handler(commands=['start'])
def cmd_start(message):
    """ Muestra las acciones disponibles al iniciar una conversacion. """
    
    bot.send_message(message.chat.id,"Buen dia, se ha comunicado con Distri Romel Sas")
    
    #definimos tres botones
    markup= ReplyKeyboardMarkup(one_time_keyboard=True,
                                input_field_placeholder="Pulsa un boton",
                                resize_keyboard=True)
    markup.add("Realizar pedido","Ayuda","Salir")
    #preguntamos por la accion
    msg = bot.send_message(message.chat.id, "Como podemos ayudarle?",reply_markup=markup)
    bot.register_next_step_handler(msg,realizar_pedido)

#responde a las entradas de texto:
@bot.message_handler(content_types=["text"])
def saludo_inicial(message):
    """ Muestra las acciones disponibles al iniciar una conversacion. """
    
    if message.text.lower() in saludo:
        bot.send_message(message.chat.id,"Buen dia, se ha comunicado con Distri Romel Sas")
    
        #definimos dos botones
        markup= ReplyKeyboardMarkup(one_time_keyboard=True,
                                    input_field_placeholder="Pulsa un boton",
                                    resize_keyboard=True)
        markup.add("Realizar pedido","Ayuda","Salir")
        #preguntamos por la accion
        msg = bot.send_message(message.chat.id, "Como podemos ayudarle?",reply_markup=markup)
        bot.register_next_step_handler(msg,realizar_pedido)



#responde a las entradas de texto:
@bot.message_handler(content_types=["text"])
def realizar_pedido(message):
    """Evalua que accion se va a ejecutar:"""
    
    if message.text.lower()=="realizar pedido":
        markup = ForceReply()  # para responder citado
        msg = bot.send_message(message.chat.id,"Por favor ingrese su numero de cedula", reply_markup=markup)
        bot.register_next_step_handler(msg,corroborar_cedula)
    
    if message.text.lower()=="ayuda":
        markup= ReplyKeyboardMarkup(one_time_keyboard=True,
                                    input_field_placeholder="Pulsa un boton",
                                    resize_keyboard=True)
        markup.add("Realizar pedido","Salir")
       
        #preguntamos por la accion
        msg = bot.send_message(message.chat.id,"link de youtube con video explicativo",reply_markup=markup)
        bot.register_next_step_handler(msg,realizar_pedido)
    
    if message.text.lower()=="salir":
        markup= ReplyKeyboardRemove()
        bot.send_message(message.chat.id,"Gracias por comunicarse con nosotros, Hasta luego",reply_markup=markup)
        

#Corrobora que la cedula que se esta ingresando exista,
#que sea un dato entero y que se encuentre en la BD:
def corroborar_cedula(message):
    #Verifica que el dato ingresado por el usuario sea un entero y que no contenga letras:
    if not message.text.isnumeric():
        #informa error y se vuelve a preguntar
        msg = bot.send_message(message.chat.id, "ERROR: Debes indicar un numero valido. \n cual es tu cedula?") #,reply_markup=markup)
        bot.register_next_step_handler(msg,corroborar_cedula)
    
    if message.text.isnumeric():
        
        cedula= message.text
        bot.send_message(message.chat.id, "Validando informacion...")
        
        #Verifica si el usuario existe en la BD:
        exists = db.session.query(db.exists().where(Cliente.identificacion == cedula)).scalar()
        exists = str(exists)
        print("existe o no:",exists.split())
        print("tipo:",type(exists))
        
        #Verifica que el usuario este en la bd, si el usuario esta
        #se procede a hacer pedido, sino se piden datos al usuario
        #para ingresarlo a la BD:
        if exists == "True":
            cedula = str(cedula)

            print("AL VERIFICAR QUE EXISTE LA CEDULA:",cedula)
            
            print("entre")
            
            #Trae todos los datos del cliente de la BD:
            cliente = db.session.query(Cliente).filter(Cliente.identificacion == cedula).one()
            
            print("cliente en el back:",cliente)
            formatted_cliente = format_cliente(cliente)
            
            nombre1 = formatted_cliente['nombre1']
            nombre2 = formatted_cliente['nombre2']
            nombre1 = nombre1.lower()
            nombre2 = nombre2.lower()
            nombrecompleto = nombre1 + " " + nombre2
            chatId = message.chat.id
            
            #guarda datos del cliente y el id de la conversacion con el bot
            datosAlmacenar = {"chatId":str(chatId),"identificacion":str(cedula)}
            
            print("truesito pa")
                    
            #envia datos del cliente y del bot para almacenarlos en un diccionario
            req= requests.post("https://flask-web-bot-app.loca.lt/botdata",
            data = json.dumps(datosAlmacenar), 
            headers={"Content-Type": "application/json"})
            print(req.text)
            print("###############################################")
            
            #####   ABRIR WEBAPP:   #####
            web_app_url = "https://regal-meerkat-6adcf2.netlify.app"
            keyboard = telebot.types.InlineKeyboardMarkup()
            markup2=telebot.types.InlineKeyboardButton(text="REALIZAR PEDIDO :)",web_app=WebAppInfo(url=web_app_url))
            keyboard.add(markup2) #se añade boton inline que permitira abrir la WebApp
            msg=bot.send_message(message.chat.id, text=f"Hola {nombrecompleto}, que vas a pedir el dia de hoy?", reply_markup=keyboard)
            print("ABER EL MSG:",msg)
            #####   ABRIR WEBAPP:   #####
            
# En caso que el usuario no existe se piden los
# siguientes datos para almacenarlo en la BD:
def preguntar_primer_nombre(message):
    """almacena nombres del usuario y pregunta apellidos."""
    nombres = message.text
    nombres = nombres.split()
    print("WEEE:",nombres)
    print("tipo",type(nombres))
    #va almacenando los datos en el diccionario 
    if (len(nombres)==1):
        primerNombre = nombres[0]
        segundoNombre = ""
        print(primerNombre)
        print(segundoNombre)
        usuarios[message.chat.id]["nombre1"] = primerNombre
        usuarios[message.chat.id]["nombre2"] = segundoNombre
    elif (len(nombres)==2):
        primerNombre = nombres[0]
        segundoNombre = nombres[1]
        print(primerNombre)
        print(segundoNombre)
        usuarios[message.chat.id]["nombre1"] = primerNombre
        usuarios[message.chat.id]["nombre2"] = segundoNombre
           
    markup = ForceReply()  # para responder citado
    msg = bot.send_message(message.chat.id,"Cuales son sus apellidos?:", reply_markup=markup)
    bot.register_next_step_handler(msg,preguntar_apellidos)

def preguntar_apellidos(message):
    """almacena apellidos del usuario y pregunta nombre del negocio."""
    apellidos = message.text
    apellidos = apellidos.split()
    print("WEEE:",apellidos)
    print("tipo",type(apellidos))
    #va almacenando los datos en el diccionario  
    if (len(apellidos)==1):
        primerApellido = apellidos[0]
        segundoApellido = ""
        print(primerApellido)
        print(segundoApellido)
        usuarios[message.chat.id]["apellido1"] = primerApellido
        usuarios[message.chat.id]["apellido2"] = segundoApellido
    elif (len(apellidos)==2):
        primerApellido = apellidos[0]
        segundoApellido = apellidos[1]
        print(primerApellido)
        print(segundoApellido)
        usuarios[message.chat.id]["apellido1"] = primerApellido
        usuarios[message.chat.id]["apellido2"] = segundoApellido  
    
    markup = ForceReply()  # para responder citado
    msg = bot.send_message(message.chat.id,"Por favor ingrese el nombre de su negocio", reply_markup=markup)
    bot.register_next_step_handler(msg,preguntar_nombre_negocio)


def preguntar_nombre_negocio(message):
    """almacena nombre del negocio y pregunta direccion."""
    nombreNegocio = message.text 
    print("nombreNegocio:",nombreNegocio)
    usuarios[message.chat.id]["nombrenegocio"] = nombreNegocio
    #va almacenando los datos en el diccionario
    
    markup = ForceReply()  # para responder citado
    msg = bot.send_message(message.chat.id,"Por favor ingrese su direccion", reply_markup=markup)
    bot.register_next_step_handler(msg,preguntar_direccion)
    
def preguntar_direccion(message):
    """almacena direccion y pregunta correo del usuario."""
    direccion = message.text
    print("direccion:",direccion)
    #va almacenando los datos en el diccionario
    usuarios[message.chat.id]["direccion"] = direccion
    
    markup = ForceReply()  # para responder citado
    msg = bot.send_message(message.chat.id,"Por favor ingrese su correo electronico:", reply_markup=markup)
    bot.register_next_step_handler(msg,preguntar_correo)
    
def preguntar_correo(message):
    """almacena correo y pregunta celular del usuario."""
    correo = message.text
    print("correo:",correo)
    #va almacenando los datos en el diccionario
    usuarios[message.chat.id]["correo"] = correo
    
    markup = ForceReply()  # para responder citado
    msg = bot.send_message(message.chat.id,"Por favor ingrese el numero de su celular", reply_markup=markup)
    bot.register_next_step_handler(msg,preguntar_celular)
 
def preguntar_celular(message):
    """almacena celular y pregunta barrio del usuario."""
    cel = message.text
    print("celular:",cel)
    #va almacenando los datos en el diccionario
    usuarios[message.chat.id]["celular"] = cel
    
    markup = ForceReply()  # para responder citado
    msg = bot.send_message(message.chat.id,"Por favor ingrese el barrio", reply_markup=markup)
    bot.register_next_step_handler(msg,preguntar_barrio)

def preguntar_barrio(message):
    """almacena barrio y pregunta ciudad del usuario."""
    barrio = message.text
    print("barrio:",barrio)
    #va almacenando los datos en el diccionario
    usuarios[message.chat.id]["barrio"] = barrio
    
    markup = ForceReply()  # para responder citado
    msg = bot.send_message(message.chat.id,"Por favor ingrese su ciudad", reply_markup=markup)
    bot.register_next_step_handler(msg,guardar_datos_usuario)
      
#Funcion que permite almacenar los datos de
#un nuevo usuario en la BD:
def guardar_datos_usuario(message):
    """almacena ciudad y obtiene fecha de creacion del usuario."""
    ciudad = message.text
    print("ciudad:",ciudad)
    
    fecha= fecha_actual()           #Se obtiene la fecha actual
    
    usuarios[message.chat.id]["ciudad"] = ciudad
    usuarios[message.chat.id]["creacion"] = fecha
    
    texto = 'Datos introducidos: \n'
    texto+= f'<code>identificacion:</code>{usuarios[message.chat.id]["identificacion"]}\n'
    texto+= f'<code>nombre1:</code>{usuarios[message.chat.id]["nombre1"]}\n'
    texto+= f'<code>nombre2:</code>{usuarios[message.chat.id]["nombre2"]}\n'
    texto+= f'<code>apellido1:</code>{usuarios[message.chat.id]["apellido1"]}\n'
    texto+= f'<code>apellido2:</code>{usuarios[message.chat.id]["apellido2"]}\n'
    texto+= f'<code>nombrenegocio:</code>{usuarios[message.chat.id]["nombrenegocio"]}\n'
    texto+= f'<code>direccion:</code>{usuarios[message.chat.id]["direccion"]}\n'
    texto+= f'<code>correo:</code>{usuarios[message.chat.id]["correo"]}\n'
    texto+= f'<code>celular:</code>{usuarios[message.chat.id]["celular"]}\n'
    texto+= f'<code>barrio:</code>{usuarios[message.chat.id]["barrio"]}\n'
    texto+= f'<code>ciudad:</code>{usuarios[message.chat.id]["ciudad"]}\n'
    texto+= f'<code>creacion:</code>{usuarios[message.chat.id]["creacion"]}\n'
    markup = ReplyKeyboardRemove()  # eliminar botones
    bot.send_message(message.chat.id,texto, parse_mode="html",reply_markup=markup)
    print(usuarios)
    
    clienteNuevo = usuarios[message.chat.id]
    print(clienteNuevo)
    """guarda los datos del usuario en la BD."""
    
    cliente = Cliente(identificacion = usuarios[message.chat.id]["identificacion"] ,
                      nombre1 = usuarios[message.chat.id]["nombre1"],
                      nombre2=usuarios[message.chat.id]["nombre2"],
                      apellido1=usuarios[message.chat.id]["apellido1"],
                      apellido2=usuarios[message.chat.id]["apellido2"],
                      nombrenegocio=usuarios[message.chat.id]["nombrenegocio"],
                      direccion=usuarios[message.chat.id]["direccion"],
                      correo=usuarios[message.chat.id]["correo"],
                      celular=usuarios[message.chat.id]["celular"],
                      barrio=usuarios[message.chat.id]["barrio"],
                      ciudad=usuarios[message.chat.id]["ciudad"],
                      creacion=usuarios[message.chat.id]["creacion"])
    
    db.session.add(cliente)
    db.session.commit()
    
    #para borrar el usuario que hay en cache :
    del usuarios[message.chat.id]
    
    
    bot.send_message(message.chat.id,"Datos almacenados correctamente")
    
    
    markup= ReplyKeyboardMarkup(one_time_keyboard=True,
                                        input_field_placeholder="Pulsa un boton",
                                        resize_keyboard=True)
    markup.add("Realizar pedido","Salir")
        
    #preguntamos por la accion:
    msg = bot.send_message(message.chat.id,"Necesitas algo mas?",reply_markup=markup)
    bot.register_next_step_handler(msg,realizar_pedido)


#almacena datos del usuario y del bot para
#que despues estos puedan compararse con
#la informacion solicitada por el front:
@web_server.route('/botdata',methods=['GET','POST'])
async def datosbot():
    if request.method == 'POST':
        data = request.get_json() # se obtienen los datos del request que llegan al endpoint
        chatid = data["chatId"]
        identificacion = data["identificacion"]
        
        
        usuariosAct[chatid]={}
        usuariosAct[chatid]["identificacion"] = identificacion
        usuariosAct[chatid]["chatid"] = chatid
        
        
        print("llamado del back:")
        print("ABER QUE CHUCHAS:",data)
        print("ABER QUE CHUCHAS:",chatid)
        print("ABER QUE CHUCHAS:",identificacion)
        
        return data
        
        
#Endpoint que recibe el pedido que llega desde el front:
@web_server.route('/recibePedido',methods=['GET', 'POST'])
async def recibePedido():
    
    if request.method == 'POST':
       print("WEEEEEE")
       req = request.get_json(silent=True, force=True) #ensayar con esto
       res = json.dumps(req, indent=4)
       print(res)
       ped = json.loads(res)
       pedidoCliente = ped
       print("pedido:\n",pedidoCliente)
       
       
       ######## datos para tabla pedidos ########
       identificacion = 0
       nombrenegocio = ""
       
       chatID = ped["datosUsuario"]["id"]
       chatID = str(chatID)
       print("ABER_CHATID:",chatID)
       print("USUARIOSACTIVOS:",usuariosAct)
       
       if usuariosAct[chatID]:
           print("siuuu")
           identificacion = usuariosAct[chatID]["identificacion"]
       
       print("identificacion:",identificacion)
       datoscliente = datos_cliente(identificacion)
       print("datoscliente:",datoscliente)
       nombres= (datoscliente.nombre1 + " " + datoscliente.nombre2)
       print("nombres:",nombres)
       apellidos= (datoscliente.apellido1 + " " + datoscliente.apellido2)
       print("apellidos:",apellidos)
       nombrenegocio = datoscliente.nombrenegocio
       print("nombrenegocio:",nombrenegocio)
       direccion = datoscliente.direccion
       print("direccion:",direccion)
       ciudad = datoscliente.ciudad
       print("ciudad:",ciudad)
       barrio = datoscliente.barrio
       print("barrio:",barrio)
       correo = datoscliente.correo
       print("correo:",correo)
       celular = datoscliente.celular
       print("celular:",celular)
       
       fechapedido = fecha_actual()                 #se obtiene la fecha actual
       fechamaxentrega = fecha_max_entrega()        #se obtiene la fecha maxima de entrega (1 dia mas)
       totalpagar=0
       
       ######## datos para tabla pedidos ########
    
       cantidades=[]
       preciosxcantidad=[]
       codigosproducto=[]
       descripciones=[]
       precios=[]
       
       for i in ped:
           cantidad=0
           precioxcantidad=0
           codigoproducto=0
           descripcion=""
           precioprod=0

           if i.isdigit():
               cantidad = ped[i]["cantidad"]
               cantidades.append(cantidad)
               
               precioprod = ped[i]["precio"]
               precios.append(precioprod)
               
               precioxcantidad = cantidad*precioprod
               preciosxcantidad.append(precioxcantidad)
               
               codigoproducto = ped[i]["codigo"]
               codigosproducto.append(codigoproducto)
               
               descripcion = ped[i]["descripcion"]
               descripciones.append(descripcion)
               
               totalpagar = totalpagar + precioxcantidad
       
       print("cantidades",cantidades)
       print("preciosxcantidad",preciosxcantidad)
       print("codigosproducto",codigosproducto)
       print("descripciones",descripciones)
       print("precios",precios)
       print("totalpagar",totalpagar)
       
       
       ######## Datos que se insertaran en la tabla pedidos: ########
    
       pedidoCompleto = Pedido(identificacion=identificacion,nombres=nombres,
                               apellidos=apellidos,nombrenegocio=nombrenegocio,direccion=direccion,
                               ciudad=ciudad,barrio=barrio,correo=correo,celular=celular,fechapedido=fechapedido,
                               fechamaxentrega=fechamaxentrega,totalpagar=totalpagar)
       db.session.add(pedidoCompleto)
       db.session.commit()
       print(pedidoCompleto)
       print("pedido agregado")
       
       maxIdPedido = max_id_pedidos()           #para poder incrementar el id en la bd
       print("max id pedidos:",maxIdPedido)
       idpedido = maxIdPedido
    
       ############ DATOS QUE SE VAN A ENVIAR AL PROVEEDOR: ############   
       TextoPedUsuario.textoPedidoUsuario+= f'<code><b>• Id pedido:</b></code>{idpedido}\n'
       TextoPedUsuario.textoPedidoUsuario+= f'<code><b>Identificacion:</b></code>{identificacion}\n'
       TextoPedUsuario.textoPedidoUsuario+= f'<code><b>Nombres:</b></code>{nombres}\n'
       TextoPedUsuario.textoPedidoUsuario+= f'<code><b>Apellidos:</b></code>{apellidos}\n'
       TextoPedUsuario.textoPedidoUsuario+= f'<code><b>Nombre negocio:</b></code>{nombrenegocio}\n'
       TextoPedUsuario.textoPedidoUsuario+= f'<code><b>Direccion:</b></code>{direccion}\n'
       TextoPedUsuario.textoPedidoUsuario+= f'<code><b>Ciudad:</b></code>{ciudad}\n'
       TextoPedUsuario.textoPedidoUsuario+= f'<code><b>Barrio:</b></code>{barrio}\n'
       TextoPedUsuario.textoPedidoUsuario+= f'<code><b>Correo:</b></code>{correo}\n'
       TextoPedUsuario.textoPedidoUsuario+= f'<code><b>Celular:</b></code>{celular}\n'
       TextoPedUsuario.textoPedidoUsuario+= f'<code><b>Fecha pedido:</b></code>{fechapedido}\n'
       TextoPedUsuario.textoPedidoUsuario+= f'<code><b>Fecha max entrega:</b></code>{fechamaxentrega}\n'
       TextoPedUsuario.textoPedidoUsuario+= f'<code><b>Total a pagar:</b></code>{totalpagar}\n'
    
       #Calcula maximo id de las ordenes:
       maxIdOrden = max_id_ordenes()            #para poder incrementar el id en la bd
       print("max id ordenes:",maxIdOrden)
       idorden = maxIdOrden + 1
    
       #for para ir agregando cada orden con el mismo numero de pedido:
       j=0
       tam=len(codigosproducto)
       while(j<tam):
           ordenfinal={}
           ordenfinal["idorden"] = idorden
           ordenfinal["idpedido"] = idpedido
           ordenfinal["codigo"] = str(codigosproducto[j])
           ordenfinal["descripcion"] = descripciones[j]
           ordenfinal["precio"] = precios[j]
           ordenfinal["cantidad"] = cantidades[j]
           ordenfinal["precioxcantidad"] = preciosxcantidad[j]
           ############ DATOS QUE SE VAN A ENVIAR AL PROVEEDOR ############
        
           if(j==0):
               TextoPedUsuario.textoPedidoUsuario += '\n<u><b>------------------</b></u> \n\n'
               TextoPedUsuario.textoPedidoUsuario += '<u><b>Datos de la Orden:</b></u> \n'
           
           TextoPedUsuario.textoPedidoUsuario+= f'<code><b>• Id Orden:</b></code>{ordenfinal["idorden"]}\n'
           TextoPedUsuario.textoPedidoUsuario+= f'<code><b>Id Pedido:</b></code>{ordenfinal["idpedido"]}\n'
           TextoPedUsuario.textoPedidoUsuario+= f'<code><b>Codigo del producto:</b></code>{ordenfinal["codigo"]}\n'
           TextoPedUsuario.textoPedidoUsuario+= f'<code><b>Descripcion del producto:</b></code>{ordenfinal["descripcion"]}\n'
           TextoPedUsuario.textoPedidoUsuario+= f'<code><b>Precio:</b></code>{ordenfinal["precio"]}\n'
           TextoPedUsuario.textoPedidoUsuario+= f'<code><b>Cantidad:</b></code>{ordenfinal["cantidad"]}\n'
           TextoPedUsuario.textoPedidoUsuario+= f'<code><b>Precio X Cantidad:</b></code>{ordenfinal["precioxcantidad"]}\n\n'

           ######## Datos que se insertaran en la tabla ordenes: ########
           
           orden = Orden(idpedido=idpedido,codigo=str(codigosproducto[j]),descripcion=descripciones[j],
                         precio=precios[j],cantidad=cantidades[j],precioxcantidad=preciosxcantidad[j])
           db.session.add(orden)
           db.session.commit()
           print(orden)
           print("orden agregada")
           
           idorden=idorden+1
           
           j=j+1
           
           if(j>=tam):
               #Se envia mensaje al grupo de Telegram del proveedor con el pedido correspondiente:
               bot.send_message(-860836322, TextoPedUsuario.textoPedidoUsuario,parse_mode="html")
               #Se reinicia el texto del pedido, para asi poder tomar uno nuevo:
               TextoPedUsuario.textoPedidoUsuario = '<u><b>Datos Pedido:</b></u> \n'
    
               
       print("PedidoListo")
       msgid = usuariosAct[chatID]["chatid"]
       print("msgid:",msgid)
       bot.send_message(msgid, "<u><b>Pedido realizado con exito!</b></u>",parse_mode="html")
        
       markup= ReplyKeyboardMarkup(one_time_keyboard=True,
                                   input_field_placeholder="Pulsa un boton",
                                   resize_keyboard=True)
       markup.add("Realizar pedido","Salir")
        
       #preguntamos por la accion:
       msg = bot.send_message(msgid,"Necesitas algo mas?",reply_markup=markup)
            
       #se le dice al bot el paso a seguir:     
       bot.register_next_step_handler(msg,realizar_pedido)        
       
       del usuariosAct[chatID]
       print("se borro un usuario:",usuariosAct)
       
       return pedidoCliente
       
    
    if request.method == 'GET':
        
        return "pedido no recibido"


# MAIN:
if __name__ == '__main__':
    
    # Blueprints
    web_server.register_blueprint(mainP, url_prefix='/prod')   #productos
    web_server.register_blueprint(mainO, url_prefix='/ord')   #orden
    web_server.register_blueprint(mainPe, url_prefix='/ped')   #pedido
    web_server.register_blueprint(mainC, url_prefix='/cli')   #clientes
    
    print("INICIANDO BOT...")
    
    #Se elimina cualquier webhook que pueda estar asociado al bot previamente:
    bot.remove_webhook() 
    
    #Pequeña pausa para eliminar el webhook:
    time.sleep(1)
    
    #Se define y asigna el webhook mediante el cual, va a recibir updates el bot:
    bot.set_webhook(url=f"{webURL}") 
   
    
    web_server.run()
    