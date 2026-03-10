import socket
from noise.connection import NoiseConnection
from itertools import cycle
import threading
from pathlib import Path
from stem.control import Controller


class Server:
    def __init__(self, port, username):
        self.proto = None
        self.user_name = username[0]
        self.port = port[0]
        self.server = socket.socket()
        self.client = None
        self.client_message = None
        self.serv_message = None
        self.file_path = None
        self.running = True
        self.quit_checker = None
    
    def server_client_connect(self) :
        try:
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind(('0.0.0.0', self.port))
            self.server.listen()

            self.client, clinet_addr = self.server.accept()

            self.proto = NoiseConnection.from_name(b'Noise_NN_25519_ChaChaPoly_SHA256')
            self.proto.set_as_responder()
            self.proto.start_handshake()

            for action in cycle(['receive', 'send']):
                if self.proto.handshake_finished:
                    break
                elif action == 'send':
                    ciphertext = self.proto.write_message()
                    self.client.sendall(ciphertext)
                elif action == 'receive':
                    data = self.client.recv(2048)
                    plaintext = self.proto.read_message(data)

            return self.client, clinet_addr
        
        except KeyboardInterrupt:
            print('keyboard intrepted , socket is closing ')
            self.server.close()
        except Exception as e:
            print(e)
    
    def server_snt_msg(self):
        while self.running:
            message = input('\nyou : ')
            self.serv_message = self.user_name + ' : ' + message

            if not self.running:
             break
            if message:
                if message == 'quit':
                    
                    self.client.sendall(self.proto.encrypt(self.serv_message.encode()))
                    print('\nyou entered quit , the connection is terminating......', flush=True)
                    self.running = False
                    break
                self.client.sendall(self.proto.encrypt(self.serv_message.encode()))
        
        
    def server_recv_msg(self):

        while self.running:

            try :
                client_message = self.client.recv(1024)
            except OSError as e :
                if e.winerror in (10053, 10054):
                    print('The connection closed peacefully...')
                else:
                    raise
            except Exception as e :
                print(e)
                
            if not self.running:
                break

            client_message_decrypted = self.proto.decrypt(client_message).decode()
            self.quit_checker = list(client_message_decrypted.split())
            if len(self.quit_checker) == 3 and self.quit_checker[2] == 'quit':
                self.running = False
                print(f'\n{client_message_decrypted}') 
                print('\n the connection is terminating ...',flush=True)
                
                break
            print(f'\n {client_message_decrypted}')
        
    def serv_closing(self):
        try:
            self.client.close()
            self.server.close()
        except KeyboardInterrupt:
            print("\nServer stopped manually.")



