import threading

class Counter(object):

    def __init__(self):
        self.lock = threading.Lock()
        self.count = 0

    @property
    def value(self):
        return self.count

    def inc(self):
        try:
            self.lock.acquire()
            self.count = self.count + 1
        finally:
            self.lock.release()

    def dec(self):
        try:
            self.lock.acquire()
            self.count = self.count - 1
        finally:
            self.lock.release()


