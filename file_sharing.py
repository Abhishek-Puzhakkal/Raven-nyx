import socket
from cryptography.fernet import Fernet
from noise.connection import NoiseConnection
from pathlib import Path
from tqdm import tqdm
from server import RecvExactBytes
import hashlib
from itertools import cycle
import json
from stem.control import Controller
import socks


class File_sender():
    def __init__(self, addr, port, file_path):
        self.key = b'5BH7FCe5mrbIMGbebcuy3wg9PCjhsk3_qqVqZbtuU4s='
        self.addr = addr[0]
        self.port = port[0]
        self.file_path = file_path[0]
        self.sender_socket = socket.socket()
    
    def send_file(self):
        path_of_file = Path(self.file_path).expanduser()
        file_encryption = Fernet(self.key)

        if path_of_file.is_file():
            file_size = path_of_file.stat().st_size

            self.sender_socket.connect((self.addr, self.port))
            print('connection succesfull....')

            self.sender_socket.sendall(str(file_size).encode())

            with open(path_of_file, 'rb') as file:
                p_bar = tqdm(total=file_size, unit='B', unit_scale=True)

                while True:

                    file_chunk = file.read(1024)
                    

                    if not file_chunk:
                        break

                    encrypted_file_chunk = file_encryption.encrypt(file_chunk)
                    self.sender_socket.sendall(encrypted_file_chunk)
                    p_bar.update(len(file_chunk))
                p_bar.close()
                print('file sharing completed...')
            self.sender_socket.close()
        else:
            print(f'{self.file_path} is not a file or not exist  in machine')


class file_reciver():
    def __init__(self, file_path, port):
        self.key = b'5BH7FCe5mrbIMGbebcuy3wg9PCjhsk3_qqVqZbtuU4s='
        self.port = port[0]
        self.file_path = file_path[0]
        self.recever_socket = socket.socket()
    
    def recvfile(self):
        filepath = Path(self.file_path).expanduser()
        filepath.parent.mkdir(parents=True, exist_ok=True)
        file_decryption = Fernet(self.key)
        if not filepath.exists():
            self.recever_socket.bind(('0.0.0.0', self.port))
            self.recever_socket.listen()
            file_sender, file_sender_addr = self.recever_socket.accept()

            if file_sender:
                print(f'machine connected to {file_sender_addr}')
                file_size = int(file_sender.recv(1024).decode())
                with open(filepath, 'wb') as file:
                    p_bar = tqdm(total=file_size, unit='B', unit_scale=True)

                    while True:

                        file_chunk = file_sender.recv(1024)
                       
                        if not file_chunk:
                            break

                        decrypted_file_chunk = file_decryption.decrypt(file_chunk)
                        file.write(decrypted_file_chunk)
                        p_bar.update(len(file_chunk))
                    
                    p_bar.close()
                    print('file received completely...')
            self.recever_socket.close()
        else:
            print(f'{self.file_path} alredy exist in machine, to recv the file you need a empty file or a new file ')

