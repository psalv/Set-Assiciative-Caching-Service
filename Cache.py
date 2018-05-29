
import threading
import time
from enum import Enum


# TODO: I probably want to package these classes within the Cache class, these interfaces don't need to be public


class CacheAction(Enum):
    ADD = 0
    UPDATE = 1
    GET = 2


class ThreadNotifierFIFOList(object):

    class ListNode(object):

        def __init__(self, val):
            self.val = val
            self.next = None

        def __repr__(self):
            return str(self.val)

    def __init__(self, _condition):
        self._condition = _condition
        self._head = None
        self._tail = None

    def is_empty(self):
        return self._head is None

    def append(self, item):

        # if threads are asleep then wake them and make them do the worker

        with self._condition:
            self._condition.notify_all()         # all of the threads will awaken

        if self._head is None:
            self._head = ThreadNotifierFIFOList.ListNode(item)
            self._tail = self._head
        else:
            self._tail.next = ThreadNotifierFIFOList.ListNode(item)
            self._tail = self._tail.next

    def peek(self):
        if self._head is not None:
            return self._head.val
        else:
            return None

    def pop(self):
        if self._head:
            item = self._head.val
            self._head = self._head.next
            return item
        else:
            return None


class WorkerJob(object):

    def __init__(self, job_type, job_data):
        self.job_type = job_type
        self.job_data = job_data

    def __repr__(self):
        return str(self.job_type) + " - " + str(self.job_data)


"""

Key mapping strategy

I will be using double hashing.

To reduce the time it will take to entirely fill the cache, the cache will need to be larger than the number of 
elements it stores, and then when it reaches a certain threshold of fullness it will begin removing items.

    Make the table double the size of the number of available lines

This means that the removed items will not necessarily be in the position of the new item.

This also means that removed items must be marked with an AVAILABLE flag for open addressing.






To solve:
1) Store data in limited space
2) Store and update recently used
3) Be able to sift through items by hw recently they were used

    Idea: keep doubley linked list of everything that gets used (just pointers on the DataObjects)
    Update with each use (newly used at front, old at the back)
    
        Wouldn't need to keep the time of access, just the order
        Need a wrapper class for the data that has prev and next pointers
        
        ** I like this idea **





Email question:
I've been keep away from HashMaps as a way to store the data because I do not have explicit control

Hi!

I was working on this problem today (I implemented parallelization), and have reached the point where I'd like to refine 
the way in which I'm storing the data.

I had planned to implement a custom, fixed-size of hash table; however, the only advantage that I can see in using my own
over a hash map would be that when implementing my own I have explicit control over the size of the cache. 

My question then, is do you think the trade off of greater code complexity for more control 

"""


