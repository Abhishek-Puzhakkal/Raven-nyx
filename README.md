# GHOST_PIPE

### INTRODUCTION

  GhostPipe is a LAN-based communication and file-sharing tool developed using Python. It supports one-to-one chat and group chatting. There are no OS limitations, and it works across different operating systems.

File sharing is supported only between two computers (one-to-one), not one-to-many.

Currently, GhostPipe is a CLI-based tool. In the future, it will include a TUI built using the Textual framework.

### FEATURES

  1.file sharing from one computer to another computer
  2.ONE-TO-ONE chat, one server and one client
  3.GROUP-CHAT, one server and many clients

### INSTALLATION

    git  clone https://github.com/Abhishek-Puzhakkal/ghost_pipe.git

    cd ghost_pipe

    python -m venv venv 

    source venv/bin/activate      # Linux

    venv\\Scripts\\activate         # Windows

    pip install -r requirements.txt

### USAGE 

   ONE TO ONE CHAT 

  ghost_pipe.py listen --port < specify a port for server listening for incoming connection> -u <server username for the chat>

  #Above command is for server to listen for client connection then later communication 
                    # To end the chat just type and send 'quit'
                    
    python ghost_pipe.py listen --port 1234 -u server 

  ghost_pipe.py connect --addr <internal ip of the server> --port <server listening port> -u < your usernmae for the chat>

  #Above command is for connect to server for the one to one chat
                    #To end the chat just type and send 'quit'

    python ghost_pipe.py connect --addr 192.168.1.3 --port 1234 -u client
                                        
  GROUP CHATTING

  ghost_pipe.py listen-groupchat --port <specify a port for server listening for incoming connection> -u <server username for the group chat >

  #Above command is for server to listening and initiating group chat
                    # To end the chat just type and send 'quit'

    python ghost_pipe.py listen-groupchat --port 1234 -u server
                
  ghost_pipe.py connect-groupchat --addr <internal ip of the server> --port <server listening port> -u < your usernmae for the chat>

  #Above command is for client's to connect to server for the group chat 
                    # To end the chat just type and send 'quit'

    python ghost_pipe.py connect-groupchat --addr 192.168.1.3 --port 1234 -u client_1
                                        
  ### FILE SHARING**

  FILE RECEIVER COMMAND 

  ghost_pipe.py accept_file --port <specify a port for sender to connect> --path < specify a path to save the file >

  if the received file need to save the same directory , just specify the file name , other wise full path is needed 

    python ghost_pipe.py accept_file --port 1234 --path received_file.txt
                
  FILE SENDER COMMAND

  ghost_pipe.py share --file < path of the sending file > --addr < internal ip of receiver > --port < listening port of receiver > 
  
  if the file, that need to send , is in same directory just specify the name of the file , otherwise full path is needed

    python ghost_pipe.py share --file hello.txt --addr 192.168.1.3 --port 1234

### HOW THIS TOOL BASICALLY WORK 

  In this this tool both client and server side can be client and server, don't be confused , just imagine client_a and client_b  is chatting, the code in both side have the capability to be a client and server , it decide by the command , 

Then the person with server script , listen on specific port on all available network interfaces in server side machine , the client connect to server socket , then begin the chat, if one side sent 'quit' the socket will close , this is the basic idea 

HOW THE GROUP CHAT : - 
  In this tool the group chat designed like a star, i mean the machine running server will be the center node or dot , then every client connected to server, client_a don't have connection with other clients , only to server , but same time the server is connected to every client , then server broadcast the client message to every one, with a 'broadcast-flag' , the server side message have another flag 'server side flag' to inform the clients that from server side , 
  if one client quit , server close that connection , only that if total no.of clients in chat is more than 2 , also inform other's that client is quit from the chat , if server sent "quit" the entire chat is closed , 
  if only 2 members is group chat (server and client) it basically work like first description nothing more 

  The tool entirely on TCP connection , and  full duplex mode , what is mean by full duplex ???, after the connection any side can sent message , not need to one side to wait until other side to sent message , any side can sent and receive any time , also in group chat at any time new members can add to this chat , This is possible by using Threading , i used Threading in this tool , some threads are running in background , like , senting message , receiving message , adding new clients like that , that why this feel in full duplex 


## Architecture

- Built using Python socket module
- TCP based communication
- Data encryption using cryptography fernet key
- Multi-threaded server design
- Broadcast-based group messaging
- Star pattern for group chat

## Limitations

- LAN only (no NAT traversal)
- Basic level encryption using pre shared key

## Future Improvements

- TUI using Textual
- End-to-end encryption using public key exchange

                    
### **Author :- Abhishek Puzhakkal**

  







  