class LanFilesender():
    def __init__(self, file_path, receiver_addr, port ):
        self.file_path = file_path[0]
        self.recevier_addr = receiver_addr[0]
        self.port = port[0]
        self.file_sender_socket = socket.socket()
        self.session_key =  NoiseConnection.from_name(b'Noise_NN_25519_ChaChaPoly_SHA256')

    
    def send_file(self):
        
        file_path = Path(self.file_path).expanduser()

        if file_path.exists():

            self.file_sender_socket.connect((self.recevier_addr, self.port))
            print('\nconnection successfull... \n handshake starting....')
            self.session_key.set_as_initiator()
            self.session_key.start_handshake()
            message = self.session_key.write_message()
            message_size_header = len(message).to_bytes(4,'big')
            self.file_sender_socket.sendall(message_size_header + message)
            recv_exact_byte = RecvExactBytes()

            received_message_header = recv_exact_byte.recv_exact_bytes(self.file_sender_socket, 4)
            received_message_size = int.from_bytes(received_message_header, 'big')

            received_message = recv_exact_byte.recv_exact_bytes(self.file_sender_socket, received_message_size)

            payload = self.session_key.read_message(received_message)

            print(f'\nhandshake finished...\n creating checksum of   {self.file_path}')
            sha256_hash = hashlib.sha256()

            with open(file_path, 'rb') as file:
                while True:
                    data = file.read(65536)
                    if not data:
                        break
                    
                    sha256_hash.update(data)
            
            print(f'\nchecksum :-  {sha256_hash.hexdigest()}')

            file_size = file_path.stat().st_size

            file_sending_header = {

                'file_size' : file_size,
                'checksum' : sha256_hash.hexdigest()

            }

            encrypted_file_sending_header = self.session_key.encrypt(json.dumps(file_sending_header).encode())
            len_encrypted_file_sending_header = len(encrypted_file_sending_header).to_bytes(2, 'big')

            self.file_sender_socket.sendall(len_encrypted_file_sending_header + encrypted_file_sending_header)
            
            response_flag_size = recv_exact_byte.recv_exact_bytes(self.file_sender_socket, 2)

            response_flag_size_int_form = int.from_bytes(response_flag_size,'big')

            response_flag = recv_exact_byte.recv_exact_bytes(self.file_sender_socket, response_flag_size_int_form)

            if 'FILE_HEADER_GOT_SUCCESSFULLY' == self.session_key.decrypt(response_flag).decode():

                print('\nfile sending...')

                with open(file_path, 'rb') as file:
                    p_bar = tqdm(total=file_size, unit='B', unit_scale=True, desc='Sending')

                    while chunk := file.read(64 * 1024):
                        encrypted_chunk = self.session_key.encrypt(chunk)
                        encrypted_chunk_size = len(encrypted_chunk).to_bytes(4, 'big')
                        self.file_sender_socket.sendall(encrypted_chunk_size + encrypted_chunk)
                        p_bar.update(len(chunk))
                    p_bar.close()
                        
                print('\nfile sending completed ...')

                print('\nwaiting for client verification...')
                response_flag_size = recv_exact_byte.recv_exact_bytes(self.file_sender_socket, 2)

                response_flag_size_int_form = int.from_bytes(response_flag_size,'big')

                response_flag = recv_exact_byte.recv_exact_bytes(self.file_sender_socket, response_flag_size_int_form)

                if 'FILE_DOWNLOADED_SUCCESSFULLY' == self.session_key.decrypt(response_flag).decode():
                    print('\nclient verification successfull, file sended and recevied successfully ...')
                    self.file_sender_socket.close()
                else:
                    print('\nsomething went wrong...')
                    print('\nclient failed while verifying the checksum, checksum missmatch occured ... \n please repeat the filesharing..')
                    self.file_sender_socket.close()
            
            else:
                print('\nsomething went wrong...')
                self.file_sender_socket.close()
        else:
            print(f'\n{self.file_path} not exists...')


class LanFileReceiver():
    def __init__(self, file_path, port):
        self.file_path = file_path[0]
        self.port = port[0]
        self.file_recevier_socket = socket.socket()
        self.session_key = NoiseConnection.from_name(b'Noise_NN_25519_ChaChaPoly_SHA256')

    def recv_file(self):
        
        file_path = Path(self.file_path).expanduser()

        if file_path.exists():

            user_choice = input(f'{self.file_path} alredy exists, you need to continue , type "yes" or "no" : ').lower()

            if user_choice != 'yes' and user_choice != 'no':
                print('invalid input')
            elif user_choice == 'no':
                print('please run the command once again with valid file path')
            elif user_choice == 'yes':
                print('okay then you need to rewrite the file or append to the file ?')
                print('for rewriting the file just type : R \n for appending the file just type : A')
                
                user_choice = input(' : ').upper()

                if user_choice != 'R' and user_choice != 'A':
                    print('invalid input')
                
                elif user_choice == 'R':
                    pass
                else:
                    pass
        else:

            self.file_recevier_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            self.file_recevier_socket.bind(('0.0.0.0', self.port))

            self.file_recevier_socket.listen()

            client_socket , addr = self.file_recevier_socket.accept()

            print(f'\n{addr} connected successfully...\n handshake initialising...')

            self.session_key.set_as_responder()
            self.session_key.start_handshake()

            for action in cycle(['receive', 'send']):
                if self.session_key.handshake_finished:
                    break
                elif action == 'send':
                    ciphertext = self.session_key.write_message()
                    ciphertext_size_header = len(ciphertext).to_bytes(4,'big')
                    client_socket.sendall(ciphertext_size_header + ciphertext)
                elif action == 'receive':
                    recv_exact_byte = RecvExactBytes()

                    received_message_header = recv_exact_byte.recv_exact_bytes(client_socket, 4)
                    received_message_size = int.from_bytes(received_message_header, 'big')

                    received_message = recv_exact_byte.recv_exact_bytes(client_socket, received_message_size)    

                    plaintext = self.session_key.read_message(received_message)                

            print(f'\nhandshake finished...')

            file_header_size = recv_exact_byte.recv_exact_bytes(client_socket, 2)

            encrypted_file_header = recv_exact_byte.recv_exact_bytes(client_socket, int.from_bytes(file_header_size,'big'))

            file_header = json.loads(self.session_key.decrypt(encrypted_file_header).decode())

            file_size = file_header['file_size']
            
            checksum = file_header['checksum']
            print(f'\nsender given metadata  file_size_in_bytes : { file_size}   checksum = {checksum}')

            if file_size and checksum:
                response_flag = self.session_key.encrypt('FILE_HEADER_GOT_SUCCESSFULLY'.encode())

                size_response_flag = len(response_flag).to_bytes(2, 'big')

                client_socket.sendall(size_response_flag + response_flag)

                with open(file_path, 'wb') as file:

                    received_chunk_size = 0

                    p_bar = tqdm(total=file_size, unit='B', unit_scale=True, desc="Receiving")

                    while received_chunk_size < file_size:

                        chunk_size = recv_exact_byte.recv_exact_bytes(client_socket, 4)

                        encrypted_chunk = recv_exact_byte.recv_exact_bytes(client_socket, int.from_bytes(chunk_size, 'big'))
                        decrypted_chunk = self.session_key.decrypt(encrypted_chunk)
                        

                        if not encrypted_chunk:
                            break


                        file.write(decrypted_chunk)

                        received_chunk_size += len(decrypted_chunk)

                        p_bar.update(len(decrypted_chunk))
                    
                    p_bar.close()
                
                print('\nfile received ...\n Recalculating checksum of received file ...')

                sha256_hash = hashlib.sha256()

                with open(file_path, 'rb') as file:
                    while True:
                        data = file.read(65536)
                        if not data:
                            break
                        
                        sha256_hash.update(data)

                if sha256_hash.hexdigest() == checksum:

                    print(f'\nRecalculated_checksum :- {sha256_hash.hexdigest()}\nChecksum matches')
                    print('File received successfully...')
                    response_flag = self.session_key.encrypt('FILE_DOWNLOADED_SUCCESSFULLY'.encode())
                    response_flag_size = len(response_flag).to_bytes(2, 'big')
                    client_socket.sendall(response_flag_size + response_flag)
                    client_socket.close()
                    self.file_recevier_socket.close()
                else:
                    response_flag = self.session_key.encrypt('FILE_DOWNLOADED_UNSUCCESSFULLY'.encode())
                    response_flag_size = len(response_flag).to_bytes(2, 'big')
                    client_socket.sendall(response_flag_size + response_flag)
                    print('\nSomthing went wrong... \n Checksum missmatch...')
                    print(f'\nsender given checksum :- {checksum}')
                    print(f'\nreceived file checksum :- {sha256_hash.hexdigest()} \n please resume the program ')
                    client_socket.close()
                    self.file_recevier_socket.close()

