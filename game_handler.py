import display


# give the type of request and a description of it
def request(nb_player, self, token_info, hands):
    request_type = None
    print(display.ask())
    while request_type is None:
        try:
            request_type = input()
            if (request_type != "play") and (request_type != "info"):
                request_type = None
                print("Invalid input")
            if (request_type == "info") and (token_info < 1):
                request_type = None
                print("You can't share an information because their is no more information token")
        except ValueError:
            print("Invalid input")
    if request_type == "play":
        content = play_card(hands, self)
    else:
        content = give_info(nb_player, self)
    return request_type, content


# get the number of the card to play from the player
def play_card(hands, self):
    card = None
    print(display.ask_card())
    while card is None:
        try:
            card = int(input())
            if card < 1 or card > 5:
                card = None
                print("Invalid input")
            if hands[self][card - 1] == ('null', 0):
                card = None
                print("You can't share a card that does not exist")
        except ValueError:
            print("Invalid input")
    card = card - 1
    return str(card)


# get a description of what info the player want to share
def give_info(nb_player, self):
    player = None
    print(display.ask_info_player())
    while player is None:
        try:
            player = int(input())
            if player < 1 or player > nb_player:
                player = None
                print("Invalid input")
            if player == (self + 1):
                player = None
                print("You can't share information about yourself")
        except ValueError:
            print("Invalid input")
    player = player - 1
    info_type = None
    print(display.ask_info_type())
    while info_type is None:
        try:
            info_type = input()
            if (info_type != "c") and (info_type != "n"):
                info_type = None
                print("Invalid input")
        except ValueError:
            print("Invalid input")
    card = None
    print(display.ask_info_card())
    while card is None:
        try:
            card = int(input())
            if card < 1 or card > 5:
                card = None
                print("Invalid input")
        except ValueError:
            print("Invalid input")
    card = card - 1
    return str(player) + " " + info_type + " " + str(card)


# request the number of players (to use at the start of the server)
def server_players():
    nb_players = None
    print(display.server_init())
    while nb_players is None:
        try:
            nb_players = int(input())
            if nb_players < 2 or nb_players > 5:
                nb_players = None
                print("Invalid input")
        except ValueError:
            print("Invalid input")
    return nb_players


# complete the info request from the player with the missing cards
def info_complete(info, hands):
    content = info.split()
    player = int(content[0])
    info_type = content[1]
    cards = []
    for i in range(len(hands[player])):
        if info_type == "c":
            if hands[player][i][0] == hands[player][int(content[2])][0]:
                cards.append(i)
        else:
            if hands[player][i][1] == hands[player][int(content[2])][1]:
                cards.append(i)
    return player, info_type, cards


# Say if the victory conditions are met
def victory(table):
    res = True
    for i in table:
        if i != 5:
            res = False
    return res


# Give the state of the game: 0 -> still going, 1 -> victory, -1 -> defeat
def end(fuse, table):
    res = 0
    if fuse < 1:
        res = - 1
    if victory(table):
        res = 1
    return res


# get the id of a color
def color_id(color, colors):
    res = -1
    for i in range(len(colors)):
        if colors[i] == color:
            res = i
    return res
