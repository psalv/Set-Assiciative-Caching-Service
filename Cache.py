
import threading
from time import time
from enum import Enum


class CacheAction(Enum):
    ADD = 0
    UPDATE = 1


class ListNode(object):

    def __init__(self, val):
        self.val = val
        self.next = None


class ThreadNotifierFIFOList(object):

    def __init__(self):
        self._cond = threading.Condition()
        self._head = None
        self._tail = None

    def append(self, item):
        with self._cond:
            self._cond.notify_all()

        if self._head is None:
            self._head = ListNode(item)
            self._tail = self.head
        else:
            self._tail.next = ListNode(item)
            self._tail = self._tail.next

    def pop(self):
        with self._cond:
            while self._head is None:
                self._cond.wait()

            if self._head:
                item = self._head.val
                self._head = self._head.next
                return item
            else:
                return None







# current goal:
    # waking thread up when something add to queue and then printing that arg
    # getting it to act accordingly to the queue it is responding to
        # >>> only 1 queue??? check for updates upon action
        # this idea of just having one jobs queue seems to make the most sense


def worker():
    # read in value from the jobs queue
    # test if it is an update or not

    # if not update, find next index to remove (if set is full fidn index based on replacement algorithm)
    # if update, then find the current position of the element and update accordingly (will only be in 1 set)
            # issue: how do I differentiate the data on the same line of one set as another if keys are kept external ????

            # a way around this: store the key with the value, so we will know what position the key is in
            # and then when we check we only take the line where the key matches



    # once i know which line to alter then I enter a thread safe region where the data is actually updated

    # a note on races: we want to reduce the number of misses so we should only actually do replacement if there definitely
    # isn't an available spot in one of the four sets, so there should be a check before doing this
        # i don't think this is necessary actually, because we can just use the first to get placing it in alwyas

    # on add: all threads race to get to this position and the first is the one that adds into it's corresponding set

    #  on update: when a thread gets to this position it should only have an index to replace if it is the correct set,
        # the other sets should have None and then exit gracefully
        # this is where the issue will occur since multiple threads may have information on this line

    print('In thread')


class JobThread(threading.Thread):

    def run(self):
        print("running")


l = NotifierList()
t1 = JobThread(target=worker)
t1.start()



# time.time() ## to get the current time

class NWaySetAssociativeCache(object):

    def __init__(self, n=4, replacement_algorithm="LRU", lines=32):
        self.n = n
        self.l = lines
        self.data_information = {}                  # key: [most recent access time, line number]
        self.set_fullness = [0] * n                 # number of elements currently in each set
        self.sets = [[None] * self.l] * n           # the sets themselves, arrays with l lines, there are n of them

        self.jobs_queue = ThreadNotifierFIFOList()

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
        self.jobs_queue.append((key, value))
        # if key in self.data_information:
        #     self._update(key, value)
        # else:
        #     self.fifo_add.append((key, value))
    #
    # def _update(self, key, value):
    #     pass
