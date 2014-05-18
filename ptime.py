import time
import threading
import cProfile

def ptime(func):
    def _wrapper(*args, **kwargs):
        fname = func.func_name
        prof = cProfile.Profile()
        retval = prof.runcall(func, *args, **kwargs)
        tid = threading.current_thread()
        fn = ''.join([str(fname), str(tid), '.profile'])
        prof.dump_stats(fn)
        return retval
    return _wrapper
		
		