import os
import sys
import socket
 
def user():
    answer = 3
    while answer not in [1, 2]:
        print("1. to get current date/time")
        print("2. to terminate time server")
        answer = int(input())
    return answer
 
HOST = "localhost"
PORT = 6666

def traduction (reponse):
    fuse = int(reponse[4])
    info = int(reponse[2])
    id_joueur = int(reponse[0])
    couleur = []
    table = []
    deck =[]
    hand_deck = []
    hand = []
    i = 8
    temp = ""
    while reponse[i] != "]":
        while reponse[i] != "'":
            temp = temp + reponse [i]
            i = i + 1
        i = i + 1
        if temp != ", ":
            couleur.append(temp)
        temp = ""
    i = i + 2
    while reponse[i] != "]":
        if reponse[i] == '0':
            table.append(int(reponse[i]))
        i = i + 1
    i = i + 4
    
    while reponse[i] != ";": #i < len(reponse) :  
        temp = ""
        while reponse[i] != ",":
            if reponse[i] != "'":
                temp = temp + reponse[i]
            i = i + 1
        temp2 = 0
        i = i + 1
        while reponse[i] != ")":
            if reponse[i] != " ":
                temp2 = int(reponse[i])
            i = i + 1
        while reponse[i] != "(" and reponse[i] !=  "]":
            i = i + 1
        i = i + 1
        deck.append((temp,temp2))
    i = i + 1
    #reponse[i] = [ 
    while reponse[i] != "]":
        while reponse[i] != "]":
            temp = ""
            temp2 = 0
            i = i + 3
            #reponse[i] = ' ou 0
            while reponse[i] != ",":
                if reponse[i] != "'":
                    temp = temp + reponse[i]
                i = i + 1
            i = i + 2
            while reponse[i] != ")":
                temp2 = temp2 + int(reponse[i])
                i = i + 1
            hand.append((temp, temp2))
            if reponse[i] != "]":
                i = i + 1
        hand_deck.append((hand))
        hand = []
        #reponse[i] = ]
        i = i + 1
    return fuse, info, id_joueur, couleur, table, deck, hand_deck

if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        ppid = os.getppid()
        client_socket.sendall((str(ppid)).encode())
        m = user()
        rep = client_socket.recv(2048)
        reponse = rep.decode()
        print (str(traduction(reponse)))
        #print("\n\n" + reponse)
        if m == 1:
            client_socket.send(b"1")
            resp = client_socket.recv(1024)
            if not len(resp):
                print("The socket connection has been closed!")
                sys.exit(1)
            print("Server response:", resp.decode())
        if m == 2:
            client_socket.send(b"2")