class TorFilesender():
    def __init__(self, file_path, onion_addr):
        self.file_path = file_path[0]
        self.recevier_addr = onion_addr[0]
        self.file_sender_socket = socks.socksocket()
        self.session_key =  NoiseConnection.from_name(b'Noise_NN_25519_ChaChaPoly_SHA256')

    
    def send_file(self):
        
        file_path = Path(self.file_path).expanduser()

        if file_path.exists():

            self.file_sender_socket.set_proxy(socks.SOCKS5, '127.0.0.1', 9050)
            self.file_sender_socket.connect((self.recevier_addr, 80))
            print('\nconnection successfull... \n handshake starting....')
            self.session_key.set_as_initiator()
            self.session_key.start_handshake()
            message = self.session_key.write_message()
            message_size_header = len(message).to_bytes(4,'big')
            self.file_sender_socket.sendall(message_size_header + message)
            recv_exact_byte = RecvExactBytes()

            received_message_header = recv_exact_byte.recv_exact_bytes(self.file_sender_socket, 4)
            received_message_size = int.from_bytes(received_message_header, 'big')

            received_message = recv_exact_byte.recv_exact_bytes(self.file_sender_socket, received_message_size)

            payload = self.session_key.read_message(received_message)

            print(f'\nhandshake finished...\n creating checksum of   {self.file_path}')
            sha256_hash = hashlib.sha256()

            with open(file_path, 'rb') as file:
                while True:
                    data = file.read(65536)
                    if not data:
                        break
                    
                    sha256_hash.update(data)
            
            print(f'\nchecksum :-  {sha256_hash.hexdigest()}')

            file_size = file_path.stat().st_size

            file_sending_header = {

                'file_size' : file_size,
                'checksum' : sha256_hash.hexdigest()

            }

            encrypted_file_sending_header = self.session_key.encrypt(json.dumps(file_sending_header).encode())
            len_encrypted_file_sending_header = len(encrypted_file_sending_header).to_bytes(2, 'big')

            self.file_sender_socket.sendall(len_encrypted_file_sending_header + encrypted_file_sending_header)
            
            response_flag_size = recv_exact_byte.recv_exact_bytes(self.file_sender_socket, 2)

            response_flag_size_int_form = int.from_bytes(response_flag_size,'big')

            response_flag = recv_exact_byte.recv_exact_bytes(self.file_sender_socket, response_flag_size_int_form)

            if 'FILE_HEADER_GOT_SUCCESSFULLY' == self.session_key.decrypt(response_flag).decode():

                print('\nfile sending...')

                with open(file_path, 'rb') as file:
                    p_bar = tqdm(total=file_size, unit='B', unit_scale=True, desc='Sending')

                    while chunk := file.read(64 * 1024):
                        encrypted_chunk = self.session_key.encrypt(chunk)
                        encrypted_chunk_size = len(encrypted_chunk).to_bytes(4, 'big')
                        self.file_sender_socket.sendall(encrypted_chunk_size + encrypted_chunk)
                        p_bar.update(len(chunk))
                    p_bar.close()
                        
                print('\nfile sending completed ...')

                print('\nwaiting for client verification...')
                response_flag_size = recv_exact_byte.recv_exact_bytes(self.file_sender_socket, 2)

                response_flag_size_int_form = int.from_bytes(response_flag_size,'big')

                response_flag = recv_exact_byte.recv_exact_bytes(self.file_sender_socket, response_flag_size_int_form)

                if 'FILE_DOWNLOADED_SUCCESSFULLY' == self.session_key.decrypt(response_flag).decode():
                    print('\nclient verification successfull, file sended and recevied successfully ...')
                    self.file_sender_socket.close()
                else:
                    print('\nsomething went wrong...')
                    print('\nclient failed while verifying the checksum, checksum missmatch occured ... \n please repeat the filesharing..')
                    self.file_sender_socket.close()
            
            else:
                print('\nsomething went wrong...')
                self.file_sender_socket.close()
        else:
            print(f'\n{self.file_path} not exists...')


