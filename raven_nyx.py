import argparse
from client import Client, GpChatClient, TorClient, TorGpChatClient
from server import Server, GroupChatServer, TorGpServer, TorOneToOneServer
from file_sharing import *
import threading
from ipaddrs_validation import *

command = argparse.ArgumentParser(description="     Ravenyx is a secure peer-to-peer or P2P messaging and file-sharing system designed for privacy-focused communication." \
                                                "It supports encrypted one-to-one and  group communication, and file transfer over both Tor onion services and LAN. " \
                                                "The system uses modern cryptographic protocols (noise protocol framework NN pattern handshake) to establish secure sessions and allows users to communicate without relying on centralized servers.",
                                  epilog=""" 
        USEAGE 

            LAN ONE TO ONE CHAT 

                raven_nyx.py listen --port < specify a port for server listening for incoming connection> -u <server username for the chat>

                    #Above command is for server to listen for client connection then later communication 
                    # To end the chat just type and send 'quit'
                    
                    # eg :- raven_nyx.py listen --port 1234 -u server 

                raven_nyx.py connect --addr <internal ip of the server> --port <server listening port> -u < your usernmae for the chat>

                    #Above command is for connect to server for the one to one chat
                    #To end the chat just type and send 'quit'

                    #eg :- raven_nyx.py connect --addr 192.168.1.3 --port 1234 -u client
                                        
            LAN GROUP CHATING

                raven_nyx.py listen-groupchat --port <specify a port for server listening for incoming connection> -u <server username for the group chat >

                    #Above command is for server to listening and intiating group chat
                    # To end the chat just type and send 'quit'

                    # eg :- raven_nyx.py listening-groupchat --port 1234 -u server
                
                raven_nyx.py connect-groupchat --addr <internal ip of the server> --port <server listening port> -u < your usernmae for the chat>

                    #Above command is for client's to connect to server for the group chat 
                    # To end the chat just type and send 'quit'

                    # eg :- raven_nyx.py connect-groupchat --addr 192.168.1.3 --port 1234 -u client_1
            
            TOR ONE TO ONE COMMUNICATION

                raven_nyx.py lstn-tr-cht -u <username>

                    #Above command is for server to to initialize onion service and begins the Tor based one to one communcation

                    # eg :- raven_nyx.py lstn-tr-cht -u server
                
                raven_nyx.py conn-tr-cht --addr < server onion address > -u <username>

                    #Above command for client side to connect to server

                    #eg :- raven_nyx conn-tr-cht --addr m5yq2k7x3v4t6p9n8r1s2u3w4x5y6z7a8b9c2d3e4f5g6h7i8j9k2l3.onion -u clinet

                    #Above mentioned onion address is just a demo one , not a real one
            
            TOR GROUP COMMUNCATION

                raven_nyx.py lstn_tr_gp_cht -u <username>

                    # Above command to server side to intialize onion service and begins Tor based group communication

                    # eg:- raven_nyx.py lstn_tr_gp_cht -u server
                
                raven_nyx.py conn_tr_gp_cht --addr < server onion address > -u <username>

                    #Above command for clinet side to connect tor based communcation

                    # eg :- raven_nyx.py conn_tr_gp_cht --addr m5yq2k7x3v4t6p9n8r1s2u3w4x5y6z7a8b9c2d3e4f5g6h7i8j9k2l3.onion -u client_1

                    #Above mentioned onion address is just a demo one , not a real one
                           
            LAN ONE TO ONE FILE SHARING

                FILE RECEVER COMMAND 

                    raven_nyx.py accept_file --port <specify a port for sender to connect> --path < specify a path to save the file >

                    eg :-  raven_nyx.py accept_file --port 1234 --path received_file.txt

                            #or

                        raven_nyx.py accept_file --port 1234 --path /home/kali/testing/received_file.txt

                        note :- if the received file need to save the same directory , just specify the file name , other wise full path is needed 

                
                FILE SENDER COMMAND 

                    raven_nyx.py share --file < path of the sending file > --addr < internal ip of recever > --port < listening port of receiver > 

                    eg:- raven_nyx.py share --file hello.txt --addr 192.168.1.3 --port 1234

                            #or 

                        raven_nyx.py share --file /home/kali/project/ghost_pipe/hello.txt --addr 192.168.1.3 --port 1234

                        note:- if the file, that need to send , is in same directory just specify the name of the file , otherwise full path is needed

            
            TOR ONE TO ONE FILE SHARING

                 FILE RECEVER COMMAND 

                    raven_nyx.py tr-accept-file --path < specify a path to save the file >

                    eg :-  raven_nyx.py tr-accept-file --path received_file.txt

                            #or

                        raven_nyx.py tr-accept-file --path /home/kali/testing/received_file.txt

                        note :- if the received file need to save the same directory , just specify the file name , other wise full path is needed 


                
                FILE SENDER COMMAND 

                    raven_nyx.py tr-share --file < path of the sending file > --addr <recevier onion address >  

                    eg:- raven_nyx.py tr-share --file hello.txt --addr m5yq2k7x3v4t6p9n8r1s2u3w4x5y6z7a8b9c2d3e4f5g6h7i8j9k2l3.onion

                            #or 

                        raven_nyx.py share --file /home/kali/project/ghost_pipe/hello.txt --addr m5yq2k7x3v4t6p9n8r1s2u3w4x5y6z7a8b9c2d3e4f5g6h7i8j9k2l3.onion

                        note:- if the file, that need to send , is in same directory just specify the name of the file , otherwise full path is needed

                    
                
                

                
            Author :- Abhishek Puzhakkal



                                        """, 
                                        formatter_class=argparse.RawDescriptionHelpFormatter)
