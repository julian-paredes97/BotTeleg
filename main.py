from config import *
import telebot # para manejar la api de telegram
from telebot.types import ReplyKeyboardMarkup #para crear botones
from telebot.types import ForceReply #para citar un mensaje
from telebot.types import ReplyKeyboardRemove # para eliminar botones
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton #para los botones para abrir la webapp
from flask import Flask, request, Blueprint #para crear el servidor web
import datetime
from datetime import datetime
import time
import requests
import json
#from pyngrok import ngrok,conf # para crear el tunel entre el serv web local y el otro

from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from controladores.Producto import mainP
from controladores.Orden import mainO
from controladores.Pedido import mainPe
from controladores.Cliente import mainC #, get_cliente, get_clientes
from controladores.Peticiones import mainPet #, recibePedido
#from modelos.ModeloCliente import Cliente, format_cliente

#esto neh por ahora:
#from controladores.Producto import mainP
#from controladores.Orden import mainO
#from controladores.Pedido import mainPe
#from controladores.Cliente import mainC
#from controladores.Webhook import mainW


#instanciamos el bot de telegram
bot = telebot.TeleBot(TELEGRAM_TOKEN)

#instanciamos el servidor web de flask:
web_server= Flask(__name__)

#esto es mio:
web_server.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:root123456@postgresdb.cadpgx7qqz5d.us-east-1.rds.amazonaws.com/postgres"
web_server.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db=SQLAlchemy(web_server)
CORS(web_server)
#esto es mio#


# #aber si sirve esta mamada:
# async def get_cliente2(identificacion):
#     cliente = Cliente.query.filter_by(identificacion=identificacion).one()
#     formatted_cliente = format_cliente(cliente)
#     return {formatted_cliente}

# def validar_cedula(cedula):
#     ced = cedula
#     if get_cliente(str(ced)):
#         return True
#     else:
#         return False



#esto es mio#


#markup para llamar la webapp
def gen_markup():
    #markup = quick_markup({"inline_keyboard":[[{"text":"My web app","web_app":{"url":"https://snazzy-tartufo-5f17da.netlify.app"}}]]})
    
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    
    #markup.add(InlineKeyboardButton("Yes", callback_data="cb_yes"),
    boton=InlineKeyboardButton(text= "realizar pedido",web_app="https://snazzy-tartufo-5f17da.netlify.app")
    markup.add(boton)
    #markup.add(InlineKeyboardButton("Realizar pedido", web_app = "url":"https://snazzy-tartufo-5f17da.netlify.app"))
    #text":"My web app","web_app":{"url":"https://snazzy-tartufo-5f17da.netlify.app"
                               #InlineKeyboardButton("No", callback_data="cb_no"))
    return markup



#gestiona las peticiones POST enviadas al servidor web
@web_server.route('/', methods=['POST'])
def webhook():
    #si el post recibido es un JSON:
    if request.headers.get("content-type") == "application/json":
        update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
        #print("update:",update)
        bot.process_new_updates([update])
        return "OK",200

#posibles saludos por parte del usuario
saludo=["hola","hey","buenas","buen dia","buena tarde","quisiera hacer un pedido","como esta","saludos"]


#variable global en la que guardaremos los datos del usuario
usuarios = {}

#responde a los comandos /start /help y /ayuda
#@bot.message_handler(commands=['start','help','ayuda'])
@bot.message_handler(commands=['start'])
def cmd_start(message):
    """ Muestra las acciones disponibles. """
    #markup = ReplyKeyboardRemove()
    #bot.send_message(message.chat.id,"Usa el comando/alta para introducir tus datos", reply_markup=markup)
    bot.send_message(message.chat.id,"Buen dia, se ha comunicado con Distri Romel Sas")
    
    #definimos dos botones
    markup= ReplyKeyboardMarkup(one_time_keyboard=True,
                                input_field_placeholder="Pulsa un boton",
                                resize_keyboard=True)
    markup.add("Realizar pedido","Ayuda","Salir")
    #preguntamos por la accion
    msg = bot.send_message(message.chat.id, "Como podemos ayudarle?",reply_markup=markup)
    bot.register_next_step_handler(msg,realizar_pedido)


