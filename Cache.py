
import threading
from time import time
from enum import Enum


class CacheAction(Enum):
     ADD = 0
     UPDATE = 1


class NotifierList(list):

    def __init__(self, code, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.list_code = code
        self._cond = threading.Condition()

    def append(self, item):
        with self._cond:
            super().append(item)
            self._cond.notify_all()

    def pop_or_sleep(self):
        with self._cond:
            while not len(self):
                self._cond.wait()
            return self.pop()




# time.time() ## to get the current time

class NWaySetAssociativeCache(object):

    def __init__(self, n=4, replacement_algorithm="LRU", lines=32):
        self.n = n
        self.l = lines
        self.data_information = {}                  # key: most recent access time
        self.set_fullness = [0] * n                 # number of elements currently in each set
        self.sets = [[None] * self.l] * n           # the sets themselves, arrays with l lines, there are n of them

        # When updated these lists will notify the threads that there is work to do
        self.fifo_add = NotifierList(CacheAction.ADD)
        self.fifo_update = NotifierList(CacheAction.UPDATE)

        # Checking for custom replacement algorithm
        if callable(replacement_algorithm):
            self.replacement_algorithm = replacement_algorithm
            return

        # Checking for one of the preset replacement algorithms
        elif replacement_algorithm.isalpha():
            replacement_algorithm = replacement_algorithm.upper()
            if replacement_algorithm == "LRU":
                self.replacement_algorithm = self._lru
                return
            elif replacement_algorithm == "MRU":
                self.replacement_algorithm = self._mru
                return

        # If we reach the end then no valid replacement algorithm was given
        raise ValueError("Replacement algorithm must designate LRU or MRU or be a function.")

    def _lru(self, current_set):
        """
        :param current_set: a full set
        :return: the index of the least recently used element within this set
        """
        pass

    def _mru(self):
        """
        :param current_set: a full set
        :return: the index of the most recently used element within this set
        """
        pass

    def add(self, key, value):
        if key in self.data_information:
            self._update(key, value)
        else:
            self.fifo_add.append((key, value))

    def _update(self, key, value):
        pass
