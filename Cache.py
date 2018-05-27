
import threading
import time
from enum import Enum
# from queue import Queue

# TODO: I probably want to package these classes within the Cache class, these interfaces don't need to be public


class CacheAction(Enum):
    ADD = 0
    UPDATE = 1
    GET = 2


class ListNode(object):

    def __init__(self, val):
        self.val = val
        self.next = None

    def __repr__(self):
        return str(self.val)




class ThreadNotifierFIFOList(object):

    def __init__(self, _condition):
        self.condition = _condition
        self._head = None
        self._tail = None

    def is_empty(self):
        return self._head is None

    def append(self, item):

        # if threads are asleep then wake them and make them do the worker

        self.condition.acquire()
        self.condition.notify_all()
        self.condition.release()


        # for condition in conditions:
        #     with condition:
        #         condition.notify_all()

        if self._head is None:
            self._head = ListNode(item)
            self._tail = self._head
        else:
            self._tail.next = ListNode(item)
            self._tail = self._tail.next

    def peek(self):
        return self._head.val

    def pop(self):

        # if there is another job have the threads do the worker on them
        # otherwise the threads sleep

        # with _cond:
        #     while self._head is None:
        #         _cond.wait()

        if self._head:
            item = self._head.val
            self._head = self._head.next
            return item
        else:
            return None

    # def __str__(self):
    #     cur = self._head
    #     representation = ''
    #     while cur is not None:
    #         representation +=
    #     return [str(cur) while]


class WorkerJob(object):

    def __init__(self, job_type, job_data):
        self.job_type = job_type
        self.job_data = job_data

condition = threading.Condition()
l = ThreadNotifierFIFOList(condition)
n = 3
# thread_start_semaphore = threading.Semaphore(n)         # TODO: this needs to be a class variable

NUM = 0


def worker():
    global condition
    global n
    # global thread_start_semaphore
    # global NUM

    while True:

        with condition:
            while l.is_empty():
                condition.wait()

            print(threading.get_ident())

            # Waiting for all threads to be active
            # thread_start_semaphore.acquire()
            # NUM += 1
            # while NUM != n:
            #     time.sleep(0.0001)

            print("worker has woken: ", threading.get_ident())
            time.sleep(0.001)

            print("object in q: ", l.pop())

            # Decreasing counter
            # NUM -= 1
            # thread_start_semaphore.release()


def create_threads():
    for i in range(n):                                                  # todo: change to self.n
        # conditions.append(threading.Condition())                        # todo: this needs to be a class variable
        # t = threading.Thread(target=worker, args=(conditions[-1], n,))
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()
        print(t)

create_threads()

l.append(1)

time.sleep(1)


# t1.start()
# time.sleep(2)
# t1.start()




















# def worker():
#     # read in value from the jobs queue
#     # test if it is an update or not
#
#     # if not update, find next index to remove (if set is full fidn index based on replacement algorithm)
#     # if update, then find the current position of the element and update accordingly (will only be in 1 set)
#             # issue: how do I differentiate the data on the same line of one set as another if keys are kept external ????
#
#             # a way around this: store the key with the value, so we will know what position the key is in
#             # and then when we check we only take the line where the key matches
#
#
#
#     # once i know which line to alter then I enter a thread safe region where the data is actually updated
#
#     # a note on races: we want to reduce the number of misses so we should only actually do replacement if there definitely
#     # isn't an available spot in one of the four sets, so there should be a check before doing this
#         # i don't think this is necessary actually, because we can just use the first to get placing it in alwyas
#
#     # on add: all threads race to get to this position and the first is the one that adds into it's corresponding set
#
#     #  on update: when a thread gets to this position it should only have an index to replace if it is the correct set,
#         # the other sets should have None and then exit gracefully
#         # this is where the issue will occur since multiple threads may have information on this line
#
#     print('In thread')










# time.time() ## to get the current time for comparisons




#
# class NWaySetAssociativeCache(object):
#
#     def __init__(self, n=4, replacement_algorithm="LRU", lines=32):
#         self.n = n
#         self.l = lines
#         self.data_information = {}                  # key: [most recent access time, line number]
#         self.set_fullness = [0] * n                 # number of elements currently in each set
#         self.sets = [[None] * self.l] * n           # the sets themselves, arrays with l lines, there are n of them
#
#         self.jobs_queue = ThreadNotifierFIFOList()
#
#         # Checking for custom replacement algorithm
#         if callable(replacement_algorithm):
#             self.replacement_algorithm = replacement_algorithm
#             return
#
#         # Checking for one of the preset replacement algorithms
#         elif replacement_algorithm.isalpha():
#             replacement_algorithm = replacement_algorithm.upper()
#             if replacement_algorithm == "LRU":
#                 self.replacement_algorithm = self._lru
#                 return
#             elif replacement_algorithm == "MRU":
#                 self.replacement_algorithm = self._mru
#                 return
#
#         # If we reach the end then no valid replacement algorithm was given
#         raise ValueError("Replacement algorithm parameter must designate LRU or MRU or be a function.")
#
#     def _lru(self, current_set):
#         """
#         :param current_set: a full set
#         :return: the index of the least recently used element within this set
#         """
#         pass
#
#     def _mru(self):
#         """
#         :param current_set: a full set
#         :return: the index of the most recently used element within this set
#         """
#         pass
#
#     def add(self, key, value):
#         if key not in self.data_information:
#             self.jobs_queue.append(WorkerJob(CacheAction.ADD, (key, value)))
#         else:
#             self.jobs_queue.append(WorkerJob(CacheAction.UPDATE, (key, value)))
#
#     def get(self, key):
#         self.jobs_queue.append(WorkerJob(CacheAction.GET, key))
#         # TODO: wait for thread response and then return the correct data
