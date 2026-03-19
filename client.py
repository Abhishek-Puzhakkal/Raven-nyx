import socket
from noise.connection import NoiseConnection
from pathlib import Path
from stem.control import Controller
import socks
import base64
import hashlib

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
            recv_ext_byt = RecvExactBytes()
            message = self.proto.write_message()
            message_size = len(message).to_bytes(4, 'big')
            self.client_socket.sendall(message_size + message)
            recv_msg_header = recv_ext_byt.recv_exact_bytes(self.client_socket, 4)
            received = recv_ext_byt.recv_exact_bytes(self.client_socket, int.from_bytes(recv_msg_header, 'big'))
            payload = self.proto.read_message(received)
            print('handshake finished')

            
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

                self.clinet_message = self.username + ' : '+ message

                encrypted_message = self.proto.encrypt(self.clinet_message.encode())

                encrypted_message_size_header = len(encrypted_message).to_bytes(4, 'big')


                if not self.running:
                    break

                if message == 'quit':

                    self.client_socket.sendall(encrypted_message_size_header + encrypted_message)
                    print(f'\nyou entered "quit", connection is terminating....', flush=True)
                    self.running = False
                    
                    break
                         
                self.client_socket.sendall(encrypted_message_size_header + encrypted_message)
                
    def client_recv_msg(self):

        while self.running:
            try: 
                recv_exact_byte = RecvExactBytes()
                
                header_size = recv_exact_byte.recv_exact_bytes(self.client_socket, 4)
                
                message_size = int.from_bytes(header_size, 'big')
                
                servermessage = recv_exact_byte.recv_exact_bytes(self.client_socket, message_size)
            except ConnectionError:
                print('connection error...')
                self.running = False
                break
                
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
    def client_gp_chat_connection(self):
        try :
            self.client_gp_chat_socket.connect((self.addr, self.port))
            print('connection successfull \n handshake starting...')
            self.proto = NoiseConnection.from_name(b'Noise_NN_25519_ChaChaPoly_SHA256')
            self.proto.set_as_initiator()
            self.proto.start_handshake()
            recv_ext_byt = RecvExactBytes()
            message = self.proto.write_message()
            message_size = len(message).to_bytes(4, 'big')
            self.client_gp_chat_socket.sendall(message_size + message)
            recv_msg_header = recv_ext_byt.recv_exact_bytes(self.client_gp_chat_socket, 4)
            received = recv_ext_byt.recv_exact_bytes(self.client_gp_chat_socket, int.from_bytes(recv_msg_header, 'big'))
            payload = self.proto.read_message(received)
            print('handshake finished.')
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

                    encrypted_message = self.proto.encrypt(msg.encode())

                    encrypted_message_size_header = len(encrypted_message).to_bytes(4, 'big')
                    
                    if message == 'quit':
                        self.client_gp_chat_socket.sendall(encrypted_message_size_header + encrypted_message)
                        print('you enterd the "quit", so conection terminating....')
                        self.client_running = False
                        break

                    self.client_gp_chat_socket.sendall(encrypted_message_size_header + encrypted_message)
        except KeyboardInterrupt:
            print('keyboard intrepted ....')
        except Exception as e :
            
            print(e)
    def client_gp_cht_recv_msg(self):
        try:
            while self.client_running:
                try:
                    recv_exact_byte = RecvExactBytes()
                    header_size = recv_exact_byte.recv_exact_bytes(self.client_gp_chat_socket, 4)
                    message_size = int.from_bytes(header_size, 'big')

                    message = recv_exact_byte.recv_exact_bytes(self.client_gp_chat_socket, message_size)
                except ConnectionError:
                    print('connection error found...')
                    print('connection closing...')
                    self.client_running = False
                    break
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

