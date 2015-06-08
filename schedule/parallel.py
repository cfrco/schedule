import threading
import multiprocessing
from functools import wraps

from . import CancelJob

def thread_func(job, job_func):
    assert job is not None
    assert job_func is not None

    ret = job_func()
    if isinstance(ret, CancelJob) or ret is CancelJob:
        job.canceled = True

    job.running_count.dec()

def Thread(job):
    job_func = job.job_func

    @wraps(job_func)
    def func():
        job.running_count.inc()
        thread = threading.Thread(target=thread_func, args=(job, job_func))
        thread.start()

    func.args = job_func.args
    func.keywords = job_func.keywords

    return func

def process_func(job_func, queue):
    """This function would be run in forked Processs. """
    assert job_func is not None

    ret = job_func()
    if queue:
        queue.put(ret)

    return ret

def process_thread_func(job, job_func, queue):
    process = multiprocessing.Process(target=process_func, args=(job_func, queue))
    process.start()
    process.join()

    if process.exitcode == 0:
        ret = queue.get()
        if isinstance(ret, CancelJob) or ret is CancelJob:
            job.canceled = True

    job.running_count.dec()

def Process(job):
    job_func = job.job_func
    queue = multiprocessing.Queue()

    @wraps(job_func)
    def func():
        job.running_count.inc()
        thread = threading.Thread(target=process_thread_func, args=(job, job_func, queue))
        thread.start()

    func.args = job_func.args
    func.keywords = job_func.keywords
    return func

def pool_thread_func(pool, job, job_func):
    result = pool.apply_async(process_func, args=(job_func, None))
    ret = result.get()

    if isinstance(ret, CancelJob) or ret is CancelJob:
        job.canceled = True

    job.running_count.dec()

def Pool(pool):
    def _Pool(job):
        job_func = job.job_func

        @wraps(job_func)
        def func():
            job.running_count.inc()
            thread = threading.Thread(target=pool_thread_func, args=(pool, job, job_func))
            thread.start()

        func.args = job_func.args
        func.keywords = job_func.keywords
        return func

    return _Pool