### borrar esto despues #####
# @bot.message_handler(commands=['alta'])
# def cmd_alta(message):
#    markup= ForceReply()
#    msg = bot.send_message(message.chat.id,"como te llamas?",reply_markup=markup)
#    bot.register_next_step_handler(msg,preguntar_edad)

### borrar esto despues #####




#responde al comando /alta
#@bot.message_handler(commands=['alta'])
@bot.message_handler(content_types=["text"])
#def cmd_alta(message):
def realizar_pedido(message):
    #"""Pregunta el nombre del usuario."""
    """Pregunta la cedula del usuario."""
    
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
        #msg = bot.send_message(message.chat.id,reply_markup=markup)
        bot.register_next_step_handler(msg,realizar_pedido)
    
    if message.text=="Salir":
        markup= ReplyKeyboardRemove()
        bot.send_message(message.chat.id,"Gracias por comunicarse con nosotros, Hasta luego",reply_markup=markup)
        
    #msg = bot.send_message(message.chat.id, "como te llamas?", reply_markup=markup)
    
    #requests.get('https://api.telegram.org/bot5489576102:AAEppJsThPctLwr4iEp9C5iyGMMdd9JHUXk/sendMessage?chat_id=2089210179&text=Hello User&reply_markup={"inline_keyboard":[[{"text":"My web app","web_app":{"url":"https://snazzy-tartufo-5f17da.netlify.app"}}]]}')

    #validar si la cedula ya existe en la base de datos,
    #si existe, se procede a realizar el pedido,
    #sino se procede a preguntarle todos los datos. 
    
def corroborar_cedula(message):
    #print("egg",message)
    if not message.text.isdecimal():
        #informamos error y volvemos a preguntar
        # markup = ForceReply()  # para responder citado
        #markup = ReplyKeyboardRemove()
        msg = bot.send_message(message.chat.id, "ERROR: Debes indicar un numero. \n cual es tu cedula?") #,reply_markup=markup)
        bot.register_next_step_handler(msg,corroborar_cedula)
    
    
    else:
        #toca verificar aca adentro que el usuario este en la bd, si esta
        #se procede a hacer pedido, sino se piden datos al usuario
        #aberlo = await async get_cliente2(str(1144094441))
        
        cedula= message.text
        # chatid= message.chat.id
        bot.send_message(message.chat.id, "Validando informacion...")
        # url = f'https://api.telegram.org/bot5489576102:AAEppJsThPctLwr4iEp9C5iyGMMdd9JHUXk/sendMessage?chat_id={chatid}&text=Validando informacion...'
        #     #payload = {'chat_id':chat_id,'text':text}
    
        #     #r= requests.post(url)
        # requests.post(url)
        
        cliente = requests.get(f"http://localhost:5000/cli/clientes/{cedula}") #funciona
        cli = cliente.json()
        existe = cli['exists']
        
        print("existe o nel:",existe)
        
        if existe=="True":
            nombre = cli['event']['nombre1']
            nombre = nombre.lower()
            chatId = message.chat.id   #2089210179
            print("truesito pa")
            
            
            
            
            #hasta aqui fino
            linkBot = 'https://api.telegram.org/bot5489576102:AAEppJsThPctLwr4iEp9C5iyGMMdd9JHUXk'
            markupWebApp = 'reply_markup={"inline_keyboard":[[{"text":"My web app","web_app":{"url":"https://snazzy-tartufo-5f17da.netlify.app"}}]]}'
            
            requests.get(f'{linkBot}/sendMessage?chat_id={chatId}&text=Hello User&{markupWebApp}')
            
            #hasta aqui fino
            
            #bot.send_message(message.chat.id, f"hola {nombre}, que vas a pedir el dia de hoy?",reply_markup=gen_markup())
            #bot.register_next_step_handler(msg,recibe_pedido)
        
        else:
            print("im in")
            """almacena la nueva cedula y pregunta nombres del usuario."""
            usuarios[message.chat.id]={}
            usuarios[message.chat.id]["identificacion"]=message.text
            #markup = ReplyKeyboardRemove()
            bot.send_message(message.chat.id, "No te encuentras registado en nuestra base de datos, por favor ingresa los siguientes datos personales:")
            msg = bot.send_message(message.chat.id, "Nombre completo (ej: Juan David):")#,reply_markup=markup)
            #bot.register_next_step_handler(msg,preguntar_primerNombre)
            
            bot.register_next_step_handler(msg,preguntar_primer_nombre)
        
            
        #nombre = cli['event']['nombre1']
        
        #aberlo = get_cliente(1144094441)
        
        #tempc= ced['event']['nombre1']
        
        #aberlo = get_clientes()
        
        #print("cliente",cli)
        #print("existe o nel:",existe)
        #print("nombre cliente:",nombre)
        
        #print("noj", json.dumps(tempc))
        
        #aber=validar_cedula(str(message.text))
        #print("ABER:",aber)
        #print("message texto:",message.text)
        
        # if (validar_cedula(str(message.text))==True):
        #     #"""pregunta primer nombre del usuario."""
        #     markup = ReplyKeyboardRemove()
        #     msg = bot.send_message(message.chat.id, "como es tu primer nombre?",reply_markup=markup)
        #     bot.register_next_step_handler(msg,preguntar_primerNombre)
        #     #bot.register_next_step_handler(msg,preguntar_primerNombre)
        # else:
        #     print("F MENOR")
        #     #bot.send_message(message.chat.id, "Paila menor")

