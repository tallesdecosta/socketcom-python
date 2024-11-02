import socket as sock
import threading as th

class Servidor:
    def __init__(self, mensagem_payload=1024):
        
        self.host = input('Insira o host do servidor para abrir: ')
        self.port = int(input('Insira a porta do servidor para abrir: '))
        self.mensagem_payload = mensagem_payload
        self.rodando = True
        self.threads = []
        self.clientes = {}
        self.lock = th.Lock()

        self.sock_servidor = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
        self.sock_servidor.setsockopt(sock.SOL_SOCKET, sock.SO_REUSEADDR, 1)

        self.sock_servidor.bind((self.host, self.port))
        print(f"Servidor está ativo e aguardando mensagens em {self.host}:{self.port}.")

        self.sock_servidor.listen(5)

    def alocar_cliente(self, sock_cliente, endereço):

        nome = sock_cliente.recv(self.mensagem_payload).decode('utf-8')

        with self.lock:
            self.clientes[nome.replace(' ','')] = sock_cliente

        print(f'Nova conexão: {endereço}')
        self.broadcast(f"{nome} entrou no chat, dêem as boas vindas!", nome)
        message = '\nVocê está acessando o chat BES, PUC-PR. Todas as mensagens que você enviar serão recebidas pelos outros participantes conectados ao chat por padrão. Pra enviar uma mensagem privada, primeiro envie "/p nome do remetente" e depois envie a mensagem. Caso queira sair, digite "/sair".\n'
        sock_cliente.send(message.encode('utf-8'))
        

        try:
            while True:

                mensagem = sock_cliente.recv(self.mensagem_payload).decode('utf-8')

                if mensagem:

                    if '/p' in mensagem:
                        destino = mensagem.replace('/p', '').replace(' ','')
                        print(destino)
                        mensagem = sock_cliente.recv(self.mensagem_payload).decode('utf-8')
                        self.enviar_mensagem_individual(f"(essa mensagem é privada) {nome}: {mensagem}", destino)
                    
                    elif '/sair' in mensagem:
                        break

                    else: 
                        self.broadcast(f"{nome}: {mensagem}", nome)

                else:
                    print(f"Cliente {nome} desconectado.")
                    break

        except ConnectionResetError:
            print(f"A conexão com {nome} foi resetada inesperadamente.")

        finally:

            with self.lock:
                del self.clientes[nome]

            sock_cliente.close()
            print(f"Conexão encerrada com o endereço {endereço}")
    
    def broadcast(self, mensagem, nome_remetente):
        with self.lock:
            for nome, cliente in self.clientes.items():
                if nome != nome_remetente:  
                    try:
                        cliente.send(mensagem.encode('utf-8'))
                    except sock.error:
                        cliente.close()
                        del self.clientes[nome]

    def enviar_mensagem_individual(self, mensagem, nome_destinatario):
        """Envia uma mensagem para um único cliente pelo nome."""
        with self.lock:
            cliente = self.clientes.get(nome_destinatario)
            if cliente:
                try:
                    cliente.send(mensagem.encode('utf-8'))
                except sock.error:
                    cliente.close()
                    del self.clientes[nome_destinatario]
                    print('aaa')

    def iniciar(self):
        print("Servidor está aguardando para receber mensagens de clientes . . .")
        while self.rodando:
            try:
                sock_cliente, endereço = self.sock_servidor.accept()
                print(f"Conexão de {endereço} aceita!")

                th_cliente = th.Thread(target=self.alocar_cliente, args=(sock_cliente, endereço))
                th_cliente.start()
                self.threads.append(th_cliente)

            except OSError:
                print("Servidor foi fechado")
                break

        for t in self.threads:
            t.join()


    def fechar(self):
        self.rodando = False
        self.sock_servidor.close()

if __name__ == '__main__':
    chat = Servidor()
    try:
        chat.iniciar()
    except KeyboardInterrupt:
        chat.fechar()