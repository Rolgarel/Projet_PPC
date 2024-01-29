# PPC Project - Hannabis :


This project aim to implement in Python a simplified version of the cooperative card game Hannabi.
It can be played from two to five players, in separate terminals.

---
## Rules of the game :

In this game the goal of the players is to make a suite of cards of every color.
The number of colors is equal to the number of players. For every color in the deck, there is three 1s, two 2s, two 3s, two 4s and one 5.
The game start with three fuse tokens, the number of players plus three information tokens and a hand of five cards from the deck.
During the game a player can't see his own cards, but he can see those of the others.
On each of their turn a player can either give an information on the cards of another player or play a card.
If he chose to give an information, the player can either point all the cards of a given number or a given color, which consume one information token.
If he chose to play a card, the play need to choose a card from his hand and then attempt to add it to the cards already played.
If the card is a 1 of an unplaced color or a card equal to one plus the number of the already played card of the color, the player is successful.
In this case, if the card was a 5, one information token is restored.
In the other hand, if the card is misplayed, it is then discarded and one fuse token is consumed.
The game end if all the 5s cards are played, in which case it is a game win, or if there is no more fuse tokens available.

---
## How to play :

Before anything, you need to be sure that you already have the last version of the sysv_ipc module.
If you don't, you can install it from the official website : https://semanchuk.com/philip/sysv_ipc/.
- First, you need to clone this repository on your device.
- Then, you need to start a terminal and launch a server. For this, you need to use the command "python3 server.py".
- After this, follow the instructions given by the server.
- Now, you can start the clients. For this, you first need to start a number of terminal equal to the desired number of players. Then you need to launch the clients by using the command "python3 client.py" on all those terminals.
- You can now play the game.

---