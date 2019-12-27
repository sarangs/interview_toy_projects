'''
@author: sarangsawant
'''
import threading
import Queue

pool_size = 10

class WorkQ(Queue.Queue):
    def __init__(self, func, maxsize):
        self.lock_req = maxsize != 0
        self.func = func
        self.semaphore = threading.Semaphore(maxsize)
        Queue.Queue.__init__(self, maxsize)
    
    def put(self, item):
        if self.lock_req:
            self.semaphore.acquire()
        Queue.Queue.put(self, item)
    
    def task_done(self):
        if self.lock_req:
            self.semaphore.release()
        Queue.Queue.task_done(self)

    
class Workers():
    def __init__(self, func, queue, result):
        self.func = func
        self.result = result 
        self.wQ = queue
        self.nworkers = pool_size
        self.w_workers = []
    
    def start(self):
        for i in range(self.nworkers):
            th = threading.Thread(target=self.worker)
            th.start()
            self.w_workers.append(th)
    
    def worker(self):
        while True:    
            wq = self.wQ.get()
            if wq is None:
                self.wQ.task_done()
                break
            wi = wq.get()
            args = wi
            res = wq.func(wi)
            self.result.update({args:res})
            wq.task_done()
            self.wQ.task_done()
    
    def enque(self, item):
        self.wQ.put(item)
    
    
    def terminate_workers(self):
        for j in range(self.nworkers):
            self.wQ.put(None)
        
        for k in range(self.nworkers):
            self.w_workers[k].join()
        
        self.wQ.join()
        
        

def square(x):
    return x*x


if __name__ == "__main__":
    queue = Queue.Queue()
    result = {}
    w = Workers(square, queue, result)
    w.start()
    for i in range(20):
        item = WorkQ(square, pool_size)
        
        item.put(i)
        w.enque(item)
        item.join()
    
    print(w.result)
    w.terminate_workers()
    