class TorFileReceiver():
    def __init__(self, file_path):
        self.key_path = Path('.onion_key.txt')
        self.tor_controller = Controller.from_port()
        self.file_path = file_path[0]
        self.file_recevier_socket = socket.socket()
        self.session_key = NoiseConnection.from_name(b'Noise_NN_25519_ChaChaPoly_SHA256')

    def recv_file(self):
        
        file_path = Path(self.file_path).expanduser()

        if file_path.exists():

            user_choice = input(f'{self.file_path} alredy exists, you need to continue , type "yes" or "no" : ').lower()

            if user_choice != 'yes' and user_choice != 'no':
                print('invalid input')
            elif user_choice == 'no':
                print('please run the command once again with valid file path')
            elif user_choice == 'yes':
                print('okay then you need to rewrite the file or append to the file ?')
                print('for rewriting the file just type : R \n for appending the file just type : A')
                
                user_choice = input(' : ').upper()

                if user_choice != 'R' and user_choice != 'A':
                    print('invalid input')
                
                elif user_choice == 'R':
                    pass
                else:
                    pass
        else:

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

            self.file_recevier_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.file_recevier_socket.bind(('127.0.0.1', 5000))

            self.file_recevier_socket.listen()

            client_socket , addr = self.file_recevier_socket.accept()

            print(f'\n{addr} connected successfully...\n handshake initialising...')

            self.session_key.set_as_responder()
            self.session_key.start_handshake()

            for action in cycle(['receive', 'send']):
                if self.session_key.handshake_finished:
                    break
                elif action == 'send':
                    ciphertext = self.session_key.write_message()
                    ciphertext_size_header = len(ciphertext).to_bytes(4,'big')
                    client_socket.sendall(ciphertext_size_header + ciphertext)
                elif action == 'receive':
                    recv_exact_byte = RecvExactBytes()

                    received_message_header = recv_exact_byte.recv_exact_bytes(client_socket, 4)
                    received_message_size = int.from_bytes(received_message_header, 'big')

                    received_message = recv_exact_byte.recv_exact_bytes(client_socket, received_message_size)    

                    plaintext = self.session_key.read_message(received_message)                

            print(f'\nhandshake finished...')

            file_header_size = recv_exact_byte.recv_exact_bytes(client_socket, 2)

            encrypted_file_header = recv_exact_byte.recv_exact_bytes(client_socket, int.from_bytes(file_header_size,'big'))

            file_header = json.loads(self.session_key.decrypt(encrypted_file_header).decode())

            file_size = file_header['file_size']
            
            checksum = file_header['checksum']
            print(f'\nsender given metadata  file_size_in_bytes : { file_size}   checksum = {checksum}')

            if file_size and checksum:
                response_flag = self.session_key.encrypt('FILE_HEADER_GOT_SUCCESSFULLY'.encode())

                size_response_flag = len(response_flag).to_bytes(2, 'big')

                client_socket.sendall(size_response_flag + response_flag)

                with open(file_path, 'wb') as file:

                    received_chunk_size = 0

                    p_bar = tqdm(total=file_size, unit='B', unit_scale=True, desc="Receiving")

                    while received_chunk_size < file_size:

                        chunk_size = recv_exact_byte.recv_exact_bytes(client_socket, 4)

                        encrypted_chunk = recv_exact_byte.recv_exact_bytes(client_socket, int.from_bytes(chunk_size, 'big'))
                        decrypted_chunk = self.session_key.decrypt(encrypted_chunk)
                        

                        if not encrypted_chunk:
                            break


                        file.write(decrypted_chunk)

                        received_chunk_size += len(decrypted_chunk)

                        p_bar.update(len(decrypted_chunk))
                    
                    p_bar.close()
                
                print('\nfile received ...\n Recalculating checksum of received file ...')

                sha256_hash = hashlib.sha256()

                with open(file_path, 'rb') as file:
                    while True:
                        data = file.read(65536)
                        if not data:
                            break
                        
                        sha256_hash.update(data)

                if sha256_hash.hexdigest() == checksum:

                    print(f'\nRecalculated_checksum :- {sha256_hash.hexdigest()}\nChecksum matches')
                    print('File received successfully...')
                    response_flag = self.session_key.encrypt('FILE_DOWNLOADED_SUCCESSFULLY'.encode())
                    response_flag_size = len(response_flag).to_bytes(2, 'big')
                    client_socket.sendall(response_flag_size + response_flag)
                    client_socket.close()
                    self.file_recevier_socket.close()
                else:
                    response_flag = self.session_key.encrypt('FILE_DOWNLOADED_UNSUCCESSFULLY'.encode())
                    response_flag_size = len(response_flag).to_bytes(2, 'big')
                    client_socket.sendall(response_flag_size + response_flag)
                    print('\nSomthing went wrong... \n Checksum missmatch...')
                    print(f'\nsender given checksum :- {checksum}')
                    print(f'\nreceived file checksum :- {sha256_hash.hexdigest()} \n please resume the program ')
                    client_socket.close()
                    self.file_recevier_socket.close()

