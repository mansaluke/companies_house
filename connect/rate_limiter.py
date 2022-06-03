from functools import wraps
import threading
import time
import logging
from connect.exceptions import TooManyRequests

now = time.monotonic if hasattr(time, 'monotonic') else time.time

class Throttler(object):
    '''
    Rate limit decorator class.
    '''
    def __init__(self, calls=600, call_period=500, current_time=now):
        self.call_limit = calls
        self.call_period = call_period
        self.current_time = current_time

        # Initialise the decorator state.
        self.last_reset = current_time()
        self.num_calls = 0

        # Add thread safety.
        self.lock = threading.RLock()

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kargs):
            with self.lock:
                if self.remaining_time() <= 0:
                    self.reseter()
                self.num_calls += 1
                if self.num_calls > self.call_limit:
                    self.sleeper()
            try:
                return func(*args, **kargs)
            except TooManyRequests:
                self.sleeper()
                self.reseter()
                return func(*args, **kargs)

        return wrapper

    def remaining_time(self):
        elapsed = self.current_time() - self.last_reset
        return self.call_period - elapsed

    def reseter(self):
        self.last_reset = self.current_time()
        self.num_calls = 0

    def sleeper(self):
        remaining_time = self.remaining_time()
        logging.info(f'Sleeping: {remaining_time}')
        time.sleep(remaining_time)
