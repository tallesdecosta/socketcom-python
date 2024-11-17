import socket as sock
import threading as th
from tkinter import *
from tkinter import messagebox, scrolledtext


class Cliente:
    def __init__(self, tamanho_mensagem=1024):

        self.socket = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
        self.conectado = False
        self.tamanho_mensagem = tamanho_mensagem
        

        self.janela_login = Tk()
        self.janela_login.minsize(400, 220)
        self.janela_login.title("Identifique-se!")

        self.janela_login.iconbitmap("icon.ico")
        Label(self.janela_login, text="Insira seu nome:").pack(padx=10, pady=5)
        self.entrada_nome = Entry(self.janela_login)
        
        self.entrada_nome.pack(padx=10, pady=5)
        self.entrada_nome.bind("<Return>", lambda e:self.iniciar_chat())
        

        Label(self.janela_login, text="Insira o endereço host do servidor que deseja acessar:").pack(padx=10, pady=5)
        self.entrada_host = Entry(self.janela_login)
        self.entrada_host.pack(padx=10, pady=5)
        self.entrada_host.bind("<Return>", lambda e:self.iniciar_chat())


        Label(self.janela_login, text="Insira a porta do host que deseja acessar:").pack(padx=10, pady=5)
        self.entrada_porta = Entry(self.janela_login)
        self.entrada_porta.pack(padx=10, pady=5)
        self.entrada_porta.bind("<Return>", lambda e:self.iniciar_chat())


        self.btn_login = Button(self.janela_login, text="Se conectar ao chat", command=self.iniciar_chat)
        self.btn_login.pack(pady=10)
        

    def iniciar_chat(self):
        
        self.nome = self.entrada_nome.get().strip()
        self.host = self.entrada_host.get().strip()
        self.port = self.entrada_porta.get().strip()
        
        

        try:
            self.port = int(self.port)
            if self.nome and self.host and self.port:

                try:

                    self.conectar()
                    self.janela_login.destroy()  


                    self.janela_chat = Tk()
                    self.janela_chat.title("Chat")
                    self.janela_chat.iconbitmap("icon.ico")


                    self.textarea_chat = scrolledtext.ScrolledText(self.janela_chat, wrap=WORD, state='disabled', width=50, height=20)
                    self.textarea_chat.pack(padx=25, pady=25)

                    echo = self.socket.recv(self.tamanho_mensagem).decode('utf-8')
                    self.mostrar_mensagem(echo)


                    self.conectado = True
                    th.Thread(target=self.receber_mensagens, daemon=True).start()


                    # evento <Return> eh dar enter
                    self.entrada_mensagem = Entry(self.janela_chat, width=40)
                    self.entrada_mensagem.pack(padx=10, pady=5)
                    self.entrada_mensagem.bind("<Return>", self.enviar_mensagem)


                    self.btn_enviar = Button(self.janela_chat, text="Enviar", command=self.enviar_mensagem)
                    self.btn_enviar.pack(pady=5)


                    # protocolo eh +- um evento
                    # quando a janela for deletada (X)
                    # chama o método close
                    self.janela_chat.protocol("WM_DELETE_WINDOW", self.close)


                    
                    self.janela_chat.mainloop()
                except Exception as e:
                    messagebox.showwarning("Conexão falhou", "Por favor, certifique-se que o servidor que está tentando se conectar está funcionando e/ou que as informações estão coretas.")
                    print(e)
                finally:
                    self.socket.shutdown()

            else:

                messagebox.showwarning("Identificação necessária", "Por favor, identifique-se para entrar no chat.")
        except:
            messagebox.showwarning("Dados incorretos", "Por favor, digite corretamente o host e/ou porta do servidor.")

        

    def conectar(self):
        
        self.socket.connect((self.host, self.port))
        self.socket.send(self.nome.encode('utf-8')) 


    def mostrar_mensagem(self, message):

        self.textarea_chat.config(state='normal')
        self.textarea_chat.insert(END, message + "\n")
        self.textarea_chat.config(state='disabled')
        self.textarea_chat.yview(END)  

    def enviar_mensagem(self, event=None):
        
        mensagem = self.entrada_mensagem.get() if self.entrada_mensagem else ""

        if mensagem and self.conectado:


            self.socket.send(mensagem.encode('utf-8'))
            
            
            try:
                if self.entrada_mensagem:
                    self.entrada_mensagem.delete(0, END)
                    
            except TclError:
                
                pass

    def receber_mensagens(self):
        
        while self.conectado:
            try:
                mensagem = self.socket.recv(self.tamanho_mensagem).decode('utf-8')

                if mensagem:
                    self.mostrar_mensagem(mensagem)

                else:
                    break

            except ConnectionAbortedError:
                break

            except Exception as e:
                self.mostrar_mensagem(f"Error: {e}")
                break

        self.conectado = False

    def close(self):
        
        self.conectado = False
        self.socket.close()


        if hasattr(self, 'janela_chat'):

            self.janela_chat.destroy()

        else:

            self.janela_login.quit()

    def init_interface(self):
        
        self.janela_login.mainloop()

if __name__ == '__main__':
    cliente = Cliente()
    cliente.init_interface()
