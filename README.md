# **GHOST_PIPE**

### **INTRODUCTION**

  ghost_pipe is a lan based communication and file sharing tool developed using python , in this tool ONE TO ONE , and GROUP CHATTING is possible, There is no os limitaions, work well in any os environment.
  file sharing is only from one computer to another , not one comupter to many computer's.
    currently ghost_pipe is cli tool , in upcomming future definitely it have a TUI using Textual framework 

### **FEATURES**

  1.file sharing from one commuter to another computer
  2.ONE TO ONE chat, one server an one client
  3.GROUP CHAT, one server and many client's

### **INSTALLTION

    git  clone https://github.com/Abhishek-Puzhakkal/ghost_pipe.git

    cd ghost_pipe

    source venv/bin/activate      # Linux

    venv\\Scripts\\activate         # Windows

    pip install -r requirements.txt

### **USEAGE 

   ONE TO ONE CHAT 

  ghost_pipe.py listen --port < specify a port for server listening for incoming connection> -u <server username for the chat>

  #Above command is for server to listen for client connection then later communication 
                    # To end the chat just type and send 'quit'
                    
    python ghost_pipe.py listen --port 1234 -u server 

  ghost_pipe.py connect --addr <internal ip of the server> --port <server listening port> -u < your usernmae for the chat>

  #Above command is for connect to server for the one to one chat
                    #To end the chat just type and send 'quit'

    python ghost_pipe.py connect --addr 192.168.1.3 --port 1234 -u client
                                        
  GROUP CHATING

  ghost_pipe.py listen-groupchat --port <specify a port for server listening for incoming connection> -u <server username for the group chat >

  #Above command is for server to listening and intiating group chat
                    # To end the chat just type and send 'quit'

    python ghost_pipe.py listening-groupchat --port 1234 -u server
                
  ghost_pipe.py connect-groupchat --addr <internal ip of the server> --port <server listening port> -u < your usernmae for the chat>

  #Above command is for client's to connect to server for the group chat 
                    # To end the chat just type and send 'quit'

    python ghost_pipe.py connect-groupchat --addr 192.168.1.3 --port 1234 -u client_1
                                        
  ### **FILE SHARING**

  FILE RECEVER COMMAND 

  ghost_pipe.py accept_file --port <specify a port for sender to connect> --path < specify a path to save the file >

  if the received file need to save the same directory , just specify the file name , other wise full path is needed 

    python ghost_pipe.py accept_file --port 1234 --path received_file.txt
                
  FILE SENDER COMMAND

  ghost_pipe.py share --file < path of the sending file > --addr < internal ip of recever > --port < listening port of receiver > 
  
  if the file, that need to send , is in same directery just specify the name of the file , otherwise needed the full path 

    python ghost_pipe.py share --file hello.txt --addr 192.168.1.3 --port 1234

                    
### **Author :- Abhishek Puzhakkal**

  







  
