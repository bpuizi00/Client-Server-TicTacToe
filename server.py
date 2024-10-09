import socket
import sys
import random

#Provjera je li igrac pobjedio
def check_winner(board, symbol):
    for i in range(3):
        if all([spot == symbol for spot in board[i]]):  #Provjera po redovima
            return True
        if all([board[j][i] == symbol for j in range(3)]):  #Po Stupcima
            return True
    if board[0][0] == symbol and board[1][1] == symbol and board[2][2] == symbol:  #Po glavnoj dijagonali 
        return True
    if board[0][2] == symbol and board[1][1] == symbol and board[2][0] == symbol:  #Po sporednoj dijagonali 
        return True
    return False

#Funkcija za vracanje random poteza 
def get_random_move(board):
    empty_positions = [(i, j) for i in range(3) for j in range(3) if board[i][j] == ' ']
    return random.choice(empty_positions) if empty_positions else None

#Funkcija za provjeru ima li server potencijalni pobjednicki potez pa vrati koordinate ako ima
def check_winning_move(board):
    for i in range(3):
        for j in range(3):
            if board[i][j] == ' ':  
                board[i][j] = 'X'  #Na prazno mjesto stavi privremeno X 
                if check_winner(board, 'X'):  #Provjeri jel to pobjednicki potez 
                    board[i][j] = ' '  
                    return (i, j)  #Ako je vrati koordinante polja
                board[i][j] = ' '  #Za slucaj kad nije vrati polje u prvobitno stanje
    return None  
   

#Ako su polja popunjena nerijeseno je (prethodno se provjeri ima li pobjednika)
def check_draw(board):
    return all(all(spot != ' ' for spot in row) for row in board)

#Prikaz 3x3 polja
def display_board(board):
    return '\n'.join([' | '.join(row) for row in board])

#Inicijalizacija servera
server_socket = socket.socket()
host = socket.gethostname()
port = 50454
server_socket.bind((host, port))
server_socket.listen(5)

#Server priceka da se client prikljuci 
print('Server is waiting for a connection...')
(conn, address) = server_socket.accept()

#Procita odgovor za odabir game-modea
client_mode = conn.recv(1024).decode()
if client_mode == 'client':   #Ukoliko je odabran mode client vs client onda priceka da se prikljuci drugi client
  (conn2, address2) = server_socket.accept()
  client_mode = conn2.recv(1024).decode()

#Inicijalizacija pocetnog polja
board = [[' ' for _ in range(3)] for _ in range(3)]
current_player = 'X'  
conn.send("Welcome to Tic-Tac-Toe! You are 'O'. Here's the starting board:".encode())
conn.send(f"{display_board(board)}\n".encode())

if client_mode == 'client':
  conn2.send("Welcome to Tic-Tac-Toe! You are 'X'. Here's the starting board:".encode())
  conn2.send(display_board(board).encode())

while True:
    #Potez prvog igraca
    move = None
    if client_mode == 'auto':  #Ako se igra client protiv automatiziranog servera
        print("Server's (X) turn (automated)...")
        move = check_winning_move(board)
        if move:  #Ako winning funkcija pronade potez odigra se inace ide na random
            board[move[0]][move[1]] = 'X'
        else:
            move = get_random_move(board)
            board[move[0]][move[1]] = 'X'
        
        conn.send(f"Server's move:\n{display_board(board)}\n".encode())

    elif client_mode == 'client': #Client vs client 
        valid_move= False
        while not valid_move:
            conn2.send("\nYour turn! Enter your move as 'row col':".encode())
            client_move = conn2.recv(1024).decode().strip()
            row, col = map(int, client_move.split()) #Pronade brojeve u unosu 
            if 0<= row < 3 and 0<= col <3:
                if board[row][col] == ' ':
                    board[row][col] = current_player #Ako je prazno stavi oznaku trenutnog igraca 
                    valid_move=True
                else:
                    conn2.send("Invalid move! That spot is already taken.".encode()) #Nije prazno treba ponovit unos
                    continue
            else:
                conn2.send("Wrong input! Please enter number between 0-2!".encode()) #Out of range unos 
        conn.send(f"Client2's move:\n{display_board(board)}\n".encode())


    else:
      while move is None:
          row, col = input("Enter your move (row and column) as 'row col': ").split()
          row, col = int(row), int(col)
          if 0<= row < 3 and 0<= col <3:
            if board[row][col] == ' ':
                board[row][col] = current_player
                move = (row, col)
            else:
                print("Invalid move! That spot is already taken.")
          else:
              print("Input out of range try with numbers between 0-2!")

      conn.send(f"Server's move:\n{display_board(board)}".encode())

    #Provjera je li prvi igrac pobjedio 
    if check_winner(board, current_player):
        if client_mode == 'client': 
            conn.send("Client2 wins! Game over.".encode())
            conn2.send("Client2 wins! Game over.".encode())
        else:
          conn.send("Server wins! Game over.".encode())
        break

    #Provjera izjednacenog rezultata 
    if check_draw(board):
        conn.send("It's a draw! Game over.".encode())
        if client_mode=='client':
          conn2.send("It's a draw! Game over.".encode())
        break

    #Prebacivanje na klijenta (ili drugog klijenta ovisno o modu)
    current_player = 'O'
    
    valid_move= False
    while not valid_move:
      conn.send("Your turn! Enter your move as 'row col':".encode())
      client_move = conn.recv(1024).decode().strip()
      row, col = map(int, client_move.split())
      if 0<= row < 3 and 0<= col <3:
        if board[row][col] == ' ':
            board[row][col] = current_player
            valid_move=True
        else:
            conn.send("Invalid move! That spot is already taken.".encode())
            continue
      else:
          conn.send("Wrong input! Please enter number between 0-2!".encode())

    if client_mode=='client':
      conn2.send(f"Client1's move:\n{display_board(board)}".encode())

    #Provjera je li drugi igrac pobjedio 
    if check_winner(board, current_player):
        conn.send("Client 1 won! Game over.".encode())
        if client_mode=='client':
          conn2.send("\n Client 1 won! Game over.".encode())
        break

    #Provjera za nerijeseni rezultat 
    if check_draw(board):
        conn.send("It's a draw! Game over.".encode())
        if client_mode =='client':
          conn2.send("It's a draw! Game over.".encode())
        break

    #Prebacivanje nazad na drugog igraca
    current_player = 'X'

server_socket.close()
sys.exit()
