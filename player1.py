import os
import sys
import socket
import signal
import multiprocessing
import time
from multiprocessing.managers import BaseManager
import game_handler
import display
from shared import SharedMemoryManager, SharedData


HOST = "localhost"
PORT = 6666
PORT_SHARED = 6677
KEY = b'Hippopotomonstrosesquippedaliophobie'
SharedMemoryManager.register('SharedData', SharedData)


def signal_handler(sig, frame):
    # Signal de début de tour
    if sig == signal.SIGUSR1:
        tour.value = True
    # Signal de fin de partie
    if sig == signal.SIGUSR2:
        en_cours.value = False


def traduction(reponse):
    id_joueur = int(reponse[0])
    couleur = []
    table = []
    deck = []
    hand_deck = []
    hand = []
    i = 8
    temp = ""
    while reponse[i] != "]":
        while reponse[i] != "'":
            temp = temp + reponse[i]
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

    while reponse[i] != ";":  # i < len(reponse) :
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
        while reponse[i] != "(" and reponse[i] != "]":
            i = i + 1
        i = i + 1
        deck.append((temp, temp2))
    i = i + 1
    # reponse[i] = [
    while reponse[i] != "]":
        while reponse[i] != "]":
            temp = ""
            temp2 = 0
            i = i + 3
            # reponse[i] = ' ou 0
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
        hand_deck.append(hand)
        hand = []
        # reponse[i] = ]
        i = i + 1
    return id_joueur, couleur, hand_deck


def trad(reponse):
    rep = reponse.split(";")
    id_joueur = int(rep[0])
    couleur = trad_couleur(rep[1])
    hand_deck = trad_hand(rep[2])
    return id_joueur, couleur, hand_deck


def trad_couleur(c):
    pass  # à faire


def trad_hand(hd):
    pass  # à faire


# process de gestion de jeu
def game(shared_data, player_id, colors, hand_deck, server_ppid, client_socket):
    time.sleep(1)
    os.kill(server_ppid, signal.SIGUSR1)

    # boucle de gameplay
    while en_cours.value:
        print(display.state(colors, player_id, hand_deck, shared_data.get_table(), shared_data.get_token_fuse(), shared_data.get_token_info()))
        if not tour.value:
            print(display.wait())
        while not tour.value:
            pass
        request_type, content = game_handler.request(len(hand_deck), player_id)
        if request_type == "play":
            card_to_play = int(content)
            client_socket.sendall(str(player_id) + " " + str(card_to_play))
        else:
            player, info_type, cards = game_handler.info_complete(content)
            client_socket.sendall("info")
            # envoi aux client
            shared_data.decrease_token_info()
        tour.value = False
        os.kill(server_ppid, signal.SIGUSR2)
        time.sleep(1)

    # fin de partie
    print(display.end(game_handler.end(shared_data.get_token_fuse(), shared_data.get_table()), shared_data.get_table()))


if __name__ == "__main__":
    signal.signal(signal.SIGUSR1, signal_handler)
    signal.signal(signal.SIGUSR2, signal_handler)
    time.sleep(10)

    en_cours = multiprocessing.Value("b", True)
    tour = multiprocessing.Value("b", False)
    shared_memory = SharedMemoryManager(address=(HOST, PORT_SHARED), authkey=KEY)
    shared_memory.connect()
    shared_data = shared_memory.SharedData()
    print("shared : ", shared_data.get_table())

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        # échange des ppid
        ppid = os.getppid()
        client_socket.sendall((str(ppid)).encode())
        server_ppid = int(client_socket.recv(1024).decode())
        # print("Le ppid serveur est: ", server_ppid)

        rep = client_socket.recv(1024)
        reponse = rep.decode()
        id_joueur, couleur, hand_deck = traduction(reponse)
        # print("\n\n" + reponse)

        game(shared_data, id_joueur, couleur, hand_deck, server_ppid, client_socket)
