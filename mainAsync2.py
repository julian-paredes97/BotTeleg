#!/usr/bin/python

# This is a simple echo bot using the decorator mechanism.
# It echoes any incoming text messages.
from config import *
from flask import Flask
import telebot
from telebot.async_telebot import AsyncTeleBot

from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

from aiohttp import web

import asyncio
import time
import threading
import logging

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)
#instanciamos el bot de telegram
bot = AsyncTeleBot(TELEGRAM_TOKEN)

#instanciamos el servidor web de flask:
web_server= Flask(__name__)

#esto es mio:
web_server.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:root123456@postgresdb.cadpgx7qqz5d.us-east-1.rds.amazonaws.com/postgres"
web_server.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db=SQLAlchemy(web_server)
CORS(web_server)
#esto es mio#

localtunnel = "https://flask-web-bot-app-jpc97.loca.lt"

webURL= localtunnel


# Process webhook calls
async def handle(request):
    if request.match_info.get('token') == bot.token:
        request_body_dict = await request.json()
        update = telebot.types.Update.de_json(request_body_dict)
        asyncio.ensure_future(bot.process_new_updates([update]))
        return web.Response()
    else:
        return web.Response(status=403)



# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
    await bot.reply_to(message, """\
Hi there, I am EchoBot.
I am here to echo your kind words back to you. Just say anything nice and I'll say the exact same thing to you!\
""")


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
async def echo_message(message):
    await bot.reply_to(message, message.text)
    
    
async def setup():
    # Remove webhook, it fails sometimes the set if there is a previous webhook
    await bot.remove_webhook()
    # Set webhook
    await bot.set_webhook(webURL)
    
    
# async def recibir_mensajes():
#     await bot.remove_webhook() # cuando necesite borrar el webhook pa probar con dialogflow o otra cosa
#     # #pequeña pausa
#     time.sleep(1)
#     await bot.set_webhook(url=f"{webURL}") 

#MAIN
if __name__ == '__main__':
    
    print("INICIANDO BOT...")
    
    # bot.remove_webhook() # cuando necesite borrar el webhook pa probar con dialogflow o otra cosa
    # # #pequeña pausa
    # time.sleep(1)
    # bot.set_webhook(url=f"{webURL}") 
    
    #asyncio.run(bot.run_webhooks(webURL))
    
    #asyncio.run(bot.polling())
    #print("aber")
    
    #hilo_bot= threading.Thread(name="hilo_bot",target=recibir_mensajes)
    #hilo_bot.start()
    setup()
    
    web_server.run()

#asyncio.run(bot.polling())