def preguntar_primer_nombre(message):
    """almacena nombres del usuario y pregunta apellidos."""
    nombres = message.text
    nombres = nombres.split()
    print("WEEE:",nombres)
    print("tipo",type(nombres))
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
    
    #toca ir almacenando los datos en un arreglo    
        
        
    markup = ForceReply()  # para responder citado
    msg = bot.send_message(message.chat.id,"Cuales son sus apellidos?:", reply_markup=markup)
    bot.register_next_step_handler(msg,preguntar_apellidos)

def preguntar_apellidos(message):
    """almacena apellidos del usuario y pregunta nombre del negocio."""
    apellidos = message.text
    apellidos = apellidos.split()
    print("WEEE:",apellidos)
    print("tipo",type(apellidos))
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
    
    #toca ir almacenando los datos en un arreglo    
    
    
    markup = ForceReply()  # para responder citado
    msg = bot.send_message(message.chat.id,"Por favor ingrese el nombre de su negocio", reply_markup=markup)
    bot.register_next_step_handler(msg,preguntar_nombre_negocio)


def preguntar_nombre_negocio(message):
    """almacena nombre del negocio y pregunta direccion."""
    nombreNegocio = message.text 
    print("nombreNegocio:",nombreNegocio)
    usuarios[message.chat.id]["nombrenegocio"] = nombreNegocio
    #toca ir almacenando los datos en un arreglo
    
    markup = ForceReply()  # para responder citado
    msg = bot.send_message(message.chat.id,"Por favor ingrese su direccion", reply_markup=markup)
    bot.register_next_step_handler(msg,preguntar_direccion)
    
def preguntar_direccion(message):
    """almacena direccion y pregunta correo del usuario."""
    direccion = message.text
    print("direccion:",direccion)
    #toca ir almacenando los datos en un arreglo
    usuarios[message.chat.id]["direccion"] = direccion
    
    markup = ForceReply()  # para responder citado
    msg = bot.send_message(message.chat.id,"Por favor ingrese su correo electronico:", reply_markup=markup)
    bot.register_next_step_handler(msg,preguntar_correo)
    
def preguntar_correo(message):
    """almacena correo y pregunta celular del usuario."""
    correo = message.text
    print("correo:",correo)
    #toca ir almacenando los datos en un arreglo
    usuarios[message.chat.id]["correo"] = correo
    
    markup = ForceReply()  # para responder citado
    msg = bot.send_message(message.chat.id,"Por favor ingrese el numero de su celular", reply_markup=markup)
    bot.register_next_step_handler(msg,preguntar_celular)
 
def preguntar_celular(message):
    """almacena celular y pregunta barrio del usuario."""
    cel = message.text
    print("celular:",cel)
    #toca ir almacenando los datos en un arreglo
    usuarios[message.chat.id]["celular"] = cel
    
    markup = ForceReply()  # para responder citado
    msg = bot.send_message(message.chat.id,"Por favor ingrese el barrio", reply_markup=markup)
    bot.register_next_step_handler(msg,preguntar_barrio)

