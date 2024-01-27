import os
import sys
import select
import time
import socket
import signal
from multiprocessing import Value, Array, Process, Semaphore
from multiprocessing.managers import BaseManager
import random
import concurrent.futures
import multiprocessing
import game_handler
from shared import SharedMemoryManager, SharedData

# envoie de l'id du client + la table + les cartes + tokens + la liste des couleurs

serve = Value('b', True)
HOST = "localhost"
PORT = 6666
couleurs = ["Rouge", "Vert", "Jaune", "Bleu", "Blanc"]
PORT_SHARED = 6677
KEY = b'Hippopotomonstrosesquippedaliophobie'
SharedMemoryManager.register('SharedData', SharedData)


def signal_handler(sig, frame):
    # Signal de joueur prêt
    if sig == signal.SIGUSR1:
        nb_joueurs_pret.value = nb_joueurs_pret.value + 1
    # Signal de fin de tour
    if sig == signal.SIGUSR2:
        partie_en_cours.value = game_handler.end(shared_data.get_token_fuse(), shared_data.get_table())
        attente.value = False


# fonction qui transforme le handdeck avec des zeros  pour le joueur désigné
def masque(hand_deck, n_joueur):
    res = []
    for i in range(len(hand_deck)):
        if i != n_joueur:
            res.append(hand_deck[i])
        else:
            main = []
            for j in range(5):
                main.append((0, 0))
            res.append(main)
    return res


# créé un deck avec les couleurs correspondantes au nombre de joueurs
def couleur(couleurs, nb_joueurs):
    res = []
    nombre = [1, 1, 1, 2, 2, 3, 3, 4, 4, 5]
    for i in range(nb_joueurs):
        temp = []
        for j in nombre:
            temp.append((couleurs[i], j))
        res = res + temp
    return res


# mélange le deck
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


# initialise table
def inittable(nb_j):
    for i in range(nb_j):
        table[i] = 0


# envoie les informations à faire afficher par le client
def send_game_state(player_id, shared_data, socket):
    msg = str(player_id) + ";" + str(shared_data.get_token_fuse()) + ";" + str(shared_data.get_token_info()) + ";"
    msg = msg + str(shared_data.get_table()) + ";" + str(shared_data.get_hand_deck())
    # print(msg)
    socket.sendall(msg.encode())


# process de gestion des interactions des joueurs avec le jeu
def player(shared_data, client_socket, couleurs):
    # échange des ppid
    client_pid = int(client_socket.recv(1024).decode())
    print("pid client est : ", client_pid)
    ppid = os.getppid()
    client_socket.sendall((str(ppid)).encode())

    proc_name = multiprocessing.current_process().name
    num_play = int(proc_name[(len(proc_name) - 1):]) - 3
    player_pid[num_play] = client_pid

    send_game_state(num_play, shared_data, client_socket)

    # boucle de jeu
    while partie_en_cours.value == 0:
        if joueur_actif.value == num_play:
            send_game_state(num_play, shared_data, client_socket)
            req = client_socket.recv(1024).decode()
            req = req.split(";")
            if req[0] == "play":
                pass
            if req[0] == "info":
                pass
            # traitement
            client_socket.sendall("done".encode())


    # fin de partie


# process de gestion de la boucle de jeu
def game(colors, nb_joueurs, shared_data):
    # initialisation

    # boucle de gameplay
    while partie_en_cours.value == 0:
        if nb_joueurs_pret.value == nb_joueurs:
            joueur_actif.value = shared_data.get_turn() % nb_joueurs
            os.kill(player_pid[joueur_actif.value], signal.SIGUSR1)
            while attente.value:
                pass
            attente.value = True
            shared_data.increase_turn()

    # fin partie
    for i in player_pid.value:
        os.kill(i, signal.SIGUSR2)


if __name__ == "__main__":
    signal.signal(signal.SIGUSR1, signal_handler)
    signal.signal(signal.SIGUSR2, signal_handler)

    nb_joueurs = game_handler.server_players()

    partie_en_cours = Value('i', 0)
    nb_joueurs_pret = Value('i', 0)
    attente = Value('b', True)
    joueur_actif = Value('i', 0)
    player_pid = Array('i', range(nb_joueurs))

    # création et lancement de la shared memory
    shared_memory = SharedMemoryManager(address=('', PORT_SHARED), authkey=KEY)
    shared_memory.start()
    shared_data = shared_memory.SharedData()

    # initialisation des variables globales
    shared_data.set_token_info(3 + nb_joueurs)
    shared_data.set_token_fuse(3)
    shared_data.set_table([0] * nb_joueurs)
    d = melange(couleur(couleurs, nb_joueurs))
    hd = association(d, nb_joueurs)
    shared_data.set_deck(d)
    shared_data.set_hand_deck(hd)

    # création du process de gestion de partie
    j = Process(target=game, args=(couleurs, nb_joueurs, shared_data))
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
                p = Process(target=player, args=(shared_data, client_socket, couleurs))
                p.start()