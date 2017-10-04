import threading
import queue

class ComputingThread(threading.Thread):


    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, daemon=None):
        super().__init__(group=group, target=target, name=name, args=args, kwargs=kwargs, daemon=daemon)
        self.queue = kwargs['queue']
        self.number = kwargs['number']

    def run(self):
        begin = 0
        end = self.number
        for i in range(begin, end + 1):
            if self.number % i == 0:
                self.queue.put("NOT PRIME")
                return
        self.queue.put("NOT SURE")
        return
