import random
from multiprocessing import Value, Array

nb_joueurs = 2
couleurs = Array('s', range(5))
table = Array(('s','i'), range(nb_joueurs))

def couleur(nb_joueurs):
    res = []
    couleurs = ["Rouge", "Vert", "Jaune", "Bleu", "Blanc"]##a mettre dans le main
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
        index = random.randint(0,len(deck)-1)
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

table[0].append([('uiop',1)])
print(table)
#print(association(melange(couleur(nb_joueurs)), nb_joueurs))