sub_command = command.add_subparsers(dest='mode', required=True)

connect_command = sub_command.add_parser('connect', help='client command to connect ot ONE TO ONE chat')
connect_command.add_argument('--addr',type=str, required=True, nargs=1, help='private ip of the server ', metavar='private ip' )
connect_command.add_argument('--port', type=int, required=True, nargs=1, help='listeing port of server', metavar='port number')
connect_command.add_argument('-u', required=True, type=str, nargs=1, help='you username , it will print in opposite end chating area ', metavar='username')

listent_command = sub_command.add_parser('listen', help='server command to intiate a ONE TO ONE chat ')
listent_command.add_argument('--port', type=int, required=True, nargs=1, metavar='port number', help='specify a port for incoming connection ')
listent_command.add_argument('-u', required=True, type=str, nargs=1, metavar='username', help='this will be your username , and it will print in oppsite end chating area ')

share_file_command = sub_command.add_parser('share', help='This is the command for sender to sent file ')
share_file_command.add_argument('--port', type=int, required=True, nargs=1, metavar='port numebr', help='reciver listening port number')
share_file_command.add_argument('--addr', required=True, nargs=1, metavar='private ip', help='private ip of receiver')
share_file_command.add_argument('--file', nargs=1, required=True, metavar='file path', help='The path of the file to send')

accept_file_command = sub_command.add_parser('accept_file', help='This is the command to receiver to get file ')
accept_file_command.add_argument('--path',required=True, nargs=1 , metavar='file path', help='specify a path to save the receiving file')
accept_file_command.add_argument('--port', required=True, nargs=1, type=int, metavar='port number', help='specify a portnumber to listen for incomming connection')

tor_share_file_command = sub_command.add_parser('tr-share', help='send file through tor ')
tor_share_file_command.add_argument('--file', nargs=1, required=True, metavar='file path', help='The path of the file to send')
tor_share_file_command.add_argument('--addr', required=True, nargs=1, metavar='receiver onion address', help='receiver onion address')

tor_accept_file_command = sub_command.add_parser('tr-accept-file', help='receiver to get file through tor network')
tor_accept_file_command.add_argument('--path',required=True, nargs=1 , metavar='file path', help='specify a path to save the receiving file')

connect_group_chat = sub_command.add_parser('connect-groupchat', help='Client command to connect to group chat ')
connect_group_chat.add_argument('--addr', required=True, nargs=1, type=str, metavar='private ip ', help='private ip of server')
connect_group_chat.add_argument('--port', type=int, required=True, nargs=1, metavar='port number', help='listeing port of server')
connect_group_chat.add_argument('-u', type=str, required=True, nargs=1, metavar='username', help='this is the name that will print in other member chating area while you sending message ')

listen_group_chat = sub_command.add_parser('listen-groupchat', help='server to initiate a group chat ')
listen_group_chat.add_argument('--port', type=int, nargs=1, required=True, metavar='port number', help='specify a port number to connect for clients')
listen_group_chat.add_argument('-u', type=str, nargs=1, required=True, metavar='username', help="this name will print in other's chating area while you sending message")

conn_tor_chat = sub_command.add_parser('conn-tr-cht', help='clinet to initiate tor based one to one chat')
conn_tor_chat.add_argument('--addr',type=str, nargs=1, required=True, metavar='onion address', help='specify the onion address of the server')
conn_tor_chat.add_argument('-u', type=str, required=True, nargs=1, metavar='username', help='this name will show in server chat box while you messaging'  )

tor_chat_listen = sub_command.add_parser('lstn-tr-cht', help='server to intiate tor server for communcation')
tor_chat_listen.add_argument('-u', type=str, nargs=1, required=True, metavar='username', help='specify a name , that will appear in client chat box while messaging' )

conn_tr_gp_cht = sub_command.add_parser('conn_tr_gp_cht', help='clinet to connect to server for group communcation')
conn_tr_gp_cht.add_argument('--addr', type=str, nargs=1, required=True, metavar='onion address', help='specify the server onion address')
conn_tr_gp_cht.add_argument('-u', type=str, nargs=1, required=True, metavar='username', help='this name will show in server and clients chat box while you messaging' )

lstn_tr_gp_cht = sub_command.add_parser('lstn_tr_gp_cht',help='server to intiate tor server for group communication' )
lstn_tr_gp_cht.add_argument('-u', type=str, nargs=1, required=True, metavar='username', help='specify a name , that will appear in clients chat box while you messaging')