class GroupChatServer:
    def __init__(self, port, username):
        self.gp_chat_svr_socket = socket.socket()
        self.port = port[0]
        self.username = username[0]
        self.clients_socket = None
        self.clients_addr = None
        self.server_running = True
        self.quict_checker = list()
        self.clients_socket_session_key_mapping = dict()
    def connection(self):
        self.gp_chat_svr_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.gp_chat_svr_socket.settimeout(1.0)
        self.gp_chat_svr_socket.bind(('0.0.0.0', self.port))
        self.gp_chat_svr_socket.listen()
        
        print('\nserver started listening.....')
        def server_brodcast(client):
            try : 
                
                while self.server_running:
                    sender = client
                    
                    
                    if not self.server_running:
                        break
                    try:
                        client_message = client.recv(1024)
                    except OSError as e:
                        if e.winerror in (10053, 10054):
                            pass
                        else:
                            raise
                    if not client_message:
                        break
                    if not self.server_running:
                        break
                
                    
                    session_key_client = self.clients_socket_session_key_mapping[client]
                    decrypted_client_msg = session_key_client.decrypt(client_message).decode()
                    
                    broadcasting_flag = 'broadcasting'
                    
                    if decrypted_client_msg and len(self.clients_socket_session_key_mapping) >= 2:
                        self.quict_checker = decrypted_client_msg.split()
                        username = self.quict_checker[0]
                        if len(self.quict_checker) == 3 and self.quict_checker[2] == 'quit':
                            broadcasting_message = broadcasting_flag + ' ' + decrypted_client_msg
                            print(f'\n{decrypted_client_msg}')
                            print(f'\n{username} quit, so that connection is closing...')
                            for clients, session_key in self.clients_socket_session_key_mapping.items():
                                if clients == sender:
                                    pass
                                else:
                                    clients.sendall(session_key.encrypt(broadcasting_message.encode()))
                            
                            client.close()
                            self.clients_socket_session_key_mapping.pop(client)
                            print(f' \nnow the remaining members in group chat : {len(self.clients_socket_session_key_mapping)}')
                            break
                        
                        else:
                              
                            print(f'\n{decrypted_client_msg}')
                            broadcasting_message = broadcasting_flag + ' ' + decrypted_client_msg
                            for clients, session_key in self.clients_socket_session_key_mapping.items():
                                if clients == sender:
                                    pass
                                else:
                                    clients.sendall(session_key.encrypt(broadcasting_message.encode()))
                                    
                    elif decrypted_client_msg and len(self.clients_socket_session_key_mapping) < 2:
                        self.quict_checker = decrypted_client_msg.split()
                        
                        if len(self.quict_checker) == 3 and self.quict_checker[2] == "quit":
                            print(f'\n{decrypted_client_msg}')
                            print('\nthe entire connection is closing....')
                            self.server_running = False
                            break
                        else:
                            print(f'\n{decrypted_client_msg}')
            except KeyboardInterrupt:
                print('\nkeyboard intrepted....')
            except Exception as e:
                print(e)
           

        while self.server_running:
            try:
                if not self.server_running:
                    break

                clients_socket, clients_addr = self.gp_chat_svr_socket.accept()

            except TimeoutError:
                continue
            except OSError as e:
                if not self.server_running:
                    break
                else:
                    raise
            if clients_socket:
                if not self.server_running:
                    break
                if clients_socket not in self.clients_socket_session_key_mapping:
                    print(f'\nnew connection arrived , {clients_addr} ')
                    noise = NoiseConnection.from_name(b'Noise_NN_25519_ChaChaPoly_SHA256')
                    noise.set_as_responder()
                    noise.start_handshake()

                    # Perform handshake. Break when finished
                    for action in cycle(['receive', 'send']):
                        if noise.handshake_finished:
                            break
                        elif action == 'send':
                            ciphertext = noise.write_message()
                            clients_socket.sendall(ciphertext)
                        elif action == 'receive':
                            data = clients_socket.recv(2048)
                            plaintext = noise.read_message(data)
                    
                    self.clients_socket_session_key_mapping[clients_socket] = noise
                    threading.Thread(target=server_brodcast, args=(clients_socket,)).start()
                    
    def gp_srvr_snt_msg(self):
        try : 
            server_message_flag = 'admin'
            while self.server_running :
                server_message = input('\nyou : ')
                if not self.server_running:
                    break

                if server_message:
                    server_message_broadcast = server_message_flag + ' ' + self.username + ' : '+ server_message
                    
                    if server_message == 'quit':
                        self.server_running = False
                        for clients, session_key in self.clients_socket_session_key_mapping.items():
                            
                            clients.sendall(session_key.encrypt(server_message_broadcast.encode()))
                        print('you enterd quit , connection going to terminate....')
                        
                        break
                    for clients, session_key in self.clients_socket_session_key_mapping.items():
                        clients.sendall(session_key.encrypt(server_message_broadcast.encode()))
        except KeyboardInterrupt:
            print('keyboard interpted....')
        except Exception as e:
            print(e)
                
    def gp_chat_close(self):
        try :
            for clients in self.clients_socket_session_key_mapping:
                clients.close()
            self.gp_chat_svr_socket.close()
            print('entire connection closed peacefully....')
        except KeyboardInterrupt:
            print("\nServer stopped manually.")