class TorClient():
    def __init__(self, onion_addr, username):
        self.tor_proto = None
        self.username = username[0]
        self.tor_server_addr = onion_addr[0]
        self.client_socket = socks.socksocket()
        self.clinet_message = None
        self.server_message = None
        self.running = True
        self.quit_checker = list()
        

    def clinet_tor_server_connection(self) -> bool:
        try:

            validation = OnionAddressValidation()

            if validation.validate_onion_addrs(self.tor_server_addr):

                contact_list = ContactLsit()
                contact_list_exist = Path('.contact_list')

                if contact_list_exist.exists():
                    print(f'checking is {self.tor_server_addr} is in you contact list  ')
                    if not contact_list.check_address_exist(self.tor_server_addr):
                        print(f'{self.tor_server_addr} is not in your contact list you need to add it ??')
                        choice = input('enter yes or no : ').lower().strip()

                        while choice != 'yes' and choice != 'no':

                            choice = input('you must enter yse or no :- ').lower().strip()

                        if choice == 'yes' :
                            name = input('enter the name of the onion address holder : ').lower().strip()
                            if not name:
                                while not name:
                                    name = input('enter the name of the onion address holder : ').lower().strip()

                            contact_list.add_address([name, self.tor_server_addr])
                            print(f'{name} : {self.tor_server_addr}  saved to ".contact_list" file in this directory  ')
                        else:
                            pass
                else:
                    print("currently contact list not exist , \n you need to create one and add this address to contact list  ??? ")
                    choice = input('enter yes or no : ').lower().strip()

                    while choice != 'yes' and choice != 'no':

                        choice = input('you must enter yes or no :- ').lower().strip()

                    if choice == 'yes':
                        name = input('enter the name of the onion address holder : ').lower().strip()
                        if not name:
                            while not name :
                                name = input('enter the name of the onion address holder : ').lower().strip()

                        contact_list.add_address([name, self.tor_server_addr])
                        print(f'{name} : {self.tor_server_addr}  saved to ".contact_list" file in this directory  ')
                    else:
                        pass
                        

                self.client_socket.set_proxy(socks.SOCKS5, '127.0.0.1', 9050)
                self.client_socket.connect((self.tor_server_addr, 80))
                print(f'client connected to {self.tor_server_addr}')
                print('handshake starting....')
                self.tor_proto = NoiseConnection.from_name(b'Noise_NN_25519_ChaChaPoly_SHA256')
                self.tor_proto.set_as_initiator()
                self.tor_proto.start_handshake()
                recv_ext_byt = RecvExactBytes()
                message = self.tor_proto.write_message()
                message_size = len(message).to_bytes(4, 'big')
                self.client_socket.sendall(message_size + message)
                recv_msg_header = recv_ext_byt.recv_exact_bytes(self.client_socket, 4)
                received = recv_ext_byt.recv_exact_bytes(self.client_socket, int.from_bytes(recv_msg_header, 'big'))
                payload = self.tor_proto.read_message(received)
                print('handshake finished.')

                
                return True
            else:
                print(f'{self.tor_server_addr} is not a vlid onion addres, communcation terminating')
                return False
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
                self.clinet_message = self.username + ' : '+ message

                encrypted_message = self.tor_proto.encrypt(self.clinet_message.encode())

                encrypted_message_size_header = len(encrypted_message).to_bytes(4, 'big')

                if message == 'quit':

                    self.client_socket.sendall(encrypted_message_size_header + encrypted_message)
                    print(f'\nyou entered "quit", connection is terminating....', flush=True)
                    self.running = False
                    
                    break

                self.client_socket.sendall(encrypted_message_size_header + encrypted_message)       

    def client_recv_msg(self):

        while self.running:
            try: 
                recv_exact_byte = RecvExactBytes()
                header_size = recv_exact_byte.recv_exact_bytes(self.client_socket, 4)
                message_size = int.from_bytes(header_size, 'big')

                servermessage = recv_exact_byte.recv_exact_bytes(self.client_socket, message_size)
            except ConnectionError:
                print('empty chunk found...')
                self.running = False
                break
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
                self.server_message = self.tor_proto.decrypt(servermessage).decode()
                
            
                if not self.running:
                    
                    break
                
                self.quit_checker = self.server_message.split()

                if len(self.quit_checker) == 3 and self.quit_checker[2] == 'quit':
                    
                    print(f'\n{self.server_message}')
                    print('\nthe connection is terminating....', flush=True)
                    self.running = False
                    break
                print(f'\n{self.server_message}')      

    def client_conn_close(self):
        try:
            self.client_socket.close()
        except KeyboardInterrupt:
            print("\nServer stopped manually.")