def preguntar_barrio(message):
    """almacena barrio y pregunta ciudad del usuario."""
    barrio = message.text
    print("barrio:",barrio)
    #toca ir almacenando los datos en un arreglo
    usuarios[message.chat.id]["barrio"] = barrio
    
    markup = ForceReply()  # para responder citado
    msg = bot.send_message(message.chat.id,"Por favor ingrese su ciudad", reply_markup=markup)
    bot.register_next_step_handler(msg,guardar_datos_usuario)
  
# def preguntar_ciudad(message):
#     """almacena ciudad y pregunta ciudad del usuario."""
#     markup = ForceReply()  # para responder citado
#     msg = bot.send_message(message.chat.id,"Por favor ingrese su ciudad", reply_markup=markup)
#     bot.register_next_step_handler(msg,fecha_creacion)    
    
# def fecha_creacion(message):
#     """almacena ciudad y obtiene fecha de creacion del usuario."""
#     #markup = ForceReply()  # para responder citado
   
#     #msg="fecha creacion"
    
#     now = datetime.now()
#     date_time = now.strftime("%y/%m/%d")
#     #return str(date_time)
#     msg = bot.send_message(message.chat.id,str(date_time))
#     bot.register_next_step_handler(msg,guardarDatosUsuario)
    
#def guardarDatosUsuario(message):
def guardar_datos_usuario(message):
    """almacena ciudad y obtiene fecha de creacion del usuario."""
    ciudad = message.text
    print("ciudad:",ciudad)
    #para la fecha de creacion:
    
    now = datetime.now()
    date_time = now.strftime("%y-%m-%d")
    fecha= date_time
    print("fecha:",fecha)
    print("tipo de la fecha:",type(fecha))
    
    
    
    
    
    
    # now = datetime.now()
    # date_time = now.strftime("%y/%m/%d")
    # datetime_object = datetime.strptime(date_time, '%y/%m/%d')
    # # extract the time from datetime_obj

    # fecha= datetime_object.date()
    # print("fecha:",fecha)
    # print("tipo de la fecha:",type(fecha))
    
    #toca ir almacenando los datos en un arreglo
    #usuarios[message.chat.id]["ciudad"] = message.text
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
    """guarda datos del usuario en la BD."""
    r= requests.post("http://localhost:5000/cli/clientes",
                     data=json.dumps(clienteNuevo),
                     headers={"Content-Type": "application/json"})
    print(r.text)
    
    #cliente = requests.get(f"http://localhost:5000/cli/clientes/{cedula}") #funciona
    #cli = cliente.json()
    
    #para borrar lo que hay en cache :
    del usuarios[message.chat.id]
    
    
    #markup = ForceReply()  # para responder citado
    #msg = bot.send_message(message.chat.id,"Datos almacenados correctamente", reply_markup=markup)
    bot.send_message(message.chat.id,"Datos almacenados correctamente")#, reply_markup=markup)
    
    #print("wee")
    #bot.register_next_step_handler(msg,preguntar_nombreNegocio)



def recibe_pedido(message):
    #recibe el pedido del cliente
    bot.send_message(message.chat.id,"que va pedir:")#, reply_markup=markup)
    
# ########################################TOdO ESTO LO COMENTO ##################################
    
    
    
    

# def preguntar_cedula(message):
#     """"Preguntar cedula al usuario"""
#     markup = ForceReply()
#     msg = bot.send_message(message.chat.id,"Cual es tu cedula?",reply_markup = markup)
#     bot.register_next_step_handler(msg,validar_cedula)

# def validar_cedula(message):
#     #istext = message.text.isdecimal() #verifica si es un digito o no
#     #print("mensaje:",message.text)
#     #print("trueORfalse:",istext)
    
#     if not message.text.isdigit():
#         #informamos error y volvemos a preguntar
#         # markup = ForceReply()  # para responder citado
#         #markup = ReplyKeyboardRemove()
#         msg = bot.send_message(message.chat.id, "ERROR: Debes indicar un numero. \n cual es tu cedula?") #,reply_markup=markup)
#         bot.register_next_step_handler(msg,validar_cedula)
    
    
#     else:
#         #markup = ReplyKeyboardRemove()
#         msg = bot.send_message(message.chat.id, "numero de cedula correcto")#,reply_markup=markup)
#         bot.register_next_step_handler(msg,preguntar_existeCedula)
#         #bot.register_next_step_handler(msg,preguntar_primerNombre)

