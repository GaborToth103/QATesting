import time
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', handlers=[logging.StreamHandler(), logging.FileHandler('docs/info.log')])

def measure_time(func):
    """Measuring time spent on function"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        logging.info(f"{func.__name__} duration {elapsed_time:.6f} seconds, {args[0]} returned: {result}")
        return result
    return wrapper
