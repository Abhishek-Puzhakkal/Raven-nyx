import socket
from noise.connection import NoiseConnection

class Client:
    def __init__(self, ip, port, username):
        self.proto = None
        self.username = username[0]
        self.server_addr = ip[0]
        self.port = port[0]
        self.client_socket = socket.socket()
        self.clinet_message = None
        self.server_message = None
        self.running = True
        self.quit_checker = list()
        

    def clinet_server_connection(self) -> bool:
        try:
            

            self.client_socket.connect((self.server_addr, self.port))
            print(f'client connected to {self.server_addr}')
            print('handshake starting....')
            self.proto = NoiseConnection.from_name(b'Noise_NN_25519_ChaChaPoly_SHA256')
            self.proto.set_as_initiator()
            self.proto.start_handshake()
            message = self.proto.write_message()
            self.client_socket.sendall(message)
            received = self.client_socket.recv(2048)
            payload = self.proto.read_message(received)

            
            return True
        except KeyboardInterrupt:
            print('keyboard intrpted ')
            self.client_socket.close()
        except Exception as e:
            
            print(e)
    def clinet_snt_msg(self):
        while self.running:
            message = input('\nyou : ')
            if not self.running:
                break

            if message: 

                if not self.running:
                    break

                if message == 'quit':
                    
                    self.clinet_message = self.username + ' : '+ message

                    self.client_socket.sendall(self.cryptography.encrypt(self.clinet_message.encode()))
                    print(f'\nyou entered "quit", connection is terminating....', flush=True)
                    self.running = False
                    
                    break
                    
                    
                
                self.clinet_message = self.username + ' : '+ message

                self.client_socket.sendall(self.proto.encrypt(self.clinet_message.encode()))
                

        


    def client_recv_msg(self):

        while self.running:
            try: 
                servermessage = self.client_socket.recv(1024)
            except OSError as e:
                if e.winerror == 10053:
                    print('connection closed peacefully...')
                
                else:
                    raise
            except Exception as e :
                
                print(e)
            

            if not self.running:
                
                break

            if servermessage:
                self.server_message = self.proto.decrypt(servermessage).decode()
                
            
                if not self.running:
                    
                    break
                
                self.quit_checker = self.server_message.split()

                if len(self.quit_checker) == 3 and self.quit_checker[2] == 'quit':
                    
                    print(f'\n{self.server_message}')
                    print('\nthe connection is terminating....', flush=True)
                    self.running = False
                    break
                print(f'\n{self.server_message}')

        

    def clt_close(self):
        try:
            self.client_socket.close()
        except KeyboardInterrupt:
            print("\nServer stopped manually.")


class GpChatClient:
    def __init__(self, addr:str, port:int, username:str):
        self.uername = username[0]
        self.port = port[0]
        self.addr = addr[0]
        self.client_gp_chat_socket = socket.socket()
        self.client_running = True
        self.quit_checker = list()
        self.proto = None
        '''self.gp_cht_cryptography_ky = b'2b1gSNyIH1g3-huR0gAHcuCZK1mFURW46xiuWsEnw_M='
        self.gp_cryptography_object = Fernet(self.gp_cht_cryptography_ky)'''
    def client_gp_chat_connection(self):
        try :
            self.client_gp_chat_socket.connect((self.addr, self.port))
            self.proto = NoiseConnection.from_name(b'Noise_NN_25519_ChaChaPoly_SHA256')
            self.proto.set_as_initiator()
            self.proto.start_handshake()
            message = self.proto.write_message()
            self.client_gp_chat_socket.sendall(message)
            received = self.client_gp_chat_socket.recv(2048)
            payload = self.proto.read_message(received)
            return True
        except Exception as e :
            
            print(e)
    def client_gp_cht_snt_msg(self):
        try:

            while self.client_running:
                message = input('\nyou : ')
                if not self.client_running:
                    break
                
                if message:
                    msg = self.uername + ' : ' + message
                    
                    if message == 'quit':
                        self.client_gp_chat_socket.sendall(self.proto.encrypt(msg.encode()))
                        print('you enterd the "quit", so conection terminating....')
                        self.client_running = False
                        break

                    self.client_gp_chat_socket.sendall(self.proto.encrypt(msg.encode()))
        except KeyboardInterrupt:
            print('keyboard intrepted ....')
        except Exception as e :
            
            print(e)
    def client_gp_cht_recv_msg(self):
        try:
            while self.client_running:
                try:
                    message = self.client_gp_chat_socket.recv(1024)
                except OSError as e:
                    if e.winerror in (10053, 10054):
                        pass
                    else: raise
                except Exception as e:
                    
                    print(e)
                
                if not self.client_running:
                    break
                
                decrypted_msg = self.proto.decrypt(message).decode()

                self.quit_checker = decrypted_msg.split()
                
                printing_msg = ' '.join(self.quit_checker[1::])
                

                if self.quit_checker[0] == 'broadcasting':
                    if len(self.quit_checker) == 4 and self.quit_checker[3] == 'quit':
                        print(f'\n{printing_msg}')
                        print(f'{self.quit_checker[1]} entered "quit" that person is terminating from group...')
                    else:print(f'\n{printing_msg}')
                elif self.quit_checker[0] == 'admin':
                    if len(self.quit_checker) == 4 and self.quit_checker[3] == 'quit':
                        print(f'\n{printing_msg}')
                        print('server enterd "quit", enteire chat is terminating...')
                        self.client_running = False
                        break
                    print(f'\n{printing_msg}')
        except KeyboardInterrupt :
            print('\nkeyboard interepted...')
        except Exception as e :
            
            print(e)
                

    def client_gp_cht_connection_cls(self):
        try :
            self.client_gp_chat_socket.close()
            print('\nthe connection closed peacefully....')
        except KeyboardInterrupt:
            print("\nServer stopped manually.")

        
        
    




    

        



        
        