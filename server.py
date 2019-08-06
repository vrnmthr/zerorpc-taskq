import random

import gevent
import zerorpc
from gevent import subprocess
from gevent.event import AsyncResult
from gevent.lock import Semaphore, BoundedSemaphore
from gevent.queue import Queue


class Worker:

    def __init__(self, id, process, client):
        self.id = id
        self.process = process
        self.client = client
        self.pid = None


class Request:
    def __init__(self, function, args):
        """
        :param function: function to execute
        :param args: arguments to execute with
        :param worker: worker to execute on
        :param handler: greenlet handler
        """
        self.future = AsyncResult()
        self.worker = None
        self.handler = None
        self.function = function
        self.args = args
        self.pid = args["pid"]

    def assign_worker(self, worker):
        self.worker = worker
        worker.pid = self.pid
        print("request {} assigned to worker {}".format(self.pid, worker.id))

    def process(self):
        try:
            result = self.worker.client.call(self.function, self.args)
            self.future.set(result)  # complete the initial request
        except Exception as e:
            self.future.set_exception(e)

    def cancel(self):
        if self.worker is not None and self.handler is not None:
            # only cancel handler and process if already assigned
            self.worker.process.kill()
            print("killed worker {}".format(self.worker.id))
            self.handler.kill()
            print("killed handler {}".format(self.handler))

        # complete the future
        self.future.set("cancelled")


class MyService:

    def __init__(self, num_workers=1):
        self.taskq = Queue()
        # start the task daemon automatically
        gevent.spawn(self._taskd)

        # pid -> requests for all jobs
        self.requests = {}
        # id -> workers
        self.workers = {}
        self.lock = Semaphore()
        self.bound = BoundedSemaphore(num_workers)

        for _ in range(num_workers):
            self._start_and_register_worker()

    def _taskd(self):
        for request in self.taskq:  # blocks until next request
            # wait until a worker is free
            self.bound.acquire()
            # execute the job if not completed
            if not request.future.ready():
                with self.lock:
                    request.assign_worker(self._find_free_worker())
                    greenlet = gevent.spawn(request.process)
                    request.handler = greenlet
            else:
                print("request {} already completed, skipping assignment".format(request.pid))
                self.bound.release()

    def _find_free_worker(self):
        for id in self.workers:
            if self.workers[id].pid is None:
                return self.workers[id]
        print("no workers found")

    def _get_request_with_pid(self, pid):
        if pid in self.requests:
            return self.requests[pid]
        return None

    def cancel(self, pid):
        with self.lock:
            req = self._get_request_with_pid(pid)

            if req is not None:
                print("cancelling request {}".format(pid))
                req.cancel()
                if req.worker is not None:
                    print("unregistering worker {}".format(req.worker.id))
                    del self.workers[req.worker.id]
                    self._start_and_register_worker()
            else:
                print("pid {} not found".format(pid))

    def launch(self, function, args):
        try:
            # check for valid pid
            with self.lock:
                pid = args["pid"]
                print("received request {}".format(pid))
                if self._get_request_with_pid(pid) is not None:
                    raise ValueError("pid already exists")
                request = Request(function, args)
                self.taskq.put(request)
                self.requests[pid] = request
                print("queued request {}".format(pid))

            # block until request is completed (can also raise an exception)
            result = request.future.get()
            print("finished request {}".format(pid))
        except Exception as e:
            result = e
        finally:
            with self.lock:
                # remove the job from the jobs map if it is present (may not be if cancelled)
                if request.pid in self.requests:
                    del self.requests[request.pid]
                # free worker if necessary
                if request.worker is not None:
                    request.worker.pid = None
                    self.bound.release()
                print("released resources for request {}".format(pid))
            return result

    def _start_and_register_worker(self):
        port = random.randint(5000, 6000)
        endpoint = "tcp://127.0.0.1:{}".format(port)
        cmd = "python3 worker.py {}".format(endpoint)
        proc = subprocess.Popen(cmd, shell=True)
        client = zerorpc.Client(endpoint, timeout=100000, heartbeat=None)
        worker = Worker(port, proc, client)
        self.workers[worker.id] = worker
        print("started worker {}".format(port))


s = zerorpc.Server(MyService(), heartbeat=None)
s.bind("tcp://127.0.0.1:4444")
print("starting server...")
s.run()
