from multiprocessing.managers import BaseManager
from multiprocessing import Semaphore


SEM_LOCK = 6


# the manager of the shared memory
class SharedMemoryManager(BaseManager):
    pass


# the object containing the shared data (with the semaphores)
class SharedData:
    def __init__(self):
        # add lock
        self.token_info = 0
        self.sem_ti = Semaphore(SEM_LOCK)
        self.token_fuse = 0
        self.sem_tf = Semaphore(SEM_LOCK)
        self.table = []
        self.sem_tab = Semaphore(SEM_LOCK)

    def get_table(self):
        res = []
        self.sem_tab.acquire()
        for i in self.table:
            res.append(i)
        self.sem_tab.release()
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

    # increment an int in the given position of table
    def tab_increment(self, position):
        for i in range(SEM_LOCK):
            self.sem_tab.acquire()
        self.table[position] = self.table[position] + 1
        for i in range(SEM_LOCK):
            self.sem_tab.release()
