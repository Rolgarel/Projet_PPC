from multiprocessing.managers import BaseManager
from multiprocessing import Semaphore


SEM_LOCK = 6


# the manager of the shared memory
class SharedMemoryManager(BaseManager):
    pass


# the object containing the shared data (with the semaphores)
class SharedData:
    def __init__(self):
        self.token_info = 0
        self.sem_ti = Semaphore(SEM_LOCK)
        self.token_fuse = 0
        self.sem_tf = Semaphore(SEM_LOCK)
        self.table = []
        self.sem_tab = Semaphore(SEM_LOCK)

        self.turn = 0
        self.sem_turn = Semaphore(SEM_LOCK)

        self.hand_deck = []
        self.sem_hd = Semaphore(SEM_LOCK)
        self.deck = []
        self.sem_deck = Semaphore(SEM_LOCK)

    def get_table(self):
        res = []
        self.sem_tab.acquire()
        for i in self.table:
            res.append(i)
        self.sem_tab.release()
        return res

    def get_hand_deck(self):
        res = []
        self.sem_hd.acquire()
        for i in self.hand_deck:
            res.append(i)
        self.sem_hd.release()
        return res

    def get_deck(self):
        res = []
        self.sem_deck.acquire()
        for i in self.deck:
            res.append(i)
        self.sem_deck.release()
        return res

    def get_token_info(self):
        self.sem_ti.acquire()
        res = self.token_info
        self.sem_ti.release()
        return res

    def get_token_fuse(self):
        self.sem_tf.acquire()
        res = self.token_fuse
        self.sem_tf.release()
        return res

    def get_turn(self):
        self.sem_turn.acquire()
        res = self.turn
        self.sem_turn.release()
        return res

    def set_token_info(self, new_token_info):
        for i in range(SEM_LOCK):
            self.sem_ti.acquire()
        self.token_info = new_token_info
        for i in range(SEM_LOCK):
            self.sem_ti.release()

    def set_token_fuse(self, new_token_fuse):
        for i in range(SEM_LOCK):
            self.sem_tf.acquire()
        self.token_fuse = new_token_fuse
        for i in range(SEM_LOCK):
            self.sem_tf.release()

    def set_table(self, new_table):
        for i in range(SEM_LOCK):
            self.sem_tab.acquire()
        self.table = []
        for i in new_table:
            self.table.append(i)
        for i in range(SEM_LOCK):
            self.sem_tab.release()

    def set_hand_deck(self, new_table):
        for i in range(SEM_LOCK):
            self.sem_hd.acquire()
        self.hand_deck = []
        for i in new_table:
            self.hand_deck.append(i)
        for i in range(SEM_LOCK):
            self.sem_hd.release()

    def set_deck(self, new_table):
        for i in range(SEM_LOCK):
            self.sem_deck.acquire()
        self.deck = []
        for i in new_table:
            self.deck.append(i)
        for i in range(SEM_LOCK):
            self.sem_deck.release()

    # increment an int in the given position of table
    def tab_increment(self, position):
        for i in range(SEM_LOCK):
            self.sem_tab.acquire()
        self.table[position] = self.table[position] + 1
        for i in range(SEM_LOCK):
            self.sem_tab.release()

    def decrease_token_info(self):
        for i in range(SEM_LOCK):
            self.sem_ti.acquire()
        self.token_info = self.token_info - 1
        for i in range(SEM_LOCK):
            self.sem_ti.release()

    def decrease_token_fuse(self):
        for i in range(SEM_LOCK):
            self.sem_tf.acquire()
        self.token_fuse = self.token_fuse - 1
        for i in range(SEM_LOCK):
            self.sem_tf.release()

    def increase_token_info(self):
        for i in range(SEM_LOCK):
            self.sem_ti.acquire()
        self.token_info = self.token_info + 1
        for i in range(SEM_LOCK):
            self.sem_ti.release()

    def increase_token_fuse(self):
        for i in range(SEM_LOCK):
            self.sem_tf.acquire()
        self.token_fuse = self.token_fuse + 1
        for i in range(SEM_LOCK):
            self.sem_tf.release()

    def increase_turn(self):
        for i in range(SEM_LOCK):
            self.sem_turn.acquire()
        self.turn = self.turn + 1
        for i in range(SEM_LOCK):
            self.sem_turn.release()

    def get_card(self):
        res = ('null', 0)
        for i in range(SEM_LOCK):
            self.sem_deck.acquire()
        if self.deck:
            res = self.deck.pop()
        for i in range(SEM_LOCK):
            self.sem_deck.release()
        return res

    # give a card to a player
    def give_card(self, card, player, c_id):
        for i in range(SEM_LOCK):
            self.sem_hd.acquire()
        self.hand_deck[player][c_id] = card
        for i in range(SEM_LOCK):
            self.sem_hd.release()

    # remove a card from a player
    def take_card(self, card_id, player):
        for i in range(SEM_LOCK):
            self.sem_hd.acquire()
        res = self.hand_deck[player][card_id]
        self.hand_deck[player][card_id] = ('null', 0)
        for i in range(SEM_LOCK):
            self.sem_hd.release()
        return res
