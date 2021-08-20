from flask import Flask, render_template
from flask_sse import sse
from flask import request
from flask import jsonify
import json 


app = Flask(__name__)
app.config["REDIS_URL"] = "redis://localhost"
app.register_blueprint(sse, url_prefix='/stream')


usuario_carona = []
carona = []
notificacao_carona = []

usuario_caroneiro = []
caroneiro = []
notificacao_caroneiro = []

id_noti_desejo_carona = 0 
id_noti_ofereco_carona = 1000




def publish_carona(item):
    with app.app_context():
        sse.publish({"message": "Hello!"}, type='carona')
        return 'Notificação enviada carona'



def publish_caroneiro(item):
    with app.app_context():
        sse.publish({"message": "Hello!"}, type='caroneiro')
        return 'Notificação enviada caroneiro'


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/css')
def css():
    return render_template("style.css")



@app.route("/desejo_carona", methods=['POST'])
def desejo_carona():
    if request.method == 'POST':
        item = request.form.to_dict()
        carona.append(item)
        verifica_caroneiro_noti(item)
        print(carona)
    return item


@app.route("/ofereco_carona", methods=['POST'])
def ofereco_carona():
    if request.method == 'POST':
        item = request.form.to_dict()
        print(item)
        caroneiro.append(item)
        verifica_carona_noti(item)
        print(caroneiro)
    return "Oferta de carona cadastrada"


def verifica_caroneiro_noti(carona):
    for aux_caroneiro_noti in notificacao_caroneiro:
        if  carona['origem']== aux_caroneiro_noti['origem'] and carona['destino'] == aux_caroneiro_noti['destino'] and carona['data']== aux_caroneiro_noti['data']:
            publish(carona)


#Verifica se a oferta de carona cadastrada satisfaz alguma notificação já cadastrada
def verifica_carona_noti(caroneiro):
    for aux_carona_noti in notificacao_carona:
        if  caroneiro['origem']== aux_carona_noti['origem'] and caroneiro['destino'] == aux_carona_noti['destino'] and caroneiro['data']== aux_carona_noti['data']:
            publish(caroneiro)

#Verifica se alguma oferta carona já cadastrada satisfaz a viagem ofertada pelo caroneiro
def verifica_nova_noti_carona(carona):
    for aux_caroneiro in caroneiro:
        if  carona['origem']== aux_caroneiro['origem'] and carona['destino'] == aux_caroneiro['destino'] and carona['data']== aux_caroneiro['data']:
            publish(aux_caroneiro)


#Verifica se alguma carona já cadastrada satisfaz a viagem ofertada pelo caroneiro
def verifica_nova_noti_caroneiro(caroneiro):
    for aux_carona in carona:
        if  caroneiro['origem']== aux_carona['origem'] and caroneiro['destino'] == aux_carona['destino'] and caroneiro['data']== aux_carona['data']:
            publish(aux_carona)



@app.route("/notificao_desejo_carona", methods=['POST'])
def notificao_desejo_carona():
    if request.method == 'POST':
        item = request.form.to_dict()
        global id_noti_desejo_carona
        id_noti_desejo_carona += 1
        item['id'] = id_noti_desejo_carona
        notificacao_carona.append(item)
        print(notificacao_carona)
        verifica_nova_noti_carona(item)
        return item 

#Cadastra uma notificação, retorna o ID
@app.route("/notificao_ofereco_carona", methods=['POST'])
def notificao_ofereco_carona():
    if request.method == 'POST':
        item = request.form.to_dict()
        global id_noti_ofereco_carona
        id_noti_ofereco_carona += 1
        item['id'] = id_noti_ofereco_carona
        notificacao_caroneiro.append(item)
        print(notificacao_caroneiro)
        verifica_nova_noti_caroneiro(item)
        return id_noti_ofereco_carona 


#remove a viagem da lista de caronas notificadas
@app.route("/cancelar_carona", methods=['GET'])
def cancelar_carona():
    if request.method == 'GET':
        id_cancelar = request.args.get('id')
        print(id_cancelar)
    for dicts in notificacao_carona:
        for key,value in dicts.items():
            if (key == 'id'):
                if(int(value) == int(id_cancelar)):
                    notificacao_carona.remove(dicts)
                    print(notificacao_carona)
                    return "Viagem removida!"
    
    print(notificacao_carona)
    return "Id não está na Lista"


#remove a viagem da lista de caroneiros notificados
@app.route("/cancelar_caroneiro", methods=['GET'])
def cancelar_caroneiro():
    if request.method == 'GET':
            id_cancelar = request.args.get('id')
            print(id_cancelar)
    for dicts in notificacao_caroneiro:
        for key,value in dicts.items():
            if (key == 'id'):
                if(int(value) == int(id_cancelar)):
                    notificacao_caroneiro.remove(dicts)
                    print(notificacao_caroneiro)
                    return "Viagem removida!"
    
    print(notificacao_caroneiro)
    return "Id não está na Lista"




@app.route('/hello')
def publish_hello():
    publish()
    return "Message sent!"