# def preguntar_existeCedula(message):
#     print("mensaje:",message.text)
    
#     if(message.text.isdigit()):
#         msg =  bot.send_message(message.chat.id, "su cedula no se encuentra registrada,\n"
#                                 "por favor ingrese los siguientes datos: ")
#         bot.register_next_step_handler(msg,preguntar_primerNombre)
        
#     else:
#         print("FFFFFFFFF")
#     #crear if que valide si esa cedula ya existe en el backend
    
    
# def preguntar_primerNombre(message):
#     """pregunta primer nombre del usuario."""
#     #markup = ForceReply()  # para responder citado
#     msg = bot.send_message(message.chat.id,"Cual es su primer nombre? (ej: Juan)")#, reply_markup=markup)
#     bot.register_next_step_handler(msg,preguntar_segundoNombre)
    
# def preguntar_segundoNombre(message):
#     """pregunta segundo nombre del usuario."""
#     markup = ForceReply()  # para responder citado
#     msg = bot.send_message(message.chat.id,"Por favor ingrese su segundo nombre (ej: David)", reply_markup=markup)
#     bot.register_next_step_handler(msg,preguntar_primerApellido)  

# def preguntar_primerApellido(message):
#     """pregunta primer apellido del usuario."""
#     markup = ForceReply()  # para responder citado
#     msg = bot.send_message(message.chat.id,"Por favor ingrese su primer apellido", reply_markup=markup)
#     bot.register_next_step_handler(msg,preguntar_segundoApellido)  

# def preguntar_segundoApellido(message):
#     """pregunta segundo apellido del usuario."""
#     markup = ForceReply()  # para responder citado
#     msg = bot.send_message(message.chat.id,"Por favor ingrese su segundo apellido", reply_markup=markup)
#     bot.register_next_step_handler(msg,preguntar_nombreNegocio)

# def preguntar_nombreNegocio(message):
#     """pregunta segundo apellido del usuario."""
#     markup = ForceReply()  # para responder citado
#     msg = bot.send_message(message.chat.id,"Por favor ingrese el nombre de su negocio", reply_markup=markup)
#     bot.register_next_step_handler(msg,preguntar_direccion)
    
# def preguntar_direccion(message):
#     """pregunta segundo apellido del usuario."""
#     markup = ForceReply()  # para responder citado
#     msg = bot.send_message(message.chat.id,"Por favor ingrese su direccion", reply_markup=markup)
#     bot.register_next_step_handler(msg,preguntar_correo)
    
# def preguntar_correo(message):
#     """pregunta segundo apellido del usuario."""
#     markup = ForceReply()  # para responder citado
#     msg = bot.send_message(message.chat.id,"Por favor ingrese su correo electronico", reply_markup=markup)
#     bot.register_next_step_handler(msg,preguntar_celular)
 
# def preguntar_celular(message):
#     """pregunta celular del usuario."""
#     markup = ForceReply()  # para responder citado
#     msg = bot.send_message(message.chat.id,"Por favor ingrese el numero de su celular", reply_markup=markup)
#     bot.register_next_step_handler(msg,preguntar_barrio)

# def preguntar_barrio(message):
#     """pregunta barrio del usuario."""
#     markup = ForceReply()  # para responder citado
#     msg = bot.send_message(message.chat.id,"Por favor ingrese el barrio", reply_markup=markup)
#     bot.register_next_step_handler(msg,preguntar_ciudad)
  
# def preguntar_ciudad(message):
#     """pregunta ciudad del usuario."""
#     markup = ForceReply()  # para responder citado
#     msg = bot.send_message(message.chat.id,"Por favor ingrese su ciudad", reply_markup=markup)
#     bot.register_next_step_handler(msg,fecha_creacion)    
    
# def fecha_creacion(message):
#     """obtiene fecha de creacion del usuario."""
#     #markup = ForceReply()  # para responder citado
   
#     #msg="fecha creacion"
    
#     now = datetime.now()
#     date_time = now.strftime("%y/%m/%d")
#     #return str(date_time)
#     msg = bot.send_message(message.chat.id,str(date_time))
#     bot.register_next_step_handler(msg,guardarDatosUsuario)
    