class LanFillesSender():
    def __init__(self, file_path, receiver_addr, port):
        self.file_paths = file_path
        self.recevier_addr = receiver_addr[0]
        self.port = port[0]
        self.file_sender_socket = socks.socksocket()
        self.session_key =  NoiseConnection.from_name(b'Noise_NN_25519_ChaChaPoly_SHA256')
     
    def send_filles(self):

        #below for loop checks any non valid filepaths in userinput 

        for files in range(len(self.file_paths)):

            file_path_valid = Path(self.file_paths[files]).expanduser()

            file_path_set = set()

            if not file_path_valid.exists():

                print(f'{self.file_paths[files]} is not a valid path ...')
                choice = input(f'you need to remove {self.file_paths[files]} or update it \n for removing this file path type "remv" \n to update type "rename" \n').lower().strip()

                if choice != 'remv' or choice != 'rename':

                    invalidd = True

                    while invalidd:
                        choice = input(f'you must answer this qn you need to remove {self.file_paths[files]} or update it \n for removing this file path type "remv" \n to update type "rename" \n').lower().strip()
                        if choice == 'remv' or choice == 'rename':
                            invalidd = False
                    
                    if choice == 'remv':

                        self.file_paths.pop(files)
                    else:

                        valid_path = Path(input('enter a valid path = ').strip())

                        if not valid_path.exists():

                            while True:

                                valid_path = Path(input('enter a valid path = ').strip())

                                if valid_path.exists() and valid_path not in file_path_set:
                                    break
                            
                            self.file_paths[files] = valid_path
                            file_path_set.add(valid_path)
                        elif valid_path.exists() and valid_path in file_path_set:

                            print(f'{valid_path} alredy listed in seding list , please provide a valid one ... ')
                            while True:

                                valid_path = Path(input('enter a valid path = ').strip())

                                if valid_path.exists() and valid_path not in file_path_set:
                                    break
                            self.file_paths[files] = valid_path
                            file_path_set.add(valid_path)
                        else:
                            self.file_paths[files] = valid_path
                            file_path_set.add(valid_path)
            else:
                file_path_set.add(self.file_paths[files])

        if self.file_paths:

            self.file_sender_socket.connect((self.recevier_addr, self.port))
            print('\nconnection successfull... \n handshake starting....')
            self.session_key.set_as_initiator()
            self.session_key.start_handshake()
            message = self.session_key.write_message()
            message_size_header = len(message).to_bytes(4,'big')
            self.file_sender_socket.sendall(message_size_header + message)
            recv_exact_byte = RecvExactBytes()

            received_message_header = recv_exact_byte.recv_exact_bytes(self.file_sender_socket, 4)
            received_message_size = int.from_bytes(received_message_header, 'big')

            received_message = recv_exact_byte.recv_exact_bytes(self.file_sender_socket, received_message_size)

            payload = self.session_key.read_message(received_message)

            print('handshake finished...')

            sending_files = []
            #from user given valid paths collects the end file name to a list then that list send first to server 
            for file_path in self.file_paths:
                sending_files.append(Path(file_path).name)
            
            encrypted_seding_file_data = self.session_key.encrypt(','.join(sending_files).encode())

            len_encrypted_seding_file_data = len(encrypted_seding_file_data).to_bytes(4,'big')

            self.file_sender_socket.sendall(len_encrypted_seding_file_data + encrypted_seding_file_data)

            intial_flag_header = recv_exact_byte.recv_exact_bytes(self.file_sender_socket, 2)
            intial_flag_size = int.from_bytes(intial_flag_header, 'big')
            intial_flag = recv_exact_byte.recv_exact_bytes(self.file_sender_socket, intial_flag_size)

            if self.session_key.decrypt(intial_flag).decode() == 'FILE_INFO_GOT':

                del sending_files

                recver_confermation_flag_header = recv_exact_byte.recv_exact_bytes(self.file_sender_socket,2)
                flag_size = int.from_bytes(recver_confermation_flag_header,'big')
                recver_confermation_flag = recv_exact_byte.recv_exact_bytes(self.file_sender_socket, flag_size)

                actual_confermation_flag = self.session_key.decrypt(recver_confermation_flag).decode()

                
                if actual_confermation_flag == 'REMV_FILES_AND_SEND':

                    removing_files_info_header = recv_exact_byte.recv_exact_bytes(self.file_sender_socket,4)
                    flag_size = int.from_bytes(removing_files_info_header,'big')
                    removing_files_info = recv_exact_byte.recv_exact_bytes(self.file_sender_socket, flag_size)

                    removing_files_info_decrypted = self.session_key.decrypt(removing_files_info)

                    removing_files_info_decrypted = removing_files_info_decrypted.split(',')

                    for index_num in removing_files_info_decrypted:

                        self.file_paths[int(index_num)] = None

                elif actual_confermation_flag == 'START_SENDING':
                    pass



                file_pointer = 0

                
                while file_pointer < len(self.file_paths):

                    if self.file_paths[file_pointer]:

                        file_path = Path(self.file_paths[file_pointer])
                
                        print(f'creating checksum of   {file_path}')
                        sha256_hash = hashlib.sha256()

                        with open(file_path, 'rb') as file:
                            while True:
                                data = file.read(65536)
                                if not data:
                                    break
                                
                                sha256_hash.update(data)
                        
                        print(f'\nchecksum of {file_path} :-  {sha256_hash.hexdigest()}')

                        file_size = file_path.stat().st_size

                        file_sending_header = {

                            'file_size' : file_size,
                            'checksum' : sha256_hash.hexdigest()

                        }

                        encrypted_file_sending_header = self.session_key.encrypt(json.dumps(file_sending_header).encode())
                        len_encrypted_file_sending_header = len(encrypted_file_sending_header).to_bytes(2, 'big')

                        self.file_sender_socket.sendall(len_encrypted_file_sending_header + encrypted_file_sending_header)
                        
                        response_flag_size = recv_exact_byte.recv_exact_bytes(self.file_sender_socket, 2)

                        response_flag_size_int_form = int.from_bytes(response_flag_size,'big')

                        response_flag = recv_exact_byte.recv_exact_bytes(self.file_sender_socket, response_flag_size_int_form)

                        if 'FILE_HEADER_GOT_SUCCESSFULLY' == self.session_key.decrypt(response_flag).decode():

                            print('\nfile sending...')

                            with open(file_path, 'rb') as file:
                                p_bar = tqdm(total=file_size, unit='B', unit_scale=True, desc='Sending')

                                while chunk := file.read(64 * 1024):
                                    encrypted_chunk = self.session_key.encrypt(chunk)
                                    encrypted_chunk_size = len(encrypted_chunk).to_bytes(4, 'big')
                                    self.file_sender_socket.sendall(encrypted_chunk_size + encrypted_chunk)
                                    p_bar.update(len(chunk))
                                p_bar.close()
                                    
                            print('\nfile sending completed ...')

                            print('\nwaiting for client verification...')
                            response_flag_size = recv_exact_byte.recv_exact_bytes(self.file_sender_socket, 2)

                            response_flag_size_int_form = int.from_bytes(response_flag_size,'big')

                            response_flag = recv_exact_byte.recv_exact_bytes(self.file_sender_socket, response_flag_size_int_form)

                            if 'FILE_DOWNLOADED_SUCCESSFULLY' == self.session_key.decrypt(response_flag).decode():
                                print(f'\nclient verification successfull, {file_path} sended and recevied successfully ...')
                                file_pointer += 1
                                
                            else:
                                print('\nsomething went wrong...')
                                print(f'\nclient failed while verifying the checksum, checksum missmatch occured ... \n program going forward with next file\n this {file_path} will send at the end...')
                                
                                itemm = self.file_paths.pop(file_pointer)
                                self.file_paths.append(itemm)

                        
                        else:
                            print('\n internal flags are not received successfully network issue may be connection closing...')
                    
                            self.file_sender_socket.close()
                            break
                
                print('session closing....')

                self.file_sender_socket.close()
                

            else:
                print('client respose failure...')
                self.file_sender_socket.close()

        else:
            print(f'non of the file path is valid , program is terminating ...')