class TorOneToOneServer():
    def __init__(self, username:list):
        self.key_path = Path('.onion_key.txt')
        self.server_running = True
        self.tor_server_socket = socket.socket()
        self.tor_controller = Controller.from_port()
        self.tor_clinet_socket = None
        self.username = username[0]
        self.server_message = None
        self.quit_checker = list()
        self.tor_proto = None
    
    def tor_server_clinet_connect(self):

        self.tor_controller.authenticate()
        if not self.key_path.exists():
            service = self.tor_controller.create_ephemeral_hidden_service({80: 5000}, await_publication = True)
            print("Started a new hidden service with the address of %s.onion" % service.service_id)

            with open(self.key_path, 'w') as key_file:
                key_file.write('%s:%s' % (service.private_key_type, service.private_key))
        else:
            with open(self.key_path) as key_file:
                 key_type, key_content = key_file.read().split(':', 1)

            service = self.tor_controller.create_ephemeral_hidden_service({80: 5000}, key_type = key_type, key_content = key_content, await_publication = True)
            print("Resumed %s.onion" % service.service_id)

        self.tor_server_socket.bind(('127.0.0.1', 5000))
        self.tor_server_socket.listen()

        self.tor_clinet_socket, clinet_addr = self.tor_server_socket.accept()

        self.tor_proto = NoiseConnection.from_name(b'Noise_NN_25519_ChaChaPoly_SHA256')
        self.tor_proto.set_as_responder()
        self.tor_proto.start_handshake()

        for action in cycle(['receive', 'send']):
            if self.tor_proto.handshake_finished:
                break
            elif action == 'send':
                ciphertext = self.tor_proto.write_message()
                self.tor_clinet_socket.sendall(ciphertext)
            elif action == 'receive':
                data = self.tor_clinet_socket.recv(2048)
                plaintext = self.tor_proto.read_message(data)

        return clinet_addr

    def tor_server_snt_message(self):

        while self.server_running:

            message = input('\nyou : ')

            self.server_message = self.username + ' : ' + message
            if not self.server_running:
                break

            if message:

                if message == 'quit':

                    self.tor_clinet_socket.sendall(self.tor_proto.encrypt(self.server_message.encode()))
                    print('you entered quit , entire connection is closing...')

                    self.server_running == False
                    break
                self.tor_clinet_socket.sendall(self.tor_proto.encrypt(self.server_message.encode()))
    
    def tor_server_recv_message(self):
         while self.server_running:

            try :
                client_message = self.tor_clinet_socket.recv(1024)
            except OSError as e :
                if e.winerror in (10053, 10054):
                    print('The connection closed peacefully...')
                else:
                    raise
            except Exception as e :
                print(e)
                
            if not self.server_running:
                break

            client_message_decrypted = self.tor_proto.decrypt(client_message.decode())
            self.quit_checker = list(client_message_decrypted.split())
            if len(self.quit_checker) == 3 and self.quit_checker[2] == 'quit':
                self.server_running = False
                print(f'\n{client_message_decrypted}') 
                print('\n the connection is terminating ...',flush=True)
                
                break
            print(f'\n {client_message_decrypted}')

    def tor_server_closing(self):
        try:
            if self.tor_clinet_socket:
                self.tor_clinet_socket.close()
        except:
            pass
        try:
            if self.tor_server_socket:
                self.tor_server_socket.close()
        except:
            pass
        try:
            if self.tor_controller:
                self.tor_controller.close()
        except:
            pass

