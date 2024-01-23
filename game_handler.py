import display


# give the type of request and a description of it
def request(nb_player, self):
    request_type = None
    print(display.ask())
    while request_type is None:
        try:
            request_type = input()
            if (request_type != "play") and (request_type != "info"):
                request_type = None
                print("Invalid input")
        except ValueError:
            print("Invalid input")
    if request_type == "play":
        content = play_card()
    else:
        content = give_info(nb_player, self)
    return request_type, content


# get the number of the card to play from the player
def play_card():
    card = None
    print(display.ask_card())
    while card is None:
        try:
            card = int(input())
            if card < 1 or card > 5:
                card = None
                print("Invalid input")
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
            if player < 1 or player > nb_player or player == (self + 1):
                player = None
                print("Invalid input")
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
    return str(player) + info_type + str(card)
