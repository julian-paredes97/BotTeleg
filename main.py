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
from controladores.Producto import mainP , get_productos, update_cantidad_producto
from controladores.ProductosxPedido import mainPxP
from controladores.Pedido import mainPe
from controladores.Cliente import mainC , datos_cliente
from modelos.ModeloPedido import Pedido
from modelos.ModeloProductosxPedido import ProductoxPedido
from modelos.ModeloCliente import Cliente , format_cliente
from controladores.Helpers import max_id_pedidos, max_id_productosxpedido , TextoPedUsuario , TextoPedcliente, fecha_actual, fecha_max_entrega


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
#que posteriormente se enviaran al cliente:
TextoPedcliente.textoPedidoCliente = '<u><b>Datos Pedido:</b></u> \n'
#Clase en la que guardaremos el texto con los datos del pedido del usuario
#que posteriormente se enviaran al proveedor:
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
    markup.add("Realizar pedido","Contactenos","Ayuda","Salir")
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
        markup.add("Realizar pedido","Contactenos","Ayuda","Salir")
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
        
    if message.text.lower()=="contactenos":
        
        markup= ReplyKeyboardMarkup(one_time_keyboard=True,
                                    input_field_placeholder="Pulsa un boton",
                                    resize_keyboard=True)
        markup.add("Realizar pedido","Salir")
        
        #enviar mensaje con informacion del proveedor:
        
        textContacto = f'<b>Encuentranos en Instagram como:</b> @distriromel\n'
        textContacto += f'<b>Nuestros horarios de atencion son:</b>\n'
        textContacto += f'-Lunes a Viernes de 7:00-16:30\n'
        textContacto += f'-Sabados de 7:00-15:00\n'
        textContacto += f'<b>Nos encontramos ubicados en:</b>\n'
        textContacto += f'Carrera 2N #46CN-06, Cali, Valle del Cauca, Colombia\n'
        textContacto += f'<b>Para mayor informacion comuniquese al:</b>\n'
        textContacto += f'+57 310 5946667\n'
        textContacto += f'<b>O escribanos un correo a:</b>\n'
        textContacto += f'distriromel@outlook.com'
        
        msg = bot.send_message(message.chat.id,textContacto, parse_mode="html",reply_markup=markup)
        bot.register_next_step_handler(msg,realizar_pedido)
        
    
    if message.text.lower()=="ayuda":
        markup= ReplyKeyboardMarkup(one_time_keyboard=True,
                                    input_field_placeholder="Pulsa un boton",
                                    resize_keyboard=True)
        markup.add("Realizar pedido","Salir")
       
        #videos de ayuda para el cliente:
        textoayuda1 = f'<b>¿Cómo registrarse?: </b>\n'
        textoayuda1 += f'https://youtu.be/xCOB9ThNJok \n'
        textoayuda2 = f'<b>¿Cómo realizar un pedido?: </b>\n'
        textoayuda2 += f'https://youtu.be/wXy3EbPLhzw \n'
        
        msg = bot.send_message(message.chat.id,textoayuda1, parse_mode="html",reply_markup=markup)
        msg = bot.send_message(message.chat.id,textoayuda2, parse_mode="html",reply_markup=markup)
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
            web_app_url = "https://inquisitive-puffpuff-273fd1.netlify.app"
            keyboard = telebot.types.InlineKeyboardMarkup()
            markup2=telebot.types.InlineKeyboardButton(text="REALIZAR PEDIDO :)",web_app=WebAppInfo(url=web_app_url))
            keyboard.add(markup2) #se añade boton inline que permitira abrir la WebApp
            msg=bot.send_message(message.chat.id, text=f"Hola {nombrecompleto}, que vas a pedir el dia de hoy?", reply_markup=keyboard)
            print("MSG:",msg)
            #####   ABRIR WEBAPP:   #####
            
        if exists == "False":
            """almacena la nueva cedula y pregunta nombres del usuario."""
            print("entre")
            
            usuarios[message.chat.id]={}
            usuarios[message.chat.id]["identificacion"]=message.text
            markup = ForceReply()  # para responder citado
            bot.send_message(message.chat.id, "No te encuentras registado en nuestra base de datos, por favor ingresa los siguientes datos personales:")
            msg = bot.send_message(message.chat.id, "Nombre completo (ej: Juan David):",reply_markup=markup)
            bot.register_next_step_handler(msg,preguntar_primer_nombre)
            
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
        print("Data:",data)
        print("chatid:",chatid)
        print("identificacion:",identificacion)
        
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
       
       #### PRODUCTOS: ######
       
       #Trae los productos que hay actualmente en la BD:
       productosActuales = get_productos()
       productosActuales = productosActuales["productos"]
       print("productosActuales:\n", productosActuales)
       
       
       #### PRODUCTOS: ######
       
       
       ######## datos para tabla pedidos ########
       identificacion = 0
       nombrenegocio = ""
       
       chatID = ped["datosUsuario"]["id"]
       chatID = str(chatID)
       print("CHATID:",chatID)
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
       
       ######## datos para tabla pedidos y ordenes ########
    
       cantidades=[]
       preciosxcantidad=[]
       codigosproducto=[]
       descripciones=[]
       precios=[]
       #datos para comparar con los de lea BD:
       sinStock = []
       
       for i in ped:
           cantidad=0
           precioxcantidad=0
           codigoproducto=0
           descripcion=""
           precioprod=0
           #datos para comparar con los de la BD:
           cantidadBD = 0

           if i.isdigit():
               
               cantidad = ped[i]["cantidad"]
               precioprod = ped[i]["precio"]
               precioxcantidad = cantidad*precioprod
               codigoproducto = ped[i]["codigo"]
               descripcion = ped[i]["descripcion"]
               
               #For que permite validar la cantidad de productos disponibles en la BD:
               for j in productosActuales:
                   if j["codigo"] == codigoproducto:
                       cantidadBD = j["cantidad"]
                       
                       if cantidadBD < 100:
                           #Se envia mensaje al grupo de Telegram del proveedor para avisar que hay escasez de X producto:
                           bot.send_message(-860836322,text=f"<b>• Hay pocas unidades de {descripcion}, codigo del producto: {codigoproducto}</b>", parse_mode="html")
                       
                       if ((cantidad > cantidadBD) or (cantidadBD == 0)): 
                           #coloca todo en 0s para que no cuente en el pedido, ya que no esta disponible
                           print("No hay en stock")
                           cantidades.append(0)
                           precios.append(0)
                           preciosxcantidad.append(0)
                           codigosproducto.append(codigoproducto)
                           sinStock.append(codigoproducto)
                           descripciones.append(descripcion)
                           totalpagar = totalpagar + 0

                       if cantidadBD >= cantidad:
                           update_cantidad_producto(codigoproducto,cantidad) #resta en la BD la cantidad en stock
                           cantidades.append(cantidad)
                           precios.append(precioprod)
                           preciosxcantidad.append(precioxcantidad)
                           codigosproducto.append(codigoproducto)
                           descripciones.append(descripcion)
                           totalpagar = totalpagar + precioxcantidad
       
       print("cantidades",cantidades)
       print("preciosxcantidad",preciosxcantidad)
       print("codigosproducto",codigosproducto)
       print("descripciones",descripciones)
       print("precios",precios)
       print("totalpagar",totalpagar)
       
       
       ######## Datos que se insertaran en la tabla pedidos: ########
    
       pedidoCompleto = Pedido(identificacion=identificacion,fechapedido=fechapedido,
                               fechamaxentrega=fechamaxentrega,totalpagar=totalpagar)
       db.session.add(pedidoCompleto)
       db.session.commit()
       print(pedidoCompleto)
       print("pedido agregado")
       
       maxIdPedido = max_id_pedidos()           #para poder incrementar el id en la bd
       print("max id pedidos:",maxIdPedido)
       idpedido = maxIdPedido
    
       ############ DATOS QUE SE VAN A ENVIAR AL PROVEEDOR: ############   
       TextoPedUsuario.textoPedidoUsuario+= f'<b>• Id pedido: </b>{idpedido}\n'
       TextoPedUsuario.textoPedidoUsuario+= f'<b>Identificacion: </b>{identificacion}\n'
       TextoPedUsuario.textoPedidoUsuario+= f'<b>Nombres: </b>{nombres}\n'
       TextoPedUsuario.textoPedidoUsuario+= f'<b>Apellidos: </b>{apellidos}\n'
       TextoPedUsuario.textoPedidoUsuario+= f'<b>Nombre negocio: </b>{nombrenegocio}\n'
       TextoPedUsuario.textoPedidoUsuario+= f'<b>Direccion: </b>{direccion}\n'
       TextoPedUsuario.textoPedidoUsuario+= f'<b>Ciudad: </b>{ciudad}\n'
       TextoPedUsuario.textoPedidoUsuario+= f'<b>Barrio: </b>{barrio}\n'
       TextoPedUsuario.textoPedidoUsuario+= f'<b>Correo: </b>{correo}\n'
       TextoPedUsuario.textoPedidoUsuario+= f'<b>Celular: </b>{celular}\n'
       TextoPedUsuario.textoPedidoUsuario+= f'<b>Fecha pedido: </b>{fechapedido}\n'
       TextoPedUsuario.textoPedidoUsuario+= f'<b>Fecha max entrega: </b>{fechamaxentrega}\n'
       TextoPedUsuario.textoPedidoUsuario+= f'<b>Total a pagar: $</b>{totalpagar}\n'
       
       ############ DATOS QUE SE VAN A ENVIAR AL CLIENTE: ############   
       TextoPedcliente.textoPedidoCliente+= f'<b>• Id pedido: </b>{idpedido}\n'
       TextoPedcliente.textoPedidoCliente+= f'<b>Identificacion: </b>{identificacion}\n'
       TextoPedcliente.textoPedidoCliente+= f'<b>Nombres: </b>{nombres}\n'
       TextoPedcliente.textoPedidoCliente+= f'<b>Apellidos: </b>{apellidos}\n'
       TextoPedcliente.textoPedidoCliente+= f'<b>Nombre negocio: </b>{nombrenegocio}\n'
       TextoPedcliente.textoPedidoCliente+= f'<b>Direccion: </b>{direccion}\n'
       TextoPedcliente.textoPedidoCliente+= f'<b>Ciudad: </b>{ciudad}\n'
       TextoPedcliente.textoPedidoCliente+= f'<b>Barrio: </b>{barrio}\n'
       TextoPedcliente.textoPedidoCliente+= f'<b>Correo: </b>{correo}\n'
       TextoPedcliente.textoPedidoCliente+= f'<b>Celular: </b>{celular}\n'
       TextoPedcliente.textoPedidoCliente+= f'<b>Fecha pedido: </b>{fechapedido}\n'
       TextoPedcliente.textoPedidoCliente+= f'<b>Fecha max entrega: </b>{fechamaxentrega}\n'
       TextoPedcliente.textoPedidoCliente+= f'<b>Total a pagar: $</b>{totalpagar}\n'
    
       #Calcula maximo id de las ordenes/productosxpedido:
       maxIdproductosxpedido = max_id_productosxpedido()            #para poder incrementar el id en la bd
       print("max id productosxpedido:",maxIdproductosxpedido)
       idproductoxpedido = maxIdproductosxpedido + 1
    
       #for para ir agregando cada orden con el mismo numero de pedido:
       j=0
       tam=len(codigosproducto)
       while(j<tam):
           
           ordenfinal={}
           codigoProd = str(codigosproducto[j])
           
           ordenfinal["idproductoxpedido"] = idproductoxpedido
           ordenfinal["idpedido"] = idpedido
           ordenfinal["codigo"] = codigoProd
           ordenfinal["descripcion"] = descripciones[j]
           ordenfinal["precio"] = precios[j]
           ordenfinal["cantidad"] = cantidades[j]
           ordenfinal["precioxcantidad"] = preciosxcantidad[j]
           
           ############ DATOS QUE SE VAN A ENVIAR AL PROVEEDOR ############
           
           if(j==0):
               TextoPedUsuario.textoPedidoUsuario += '\n<u><b>------------------</b></u> \n\n'
               TextoPedUsuario.textoPedidoUsuario += '<u><b>Datos de la Orden:</b></u> \n'
               TextoPedcliente.textoPedidoCliente += '\n<u><b>------------------</b></u> \n\n'
               TextoPedcliente.textoPedidoCliente += '<u><b>Listado de Productos:</b></u> \n'
           
           if codigoProd in sinStock:
               print("codigoProd:",codigoProd)
               print("sinStock:",sinStock)
               TextoPedUsuario.textoPedidoUsuario+= f'<b>- En el momento no tenemos disponible este producto:</b>\n'
               TextoPedcliente.textoPedidoCliente+= f'<b>- En el momento no tenemos disponible este producto:</b>\n'
           
           ####  DATOS PROVEEDOR:  ####
           TextoPedUsuario.textoPedidoUsuario+= f'<b>• Id Orden: </b>{ordenfinal["idproductoxpedido"]}\n'
           TextoPedUsuario.textoPedidoUsuario+= f'<b>Id Pedido: </b>{ordenfinal["idpedido"]}\n'
           TextoPedUsuario.textoPedidoUsuario+= f'<b>Codigo del producto: </b>{ordenfinal["codigo"]}\n'
           TextoPedUsuario.textoPedidoUsuario+= f'<b>Descripcion del producto: </b>{ordenfinal["descripcion"]}\n'
           TextoPedUsuario.textoPedidoUsuario+= f'<b>Precio: $</b>{ordenfinal["precio"]}\n'
           TextoPedUsuario.textoPedidoUsuario+= f'<b>Cantidad: </b>{ordenfinal["cantidad"]}\n'
           TextoPedUsuario.textoPedidoUsuario+= f'<b>Precio X Cantidad: $</b>{ordenfinal["precioxcantidad"]}\n\n'
           ####  DATOS CLIENTE:  ####
           TextoPedcliente.textoPedidoCliente+= f'<b>Codigo del producto: </b>{ordenfinal["codigo"]}\n'
           TextoPedcliente.textoPedidoCliente+= f'<b>Descripcion del producto: </b>{ordenfinal["descripcion"]}\n'
           TextoPedcliente.textoPedidoCliente+= f'<b>Precio: $</b>{ordenfinal["precio"]}\n'
           TextoPedcliente.textoPedidoCliente+= f'<b>Cantidad: </b>{ordenfinal["cantidad"]}\n'
           TextoPedcliente.textoPedidoCliente+= f'<b>Precio X Cantidad: $</b>{ordenfinal["precioxcantidad"]}\n\n'
           

           ######## Datos que se insertaran en la tabla productosxpedido: ########
           
           prodxped = ProductoxPedido(idpedido=idpedido,codigo=str(codigosproducto[j]),
                         precio=precios[j],cantidadped=cantidades[j],precioxcantidadped=preciosxcantidad[j])
           db.session.add(prodxped)
           db.session.commit()
           print(prodxped)
           print("productoxpedido agregado")
           
           idproductoxpedido=idproductoxpedido+1
           
           j=j+1
           
           if(j>=tam):
               print("PedidoListo")
               msgid = usuariosAct[chatID]["chatid"]
               print("msgid:",msgid)
               
               #Se envia mensaje al grupo de Telegram del proveedor con el pedido correspondiente:
               bot.send_message(-860836322, TextoPedUsuario.textoPedidoUsuario,parse_mode="html")
               #Se envia mensaje al cliente con el pedido correspondiente:
               bot.send_message(msgid, TextoPedcliente.textoPedidoCliente,parse_mode="html")
               bot.send_message(msgid, "<u><b>Pedido realizado con exito!</b></u>",parse_mode="html")
               #Se reinicia el texto del pedido, para asi poder tomar uno nuevo:
               TextoPedUsuario.textoPedidoUsuario = '<u><b>Datos Pedido:</b></u> \n'
               TextoPedcliente.textoPedidoCliente = '<u><b>Datos Pedido:</b></u> \n'
    
               
        
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
    web_server.register_blueprint(mainPe, url_prefix='/ped')   #pedido
    web_server.register_blueprint(mainC, url_prefix='/cli')   #clientes
    web_server.register_blueprint(mainPxP, url_prefix='/pxp')   #productosxpedido
    
    print("INICIANDO BOT...")
    
    #Se elimina cualquier webhook que pueda estar asociado al bot previamente:
    bot.remove_webhook() 
    
    #Pequeña pausa para eliminar el webhook:
    time.sleep(1)
    
    #Se define y asigna el webhook mediante el cual, va a recibir updates el bot:
    bot.set_webhook(url=f"{webURL}") 
   
    
    web_server.run()
    