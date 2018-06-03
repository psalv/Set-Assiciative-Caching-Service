
import threading
from enum import Enum


class CacheAction(Enum):
    PUT = 0
    GET = 1


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

    def __repr__(self):
        return str(self.key) + " - " + str(self.data)


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
        self.prev = None             # object used immediately more recently than this object

    def __repr__(self):
        return str(self.key) + " - " + str(self.data)


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
        self.data_head = [None] * n
        self.data_tail = [None] * n

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
        elif isinstance(replacement_algorithm, str):
            replacement_algorithm = replacement_algorithm.upper()
            if replacement_algorithm == "LRU":
                self._replacement_algorithm = self.lru
                return True
            elif replacement_algorithm == "MRU":
                self._replacement_algorithm = self.mru
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

        if current_item is self.data_tail[worker_thread_id]:
            self.data_tail[worker_thread_id] = current_item.prev
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
                if current_job.job_data.key not in self._keys:

                    # Determine if/which resource needs to be removed
                    remove_key = None
                    if len(worker_set) == self._lines_per_set:
                        remove_key = self._replacement_algorithm(self, worker_thread_id)

                    # Critical section, only allow changes to the cache if the job still exists
                    # Job will be removed from queue before the end of the thread safe critical section
                    self._write_lock.acquire()

                    if current_job is self._jobs_queue.peek():

                        # If a removal is necessary to maintain cache size
                        if remove_key:
                            self._update_ordering(worker_set.pop(remove_key), worker_thread_id)
                            self._keys.remove(remove_key)

                        worker_set[current_job.job_data.key] = CacheData(current_job.job_data.key, current_job.job_data.data, self.data_head[worker_thread_id])

                        if self.data_head[worker_thread_id]:
                            self.data_head[worker_thread_id].prev = worker_set[current_job.job_data.key]

                        self.data_head[worker_thread_id] = worker_set[current_job.job_data.key]

                        self._keys.add(current_job.job_data.key)

                        if self.data_tail[worker_thread_id] is None:
                            self.data_tail[worker_thread_id] = worker_set[current_job.job_data.key]

                        # The job has been completed
                        self._jobs_queue.pop()

                    self._write_lock.release()

                # Accessing/updating existing data
                else:

                    # Exactly one thread can act for a get/update job
                    if current_job.job_data.key in worker_set:

                        if current_job.job_type == CacheAction.GET:

                            self._get_data_set_index = worker_thread_id
                            with self._get_condition:
                                self._get_condition.notify_all()

                        else:

                            current_item = worker_set[current_job.job_data.key]

                            if current_job is self._jobs_queue.peek():

                                current_item.data = current_job.job_data.data

                                if current_item is not self.data_head[worker_thread_id]:

                                    # Updating linked list for keeping track of recent access within the cache
                                    self._update_ordering(current_item, worker_thread_id)
                                    current_item.prev = None
                                    current_item.next = self.data_head[worker_thread_id]

                                    if self.data_head[worker_thread_id]:
                                        self.data_head[worker_thread_id].prev = worker_set[current_job.job_data.key]

                                    self.data_head[worker_thread_id] = current_item

                        # The job has been completed
                        self._jobs_queue.pop()

            # Barrier to ensure that all threads finish the loop at the same time
            # This prevents a single thread from taking all of the jobs
            self._job_finished.wait()

    @staticmethod
    def lru(class_instance, current_set_id):
        return class_instance.data_tail[current_set_id].key

    @staticmethod
    def mru(class_instance, current_set_id):
        return class_instance.data_head[current_set_id].key

    def put(self, key, value):
        self._jobs_queue.append(WorkerJob(CacheAction.PUT, JobData(key, value)))

    def get(self, key):
        if key not in self._keys:
            raise ValueError("Specified key is not present in cache.")

        self._jobs_queue.append(WorkerJob(CacheAction.GET, JobData(key)))

        with self._get_condition:
            self._get_condition.wait()

        return self._sets[self._get_data_set_index][key].data
