from flask import Flask, request
from flask_cors import CORS
from config import *
import telegram
import telebot # para manejar la api de telegram
from telebot.types import ReplyKeyboardMarkup #para crear botones
from telebot.types import ForceReply #para citar un mensaje
from telebot.types import ReplyKeyboardRemove # para eliminar botones
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton , KeyboardButton #para los botones para abrir la webapp
from telebot.types import MenuButtonWebApp, WebAppInfo #para los botones para abrir la webapp
import time

app = Flask(__name__)

CORS(app)


#instanciamos el bot de telegram
bot = telebot.TeleBot(TELEGRAM_TOKEN)

localtunnel = "https://flask-web-bot-app.loca.lt"
pagekite = "https://flaskwebbotapp.pagekite.me/"

webURL= localtunnel

bot.remove_webhook() # cuando necesite borrar el webhook pa probar con dialogflow o otra cosa
# #pequeña pausa
time.sleep(1)
       
bot.set_webhook(url=f"{webURL}") 

session_store = {}

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    chat_id = data['message']['chat']['id']
    message = data['message']['text']

    # Retrieve the user's session from the session store
    session_id = str(chat_id)
    session = session_store.get(session_id, {})


    
    @bot.message_handler(commands=['start'])
    def cmd_start(message):
        """ Muestra las acciones disponibles. """
        #markup = ReplyKeyboardRemove()
        #bot.send_message(message.chat.id,"Usa el comando/alta para introducir tus datos", reply_markup=markup)
        bot.send_message(chat_id,"Buen dia, se ha comunicado con Distri Romel Sas")
        
        #definimos dos botones
        markup= ReplyKeyboardMarkup(one_time_keyboard=True,
                                    input_field_placeholder="Pulsa un boton",
                                    resize_keyboard=True)
        markup.add("Realizar pedido","Ayuda","Salir")
        #preguntamos por la accion
        msg = bot.send_message(chat_id, "Como podemos ayudarle?",reply_markup=markup)
        #bot.register_next_step_handler(msg,realizar_pedido)
    
    
    
    
    
    



    # Determine the user's next action based on their session state
    if session.get('state') == 'get_name':
        # Handle user input to get their name
        name = message
        session['name'] = name
        session['state'] = 'get_age'
        session_store[session_id] = session

        # Send a message to the user asking for their age
        bot.send_message(chat_id, "Thanks! Now, what's your age?")

    elif session.get('state') == 'get_age':
        # Handle user input to get their age
        age = int(message)
        session['age'] = age
        session['state'] = 'done'
        session_store[session_id] = session

        # Send a message to the user thanking them for their information
        bot.send_message(chat_id, "Thanks for sharing your information!")

    else:
        # If the user doesn't have an existing session, start a new one to get their name
        session['state'] = 'get_name'
        session_store[session_id] = session

        # Send a message to the user asking for their name
        bot.send_message(chat_id, "What's your name?")
        
        
#MAIN
if __name__ == '__main__':
    
 
    print("INICIANDO BOT...")
   
    
    
    app.run()
    
    