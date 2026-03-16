import socket
from cryptography.fernet import Fernet
from noise.connection import NoiseConnection
from pathlib import Path
from tqdm import tqdm
from server import RecvExactBytes
import hashlib
from itertools import cycle
import json

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
            print('connection successfull... \n handshake starting....')
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

            print(f'handshake finished...\n  handshke_hash = {self.session_key.get_handshake_hash()}\n starting digital figerprinting of  {self.file_path}')
            sha256_hash = hashlib.sha256()

            with open(file_path, 'rb') as file:
                while True:
                    data = file.read(65536)
                    if not data:
                        break
                    
                    sha256_hash.update(data)
            
            print(f'digithal figerprinting completed...')
            print(f'digital figer print :-  {sha256_hash.hexdigest()}')

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

                print('file sending...')

                with open(file_path, 'rb') as file:
                    p_bar = tqdm(total=file_size, unit='B', unit_scale=True)

                    while chunk := file.read(64 * 1024):
                        encrypted_chunk = self.session_key.encrypt(chunk)
                        encrypted_chunk_size = len(encrypted_chunk).to_bytes(4, 'big')
                        self.file_sender_socket.sendall(encrypted_chunk_size + encrypted_chunk)
                        print(f'chunk = {chunk} \n len = {len(chunk)}')
                        p_bar.update(len(chunk))
                    p_bar.close()
                        
                print('file sending completed ...')

                print('waiting for client verification...')
                response_flag_size = recv_exact_byte.recv_exact_bytes(self.file_sender_socket, 2)

                response_flag_size_int_form = int.from_bytes(response_flag_size,'big')

                response_flag = recv_exact_byte.recv_exact_bytes(self.file_sender_socket, response_flag_size_int_form)

                if 'FILE_DOWNLOADED_SUCCESSFULLY' == self.session_key.decrypt(response_flag).decode():
                    print('client verification successfull, file sended successfully ...')
                    self.file_sender_socket.close()
                else:
                    print('something went wrong...')
                    print('client failed while verifying the checksum, checksum missmatch occured ... \n please repeat the filesharing..')
                    self.file_sender_socket.close()
            
            else:
                print('something went wrong...')
                self.file_sender_socket.close()
        else:
            print(f'{self.file_path} not exists...')


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

            print(f'{addr} connected successfully...\n handshake initialising...')

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

            print(f'handshake finished... \n handshke_hash = {self.session_key.get_handshake_hash()}')

            file_header_size = recv_exact_byte.recv_exact_bytes(client_socket, 2)

            encrypted_file_header = recv_exact_byte.recv_exact_bytes(client_socket, int.from_bytes(file_header_size,'big'))

            file_header = json.loads(self.session_key.decrypt(encrypted_file_header).decode())

            file_size = file_header['file_size']
            
            checksum = file_header['checksum']
            print(f'file_size : { file_size} \n checksum = {checksum}')

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

                        print(f'encrypted_chunk :- {encrypted_chunk}')
                        decrypted_chunk = self.session_key.decrypt(encrypted_chunk)
                        print(f'decrypted_chunk :- {decrypted_chunk}')

                        if not encrypted_chunk:
                            break


                        file.write(decrypted_chunk)

                        received_chunk_size += len(decrypted_chunk)

                        print(f'received_chunk_size { received_chunk_size}')

                        p_bar.update(len(decrypted_chunk))
                    
                    p_bar.close()
                
                print('file received ...\n checking cheksum match...')

                sha256_hash = hashlib.sha256()

                with open(file_path, 'rb') as file:
                    while True:
                        data = file.read(65536)
                        if not data:
                            break
                        
                        sha256_hash.update(data)

                if sha256_hash.hexdigest() == checksum:

                    print('checksum correct ')
                    response_flag = self.session_key.encrypt('FILE_DOWNLOADED_SUCCESSFULLY'.encode())
                    response_flag_size = len(response_flag).to_bytes(2, 'big')
                    client_socket.sendall(response_flag_size + response_flag)
                    client_socket.close()
                    self.file_recevier_socket.close()
                else:
                    response_flag = self.session_key.encrypt('FILE_DOWNLOADED_UNSUCCESSFULLY'.encode())
                    response_flag_size = len(response_flag).to_bytes(2, 'big')
                    client_socket.sendall(response_flag_size + response_flag)
                    print('somthing went wrong... \n checksum missmatch...')
                    print(f'sender given checksum :- {checksum}')
                    print(f'received file checksum :- {sha256_hash} \n please resume the program ')
                    client_socket.close()
                    self.file_recevier_socket.close()



                    


                        








                






            












        
        

        

            


        