class TorGpChatClient:
    def __init__(self, addr:list , username:list):
        self.uername = username[0]
        self.tor_server_addr = addr[0]
        self.tor_client_gp_chat_socket = socks.socksocket()
        self.tor_client_running = True
        self.quit_checker = list()
        self.tor_proto = None
    def client_gp_chat_connection(self):
        try :
            validation = OnionAddressValidation()

            if validation.validate_onion_addrs(self.tor_server_addr):

                contact_list = ContactLsit()
                contact_list_exist = Path('.contact_list')
                if contact_list_exist.exists():
                    print(f'checking is {self.tor_server_addr} in you contact list')
                    if not contact_list.check_address_exist(self.tor_server_addr):
                        print(f'{self.tor_server_addr} is not in your contact list you need to add it ??')
                        choice = input('enter yes or no : ').lower().strip()

                        while choice != 'yes' and choice != 'no':
                            choice = input('enter yes or no : ').lower().strip()


                        if choice == 'yes':
                            name = input('enter the name of the onion address holder : ').lower()
                            contact_list.add_address([name, self.tor_server_addr])
                            print(f'{name} : {self.tor_server_addr}  saved to ".contact_list" file in this directory  ')
                        elif choice == 'no':
                            pass
                        
                else:
                    print("currently contact list not exist , \n you need to create one and add this address to contact list  ??? ")
                    choice = input('enter yes or no : ').lower().strip()

                    while choice != 'yes' and choice != 'no':

                        choice = input('you must enter yes or no :- ').lower().strip()

                    if choice == 'yes' :
                        name = input('enter the name of the onion address holder : ').lower().strip()
                        if not name:
                            while not name:
                                name = input('enter the name of the onion address holder : ').lower().strip()

                        contact_list.add_address([name, self.tor_server_addr])
                        print(f'{name} : {self.tor_server_addr}  saved to ".contact_list" file in this directory  ')
                    else:
                        pass
                   


            
                self.tor_client_gp_chat_socket.set_proxy(socks.SOCKS5, '127.0.0.1', 9050)

                self.tor_client_gp_chat_socket.connect((self.tor_server_addr, 80))
                print('connection successfull \n handshake starting...')
                self.tor_proto = NoiseConnection.from_name(b'Noise_NN_25519_ChaChaPoly_SHA256')
                self.tor_proto.set_as_initiator()
                self.tor_proto.start_handshake()
                recv_ext_byt = RecvExactBytes()
                message = self.tor_proto.write_message()
                self.tor_client_gp_chat_socket.sendall(len(message).to_bytes(4, 'big') + message)
                recv_msg_header = recv_ext_byt.recv_exact_bytes(self.tor_client_gp_chat_socket, 4)
                received = recv_ext_byt.recv_exact_bytes(self.tor_client_gp_chat_socket, int.from_bytes(recv_msg_header, 'big'))
                payload = self.tor_proto.read_message(received)
                print('handshake finished')
                return True
            else:
                print(f'{self.tor_server_addr} is not a valid onion address , communication terminating ...')
                return False
            
        except Exception as e :
            
            print(e)
    def tor_client_gp_cht_snt_msg(self):
        try:

            while self.tor_client_running:
                message = input('\nyou : ')
                encrypted_message_size_header = None
                if not self.tor_client_running:
                    break
                
                if message:
                    msg = self.uername + ' : ' + message

                    encrypted_message = self.tor_proto.encrypt(msg.encode())

                    encrypted_message_size_header = len(encrypted_message).to_bytes(4, 'big')
                    
                    
                    if message == 'quit':
                        self.tor_client_gp_chat_socket.sendall(encrypted_message_size_header + encrypted_message)
                        print('you enterd the "quit", so conection terminating....')
                        self.tor_client_running = False
                        break

                    self.tor_client_gp_chat_socket.sendall(encrypted_message_size_header + encrypted_message)

        except KeyboardInterrupt:
            print('keyboard intrepted ....')
        except Exception as e :
            
            print(e)
    def tor_client_gp_cht_recv_msg(self):
        try:
            while self.tor_client_running:
                try:
                    recv_exact_byte = RecvExactBytes()
                    header_size = recv_exact_byte.recv_exact_bytes(self.tor_client_gp_chat_socket, 4)
                    message_size = int.from_bytes(header_size, 'big')

                    message = recv_exact_byte.recv_exact_bytes(self.tor_client_gp_chat_socket, message_size)
                except ConnectionError:
                    print('empty chunk')
                    self.tor_client_running = False
                    break
                except OSError as e:
                    if e.winerror in (10053, 10054):
                        pass
                    else: raise
                except Exception as e:
                    
                    print(e)
                
                if not self.tor_client_running:
                    break
                
                decrypted_msg = self.tor_proto.decrypt(message).decode()

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
                        self.tor_client_running = False
                        break
                    print(f'\n{printing_msg}')
        except KeyboardInterrupt :
            print('\nkeyboard interepted...')
        except Exception as e :
            
            print(e)
                

    def tor_client_gp_cht_connection_cls(self):
        try :
            self.tor_client_gp_chat_socket.close()
            print('\nthe connection closed peacefully....')
        except KeyboardInterrupt:
            print("\nServer stopped manually.")

