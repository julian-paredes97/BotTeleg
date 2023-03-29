from flask import Flask, request, session
from flask_cors import CORS


web_server= Flask(__name__)

web_server.secret_key = 'super secret key'

CORS(web_server)


#envia datos del bot al front
@web_server.route('/botdata/<identificacion>',methods=['GET','POST'])
def datosbot(identificacion):
    ident= identificacion
    session["identificacion"]= ident
        
    # session[ident] = {}
    # session[ident]['identificacion'] = identificacion
        
        
        
        # session[session_id] = {}
        # session[session_id]['chat_id'] = session_id
        
    print("llamado del back:")
    print("session:")
    print(session)
    print("ABER QUE CHUCHAS:",ident)
        #usuariosAct[chatId]={}
        # # # usuariosAct[identificacion]={}
        # # # usuariosAct[identificacion]["identificacion"] = identificacion
        # # # usuariosAct[identificacion]["chatid"] = chatId
        # # # #usuariosAct[chatId]["identificacion"] = identificacion
        # # # #session["identificacion"] = identificacion    #key
        # # # print("llamado del back:")
        # # # print("ABER QUE CHUCHAS:",data)
        # # # print("ABER QUE CHUCHAS:",chatId)
        # # # print("ABER QUE CHUCHAS:",identificacion)
        # # # print("tipo ident:",type(identificacion))
    return "identificacion agregada"
      



@web_server.route('/botdata2',methods=['GET','POST'])
async def botdata2():
    if request.method == 'GET':
        print("llamado del front:")
        print("session:")
        print(session)
        identTemp = session.get("identificacion")
        print("identTemp:",identTemp)
        idaber= session["identificacion"]
        print("idaber:",idaber)
        
        return identTemp
        



#MAIN
if __name__ == '__main__':
    
    
    web_server.run()
   
    