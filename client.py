import os
import sys
import socket
import signal
import multiprocessing
from multiprocessing import Value, Array, Process, Semaphore
import time
from multiprocessing.managers import BaseManager
import game_handler
import display


HOST = "localhost"
PORT = 6666
couleurs = ["Red", "Green", "Yellow", "Blue", "White"]


def signal_handler(sig, frame):
    # Signal de début de tour
    if sig == signal.SIGUSR1:
        tour.value = True
    # Signal de fin de partie
    if sig == signal.SIGUSR2:
        en_cours.value = False


# permet de recevoir les informations à afficher et de les décoder
def receive_info(socket):
    msg = socket.recv(1024).decode()
    msg = msg.split(";")
    player_id = int(msg[0])
    fuse = int(msg[1])
    info = int(msg[2])
    table = decode_table(msg[3])
    hands = decode_hands(msg[4])
    return player_id, fuse, info, table, hands


# permet de décoder table à partir d'un string
def decode_table(t):
    table = []
    t = t[1:len(t)-1]
    t = t.split(", ")
    for i in t:
        table.append(int(i))
    return table


# permet de décoder hand_deck à partir d'un string
def decode_hands(h):
    h0 = []
    h = h[2:len(h) - 2]
    h = h.split("], [")
    for i in h:
        h1 = []
        i = i[1:len(i) - 1]
        i = i.split("), (")
        for y in i:
            y = y[1:]
            y = y.split("', ")
            h2 = (y[0], int(y[1]))
            h1.append(h2)
        h0.append(h1)
    return h0


# process de gestion de jeu
def game_client(colors, player_id, table, fuse, info, hand_deck, server_ppid, client_socket):
    # initialisation
    time.sleep(1)
    os.kill(server_ppid, signal.SIGUSR1)
    print(display.state(colors, player_id, hand_deck, table, fuse, info))  # les informations ont déjà été récupérées

    # boucle de gameplay
    while en_cours.value:
        if not tour.value and en_cours.value:
            print(display.wait())
        while not tour.value and en_cours.value:
            pass
        if tour.value:
            player_id, fuse, info, table, hand_deck = receive_info(client_socket)
            print(display.state(colors, player_id, hand_deck, table, fuse, info))
            request_type, content = game_handler.request(len(hand_deck), player_id, info, hand_deck)
            client_socket.sendall((request_type + ";" + str(player_id) + ";" + content).encode())
            tour.value = False
            client_socket.recv(1024).decode()
            os.kill(server_ppid, signal.SIGUSR2)

    # fin de partie
    player_id, fuse, info, table, hand_deck = receive_info(client_socket)
    print(display.end(game_handler.end(fuse, table), table))


if __name__ == "__main__":
    signal.signal(signal.SIGUSR1, signal_handler)
    signal.signal(signal.SIGUSR2, signal_handler)

    en_cours = multiprocessing.Value("b", True)
    tour = multiprocessing.Value("b", False)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        # échange des pid
        pid = os.getpid()
        client_socket.sendall((str(pid)).encode())
        server_ppid = int(client_socket.recv(1024).decode())
        # print("Le pid serveur est: ", server_ppid)

        player_id, fuse, info, table, hands = receive_info(client_socket)

        game_client(couleurs, player_id, table, fuse, info, hands, server_ppid, client_socket)
