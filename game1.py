import select
import time
import socket
import signal
from multiprocessing import Value, Array, Process
import random
import concurrent.futures
import multiprocessing

#envoie de l'id du client + la table + les cartes + tokens + la liste des couleurs

serve = Value('b', True)
HOST = "localhost"
PORT = 6666

#fonction qui trnasforme le handdeck avec des zeros  pour le joueur désigné
def masque(hand_deck, n_joueur):
    res = []
    for i in range(len(hand_deck)):
        if i != (n_joueur - 1):
            res.append(hand_deck[i])
        else:
            main = []
            for j in range(5):
                main.append((0,0))
            res.append(main)
    return res

def couleur(couleurs, nb_joueurs):
    res = []
    nombre = [1,1,1,2,2,3,3,4,4,5]
    for i in range (nb_joueurs):
        temp = []
        for j in nombre:
            temp.append((couleurs[i],j))
        res = res + temp
    return res

def melange(deck):
    res = []
    while len(deck) > 0:
        index = random.randint(0,len(deck) - 1)
        res.append(deck[index])
        deck.pop(index)
    return res

def association(deck, nb_j):
    res = []
    for i in range(nb_j):
        temp = []
        for j in range (5):
            temp.append(deck[0])
            deck.pop(0)
        res.append(temp)
    return res

def inittable (nb_j):
    for i in range(nb_j):
        table[i] = 0

def communication(client_socket, couleurs, deck):
    ppid = client_socket.recv(1024)
    print("Son ppid est de : ", ppid.decode())
    proc_name = multiprocessing.current_process().name
    num_play = proc_name[(len(proc_name)-1):]
    
    mess = num_play + ";" + str(token_info.value) + ";" + str(token_fuse.value) + ";" + str(couleurs) +";" + str(table[:]) + ";" + str(deck) + ";" + str(masque(hand_deck, int(num_play))) 
    client_socket.sendall(mess.encode())
    valuee = client_socket.recv(1024)
    if valuee.decode() == '1':
        ltime = time.asctime()
        client_socket.sendall(ltime.encode())
    else:
        a = "Nope"
        client_socket.sendall(a.encode())
        serve.value = False

if __name__ == "__main__":
    couleurs = ["Rouge", "Vert", "Jaune", "Bleu", "Blanc"]
    nb_joueurs = input("Combien de joueurs y a t il?")
    token_info = Value('i', 3 + int(nb_joueurs))
    token_fuse = Value('i', 3)
    table = Array('i', range(int(nb_joueurs)))
    inittable(int(nb_joueurs))
    deck = melange(couleur(couleurs, int(nb_joueurs)))
    hand_deck = association(deck, int(nb_joueurs))
    print(masque(hand_deck, 1))
    print(masque(hand_deck, 2))

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        # socket creation
        server_socket.setblocking(False)
        server_socket.listen(5)
        while serve.value:
            readable, writable, error = select.select([server_socket], [], [], 1)
            if server_socket in readable: # if server_socket is ready
                client_socket, address = server_socket.accept() # will return immediately
                p = Process(target=communication, args=(client_socket, couleurs, deck))
                p.start()
