from config import *
import telebot # para manejar la api de telegram
from telebot.types import ReplyKeyboardMarkup #para crear botones
from telebot.types import ForceReply #para citar un mensaje
from telebot.types import ReplyKeyboardRemove # para eliminar botones
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton #para los botones para abrir la webapp
from telebot.types import MenuButtonWebApp, WebAppInfo #para los botones para abrir la webapp
from flask import Flask, request, Blueprint #para crear el servidor web
import datetime
from datetime import datetime, timedelta
import time
import requests
import json
#from pyngrok import ngrok,conf # para crear el tunel entre el serv web local y el otro

from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from controladores.Producto import mainP
from controladores.Orden import mainO
from controladores.Pedido import mainPe
from controladores.Cliente import mainC #, get_cliente, get_clientes
#from controladores.Peticiones import mainPet #, recibePedido
from modelos.ModeloPedido import Pedido
from modelos.ModeloOrden import Orden
from modelos.ModeloCliente import Cliente
from utils.db import db

#import threading

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

localtunnel = "https://flask-web-bot-app.loca.lt"
pagekite = "https://flaskwebbotapp.pagekite.me/"

webURL= localtunnel

identificacionUsuario = "0"
pedidoCliente = ""

identificacionQuemada = "1234"  # esto es para pruebas

banderaPedidoListo = "False"

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


# #markup para llamar la webapp
# def gen_markup():
#     #markup = quick_markup({"inline_keyboard":[[{"text":"My web app","web_app":{"url":"https://snazzy-tartufo-5f17da.netlify.app"}}]]})
    
#     markup = InlineKeyboardMarkup()
#     markup.row_width = 2
    
#     #markup.add(InlineKeyboardButton("Yes", callback_data="cb_yes"),
#     boton=InlineKeyboardButton(text= "realizar pedido",web_app="https://snazzy-tartufo-5f17da.netlify.app")
#     markup.add(boton)
#     #markup.add(InlineKeyboardButton("Realizar pedido", web_app = "url":"https://snazzy-tartufo-5f17da.netlify.app"))
#     #text":"My web app","web_app":{"url":"https://snazzy-tartufo-5f17da.netlify.app"
#                                #InlineKeyboardButton("No", callback_data="cb_no"))
#     return markup


class IdentificacionU:
    def __init__(self, identificacion):
        self.identificacion = identificacion

class BanderaPedido:
    def __init__(self, banderaPedListo):
        self.bandera = banderaPedListo

class TextoPedUsuario:
    def __init__(self, textoPedidoUsuario):
        self.textoPedidoUsuario = textoPedidoUsuario
class TextoOrdUsuario:
    def __init__(self, textoOrdenUsuario):
        self.textoOrdenUsuario = textoOrdenUsuario
    

BanderaPedido.bandera = "False"
# #variables globales en la que guardaremos los datos del pedido del usuario
# textoPedidoUsuario = '<b>Datos Pedido:</b> \n'
# textoOrdenUsuario =  '<b>Datos de la Orden:</b> \n'
TextoPedUsuario.textoPedidoUsuario = '<u><b>Datos Pedido:</b></u> \n'
TextoOrdUsuario.textoOrdenUsuario = '<u><b>Datos de la Orden:</b></u> \n'



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
    

