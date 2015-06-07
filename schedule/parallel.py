import threading
import multiprocessing

from . import CancelJob

def thread_func(job, job_func):
    assert job is not None
    assert job_func is not None

    ret = job_func()
    if isinstance(ret, CancelJob) or ret is CancelJob:
        job.canceled = True

def Thread(job):
    job_func = job.job_func
    def func():
        thread = threading.Thread(target=thread_func, args=(job, job_func))
        thread.start()
    return func

def process_func(job_func, queue):
    assert job_func is not None

    ret = job_func()
    queue.put(ret)

def Process(job):
    job_func = job.job_func
    queue = multiprocessing.Queue()
    
    def _func():
        process = multiprocessing.Process(target=process_func, args=(job_func, queue))
        process.start()
        process.join()

        if process.exitcode == 0:
            ret = queue.get()
        else:
            ret = None

        if isinstance(ret, CancelJob) or ret is CancelJob:
            job.canceled = True

    def func():
        thread = threading.Thread(target=_func)
        thread.start()

    return func

"""
def Pool(pool):
    def _Pool(job):
        job_func = job.job_func
        def func():
            pool.apply_async(run_func, (job, job_func))
        return func

    return _Pool
"""
