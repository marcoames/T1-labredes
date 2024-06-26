from socket import *
import threading

# server configuration
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5555

# dictionary to store clients nicknames and sockets
clients = {}

# handle client connection
def handle_client(client_socket, client_address):
    try:
        while True:
            # receive message from client
            message = client_socket.recv(2048).decode()
            print(f"{get_nickname(client_socket)}:", message)
            # check if message is empty
            if not message:
                print(f"Connection with {client_address} closed.")
                break

            # process message based on command prefix
            if message.startswith("/REG"):
                handle_registration(client_socket, message)
            elif message.startswith("/MSGALL"):
                handle_message_all(client_socket,message)
                pass  
            elif message.startswith("/MSG"):
                handle_message(client_socket, message)
            else:
                print(f"Invalid message from {client_address}: {message}")
    except ConnectionResetError:
        print(f"Connection with {client_address} lost.")
    finally:
        client_socket.close()

# handle client registration
def handle_registration(client_socket, message):
    nickname = message.split()[1]
    clients[nickname] = client_socket
    print(f"New user registered: {nickname}")

# handle direct messages
def handle_message(client_socket, message):
    parts = message[5:].split(':',1)
    #print(parts)
    if len(parts) != 2:
        client_socket.send("Invalid message format. Use '<recipient>:<message>'.".encode())
        return
    
    recipient = parts[0]
    content = parts[1]
    
    if recipient in clients:
        recipient_socket = clients[recipient]
        recipient_socket.send(f"{get_nickname(client_socket)}:{content}".encode())
    else:
        client_socket.send("User not found.".encode())

# handle broadcast messages
def handle_message_all(sender_socket, message):
    parts = message[8:].split(':',1)
    #print(parts)
    if len(parts) != 1:
        sender_socket.send("Invalid message format. Use '<message>'.".encode())
        return
    
    content = parts[0]
    
     # send message to all registered users
    for nickname, recipient_socket in clients.items():
        recipient_socket.send(f"{get_nickname(sender_socket)}: {content}".encode())

# get nickname of a client
def get_nickname(client_socket):
    for nickname, socket in clients.items():
        if socket == client_socket:
            return nickname
    return "Unknown"

def main():

    #create TCP socket
    server_socket = socket(AF_INET,SOCK_STREAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(5) # queue size of 5
    print(f"Server listening on {SERVER_HOST}:{SERVER_PORT}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"New connection from {client_address}")
        
        # create a new thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

if __name__ == "__main__":
    main()
