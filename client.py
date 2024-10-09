import socket

#funkcija za odabir game modea
def choose_mode():
    choice = ' '
    while(choice == ' '):
        print("Choose your mode: ")
        print("1. Manual Mode (You control the client side)")
        print("2. Automated Mode (Client plays automatically)")
        print("3. Client vs Client")
        choice = input("Enter choice (1/2/3): ").strip()
        if choice == '2': return 'auto'
        elif choice == '3': return 'client'
        elif choice == '1': return 'manual'
        else: 
            choice = ' '
            print("\n Please enter a valid input!\n")

#Spajanje na server
socket_client = socket.socket()
host = socket.gethostname()
port = 50454
socket_client.connect((host, port))

client_mode = choose_mode() #Odabir modea i slanje informacije serveru 
socket_client.send(client_mode.encode())

while True:
    message = socket_client.recv(1024).decode()
    print(message, end=" ") #Printanje stanja igre 
    
    if "Your turn!" in message:
        move = input()
        socket_client.send(move.encode())
    
    if "Game over." in message:
        break

socket_client.close()
