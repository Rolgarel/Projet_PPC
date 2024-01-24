import math


# give a string describing the hand of another player
def hand(player, cards):
    res = "player " + str(player + 1) + ":\n"
    for i in range(len(cards)):
        if i != 0:
            res = res + "|"
        res = res + " " + str(i) + ":(" + cards[i][0] + " , " + str(cards[i][1]) + ") "
    res = res + "\n"
    return res


# give a string describing the hand of the current player
def self_hand(cards):
    res = "Your hand :\n"
    for i in range(len(cards)):
        if i != 0:
            res = res + " | "
        res = res + " " + str(i) + ":(*,*) "
    res = res + "\n"
    return res


# give a string describing the state of played cards
def table(tab, colors):
    res = "Played Cards :\n"
    for i in range(len(tab)):
        if i != 0:
            res = res + " | "
        res = res + " " + colors[i] + ": " + str(tab[i]) + " "
    res = res + "\n"
    return res


# give a string describing the remaining tokens
def tokens(fuse, info):
    res = "Fuse Tokens: " + str(fuse) + "\n"
    res = res + "Info Tokens: " + str(info) + "\n"
    return res


# give a string describing current information given to the player
def info(type, cards, data, player):
    res = "Player " + str(player + 1) + ": Cards {"
    for i in range(len(cards)):
        if i != 0:
            res = res + ", "
        res = res + str(cards[i] + 1)
    res = res + "} are all "
    if type == "c":
        res = res + data + " cards\n"
    else:
        res = res + str(data) + "s\n"
    return res


def ask():
    return "Your turn: Please enter \"play\" to play a card or \"info\" to give an info\n"


def wait():
    return "Please wait your turn\n"


def ask_info_player():
    return "Please enter the number of the player\n"


def ask_info_type():
    res = "Please enter \"c\" if you want to give information about one color"
    res = res + "or \"n\" if you want to give information about one number\n"
    return res


def ask_info_card():
    return "Please enter the number of one of the cards concerned by your info\n"


def ask_card():
    return "Please enter the number of the card you want to play\n"


def sent():
    return "Information sent\n"


# give a string composed of many returns to the line
def skip(n):
    res = ""
    for i in range(n):
        res = res + "\n"
    return res


# give a string describing the state of the ...
def state(colors, self, hands, tab, fuse, info):
    res = skip(100)
    res = res + "***********************************************************************************************\n"
    res = res + "     Actual turn\n"
    res = res + "***********************************************************************************************\n"
    res = res + skip(1)
    for i in range(len(hands)):
        if i != self:
            res = res + hand(i, hands[i])
    res = res + skip(1)
    res = res + table(tab, colors)
    res = res + tokens(fuse, info)
    res = res + skip(1)
    res = res + self_hand(hands[self])
    res = res + skip(1)
    res = res + "***********************************************************************************************\n"
    res = res + skip(1)
    return res


# give a string that describe the end of the game
def end(victory, tab):
    res = skip(100)
    res = res + "***********************************************************************************************\n"
    res = res + "\n"
    if victory:
        res = res + "     -=-= Victory =-=-\n"
        res = res + "\n"
        res = res + "  Score: " + str(score) + "\n"
    else:
        res = res + "     -=-= Defeat =-=-\n"
        res = res + "\n"
        res = res + "  Score: " + str(score(tab)) + "\n"
    res = res + "\n"
    res = res + "***********************************************************************************************\n"
    res = res + skip(2)
    return res


# give a score that depends on the played cards
def score(tab):
    res = 0
    for i in tab:
        res = res + int(math.fabs(i))
    return res


def server_init():
    return "Please enter the number of players\n"


def server_initialized():
    res = "The game is initialized!\n"
    res = res + "The players can now join the game\n"
    return res


def server_end(victory):
    res = "The game is finished!\n"
    res = res + "Players "
    if victory == 1:
        res = res + "Win\n"
    elif victory == -1:
        res = res + "Lose\n"
    return res