@bot.message_handler(commands=['pedir'])
def cmd_start(message):
    """ Muestra las acciones disponibles. """
    
    # req= requests.post("https://flask-web-bot-app.loca.lt/botdata",
    # #data = json.dumps(cedula),
    # data = json.dumps(identificacionQuemada),
    # headers={"Content-Type": "application/json"})
    # print(req.text)
    # print("###############################################")
    
    # print("aber")
    # markup = MenuButtonWebApp(InlineKeyboardButton(),"My web app",WebAppInfo("https://sweet-khapse-c8cb17.netlify.app"))
    # bot.send_message(message.chat.id,"que va pedir",reply_markup=markup)
    
    linkBot = 'https://api.telegram.org/bot5489576102:AAEppJsThPctLwr4iEp9C5iyGMMdd9JHUXk'
    markupWebApp = 'reply_markup={"keyboard":[[{"text":"My web app","web_app":{"url":"https://sweet-khapse-c8cb17.netlify.app"}}]]}'
            
    requests.get(f'{linkBot}/sendMessage?chat_id={message.chat.id}&text=Hello User&{markupWebApp}')
    
    # time.sleep(5)
    
    # markupWebApp2 = 'web_app: close'
    
    # requests.get(f'{linkBot}/sendMessage?chat_id={message.chat.id}&text=Hello User&{markupWebApp2}')
    
    # markup = ReplyKeyboardRemove()
    # bot.send_message(message.chat.id, "Pedido realizado con exito.",reply_markup=markup)
    
    


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
    
    if message.text.lower()=="salir":
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
        msg = bot.send_message(message.chat.id, "ERROR: Debes indicar un numero valido. \n cual es tu cedula?") #,reply_markup=markup)
        bot.register_next_step_handler(msg,corroborar_cedula)
    
    
    if message.text.isdecimal():   #esto era un else
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
        
        #cliente = requests.get(f"http://localhost:5000/cli/clientes/{cedula}") #funciona
        cliente = requests.get(f"{webURL}/cli/clientes/{cedula}") #funciona
        cli = cliente.json()
        existe = cli['exists']
        
        print("existe o nel:",existe)
        
        if existe=="True":
            nombre = cli['event']['nombre1']
            nombre2 = cli['event']['nombre2']
            nombre = nombre.lower()
            nombre2 = nombre2.lower()
            nombrecompleto = nombre + " " + nombre2
            chatId = message.chat.id
            print("truesito pa")
            
            
            #bot.send_message(message.chat.id, f"hola {nombrecompleto}, que vas a pedir el dia de hoy?")
            #bot.register_next_step_handler(msg,recibe_pedido)
            
            
            ### ANTES SERVIA CON ESTE GLOBAL:
            # global identificacionUsuario
            # identificacionUsuario = str(cedula)
            # print("identificacionUsuario",identificacionUsuario)
            ### ANTES SERVIA CON ESTE GLOBAL:
            
            IdentificacionU.identificacion= str(cedula)
            
            
            #envia datos del bot al front
            #req= requests.post(f"{webURL}/botdata",  #esto no te iba a servir ni a bate
            
            # req= requests.post("https://flask-web-bot-app.loca.lt/botdata",
            # #data = json.dumps(cedula),
            # data = json.dumps(identificacionUsuario),
            # headers={"Content-Type": "application/json"})
            # print(req.text)
            # print("###############################################")
            
            
            
            #hasta aqui fino
            linkBot = 'https://api.telegram.org/bot5489576102:AAEppJsThPctLwr4iEp9C5iyGMMdd9JHUXk'
            markupWebApp = 'reply_markup={"keyboard":[[{"text":"REALIZAR PEDIDO :)","web_app":{"url":"https://sweet-khapse-c8cb17.netlify.app"}}]]}'
            
            #texto=hola {nombrecompleto}, que vas a pedir el dia de hoy?
            
            requests.get(f'{linkBot}/sendMessage?chat_id={chatId}&text=hola {nombrecompleto}, que vas a pedir el dia de hoy?&{markupWebApp}')
            #requests.get(f'{linkBot}/sendMessage?chat_id={chatId}&text=Hello User&{markupWebApp}')
            
            #aqui cambiar el time sleep por un requests.get del front que se activa cuando 
            #pulse realizar pedido en el front
            
            # pedlisto = requests.get("https://velvety-pastelito-968bba.netlify.app") #funciona
            # print("PedListo:",pedlisto)
            # ped = pedlisto.json()
            # print("PED:",ped)
            
            # #existe = cli['exists']
            # print("pedlisto:",ped)
            
            # global banderaPedidoListo
            # if(banderaPedidoListo=="True"):
            #     print("que bendicion")
        
            #print("existe o nel:",existe)
            
            #esto funciona bello#
            #revisar bandera:
            
            # ESTO ES LO QUE VOY A INTENTAR#
            
            while(BanderaPedido.bandera == "False"):
                continue
       
            # ESTO ES LO QUE VOY A INTENTAR#
            
            # # ESTO ESTA fUNCIONANDO#
            # global banderaPedidoListo
            # while(banderaPedidoListo=="False"):
            #     continue
            #     #print("esperando...")
            # # ESTO ESTA fUNCIONANDO#
                
                
            if(BanderaPedido.bandera == "True"):  # ESTO ESTA fUNCIONANDO# ERA banderaPedidoListo
            #if(banderaPedidoListo=="True"):  # ESTO ESTA fUNCIONANDO# ERA banderaPedidoListo
                print("PedidoListo")
                #mensaje que se va a enviar al proveedor con el pedido:
                bot.send_message(-860836322, TextoPedUsuario.textoPedidoUsuario,parse_mode="html")#,reply_markup=markup)
                
                #ESTO QUE ESTA COMENTADP ACA SIRVE CON GLOBAL:
                #global textoPedidoUsuario
                #bot.send_message(-860836322, textoPedidoUsuario,parse_mode="html")#,reply_markup=markup)
                #mensaje que se va a enviar al proveedor con las ordenes:
                bot.send_message(-860836322, TextoOrdUsuario.textoOrdenUsuario,parse_mode="html")#,reply_markup=markup)
                #global textoOrdenUsuario
                #bot.send_message(-860836322, textoOrdenUsuario,parse_mode="html")#,reply_markup=markup)

                #mensaje que se va a enviar al proveedor con el pedido y ordenes:
                
                bot.send_message(message.chat.id, "<u><b>Pedido realizado con exito!</b></u>",parse_mode="html")#,reply_markup=markup)
                #bot.send_message(chat_id=chat_id, text='<b>Example message</b>',parse_mode=telegram.ParseMode.HTML
            #aqui vuelve al menu principal para ya salirse o hacer otro pedido:
            
            # time.sleep(2)
            
            markup= ReplyKeyboardMarkup(one_time_keyboard=True,
                                        input_field_placeholder="Pulsa un boton",
                                        resize_keyboard=True)
            markup.add("Realizar pedido","Salir")
        
            #preguntamos por la accion
            msg = bot.send_message(message.chat.id,"Necesitas algo mas?",reply_markup=markup)
            #msg = bot.send_message(message.chat.id,reply_markup=markup)
            bot.register_next_step_handler(msg,realizar_pedido)
            #esto funciona bello#
            
            
            
            
            # elif(banderaPedidoListo==False):
            #     print("noj paila")
            
            # pedlisto = requests.get("https://warm-mooncake-6a85ed.netlify.app") #funciona
            # ped = pedlisto.json()
            # #existe = cli['exists']

            # print("ped:",ped)
            # #print("existe o nel:",existe)
            
            # #cerrar webapp
            # time.sleep(5)
            # markup = ReplyKeyboardRemove()
            # bot.send_message(message.chat.id, "web app cerrada",reply_markup=markup)
            
            
            
            # ######### esto no funca ########## lo intente ayer y meh
            
            # req= requests.post(f"{webURL}/botdata",
            # #data = json.dumps(cedula),
            # data = json.dumps(identificacionUsuario),
            # headers={"Content-Type": "application/json"})
            # print(req.text)
            # print("###############################################")
            
            # #pedido = requests.get(f"{webURL}/pet/recibePedido") #funciona
            # pedido = requests.get(f"{webURL}/recibePedido") #funciona
            # ped= pedido.json()
            # print("ped:",ped)
            # print("pedido pa:",pedido)
            
            # ######### esto no funca ##########
            
            #meter esto para ver el pedido:
            # cliente = requests.get(f"http://localhost:5000/cli/clientes/{cedula}") #funciona
            # cli = cliente.json()
            # existe = cli['exists']
            
            #time.sleep(5)
            
            #cerrar webapp
            #markup = ReplyKeyboardRemove()
            #bot.send_message(message.chat.id, "web app cerrada",reply_markup=markup)
            
            #hasta aqui fino
            
            #bot.send_message(message.chat.id, f"hola {nombre}, que vas a pedir el dia de hoy?",reply_markup=gen_markup())
            #bot.register_next_step_handler(msg,recibe_pedido)
        
        else:
            print("im in")
            """almacena la nueva cedula y pregunta nombres del usuario."""
            usuarios[message.chat.id]={}
            usuarios[message.chat.id]["identificacion"]=message.text
            #markup = ForceReply()  # para responder citado
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
    #r= requests.post("http://localhost:5000/cli/clientes",
    #r= requests.post("https://flask-web-bot-app.loca.lt/cli/clientes",
    #r= requests.post("https://flaskwebbotapp.pagekite.me/cli/clientes",
    r= requests.post(f"{webURL}/cli/clientes",
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
    
    markup= ReplyKeyboardMarkup(one_time_keyboard=True,
                                        input_field_placeholder="Pulsa un boton",
                                        resize_keyboard=True)
    markup.add("Realizar pedido","Salir")
        
    #preguntamos por la accion
    msg = bot.send_message(message.chat.id,"Necesitas algo mas?",reply_markup=markup)
    #msg = bot.send_message(message.chat.id,reply_markup=markup)
    bot.register_next_step_handler(msg,realizar_pedido)



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

def max_id_pedidos():
    result = db.session.query(func.max(Pedido.idpedido)).scalar()
    return result

def max_id_ordenes():
    result = db.session.query(func.max(Orden.idorden)).scalar()
    return result

def datos_cliente(identificacion):
    #cli = db.session.query(Cliente).filter(Cliente.identificacion == identificacion)
    cli = db.session.query(Cliente).filter(
        Cliente.identificacion == str(identificacion)
    ).first()
    return cli

#results = max_id_pedidos()

#recibe bandera del front si ya acabo el pedido:
@web_server.route('/pedidoListo',methods=['POST','GET'])
def pedido_listo():
    if request.method == 'POST':
       print("WEEEEEE")
       #pedidos = request.data
       req = request.get_json(silent=True, force=True) #ensayar con esto
       res = json.dumps(req, indent=4)
       print(res)
       ped = json.loads(res)
       #aber = json.loads(res)
       
       # ESTO ES LO QUE VOY A INTENTAR#
       BanderaPedido.bandera = str(ped['flag'])
       print("bandera pedido:",BanderaPedido.bandera)
       return BanderaPedido.bandera
       
       # ESTO ES LO QUE VOY A INTENTAR#
       
    #    # ESTO ESTA fUNCIONANDO#
       
    #    global banderaPedidoListo
    #    banderaPedidoListo = str(ped['flag'])
    #    print("bandera pedido:",banderaPedidoListo)
    #    return banderaPedidoListo
    #    # ESTO ESTA fUNCIONANDO#

    else:
        print("F")
        return "Error en el pedido"
       
    # banderaPedidoListo = 
    # identif = identificacionUsuario
    # print("bandera:",identif)
    # return identif

#envia datos del bot al front
@web_server.route('/botdata',methods=['GET','POST'])
def datosbot():
    identif = IdentificacionU.identificacion
    #identif = identificacionUsuario    #ASI ESTABA ANTES
    print("identif:",identif)
    return identif


#recibir pedido que llega desde el front:
@web_server.route('/recibePedido',methods=['GET', 'POST'])
def recibePedido():
    
    if request.method == 'POST':
       print("WEEEEEE")
       #pedidos = request.data
       req = request.get_json(silent=True, force=True) #ensayar con esto
       res = json.dumps(req, indent=4)
       print(res)
       ped = json.loads(res)
       #aber = json.loads(res)
       pedidoCliente = ped
       print("pedido:\n",pedidoCliente)
       #return ped
       #return pedidoCliente
       ###########esto esta melo###
       totalpedido=0
       
       ######## datos para tabla pedidos ########
       maxIdPedido = max_id_pedidos()           #para poder incrementar el id en la bd
       print("max id pedidos:",maxIdPedido)
       idpedido = maxIdPedido + 1
       identificacion = 0
       nombrenegocio = ""
       
       #####################################
       identificacion = ped["identificacion"]
       #print("identificacion:",ped["identificacion"])
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
       
       #para sacar las fechas:
       now = datetime.now()
       date_time = now.strftime("%y-%m-%d")
       fechapedido= date_time
       print("fechapedido:",fechapedido)
       fechamaxentrega= now + timedelta(days=1)
       fechamaxentrega= fechamaxentrega.strftime("%y-%m-%d")
       print("fechamaxentrega",fechamaxentrega)
       totalpagar=0
       
       ######## datos para tabla pedidos ########
       #ENSAYAR ESTO
    #    pedidoCompleto = Pedido(nombres=nombres,apellidos=apellidos,nombrenegocio=nombrenegocio,direccion=direccion,
    #                            ciudad=ciudad,barrio=barrio,correo=correo,)
       ######## datos para tabla pedidos ########
       
       
       ######## datos para tabla ordenes ########
       maxIdOrden = max_id_ordenes()            #para poder incrementar el id en la bd
       print("max id ordenes:",maxIdOrden)
       idorden = maxIdOrden + 1
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

       #agregar pedido ya con todos los datos que se tienen
       pedidofinal = {}
       #usuarios[message.chat.id]["ciudad"] = ciudad
       pedidofinal["idpedido"] = idpedido
       pedidofinal["identificacion"] = identificacion
       pedidofinal["nombres"] = nombres
       pedidofinal["apellidos"] = apellidos
       pedidofinal["nombrenegocio"] = nombrenegocio
       pedidofinal["direccion"] = direccion
       pedidofinal["ciudad"] = ciudad
       pedidofinal["barrio"] = barrio
       pedidofinal["correo"] = correo
       pedidofinal["celular"] = celular
       pedidofinal["fechapedido"] = fechapedido
       pedidofinal["fechamaxentrega"] = fechamaxentrega
       pedidofinal["totalpagar"] = totalpagar
       print(pedidofinal)
       
       ############ DATOS QUE SE VAN A ENVIAR AL PROVEEDOR ############
       
    #    global textoPedidoUsuario
    #    textoPedidoUsuario+= f'<code>Id pedido:</code>{idpedido}\n'
    #    textoPedidoUsuario+= f'<code>Identificacion:</code>{identificacion}\n'
    #    textoPedidoUsuario+= f'<code>Nombres:</code>{nombres}\n'
    #    textoPedidoUsuario+= f'<code>Apellidos:</code>{apellidos}\n'
    #    textoPedidoUsuario+= f'<code>Nombre negocio:</code>{nombrenegocio}\n'
    #    textoPedidoUsuario+= f'<code>Direccion:</code>{direccion}\n'
    #    textoPedidoUsuario+= f'<code>Barrio:</code>{barrio}\n'
    #    textoPedidoUsuario+= f'<code>Correo:</code>{correo}\n'
    #    textoPedidoUsuario+= f'<code>Celular:</code>{celular}\n'
    #    textoPedidoUsuario+= f'<code>Fecha pedido:</code>{fechapedido}\n'
    #    textoPedidoUsuario+= f'<code>Fecha max entrega:</code>{fechamaxentrega}\n'
    #    textoPedidoUsuario+= f'<code>Total a pagar:</code>{totalpagar}\n'
       
       TextoPedUsuario.textoPedidoUsuario+= f'<code><b>Id pedido:</b></code>{idpedido}\n'
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
       
       ############ DATOS QUE SE VAN A ENVIAR AL PROVEEDOR ############
       ######## datos para tabla pedidos ########
       #ENSAYAR ESTO
    #    pedidoCompleto = Pedido(nombres=nombres,apellidos=apellidos,nombrenegocio=nombrenegocio,direccion=direccion,
    #                            ciudad=ciudad,barrio=barrio,correo=correo,celular=celular,fechapedido=fechapedido,
    #                            fechamaxentrega=fechamaxentrega,totalpagar=totalpagar)
    #    db.session.add(pedidoCompleto)
    #    db.session.commit()
    #    print("pedido agregado")
       ######## datos para tabla pedidos ########
       
       #guarda pedido del usuario en la BD:
       p= requests.post(f"{webURL}/ped/pedidos",
                        data=json.dumps(pedidofinal),
                        headers={"Content-Type": "application/json"})
       print(p.text)
       
       #for para ir agregando cada orden con el mismo numero de pedido
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
        #   global textoOrdenUsuario
        #    textoOrdenUsuario+= f'<code>Id Orden:</code>{ordenfinal["idorden"]}\n'
        #    textoOrdenUsuario+= f'<code>Descripcion del producto:</code>{ordenfinal["descripcion"]}\n'
        #    textoOrdenUsuario+= f'<code>Codigo del producto:</code>{ordenfinal["codigo"]}\n'
        #    textoOrdenUsuario+= f'<code>Precio:</code>{ordenfinal["precio"]}\n'
        #    textoOrdenUsuario+= f'<code>Cantidad:</code>{ordenfinal["cantidad"]}\n'
        #    textoOrdenUsuario+= f'<code>Precio X Cantidad:</code>{ordenfinal["precioxcantidad"]}\n'
           
           TextoOrdUsuario.textoOrdenUsuario+= f'<code><b>• Id Orden:</b></code>{ordenfinal["idorden"]}\n'
           TextoOrdUsuario.textoOrdenUsuario+= f'<code><b>Descripcion del producto:</b></code>{ordenfinal["descripcion"]}\n'
           TextoOrdUsuario.textoOrdenUsuario+= f'<code><b>Codigo del producto:</b></code>{ordenfinal["codigo"]}\n'
           TextoOrdUsuario.textoOrdenUsuario+= f'<code><b>Precio:</b></code>{ordenfinal["precio"]}\n'
           TextoOrdUsuario.textoOrdenUsuario+= f'<code><b>Cantidad:</b></code>{ordenfinal["cantidad"]}\n'
           TextoOrdUsuario.textoOrdenUsuario+= f'<code><b>Precio X Cantidad:</b></code>{ordenfinal["precioxcantidad"]}\n\n'
           
           ############ DATOS QUE SE VAN A ENVIAR AL PROVEEDOR ############
           #guarda orden del usuario en la BD:
           #guarda pedido del usuario en la BD:
           o= requests.post(f"{webURL}/ord/ordenes",
                            data=json.dumps(ordenfinal),
                            headers={"Content-Type": "application/json"})
           print(o.text)
           idorden=idorden+1
           
           
           
           j=j+1
       
       
       
       return pedidoCliente
       
    
    if request.method == 'GET':
        
    # else :
    #     print("F")
    # idpedido = request.json['idpedido']
    # identificacion = request.json['identificacion']
    # fechapedido = request.json['fechapedido']
    # fechamaxentrega = request.json['fechamaxentrega']
    # totalpagar= request.json['totalpagar']
    
    
    #pedido = Pedido(idpedido=idpedido,identificacion=identificacion,fechapedido=fechapedido,fechamaxentrega=fechamaxentrega,totalpagar=totalpagar)
    #db.session.add(pedido)
    #db.session.commit()
    
        return "pedido no recibido"



# def recibir_mensajes():
#     bot.remove_webhook() # cuando necesite borrar el webhook pa probar con dialogflow o otra cosa
#     # #pequeña pausa
#     time.sleep(1)
#     bot.set_webhook(url=f"{webURL}") 


#MAIN
if __name__ == '__main__':
    
    
    # Blueprints
    web_server.register_blueprint(mainP, url_prefix='/prod')   #productos
    web_server.register_blueprint(mainO, url_prefix='/ord')   #orden
    web_server.register_blueprint(mainPe, url_prefix='/ped')   #pedido
    web_server.register_blueprint(mainC, url_prefix='/cli')   #clientes
    #web_server.register_blueprint(mainPet, url_prefix='/pet')   #peticiones
    
    
    
    print("INICIANDO BOT...")
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
    bot.remove_webhook() # cuando necesite borrar el webhook pa probar con dialogflow o otra cosa
    # #pequeña pausa
    time.sleep(1)
    # #definimos el webhook
    # #bot.set_webhook(url="https://provbotwebapp.onrender.com")
    # bot.set_webhook(url=ngrok_url)
    #bot.set_webhook(url="https://flask-web-bot-app.loca.lt")   #localtunnel
    #bot.set_webhook(url="https://webbotflaskapi-kyha.onrender.com")
    #bot.set_webhook(url="https://flaskwebbotapp.pagekite.me")  #pagekite
    
    bot.set_webhook(url=f"{webURL}") 
    #hilo_bot= threading.Thread(name="hilo_bot",target=recibir_mensajes)
    #hilo_bot.start()
    
    #arrancamos el servidor:
    #web_server.debug=True
    #web_server.run("0.0.0.0",port=5000)
    web_server.run()
    
    #web_server.run()
    
    # #bucle infinito en el que se comprueba si hay nuevos mensajes:
    # #bot.infinity_polling()
    
    