class RecvExactBytes():
    def recv_exact_bytes(self, connection_socket, exact_byte:int):

        data = b''

        while len(data) < exact_byte:

            try:

                chunk = connection_socket.recv( exact_byte - len(data))

                if not chunk:
                    raise ConnectionError("Peer disconnected")

                data += chunk
            except Exception as e:
                raise e 
        
        return data


class ContactLsit():
    def __init__(self):
    
        self.contact_list = Path('.contact_list')
    def add_address(self, details : list):
        if self.contact_list.exists():

            with open('.contact_list', 'a') as file:
                file.write(f"{details[0]} : {details[1]}\n")
        else:
            with open('.contact_list', 'w') as file:
                file.write(f"{details[0]} : {details[1]}\n")
            self.contact_list.chmod(0o600)
    
    def check_address_exist(self, detail):
        
        address_first = True

        while address_first:
            with open('.contact_list', 'r') as file:
                for line in file:
                    line = line.strip()
                    if line.endswith(detail):
                        parts = line.split(':')
                        if parts[1].strip() == detail:
                            print(f'contact found {parts[0]} : {parts[1]}')
                            return True
                
                address_first = False
        
        while not address_first:
            with open('.contact_list', 'r') as file:
                
                for line in file:
                    line = line.strip()
                    if line.startswith(detail):
                        address_first = True
                        parts = line.split(':')
                        if parts[0].strip() == detail:
                            print(f'contact found {parts[0]} : {parts[1]}')
                            return True
                print('contact not exist in .contact_list ')
                address_first = True

        return False
    
    def show_full_contact(self):

        path_exist = Path('.contact_list')

        if path_exist.exists():

            with open('.contact_list', 'r') as file:

                for line in file:

                    print(f'{line} \n ')
        else:
            print("currently '.contact_list' file not exist ")

'''
source = https://spec.torproject.org/address-spec

For version 3 onion service addresses, onion_address is defined as:


     onion_address = base32(PUBKEY | CHECKSUM | VERSION)
     CHECKSUM = SHA3_256(".onion checksum" | PUBKEY | VERSION)[:2]

     where:
       - PUBKEY is the 32-byte ed25519 master pubkey (KP_hs_id)
         of the onion service.
       - VERSION is a one-byte version field (default value '\x03')
       - ".onion checksum" is a constant string
       - CHECKSUM is truncated to two bytes before inserting it in onion_address
'''

class OnionAddressValidation():
    def validate_onion_addrs(self, onion_address : str):
        try:
            addrs = onion_address.replace('.onion', '')
            if len(addrs) != 56:
                return False
            
            base_32_decoded = base64.b32decode(addrs.upper())

            pubkey = base_32_decoded[0:32]
            checksum = base_32_decoded[32:34]
            version = base_32_decoded[34:35]

            if version != b'\x03':
                return False
            
            recalculating_checksum = hashlib.sha3_256(b'.onion checksum' + pubkey + version).digest()

            if checksum != recalculating_checksum[:2]:
                return False
        
            return True
        except Exception as e :
            print(e)
            return False








        
        
    




    

        



        
        