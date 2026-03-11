# RAVEN NYX

### INTRODUCTION

  Ravenyx is a privacy-focused peer-to-peer messaging and file-sharing system that supports encrypted one-to-one and group communication over Tor onion services and LAN. It uses the Noise Protocol Framework (NN handshake) to establish secure sessions without relying on centralized servers
Currently, Ravennyx is a CLI-based tool. In the future, it will include a TUI built using the Textual framework.

### FEATURES

  1.file sharing from one computer to another computer in LAN and through Tor
  
  2.ONE-TO-ONE chat, one server and one client :- in LAN and Tor
  
  3.GROUP-CHAT, one server and many clients :- in LAN and Tor

### INSTALLATION

    sudo su

    apt-get install tor

    systemctl start tor

    git  clone https://github.com/Abhishek-Puzhakkal/ghost_pipe.git

    cd ghost_pipe

    python -m venv venv 

    source venv/bin/activate      # Linux

    pip install -r requirements.txt

### USAGE 

   LAN BASED ONE TO ONE CHAT 

    python3 raven_nyx.py listen --port < specify a port for server listening for incoming connection> -u <server username for the chat>

    #for example 
    
    python3 raven_nyx.py listen --port 1234 -u server 

   Above command is for server to listen for client connection then later communication 
                    # To end the chat just type and send 'quit'
                    
    

    python3 raven_nyx.py connect --addr <internal ip of the server> --port <server listening port> -u < your usernmae for the chat> 

    # example 

    python3 raven_nyx.py connect --addr 192.168.1.3 --port 1234 -u client
    
    

  Above command is for connect to server for the one to one chat
                    #To end the chat just type and send 'quit'

    
                                        
  LAN BASED GROUP CHATTING

    python3 raven_nyx.py listen-groupchat --port <specify a port for server listening for incoming connection> -u <server username for the group chat >

    #example 

     python3 raven_nyx.py listen-groupchat --port 1234 -u server

  Above command is for server to listening and initiating group chat
                    # To end the chat just type and send 'quit'

    
                
    python3 raven_nyx.py connect-groupchat --addr <internal ip of the server> --port <server listening port> -u < your usernmae for the chat>

    #example

    python3 raven_nyx.py connect-groupchat --addr 192.168.1.3 --port 1234 -u client_1

  Above command is for client's to connect to server for the group chat 
                    # To end the chat just type and send 'quit'


  NOTE ABOUT TOR BASED COMMUNICATION :-
        > importent thing is this , when you run tor based command make sure that tor is installed and it is running in you machine , otherwise             it will never work
           use :- systemctl start tor #to start tor 
        >also you must commentout two lines from /etc/tor/torrc
           ControlPort 9051
           CookieAuthentication1
        > always run Tor realted below commands as root 
        > after running the tor server based command in you directory , there will be a hidde file '.onion_key.txt'
          if you need to use another onion address next time just delete that file , then you will get new address otherwise the past address 

  TOR BASED ONE TO ONE COMMUNICATION

    > server command 

      # also you must comment out two lines from /etc/tor/torrc
           ControlPort 9051
           CookieAuthentication1

        python3 lstn-tr-cht -u <username>
        eg :- python3 raven_nyx.py lstn-tr-cht -u abhi
    
        #above command will genrate a onion address like below, but note that it take few minutues may be  , if it first time share it to client 
    
        python3 raven_nyx.py lstn-tr-cht -u abhi
        Resumed tsvord6oj1lkmda2pk64ov1coiarv4b7czqcs4stsxteaoiku2ivg1ad.onion
    
        #above metion address is a fake one 
    > client command 

        python3 conn-tr-cht --addr < onion address > -u <username>

        eg:- python3 raven_nyx.py conn-tr-cht --addr tsvord6oj1lkmda2pk64ov1coiarv4b7czqcs4stsxteaoiku2ivg1ad.onion -u parrot

        #make sure that tor is runnnign before excecuting this command , also it takelittle bit of time to connect to server 

  TOR BASED GROUP COMMUNCATION 

     > server command 

         python3 lstn_tr_gp_cht -u <username>
    > client command
         python3 conn_tr_gp_cht --addr <onion address> -u <username>

    # make sure above metiond TOR related things are followed correctly 
    

    
                                        
  ### FILE SHARING**

  FILE RECEIVER COMMAND 

    python3 raven_nyx.py accept_file --port <specify a port for sender to connect> --path < specify a path to save the file >

    #example

    python3 raven_nyx.py accept_file --port 1234 --path received_file.txt

    #or

    python3 raven_nyx.py accept_file --port 1234 --path /home/kali/testing/received_file.txt

  if the received file need to save the same directory , just specify the file name , other wise full path is needed 

    
                
  FILE SENDER COMMAND

    python3 raven_nyx.py share --file < path of the sending file > --addr < internal ip of receiver > --port < listening port of receiver > 

    #example 

    python3 raven_nyx.py share --file hello.txt --addr 192.168.1.3 --port 1234

    #or 

    python3 raven_nyx.py share --file /home/kali/project/ghost_pipe/hello.txt --addr 192.168.1.3 --port 1234
  
  if the file, that need to send , is in same directory just specify the name of the file , otherwise full path is needed

  

### HOW THIS TOOL BASICALLY WORK 

  In this this tool both client and server side can be client and server, don't be confused , just imagine client_a and client_b  is chatting, the code in both side have the capability to be a client and server , it decide by the command , 

Then the person with server script , listen on specific port on all available network interfaces in server side machine , the client connect to server socket , then begin the chat, if one side sent 'quit' the socket will close , this is the basic idea 

HOW THE GROUP CHAT : - 
  In this tool the group chat designed like a star, i mean the machine running server will be the center node or dot , then every client connected to server, client_a don't have connection with other clients , only to server , but same time the server is connected to every client , then server broadcast the client message to every one, with a 'broadcast-flag' , the server side message have another flag 'server side flag' to inform the clients that from server side , 
  if one client quit , server close that connection , only that if total no.of clients in chat is more than 2 , also inform other's that client is quit from the chat , if server sent "quit" the entire chat is closed , 
  if only 2 members is group chat (server and client) it basically work like first description nothing more 

  The tool entirely on TCP connection , and  full duplex mode , what is mean by full duplex ???, after the connection any side can sent message , not need to one side to wait until other side to sent message , any side can sent and receive any time , also in group chat at any time new members can add to this chat , This is possible by using Threading , i used Threading in this tool , some threads are running in background , like , senting message , receiving message , adding new clients like that , that why this feel in full duplex 


## Architecture

- Built using Python socket, stem, pysocks, noiseprotocol module
- TCP based communication
- Data encryption using noise protocol NN pattern handshke
- Multi-threaded server design
- Broadcast-based group messaging
- Star pattern for group chat
- tor layer 

## Limitations

- tor based communcation may take littile bit time while at intialisation ,


## Future Improvements

- TUI using Textual
- voice exchage 

                    
### **Author :- Abhishek Puzhakkal**

  







  
