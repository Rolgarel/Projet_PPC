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
PORT_SHARED = 6677
KEY = b'Hippopotomonstrosesquippedaliophobie'
SharedMemoryManager.register('SharedData', SharedData)


def signal_handler(sig, frame):
    # Signal de joueur prêt
    if sig == signal.SIGUSR1:
        nb_joueurs_pret.value = nb_joueurs_pret.value + 1
    # Signal de fin de tour
    if sig == signal.SIGUSR2:
        tour.value = tour.value + 1
        partie_en_cours.value = game_handler.end(shared_data.get_token_fuse(), table)
        attente.value = False


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


def communication(shared_data, client_socket, couleurs, deck, pipe_child):
    # échange des ppid
    client_pid = int(client_socket.recv(1024).decode())
    print("Son ppid client est : ", client_pid)
    ppid = os.getppid()
    client_socket.sendall((str(ppid)).encode())

    proc_name = multiprocessing.current_process().name
    num_play = int(proc_name[(len(proc_name) - 1):]) - 3
    # print(num_play)
    # print(str(num_play) + "")
    player_pid[num_play] = client_pid
    pipe = pipe_child[num_play - 1]
    # sockets[num_play - 1] = client_socket
    mess = (str(num_play) + ";" + str(shared_data.get_token_info()) + ";" + str(shared_data.get_token_fuse()) + ";"
            + str(couleurs) + ";" + str((shared_data.get_table()[:])) + ";" + str(deck) + ";" + str(masque(hand_deck,
                                                                                                           int(num_play))))
    # mess = str(num_play) + ";" + str(couleurs) + ";" + str(masque(hand_deck, num_play))
    # print(mess)
    client_socket.sendall(mess.encode())

    # boucle de jeu
    while partie_en_cours.value == 0:
        if attente.value == False:
            rep = client_socket.recv(1024).decode()
            pipe.send(rep)
        rep = pipe.recv()
        client_socket.sendall(rep)

    # fin de partie
    os.kill(client_pid, signal.SIGUSR2)


def send_card(pipe, card, card_id, player, player_id):
    if player != player_id:
        pipe.send((str(player) + " " + str(card_id) + " " + card[0] + " " + str(card[1])).encode())


# process de gestion de la boucle de jeu
def jeu(deck, hand_deck, colors, parent_pipe, nb_joueurs, shared_data):
    # initialisation

    # boucle de gameplay
    while partie_en_cours.value == 0:
        # print(str(nb_joueurs_pret.value))
        if nb_joueurs_pret.value == nb_joueurs:
            joueur_actif = tour.value % nb_joueurs
            os.kill(player_pid[joueur_actif], signal.SIGUSR1)
            while attente.value:
                pass
            attente.value = True
            reception = parent_pipe[joueur_actif].recv()
            if reception != "info":
                reception = int(reception)
                deck, hand_deck = game_handler.play(reception, joueur_actif, deck, hand_deck, shared_data.get_token_fuse(), shared_data.get_table(), colors)
                for i in range(nb_joueurs):
                    send_card(parent_pipe[i], hand_deck[player][reception], reception, i, joueur_actif)

    # fin partie


if __name__ == "__main__":
    signal.signal(signal.SIGUSR1, signal_handler)
    signal.signal(signal.SIGUSR2, signal_handler)

    couleurs = ["Rouge", "Vert", "Jaune", "Bleu", "Blanc"]
    nb_joueurs = game_handler.server_players()

    table = Array('i', range(nb_joueurs))

    partie_en_cours = Value('i', 0)
    nb_joueurs_pret = Value('i', 0)
    tour = Value('i', 0)
    attente = Value('b', True)
    player_pid = Array('i', range(nb_joueurs))

    # création et lancement de la shared memory
    shared_memory = SharedMemoryManager(address=('', PORT_SHARED), authkey=KEY)
    shared_memory.start()
    shared_data = shared_memory.SharedData()
    shared_data.set_token_info(3 + nb_joueurs)
    shared_data.set_token_fuse(3)
    shared_data.set_table([0] * nb_joueurs)

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
    j = Process(target=jeu, args=(deck, hand_deck, couleurs, pipe_parent, nb_joueurs, shared_data))
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
                p = Process(target=communication, args=(shared_data, client_socket, couleurs, deck, pipe_child))
                p.start()
