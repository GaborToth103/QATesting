import time
import logging

def measure_time(func):
    """Measuring time spent on function"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        logging.info(f"{func.__name__} duration {elapsed_time:.0f} seconds, returned: {result}")
        return result, elapsed_time
    return wrapper