# def guardarDatosUsuario(message):
#     """guarda datos del usuario en la BD."""
#     markup = ForceReply()  # para responder citado
#     #msg = bot.send_message(message.chat.id,"Datos almacenados correctamente", reply_markup=markup)
#     bot.send_message(message.chat.id,"Datos almacenados correctamente", reply_markup=markup)
    
#     #print("wee")
#     #bot.register_next_step_handler(msg,preguntar_nombreNegocio)
    
















        


# #responde a los mensajes de texto que no son comandos
# #@bot.message_handler(content_types=["text"])   #esto lo comente pilas 
# def bot_mensajes_texto(message):
#     """Gestiona los mensajes de texto recibidos"""
#     if message.text.lower() in (saludo):
#         """ Muestra las acciones disponibles. """
#         #markup = ReplyKeyboardRemove()
#         #bot.send_message(message.chat.id,"Usa el comando/alta para introducir tus datos", reply_markup=markup)
#         bot.send_message(message.chat.id,"Buen dia, se ha comunicado con Distri Romel Sas")
        
#         #definimos dos botones
#         markup= ReplyKeyboardMarkup(one_time_keyboard=True,
#                                     input_field_placeholder="Pulsa un boton",
#                                     resize_keyboard=True)
#         markup.add("Realizar pedido","Ayuda","Salir")
#         #preguntamos por la accion
#         msg = bot.send_message(message.chat.id, "Como podemos ayudarle?",reply_markup=markup)
#         bot.register_next_step_handler(msg,bot_mensajes_texto)
    
#     if message.text=="Realizar pedido":
#         #msg = bot.send_message(message.chat.id,"Por favor ingrese su numero de cedula")
#         #bot.register_next_step_handler(msg,preguntar_primerNombre)
#         """Pregunta la cedula del usuario."""
#         #markup = ForceReply()  # para responder citado
#         msg = bot.send_message(message.chat.id,"Por favor ingrese su numero de cedula")#, reply_markup=markup)
        
        
#         #msg = bot.send_message(message.chat.id, "como te llamas?", reply_markup=markup)
        
#         #requests.get('https://api.telegram.org/bot5489576102:AAEppJsThPctLwr4iEp9C5iyGMMdd9JHUXk/sendMessage?chat_id=2089210179&text=Hello User&reply_markup={"inline_keyboard":[[{"text":"My web app","web_app":{"url":"https://snazzy-tartufo-5f17da.netlify.app"}}]]}')

#         #validar si la cedula ya existe en la base de datos,
#         #si existe, se procede a realizar el pedido,
#         #sino se procede a preguntarle todos los datos. 
        
#         bot.register_next_step_handler(msg,validar_cedula)
        
#     if message.text=="Ayuda":
#         #bot.send_message(message.chat.id,"link de youtube con video explicativo")
#         # meter botones que manden despues a realizar pedido o a salir:
#         #definimos dos botones
#         markup= ReplyKeyboardMarkup(one_time_keyboard=True,
#                                     input_field_placeholder="Pulsa un boton",
#                                     resize_keyboard=True)
#         markup.add("Realizar pedido","Salir")
#         #preguntamos por la accion
#         #msg = bot.send_message(message.chat.id,reply_markup=markup)
#         #bot.register_next_step_handler(msg,preguntar_primerNombre)
#         #preguntamos por la accion
#         msg = bot.send_message(message.chat.id,"link de youtube con video explicativo",reply_markup=markup)
#         #msg = bot.send_message(message.chat.id,reply_markup=markup)
#         bot.register_next_step_handler(msg,bot_mensajes_texto)
    
#     if message.text=="Salir":
#         bot.send_message(message.chat.id,"Gracias por comunicarse con nosotros, Hasta luego")
    
#     #if message.text.startswith("/"):
#     #    bot.send_message(message.chat.id,"comando no disponible")
#     if message.text=="que fue":
#         bot.send_message(message.chat.id,"wee")
#     #else:
#     #    bot.send_message(message.chat.id,"hola")




    
# ################################HASTA AQUI VA LO MIO##########################################    
    
# ########################################TOdO ESTO LO COMENTO ##################################
    
    
# #########################################esto era para guiarse ##################################  
    
