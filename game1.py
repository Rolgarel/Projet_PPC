import os
import sys
import select
import time
import socket
import signal
from multiprocessing import Value, Array, Process
from multiprocessing.managers import BaseManager
import random
import concurrent.futures
import multiprocessing
import game_handler

# envoie de l'id du client + la table + les cartes + tokens + la liste des couleurs

serve = Value('b', True)
HOST = "localhost"
PORT = 6666
PORT_SHARED = 6677
KEY = b'Hippopotomonstrosesquippedaliophobie'


class SharedMemory(BaseManager):
    pass


def signal_handler(sig, frame):
    # Signal de joueur prêt
    if sig == signal.SIGUSR1:
        nb_joueurs_pret.value = nb_joueurs_pret.value + 1
    # Signal de fin de tour
    if sig == signal.SIGUSR2:
        tour.value = tour.value + 1
        partie_en_cours.value = game_handler.end(shared.get_token_fuse(), table)
        attente.value = False


def signal_handler_process():
    signal.signal(signal.SIGUSR1, signal_handler)
    signal.signal(signal.SIGUSR2, signal_handler)
    while True:
        pass


# fonction qui transforme le handdeck avec des zeros  pour le joueur désigné
def masque(hand_deck, n_joueur):
    res = []
    for i in range(len(hand_deck)):
        if i != (n_joueur - 1):
            res.append(hand_deck[i])
        else:
            main = []
            for j in range(5):
                main.append((0, 0))
            res.append(main)
    return res


def couleur(couleurs, nb_joueurs):
    res = []
    nombre = [1, 1, 1, 2, 2, 3, 3, 4, 4, 5]
    for i in range(nb_joueurs):
        temp = []
        for j in nombre:
            temp.append((couleurs[i], j))
        res = res + temp
    return res


def melange(deck):
    res = []
    while len(deck) > 0:
        index = random.randint(0, len(deck) - 1)
        res.append(deck[index])
        deck.pop(index)
    return res


def association(deck, nb_j):
    res = []
    for i in range(nb_j):
        temp = []
        for j in range(5):
            temp.append(deck[0])
            deck.pop(0)
        res.append(temp)
    return res


def inittable(nb_j):
    for i in range(nb_j):
        table[i] = 0


def communication(shared, client_socket, couleurs, deck, pipe_child):
    # échange des ppid
    client_ppid = int(client_socket.recv(1024).decode())
    print("Son ppid client est : ", client_ppid)
    ppid = os.getppid()
    client_socket.sendall((str(ppid)).encode())

    proc_name = multiprocessing.current_process().name
    num_play = int(proc_name[(len(proc_name) - 1):]) - 4
    print(str(num_play) + "")
    player_pid[num_play] = client_ppid
    pipe = pipe_child[num_play - 1]

    mess = (str(num_play) + ";" + str(shared.get_token_info()) + ";" + str(shared.get_token_fuse()) + ";" + str(
        couleurs) + ";"
            + str((shared.get_table()[:])) + ";" + str(deck) + ";" + str(masque(hand_deck, int(num_play))))
    client_socket.sendall(mess.encode())

    # boucle de jeu
    while partie_en_cours.value == 0:
        rep = pipe.recv()
        client_socket.sendall(rep)

    # fin de partie
    os.kill(client_ppid, signal.SIGUSR2)


def send_card(pipe, card, card_id, player, player_id):
    if player != player_id:
        pipe.send((str(player) + " " + str(card_id) + " " + card[0] + " " + str(card[1])).encode())


# process de gestion de la boucle de jeu
def jeu(deck, hand_deck, colors, parent_pipe, nb_joueurs):
    # initialisation

    # boucle de gameplay
    while partie_en_cours.value == 0:
        # print(str(nb_joueurs_pret.value))
        if nb_joueurs_pret.value == nb_joueurs:
            print("oui")
            joueur_actif = tour.value % nb_joueurs
            os.kill(player_pid[joueur_actif], signal.SIGUSR1)
            while attente.value:
                pass
            attente.value = True
            reception = client_socket.recv(1024).decode()
            if reception != "info":
                reception = int(reception)
                deck, hand_deck = game_handler.play(reception, joueur_actif, deck, hand_deck, fuse, table, colors)
                for i in range(nb_joueurs):
                    send_card(parent_pipe[i], hand_deck[player][reception], reception, i, joueur_actif)

    # fin partie


# process de gestion de la shared memory
def shared_server(token_info, token_fuse, table):
    SharedMemory.register('get_token_info', callable=lambda: token_info)
    SharedMemory.register('get_token_fuse', callable=lambda: token_fuse)
    SharedMemory.register('get_table', callable=lambda: table)
    shared = SharedMemory(address=('', PORT_SHARED), authkey=KEY)
    server = shared.get_server()
    server.serve_forever()


if __name__ == "__main__":
    s = multiprocessing.Process(target=signal_handler_process, args=())
    s.start()

    couleurs = ["Rouge", "Vert", "Jaune", "Bleu", "Blanc"]
    nb_joueurs = game_handler.server_players()

    token_info = 3 + nb_joueurs
    token_fuse = 3
    table = Array('i', range(nb_joueurs))

    partie_en_cours = Value('i', 0)
    nb_joueurs_pret = Value('i', 0)
    tour = Value('i', 0)
    attente = Value('b', True)
    player_pid = Array('i', range(nb_joueurs))

    # création et lancement de la shared memory
    s = Process(target=shared_server, args=(token_info, token_fuse, table))
    s.start()
    shared = SharedMemory(address=('', PORT_SHARED), authkey=KEY)

    pipe_parent = []
    pipe_child = []
    for i in range(nb_joueurs):
        p, c = multiprocessing.Pipe()
        pipe_parent.append(p)
        pipe_child.append(c)

    inittable(int(nb_joueurs))
    deck = melange(couleur(couleurs, nb_joueurs))
    hand_deck = association(deck, nb_joueurs)
    # print(masque(hand_deck, 1))
    # print(masque(hand_deck, 2))

    # création du process de gestion de partie
    j = Process(target=jeu, args=(deck, hand_deck, couleurs, pipe_parent, nb_joueurs))
    j.start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        # socket creation
        server_socket.setblocking(False)
        server_socket.listen(5)
        while serve.value:
            readable, writable, error = select.select([server_socket], [], [], 1)
            if server_socket in readable:  # if server_socket is ready
                client_socket, address = server_socket.accept()  # will return immediately
                p = Process(target=communication, args=(shared, client_socket, couleurs, deck, pipe_child))
                p.start()
