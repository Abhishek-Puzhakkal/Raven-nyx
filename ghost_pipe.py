import argparse
from client import Client, GpChatClient
from server import Server, GroupChatServer
from file_sharing import file_reciver, File_sender
import threading
from ipaddrs_validation import *

command = argparse.ArgumentParser(description='     ghost_pipe is a lan communication and file sharing tool,' \
                                        'in this tool , there is two types of communication is possible , \n 1. ONE TO ONE Communication :- one server and one client \n ' \
                                        '2.GROUP CHAT:- One server and many clients',
                                  epilog=""" 
        USEAGE 

            ONE TO ONE CHAT 

                ghost_pipe.py listen --port < specify a port for server listening for incoming connection> -u <server username for the chat>

                    #Above command is for server to listen for client connection then later communication 
                    # To end the chat just type and send 'quit'
                    
                    # eg :- ghost_pipe.py listen --port 1234 -u server 

                ghost_pipe.py connect --addr <internal ip of the server> --port <server listening port> -u < your usernmae for the chat>

                    #Above command is for connect to server for the one to one chat
                    #To end the chat just type and send 'quit'

                    #eg :- ghost_pipe.py connect --addr 192.168.1.3 --port 1234 -u client
                                        
            GROUP CHATING

                ghost_pipe.py listen-groupchat --port <specify a port for server listening for incoming connection> -u <server username for the group chat >

                    #Above command is for server to listening and intiating group chat
                    # To end the chat just type and send 'quit'

                    # eg :- ghost_pipe.py listening-groupchat --port 1234 -u server
                
                ghost_pipe.py connect-groupchat --addr <internal ip of the server> --port <server listening port> -u < your usernmae for the chat>

                    #Above command is for client's to connect to server for the group chat 
                    # To end the chat just type and send 'quit'

                    # eg :- ghost_pipe.py connect-groupchat --addr 192.168.1.3 --port 1234 -u client_1
                                        
            FILE SHARING

                FILE RECEVER COMMAND 

                    ghost_pipe.py accept_file --port <specify a port for sender to connect> --path < specify a path to save the file >
                
                FILE SENDER COMMAND 

                    ghost_pipe.py share --file < path of the sending file > --addr < internal ip of recever > --port < listening port of receiver > 

                
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

connect_group_chat = sub_command.add_parser('connect-groupchat', help='Client command to connect to group chat ')
connect_group_chat.add_argument('--addr', required=True, nargs=1, type=str, metavar='private ip ', help='private ip of server')
connect_group_chat.add_argument('--port', type=int, required=True, nargs=1, metavar='port number', help='listeing port of server')
connect_group_chat.add_argument('-u', type=str, required=True, nargs=1, metavar='username', help='this is the name that will print in other member chating area while you sending message ')

listen_group_chat = sub_command.add_parser('listen-groupchat', help='server to initiate a group chat ')
listen_group_chat.add_argument('--port', type=int, nargs=1, required=True, metavar='port number', help='specify a port number to connect for clients')
listen_group_chat.add_argument('-u', type=str, nargs=1, required=True, metavar='username', help="this name will print in other's chating area while you sending message")


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

    ip_validation = IpAddressValidation(user_input.addr)

    if ip_validation.validation():

        client = Client(user_input.addr, user_input.port, user_input.u)
        connection_result = client.clinet_server_connection()

        if connection_result:
            trd = threading.Thread(target=client.client_recv_msg)
            trd.start()

            client.clinet_snt_msg()

            client.clt_close()
    
    else : print(f'{user_input.addr} is not an private ip ')
    

elif user_input.mode == 'connect-groupchat':

    ip_validation = IpAddressValidation(user_input.addr)

    if ip_validation.validation():

        gp_cht_client = GpChatClient(user_input.addr, user_input.port, user_input.u)

        connection_result = gp_cht_client.client_gp_chat_connection()
        if connection_result:
            trd = threading.Thread(target=gp_cht_client.client_gp_cht_recv_msg)
            trd.start()
            gp_cht_client.client_gp_cht_snt_msg()
            gp_cht_client.client_gp_cht_connection_cls()
    
    else : print(f'{user_input.addr} is not an private ip ')
        
elif user_input.mode == 'listen-groupchat':
    gp_cht_server = GroupChatServer(user_input.port, user_input.u)

    trd = threading.Thread(target=gp_cht_server.connection)
    trd.start()
    gp_cht_server.gp_srvr_snt_msg()
    gp_cht_server.gp_chat_close()
    

elif user_input.mode == 'share':
    ip_validation = IpAddressValidation(user_input.addr)

    if ip_validation.validation():

        share_file = File_sender(user_input.addr, user_input.port, user_input.file)
        share_file.send_file()
    else : print(f'{user_input.addr} is not an private ip ')
elif user_input.mode == 'accept_file':
    recv_file = file_reciver(user_input.path, user_input.port)
    recv_file.recvfile()




        
        
        
        