# def preguntar_edad(message):
#     """pregunta la edad del usuario."""
#     #nombre = message.text
#     usuarios[message.chat.id]={}
#     usuarios[message.chat.id]["nombre"]=message.text
#     markup = ForceReply()  # para responder citado
#     msg = bot.send_message(message.chat.id, "cuantos años tienes?", reply_markup=markup)
#     bot.register_next_step_handler(msg,preguntar_sexo)
    
# def preguntar_sexo(message):
#     """pregunta el sexo del usuario."""
#     if not message.text.isdigit():
#         #informamos error y volvemos a preguntar
#         markup = ForceReply()  # para responder citado
#         msg = bot.send_message(message.chat.id, "ERROR: Debes indicar un numero. \n cuantos años tienes?")
#         bot.register_next_step_handler(msg,preguntar_sexo)
#     else: #si se introdujo la edad correctamente
#         usuarios[message.chat.id]["edad"] = int(message.text)
#         #definimos dos botones
#         markup= ReplyKeyboardMarkup(one_time_keyboard=True,
#                                     input_field_placeholder="Pulsa un boton",
#                                     resize_keyboard=True)
#         markup.add("Hombre","Mujer")
#         #preguntamos por el sexo
#         msg = bot.send_message(message.chat.id, "Cual es tu sexo?",reply_markup=markup)
#         bot.register_next_step_handler(msg,guardar_datos_usuario)
        
# def guardar_datos_usuario(message):
#     #Guardamos los datos introducidos por el usuario
#     #si el sexo introducido no es valido:
#     if message.text!= "Hombre" and message.text!="Mujer":
#         #informamos del error y volvemos a preguntar
#         msg = bot.send_message(message.chat.id,"ERROR: Sexo no valido. \nPulsa un boton")
#         #volvemos a ejecutar esta funcion
#         bot.register_next_step_handler(msg, guardar_datos_usuario)
#     else:  #si el sexo introducido es valido
#         usuarios[message.chat.id]["sexo"]=message.text
#         texto = 'Datos introducidos: \n'
#         texto+= f'<code>NOMBRE:</code>{usuarios[message.chat.id]["nombre"]}\n'
#         texto+= f'<code>EDAD..:</code>{usuarios[message.chat.id]["edad"]}\n'
#         texto+= f'<code>SEXO..:</code>{usuarios[message.chat.id]["sexo"]}\n'
#         markup = ReplyKeyboardRemove()  # eliminar botones
#         bot.send_message(message.chat.id,texto, parse_mode="html",reply_markup=markup)
#         print(usuarios)
#         #para borrar lo que hay en cache :
#         del usuarios[message.chat.id]

# #########################################esto era para guiarse ##################################  
#MAIN
if __name__ == '__main__':
    
    
    # Blueprints
    web_server.register_blueprint(mainP, url_prefix='/prod')   #productos
    web_server.register_blueprint(mainO, url_prefix='/ord')   #orden
    web_server.register_blueprint(mainPe, url_prefix='/ped')   #pedido
    web_server.register_blueprint(mainC, url_prefix='/cli')   #clientes
    web_server.register_blueprint(mainPet, url_prefix='/pet')   #peticiones
    
    
    
    # print("INICIANDO BOT...")
    # #definimos la ruta de archivo de configuracion de ngrok
    # conf.get_default().config_path = "./config_ngrok.yml"
    # #se establece region:
    # conf.get_default().region="us"
    # #creamos archivo de las credenciales de la api de ngrok:
    # ngrok.set_auth_token(NGROK_TOKEN)
    # #creamos un tunel https en el puerto 5000
    # ngrok_tunel = ngrok.connect(5000,bind_tls=True) 
    # #URL del tunel https creado
    # ngrok_url= ngrok_tunel.public_url
    # print("URL_NGROK:",ngrok_url)
    # #eliminamos el webhook
    # bot.remove_webhook() # cuando necesite borrar el webhook pa probar con dialogflow o otra cosa
    # #pequeña pausa
    # time.sleep(1)
    # #definimos el webhook
    # bot.set_webhook(url=ngrok_url)
    # #arrancamos el servidor:
    # #web_server.debug=True
    # web_server.run("0.0.0.0",port=5000)
    web_server.run()
    
    #web_server.run()
    
    # #bucle infinito en el que se comprueba si hay nuevos mensajes:
    # #bot.infinity_polling()
    
    