class NWaySetAssociativeCache(object):

    def __init__(self, n=4, replacement_algorithm="LRU", lines=32):

        # Setting the replacement algorithm (Either LRU, MRU, or user-defined)
        self._replacement_algorithm = None
        if not self.set_replacement_algorithm(replacement_algorithm):
            raise ValueError("Replacement algorithm parameter must designate LRU or MRU or be a function.")

        self._number_of_sets = n
        self._lines_per_set = lines



        # TODO
        self._data_information = {}                             # key: [most recent access time, line number]
        self._set_fullness = [0] * n                            # number of elements currently in each set
        self._sets = [[None] * self._lines_per_set] * n           # the sets themselves, arrays with l lines, there are n of them



        self._condition = threading.Condition()
        self._jobs_queue = ThreadNotifierFIFOList(self._condition)
        self._job_finished = threading.Barrier(self._number_of_sets)
        self._write_lock = threading.Lock()
        self._read_event = threading.Event()

        self._temp_get_set_number = None
        self._temp_get_line_number = None

        # Creating dedicated threads for reading/writing to each set
        self._create_threads()

    def set_replacement_algorithm(self, replacement_algorithm):

        # Checking for custom replacement algorithm
        if callable(replacement_algorithm):
            self._replacement_algorithm = replacement_algorithm
            return True

        # Checking for one of the preset replacement algorithms
        elif replacement_algorithm.isalpha():
            replacement_algorithm = replacement_algorithm.upper()
            if replacement_algorithm == "LRU":
                self._replacement_algorithm = self._lru
                return True
            elif replacement_algorithm == "MRU":
                self._replacement_algorithm = self._mru
                return True

        # If we reach the end then no valid replacement algorithm was given
        return False

    def _create_threads(self):
        for i in range(self._number_of_sets):
            worker_thread = threading.Thread(target=self._worker, args=(i,))
            worker_thread.daemon = True
            worker_thread.start()

    def _worker(self, worker_thread_id):  # worker_thread_id corresponds with a set that this thread will always work on
        while True:

            with self._condition:
                if self._jobs_queue.is_empty():
                    self._condition.wait()

            current_job = self._jobs_queue.peek()

            # If another thread completes the action first
            if current_job is not None:

                # Inserting new data
                if current_job.job_type is CacheAction.ADD:

                    # TODO: find open position, may need to invoke replacemnt algorithm

                    # Critical section, only allow changes to the cache if the job still exists
                    # Job will be removed before the end of the thread safe critical section
                    self._write_lock.acquire()

                    if current_job is self._jobs_queue.peek():
                        print(worker_thread_id, current_job)

                        # TODO: update the associated fields, using the open position

                        # The job has been completed
                        self._jobs_queue.pop()

                    self._write_lock.release()

                # Accessing/updating existing data
                else:

                    # TODO: find position of current data, if the element is not here then break (cannot continue, need to meet at barrier)

                    if current_job.job_type is CacheAction.GET:
                        pass    # TODO: temporarily store the data in a shared class variable indicating the set and line number
                        # TODO: set an Event to tell the main thread
                        self._read_event.set()

                    else:

                        # Critical section, only allow changes to the cache if the job still exists
                        # Job will be removed before the end of the thread safe critical section
                        self._write_lock.acquire()

                        if current_job is self._jobs_queue.peek():
                            # TODO: update the associated fields, using the found position

                            # The job has been completed
                            self._jobs_queue.pop()

                        self._write_lock.release()

            # Barrier to ensure that all threads finish the loop at the same time
            # This prevents a single thread from taking all of the jobs
            self._job_finished.wait()

    def _lru(self, current_set):
        """
        :param current_set: a full set
        :return: the index of the least recently used element within this set
        """
        # TODO, implement LRU algorithm
        pass

    def _mru(self, current_set):
        """
        :param current_set: a full set
        :return: the index of the most recently used element within this set
        """
        # TODO, implement MRU algorithm
        pass

    def put(self, key, value):
        if key not in self._data_information:
            self._jobs_queue.append(WorkerJob(CacheAction.ADD, (key, value)))
        else:
            self._jobs_queue.append(WorkerJob(CacheAction.UPDATE, (key, value)))

    def get(self, key):
        self._jobs_queue.append(WorkerJob(CacheAction.GET, key))
        with self._read_event:
            self._read_event.wait()
            self._read_event.clear()

        # TODO: using the temporary variables return the required data


if __name__ == '__main__':
    test_cache = NWaySetAssociativeCache()
    test_cache.put(1, 1)
    test_cache.put(2, 2)
    test_cache.put(3, 3)
    time.sleep(2)


































### HARD TIME


#
# if current_job.job_type is CacheAction.ADD:
#     print("ADD")
#
#     # find position
#     # possibly involve the replacement algorithm
#
#     self._read_write_lock.acquire()
#
#     if current_job is self._jobs_queue.peek():
#         # update required fields
#
#         self._jobs_queue.pop()
#
#     self._read_write_lock.release()
#
#     # release lock
#
# elif current_job.job_type is CacheAction.UPDATE:
#
#     # search expected position
#
#
#     self._read_write_lock.acquire()
#
#     if current_job is self._jobs_queue.peek():
#         # update required fields
#
#         self._jobs_queue.pop()
#
#     self._read_write_lock.release()
#
#     # if we find the correct value
#
#     # updated required fields
#
#     # pop the job
#
# else:  # CacheAction.GET
#     pass





















#### DEATH ROW


# class FinishedEvent(threading.Event):
#
#     def __init__(self, _n):
#         super().__init__()
#         self._n = _n
#         self._count = 0
#
#     def set(self):
#         self._count += 1
#         if self._count == self._n:
#             with self._cond:
#                 self._flag = True
#                 self._cond.notify_all()
#
#     def clear(self):
#         with self._cond:
#             self._flag = False
#             self._count = 0











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



#
#
#
# def worker(condition, jobs_queue):
#     while True:
#
#         with condition:
#             if l.is_empty():
#                 condition.wait()
#
#             print("worker has woken: ", threading.get_ident())
#             time.sleep(0.001)
#
#             # do work
#
#             # need to have critical sections associated with popping and doing the actual updates to the class variables
#                 # time.time() ## to get the current time for comparisons
#
#             l.pop()
