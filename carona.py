import sys
import threading
import Pyro4
import serpent
import carona_chave
from Crypto.PublicKey import RSA
import json

if sys.version_info < (3, 0):
    input = raw_input


# The daemon is running in its own thread, to be able to deal with server
# callback messages while the main thread is processing user input.
#Cria um Objeto Carona (Cliente)
class Carona(object):
    def __init__(self):
        nameserver = Pyro4.locateNS()
        uri = nameserver.lookup("example.servidor")
        self.servidor = Pyro4.core.Proxy(uri)
        self.abort = 0
        self.nome = ''
        self.telefone = ''

    #metodo estilo callback
    #OneWay -> Não espera resposta
    @Pyro4.expose
    @Pyro4.oneway
    def message(self, msg):
        print("NOVA NOTIFICAÇÃO:")
        print("Dados do Caroneiro - ")
        print(msg['nome'])
        print(msg['telefone'])
        print("Dados da viagem - ")
        print(msg['origem'])
        print(msg['destino'])
        print(msg['data'])


    #Loop infinito com as açoes
    def start(self):

        self.cadastrar()
        self.inserir_carona()
        while(True):
            option = input("1 - Cancelar Carona \n2 - Acompanhar notificação\n3 - Fazer nova viagem \n0 - Sair\n").strip()
            if(option == '1'):
                self.cancelar_carona()
            elif(option == '2'):
                pass
            elif(option == '3'):
                self.inserir_carona()
            elif(option == '0'):
                break
            else:
                print("Opção Inválida")

        print("Arigato!")

        self.abort = 1
        self._pyroDaemon.shutdown()



    #Cadastra um usuário 
    def cadastrar(self):
        chaves = carona_chave.gerar_chaves()
        chave_publica = carona_chave.gerar_public(chaves)
        nome = input("Insira seu nome: ").strip()
        telefone = input("Insira seu telefone: ").strip()
        self.nome = nome
        self.telefone = telefone
        if (nome and telefone):
            item = {'nome':nome,'telefone':telefone}
            self.servidor.cadastrar_usuario_carona(item)
            print("Usuário cadastrado com sucesso! \n")
        else:
            print("Faltam dados! \n")
    
    #Insere Carona no servidor
    def inserir_carona(self):
        print("Vamos cadastrar sua viagem desejada! \n")
        nome = self.nome
        telefone = self.telefone
        origem = input("Insira seu local de origem: ").strip()
        destino = input("Insira seu local de destino: ").strip()
        data = input("Insira a data no formato dd/mm/aaaa: ").strip()
        if (origem and destino and data):
            item = {'nome':nome,'telefone':telefone,'origem':origem,'destino':destino,'data':data}
            self.servidor.desejo_carona(item)
            notificacao = input("Deseja receber notificação caso alguma viagem atenda esses critérios? \n s para Sim \n n para Não\n").strip()
            if(notificacao == 's'):
                self.cadastrar_notificacao(item)
            else:
                print('ok :(\n')
        else:
            print("Dados inválidos")


    #Cadastra a notificação no Servidor
    def cadastrar_notificacao(self,viagem):
            
            print("Validando Chave..\n")
            chaves = RSA.import_key(open("carona_private.pem").read())
            chave_publica = RSA.import_key(open("carona_receiver.pem").read())
            assinatura = carona_chave.assinatura(chaves,"hash_test")
            if self.servidor.validar_carona("hash_test"):
                print("Chave válida\n")
                print("Cadastrando sua viagem para ser notificada...\n")
                item = {'nome':viagem['nome'],'telefone':viagem['telefone'],'origem':viagem['origem'],'destino':viagem['destino'],'data':viagem['data']}
                id_noti = self.servidor.notificao_desejo_carona(item,self)
                print("O id da sua viagem é: ")
                print(id_noti)
            else:
                print("Chave inválida")
            

    #Remove a carona por ID
    def cancelar_carona(self):
        id_cancelar = input("Insira o Id da viagem que deseja cancelar: \n").strip()
        response = self.servidor.cancelar_carona(id_cancelar)
        print(response)




#Cria uma thread para o objeto Carona
class DaemonThread(threading.Thread):
    def __init__(self, carona):
        threading.Thread.__init__(self)
        self.carona = carona
        self.setDaemon(True)

    def run(self):
        with Pyro4.core.Daemon() as daemon:
            daemon.register(self.carona)
            daemon.requestLoop(lambda: not self.carona.abort)


carona = Carona()
daemonthread = DaemonThread(carona)
daemonthread.start()
carona.start()
print('Exit.')