class TorGpServer():
    def __init__(self, username:list):
        self.tor_server_username = username[0]
        self.tor_gp_chat_svr_socket = socket.socket()
        self.tor_gp_chat_controller = Controller.from_port()
        self.key_path = Path('.onion_key.txt')
        self.tor_server_running = True
        self.tor_clients_socket_session_key_mapping = dict()
        self.quict_checker = list()
    def tor_server_client_connection(self):
        self.tor_gp_chat_controller.authenticate()
        if not self.key_path.exists():
            service = self.tor_gp_chat_controller.create_ephemeral_hidden_service({80: 5000}, await_publication = True)
            print("Started a new hidden service with the address of %s.onion" % service.service_id)

            with open(self.key_path, 'w') as key_file:
                key_file.write('%s:%s' % (service.private_key_type, service.private_key))
        else:
            with open(self.key_path) as key_file:
                 key_type, key_content = key_file.read().split(':', 1)

        service = self.tor_gp_chat_controller.create_ephemeral_hidden_service({80: 5000}, key_type = key_type, key_content = key_content, await_publication = True)
        print("Resumed %s.onion" % service.service_id)
        self.tor_gp_chat_svr_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tor_gp_chat_svr_socket.settimeout(1.0)
        self.tor_gp_chat_svr_socket.bind(('127.0.0.1', 5000))
        self.tor_gp_chat_svr_socket.listen()
        
        print('\nserver started listening.....')
        def tor_server_brodcast(client):
            try : 
                
                while self.tor_server_running:
                    sender = client
                    
                    
                    if not self.tor_server_running:
                        break
                    try:
                        client_message = client.recv(1024)
                    except OSError as e:
                        if e.winerror in (10053, 10054):
                            pass
                        else:
                            raise
                    '''if not client_message:
                        break'''
                    if not self.server_running:
                        break
                
                    
                    session_key_client = self.tor_clients_socket_session_key_mapping[client]
                    decrypted_client_msg = session_key_client.decrypt(client_message).decode()
                    
                    broadcasting_flag = 'broadcasting'
                    
                    if decrypted_client_msg and len(self.tor_clients_socket_session_key_mapping) >= 2:
                        self.quict_checker = decrypted_client_msg.split()
                        username = self.quict_checker[0]
                        if len(self.quict_checker) == 3 and self.quict_checker[2] == 'quit':
                            broadcasting_message = broadcasting_flag + ' ' + decrypted_client_msg
                            print(f'\n{decrypted_client_msg}')
                            print(f'\n{username} quit, so that connection is closing...')
                            for clients, session_key in self.tor_clients_socket_session_key_mapping.items():
                                if clients == sender:
                                    pass
                                else:
                                    clients.sendall(session_key.encrypt(broadcasting_message.encode()))
                            
                            client.close()
                            self.tor_clients_socket_session_key_mapping.pop(client)
                            print(f' \nnow the remaining members in group chat : {len(self.tor_clients_socket_session_key_mapping)}')
                            break
                        
                        else:
                              
                            print(f'\n{decrypted_client_msg}')
                            broadcasting_message = broadcasting_flag + ' ' + decrypted_client_msg
                            for clients, session_key in self.tor_clients_socket_session_key_mapping.items():
                                if clients == sender:
                                    pass
                                else:
                                    clients.sendall(session_key.encrypt(broadcasting_message.encode()))
                                    
                    elif decrypted_client_msg and len(self.clients_socket_session_key_mapping) < 2:
                        self.quict_checker = decrypted_client_msg.split()
                        
                        if len(self.quict_checker) == 3 and self.quict_checker[2] == "quit":
                            print(f'\n{decrypted_client_msg}')
                            print('\nthe entire connection is closing....')
                            self.server_running = False
                            break
                        else:
                            print(f'\n{decrypted_client_msg}')
            except KeyboardInterrupt:
                print('\nkeyboard intrepted....')
            except Exception as e:
                print(e)
           

        while self.tor_server_running:
            try:
                if not self.server_running:
                    break

                clients_socket, clients_addr = self.tor_gp_chat_svr_socket.accept()

            except TimeoutError:
                continue
            except OSError as e:
                if not self.server_running:
                    break
                else:
                    raise
            if clients_socket:
                if not self.server_running:
                    break
                if clients_socket not in self.tor_clients_socket_session_key_mapping:
                    print(f'\nnew connection arrived , {clients_addr} ')
                    noise = NoiseConnection.from_name(b'Noise_NN_25519_ChaChaPoly_SHA256')
                    noise.set_as_responder()
                    noise.start_handshake()

                    # Perform handshake. Break when finished
                    for action in cycle(['receive', 'send']):
                        if noise.handshake_finished:
                            break
                        elif action == 'send':
                            ciphertext = noise.write_message()
                            clients_socket.sendall(ciphertext)
                        elif action == 'receive':
                            data = clients_socket.recv(2048)
                            plaintext = noise.read_message(data)
                    
                    self.tor_clients_socket_session_key_mapping[clients_socket] = noise
                    threading.Thread(target=tor_server_brodcast, args=(clients_socket,)).start()
                    
    def tor_gp_srvr_snt_msg(self):
        try : 
            tor_server_message_flag = 'admin'
            while self.tor_server_running :
                server_message = input('\nyou : ')
                if not self.tor_server_running:
                    break

                if server_message:
                    server_message_broadcast = tor_server_message_flag + ' ' + self.tor_server_username + ' : '+ server_message
                    
                    if server_message == 'quit':
                        self.tor_server_running = False
                        for clients, session_key in self.tor_clients_socket_session_key_mapping.items():
                            
                            clients.sendall(session_key.encrypt(server_message_broadcast.encode()))
                        print('you enterd quit , connection going to terminate....')
                        
                        break
                    for clients, session_key in self.tor_clients_socket_session_key_mapping.items():
                        clients.sendall(session_key.encrypt(server_message_broadcast.encode()))
        except KeyboardInterrupt:
            print('keyboard interpted....')
        except Exception as e:
            print(e)
                
    def tor_gp_chat_close(self):
        try :
            if self.tor_clients_socket_session_key_mapping:
                for clients in self.tor_clients_socket_session_key_mapping:
                    clients.close()
            if self.tor_gp_chat_svr_socket:
                self.tor_gp_chat_svr_socket.close()
            if self.tor_gp_chat_controller:
                self.tor_gp_chat_controller.close()

            print('entire connection closed peacefully....')
        except KeyboardInterrupt:
            print("\nServer stopped manually.")



    




    

        

        
            

                        



        