class LanFillesReceiver():
    def __init__(self, port):
        '''self.file_path = file_path[0]'''
        self.port = port[0]
        self.file_recevier_socket = socket.socket()
        self.session_key = NoiseConnection.from_name(b'Noise_NN_25519_ChaChaPoly_SHA256')

    def recv_files(self):
        
        '''file_path = Path(self.file_path).expanduser()'''
        abs_file_path = Path('~/Downloads/.Raven_nyx_downloads').expanduser()

        abs_file_path.mkdir(mode=700, parents=True, exist_ok=True)


        self.file_recevier_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.file_recevier_socket.bind(('0.0.0.0', self.port))

        self.file_recevier_socket.listen()

        client_socket , addr = self.file_recevier_socket.accept()

        print(f'\n{addr} connected successfully...\n handshake initialising...')

        self.session_key.set_as_responder()
        self.session_key.start_handshake()

        for action in cycle(['receive', 'send']):
            if self.session_key.handshake_finished:
                break
            elif action == 'send':
                ciphertext = self.session_key.write_message()
                ciphertext_size_header = len(ciphertext).to_bytes(4,'big')
                client_socket.sendall(ciphertext_size_header + ciphertext)
            elif action == 'receive':
                recv_exact_byte = RecvExactBytes()

                received_message_header = recv_exact_byte.recv_exact_bytes(client_socket, 4)
                received_message_size = int.from_bytes(received_message_header, 'big')

                received_message = recv_exact_byte.recv_exact_bytes(client_socket, received_message_size)    

                plaintext = self.session_key.read_message(received_message)                

        print(f'\nhandshake finished...')

        downloading_file_header_len = recv_exact_byte.recv_exact_bytes(client_socket, 4)

        downloadng_files_encrypted = recv_exact_byte.recv_exact_bytes(client_socket, int.from_bytes(downloading_file_header_len, 'big'))

        downloading_files_decrypted = self.session_key.decrypt(downloadng_files_encrypted).decode()

        downloading_files_decrypted = downloading_files_decrypted.split(',')

        non_downloading_file_list = []


        if downloading_files_decrypted:

            downloading_file_success_flag_encrypted = self.session_key.encrypt('FILE_INFO_GOT'.encode())

            len_downloading_flag_success_flag_encrypted = len(downloading_file_success_flag_encrypted).to_bytes(2,'big')

            client_socket.sendall(len_downloading_flag_success_flag_encrypted + downloading_file_success_flag_encrypted)

            
            for files in range(len(downloading_files_decrypted)):

                file_path_valid = abs_file_path / downloading_files_decrypted[files]

                file_path_set = set()

                if file_path_valid.exists():

                    print(f'{downloading_files_decrypted[files]} is alredy exsit in {file_path_valid} ...')
                    choice = input(f'you must remove it from downloading list or update it with another non existing filename instead of  {downloading_files_decrypted[files]} \n for removing this file from downloading list  type "remv" \n to update type "rename" \n').lower().strip()

                    if choice != 'remv' or choice != 'rename':

                        invalidd = True

                        while invalidd:
                            choice = input(f'you must answer this qn you need to remove {downloading_files_decrypted[files]} or update it with another file name  \n for removing this file type "remv" \n to update type "rename" \n').lower().strip()
                            if choice == 'remv' or choice == 'rename':
                                invalidd = False
                        
                        if choice == 'remv':

                            downloading_files_decrypted.pop(files)

                            non_downloading_file_list.append(str(file))
                        else:

                            valid_path = Path(input('enter a valid file name  = ').strip())

                            if valid_path.exists():

                                while True:

                                    valid_path = Path(input('enter a valid path = ').strip())

                                    if valid_path.exists() and valid_path not in file_path_set:
                                        break
                                
                                downloading_files_decrypted[files] = valid_path
                                file_path_set.add(valid_path)
                            elif not valid_path.exists() and valid_path in file_path_set:

                                print(f'{valid_path} alredy listed in downloading list , please provide a valid one ... ')
                                while True:

                                    valid_path = Path(input('enter a valid file name  = ').strip())

                                    if not valid_path.exists() and valid_path not in file_path_set:
                                        break

                                downloading_files_decrypted[files] = valid_path
                                file_path_set.add(valid_path)
                            else:
                                downloading_files_decrypted[files] = valid_path
                                file_path_set.add(valid_path)
                     
                    elif choice == 'remv':
                        downloading_files_decrypted.pop(files)

                        non_downloading_file_list.append(str(file))
                    
                    else:
                        valid_path = Path(input('enter a valid file name  = ').strip())

                        if valid_path.exists():

                            while True:

                                valid_path = Path(input('enter a valid path = ').strip())

                                if valid_path.exists() and valid_path not in file_path_set:
                                    break
                            
                            downloading_files_decrypted[files] = valid_path
                            file_path_set.add(valid_path)
                        elif not valid_path.exists() and valid_path in file_path_set:

                            print(f'{valid_path} alredy listed in downloading list , please provide a valid one ... ')
                            while True:

                                valid_path = Path(input('enter a valid file name  = ').strip())

                                if not valid_path.exists() and valid_path not in file_path_set:
                                    break

                            downloading_files_decrypted[files] = valid_path
                            file_path_set.add(valid_path)
                        else:
                            downloading_files_decrypted[files] = valid_path
                            file_path_set.add(valid_path)


                    
                else:
                    pass

        

            if non_downloading_file_list:

                remove_seding_files_flag = self.session_key.encrypt('REMV_FILES_AND_SEND'.encode())
                len_remove_seding_files_flag = len(remove_seding_files_flag).to_bytes(2,'big')
                client_socket.sendall(len_remove_seding_files_flag + remove_seding_files_flag)

                encrypted_non_downloading_file_list = self.session_key.encrypt(','.join(non_downloading_file_list).encode())
                len_encrypted_non_downloadnig_file_list = len(encrypted_non_downloading_file_list).to_bytes(4,'big')
                client_socket.sendall(len_encrypted_non_downloadnig_file_list + encrypted_non_downloading_file_list)

            else:

                start_sending = self.session_key.encrypt('START_SENDING'.encode())
                len_start_sending = len(start_sending).to_bytes(2,'big')
                client_socket.sendall(len_start_sending + start_sending)
                

            file_pointer = 0

            correption_set = set()


            while file_pointer < len(downloading_files_decrypted):

                full_path = abs_file_path / downloading_files_decrypted[file_pointer]

                file_header_size = recv_exact_byte.recv_exact_bytes(client_socket, 2)

                encrypted_file_header = recv_exact_byte.recv_exact_bytes(client_socket, int.from_bytes(file_header_size,'big'))

                file_header = json.loads(self.session_key.decrypt(encrypted_file_header).decode())

                file_size = file_header['file_size']
                
                checksum = file_header['checksum']
                print(f'\nsender given metadata  file_size_in_bytes : { file_size}   checksum = {checksum}')

                if file_size and checksum:
                    response_flag = self.session_key.encrypt('FILE_HEADER_GOT_SUCCESSFULLY'.encode())

                    size_response_flag = len(response_flag).to_bytes(2, 'big')

                    client_socket.sendall(size_response_flag + response_flag)


                    with open(full_path, 'wb') as file:

                        received_chunk_size = 0

                        p_bar = tqdm(total=file_size, unit='B', unit_scale=True, desc="Receiving")

                        while received_chunk_size < file_size:

                            chunk_size = recv_exact_byte.recv_exact_bytes(client_socket, 4)

                            encrypted_chunk = recv_exact_byte.recv_exact_bytes(client_socket, int.from_bytes(chunk_size, 'big'))
                            decrypted_chunk = self.session_key.decrypt(encrypted_chunk)
                
                            file.write(decrypted_chunk)

                            received_chunk_size += len(decrypted_chunk)

                            p_bar.update(len(decrypted_chunk))
                        
                        p_bar.close()
                    
                    print('\nfile received ...\n Recalculating checksum of received file ...')

                    sha256_hash = hashlib.sha256()

                    with open(full_path, 'rb') as file:
                        while True:
                            data = file.read(65536)
                            if not data:
                                break
                            
                            sha256_hash.update(data)

                    if sha256_hash.hexdigest() == checksum:

                        print(f'\nRecalculated_checksum :- {sha256_hash.hexdigest()}\nChecksum matches')
                        print('File received successfully...')
                        response_flag = self.session_key.encrypt('FILE_DOWNLOADED_SUCCESSFULLY'.encode())
                        response_flag_size = len(response_flag).to_bytes(2, 'big')
                        client_socket.sendall(response_flag_size + response_flag)
                        file_pointer += 1
                    else:
                        response_flag = self.session_key.encrypt('FILE_DOWNLOADED_UNSUCCESSFULLY'.encode())
                        response_flag_size = len(response_flag).to_bytes(2, 'big')
                        client_socket.sendall(response_flag_size + response_flag)
                        print('\nSomthing went wrong... \n Checksum missmatch...')
                        print(f'\nsender given checksum :- {checksum}')
                        print(f'\nreceived file checksum :- {sha256_hash.hexdigest()} \n')
                        print(f'deleting {full_path}')
                        full_path.unlink()
                        itemm = downloading_files_decrypted.pop(file_pointer)
                        if itemm in correption_set:
                            print(f'{itemm} alredy tried once aging checksum mismathc occured so program going to kick out {itemm} from trying to downloading again')
                            file_pointer += 1
                        else:
                            downloading_files_decrypted.append(itemm)
                            correption_set.add(itemm)
                            print(f'{itemm} will contiue downloding at last for one more time ')

                












                
                            

                        


                            








                    






                












    
    

    

        


    