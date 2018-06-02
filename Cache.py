
import threading
import time
from enum import Enum


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


class JobData(object):

    def __init__(self, key, data=None):
        self.key = key
        self.data = data


class WorkerJob(object):

    def __init__(self, job_type, job_data):
        self.job_type = job_type
        self.job_data = job_data

    def __repr__(self):
        return str(self.job_type) + " - " + str(self.job_data)


class CacheData(object):

    def __init__(self, key, data, next_item):
        self.key = key
        self.data = data
        self.next = next_item        # object used immediately less recently than this object
        self.prev = None        # object used immediately more recently than this object


class NWaySetAssociativeCache(object):

    def __init__(self, n=4, replacement_algorithm="LRU", lines=32):

        # Setting the replacement algorithm (Either LRU, MRU, or user-defined)
        self._replacement_algorithm = None
        if not self._set_replacement_algorithm(replacement_algorithm):
            raise ValueError("Replacement algorithm parameter must designate LRU or MRU or be a function.")

        self._number_of_sets = n
        self._lines_per_set = lines

        # Data storage and retrieval
        self._keys = set()
        self._sets = [{} for i in range(n)]
        self._data_head = [None] * n
        self._data_tail = [None] * n

        # Jobs parallelization objects
        self._new_job_condition = threading.Condition()
        self._jobs_queue = ThreadNotifierFIFOList(self._new_job_condition)
        self._job_finished = threading.Barrier(self._number_of_sets)
        self._write_lock = threading.Lock()
        self._get_condition = threading.Condition()

        self._get_data_set_index = None

        # Creating dedicated threads for reading/writing to each set
        self._create_threads()

    def _set_replacement_algorithm(self, replacement_algorithm):

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

    def _update_ordering(self, current_item, worker_thread_id):
        if current_item.prev:
            current_item.prev.next = current_item.next

        if current_item is self._data_tail[worker_thread_id]:
            self._data_tail[worker_thread_id] = current_item.prev
        else:
            current_item.next.prev = current_item.prev

    def _worker(self, worker_thread_id):

        # worker_thread_id corresponds with a set that this thread will always work on
        worker_set = self._sets[worker_thread_id]
        while True:

            # Waiting and acquiring new job when queue is not empty
            with self._new_job_condition:
                if self._jobs_queue.is_empty():
                    self._new_job_condition.wait()
            current_job = self._jobs_queue.peek()

            if current_job is not None:

                # Inserting new data
                if current_job.job_type is CacheAction.ADD:

                    # Determine if/which resource needs to be removed
                    remove_key = None
                    if len(worker_set) == self._lines_per_set:
                        remove_key = self._replacement_algorithm(worker_thread_id)

                    # Critical section, only allow changes to the cache if the job still exists
                    # Job will be removed from queue before the end of the thread safe critical section
                    self._write_lock.acquire()

                    if current_job is self._jobs_queue.peek():

                        # If a removal is necessary to maintain cache size
                        if remove_key:
                            self._update_ordering(worker_set.pop(remove_key), worker_thread_id)
                            self._keys.remove(remove_key)

                        worker_set[current_job.job_data.key] = CacheData(current_job.job_data.key, current_job.job_data.data, self._data_head[worker_thread_id])
                        self._data_head[worker_thread_id] = worker_set[current_job.job_data.key]

                        self._keys.add(current_job.job_data.key)

                        if self._data_tail[worker_thread_id] is None:
                            self._data_tail[worker_thread_id] = worker_set[current_job.job_data.key]

                        # The job has been completed
                        self._jobs_queue.pop()

                    self._write_lock.release()

                # Accessing/updating existing data
                else:

                    # Exactly one thread can act for a get/update job
                    if current_job.job_data.key in worker_set:

                        if current_job.job_type is CacheAction.GET:

                            self._get_data_set_index = worker_thread_id
                            with self._get_condition:
                                self._get_condition.notify_all()

                        else:

                            current_item = worker_set[current_job.job_data.key]

                            if current_job is self._jobs_queue.peek():

                                current_item.data = current_job.job_data.data

                                if current_item is not self._data_head[worker_thread_id]:

                                    # Updating linked list for keeping track of recent access within the cache
                                    self._update_ordering(current_item, worker_thread_id)
                                    current_item.prev = None
                                    current_item.next = self._data_head[worker_thread_id]
                                    self._data_head[worker_thread_id] = current_item

                        # The job has been completed
                        self._jobs_queue.pop()

            # Barrier to ensure that all threads finish the loop at the same time
            # This prevents a single thread from taking all of the jobs
            self._job_finished.wait()

    def _lru(self, current_set_id):
        """
        :param current_set: the ID of the set being accessed
        :return: the index of the least recently used element within this set
        """
        return self._data_tail[current_set_id].key

    def _mru(self, current_set_id):
        """
        :param current_set: the ID of the set being accessed
        :return: the index of the most recently used element within this set
        """
        return self._data_head[current_set_id].key

    def put(self, key, value):
        if key not in self._keys:
            self._jobs_queue.append(WorkerJob(CacheAction.ADD, JobData(key, value)))
        else:
            self._jobs_queue.append(WorkerJob(CacheAction.UPDATE, JobData(key, value)))

    def get(self, key):
        if key not in self._keys:
            raise ValueError("Specified key is not present in cache.")

        self._jobs_queue.append(WorkerJob(CacheAction.GET, JobData(key)))

        with self._get_condition:
            self._get_condition.wait()

        return self._sets[self._get_data_set_index][key].data

if __name__ == '__main__':
    test_cache = NWaySetAssociativeCache()
    test_cache.put(1, 10)
    test_cache.put(2, 20)

    time.sleep(0.0001)

    print(test_cache.get(1))
    print(test_cache.get(2))



























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
