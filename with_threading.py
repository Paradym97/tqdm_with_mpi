import time
import threading
import functools
import tqdm


def long_running_function(*args, **kwargs):
    # print("Running with args:%s and kwargs:%s" % (args, kwargs))
    time.sleep(5)
    return "success"


def provide_progress_bar(function, estimated_time, tstep=0.2, tqdm_kwargs={}, args=[], kwargs={}):
    """Tqdm wrapper for a long-running function

    args:
        function - function to run
        estimated_time - how long you expect the function to take
        tstep - time delta (seconds) for progress bar updates
        tqdm_kwargs - kwargs to construct the progress bar
        args - args to pass to the function
        kwargs - keyword args to pass to the function
    ret:
        function(*args, **kwargs)
    """
    ret = [None]  # Mutable var so the function can store its return value
    def myrunner(function, ret, *args, **kwargs):
        ret[0] = function(*args, **kwargs)

    thread = threading.Thread(target=myrunner, args=(function, ret) + tuple(args), kwargs=kwargs)
    pbar = tqdm.tqdm(total=estimated_time, **tqdm_kwargs)

    thread.start()
    while thread.is_alive():
        thread.join(timeout=tstep)
        pbar.update(tstep)
    pbar.close()
    return ret[0]


def progress_wrapped(estimated_time, tstep=0.2, tqdm_kwargs={}):
    """Decorate a function to add a progress bar"""
    def real_decorator(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            return provide_progress_bar(function, estimated_time=estimated_time, tstep=tstep, tqdm_kwargs=tqdm_kwargs, args=args, kwargs=kwargs)
        return wrapper
    return real_decorator


@progress_wrapped(estimated_time=5)
def another_long_running_function(*args, **kwargs):
    # print("Running with args:%s and kwargs:%s" % (args, kwargs))
    time.sleep(5)
    return "success"



if __name__ == '__main__':
    # Basic example
    retval = provide_progress_bar(long_running_function, estimated_time=5)
    print(retval)

    # Full example
    retval = provide_progress_bar(long_running_function,
        estimated_time=5, tstep=1/5.0,
        tqdm_kwargs={"bar_format":'{desc}: {percentage:3.0f}%|{bar}| {n:.1f}/{total:.1f} [{elapsed}<{remaining}]'},
        args=(1, "foo"), kwargs={"spam":"eggs"}
    )
    print(retval)

    # Example of using the decorator
    retval = another_long_running_function()
    print(retval)