user_input = command.parse_args()

if user_input.mode == 'listen':
    server = Server(user_input.port, user_input.u)
    print(f'server started listening on port : {user_input.port}')
    clinett, clinet_addr = server.server_client_connect()
    if clinett:
        print(f'connected to {clinet_addr}')
        trd = threading.Thread(target=server.server_recv_msg)
        trd.start()
        server.server_snt_msg()
        server.serv_closing()

        
elif user_input.mode == 'connect':

    ip_validation = IpAddressValidation()

    if ip_validation.validation(user_input.addr):

        client = Client(user_input.addr, user_input.port, user_input.u)
        connection_result = client.clinet_server_connection()

        if connection_result:
            trd = threading.Thread(target=client.client_recv_msg)
            trd.start()

            client.clinet_snt_msg()

            client.clt_close()
    
    else : print(f'{user_input.addr[0]} is not an private ip ')
    

elif user_input.mode == 'connect-groupchat':

    ip_validation = IpAddressValidation()

    if ip_validation.validation(user_input.addr):

        gp_cht_client = GpChatClient(user_input.addr, user_input.port, user_input.u)

        connection_result = gp_cht_client.client_gp_chat_connection()
        if connection_result:
            try:
                trd = threading.Thread(target=gp_cht_client.client_gp_cht_recv_msg)
                trd.start()
                gp_cht_client.client_gp_cht_snt_msg()
                '''gp_cht_client.client_gp_cht_connection_cls()
                trd.join()'''
            except KeyboardInterrupt:
                print("\nServer stopped manually.")
            finally:
                gp_cht_client.client_gp_cht_connection_cls()
                if trd:
                    trd.join()

            
    
    else : print(f'{user_input.addr[0]} is not an private ip ')
        
elif user_input.mode == 'listen-groupchat':
    gp_cht_server = GroupChatServer(user_input.port, user_input.u)
    try :
        trd = threading.Thread(target=gp_cht_server.connection)
        trd.start()
        gp_cht_server.gp_srvr_snt_msg()
        '''gp_cht_server.gp_chat_close()
        print(f"Is the thread actually dead? {not trd.is_alive()}")
        trd.join()
        '''
    except KeyboardInterrupt:
        print("\nServer stopped manually.")
    finally:
        gp_cht_server.gp_chat_close()
        if trd:
            trd.join()

elif user_input.mode == 'conn-tr-cht':
    tr_client = TorClient(user_input.addr, user_input.u)
    connection_result = tr_client.clinet_tor_server_connection()
    if connection_result:
        trd = threading.Thread(target=tr_client.client_recv_msg)
        trd.start()
        tr_client.clinet_snt_msg()
        tr_client.client_conn_close()

elif user_input.mode == 'lstn-tr-cht':
    tr_server = TorOneToOneServer(user_input.u)
    clinett, clinet_addr = tr_server.tor_server_clinet_connect()
    if clinett:
        print(f'connected to {clinet_addr}')
        trd = threading.Thread(target=tr_server.tor_server_recv_message)
        trd.start()
        tr_server.tor_server_snt_message()
        tr_server.tor_server_closing()

elif user_input.mode == 'conn_tr_gp_cht':
    tor_gp_cht_client = TorGpChatClient(user_input.addr, user_input.u)

    connection_result = tor_gp_cht_client.client_gp_chat_connection()
    if connection_result:
        try:
            trd = threading.Thread(target=tor_gp_cht_client.tor_client_gp_cht_recv_msg)
            trd.start()
            tor_gp_cht_client.tor_client_gp_cht_snt_msg()
        except KeyboardInterrupt:
            print("\nServer stopped manually.")
        finally:
            tor_gp_cht_client.tor_client_gp_cht_connection_cls()
            if trd:
                trd.join()

elif user_input.mode == 'lstn_tr_gp_cht':
    tor_gp_cht_server = TorGpServer(user_input.u)
    try :
        trd = threading.Thread(target=tor_gp_cht_server.tor_server_client_connection)
        trd.start()
        tor_gp_cht_server.tor_gp_srvr_snt_msg()
    except KeyboardInterrupt:
        print("\nServer stopped manually.")
    finally:
        tor_gp_cht_server.tor_gp_chat_close()
        if trd:
            trd.join()



elif user_input.mode == 'share':
    ip_validation = IpAddressValidation()

    if ip_validation.validation(user_input.addr):

        share_file = LanFilesender(user_input.file, user_input.addr, user_input.port)
        share_file.send_file()
    else : print(f'{user_input.addr[0]} is not an private ip ')
elif user_input.mode == 'accept_file':
    recv_file = LanFileReceiver(user_input.path, user_input.port)
    recv_file.recv_file()

elif user_input.mode == 'tr-share':
    share_file = TorFilesender(user_input.file, user_input.addr)
    share_file.send_file()
elif user_input.mode == 'tr-accept-file':
    recv_file = TorFileReceiver(user_input.path)
    recv_file.recv_file()




        
        
        
        







