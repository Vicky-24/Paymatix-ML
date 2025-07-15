import time
import logging

log_name = "application_log"
# Create and configure logger
logging.basicConfig(filename=f"{log_name}.log",
                    level=logging.INFO,
                    format='%(asctime)s | %(levelname)s | %(message)s',
                    filemode='w')
logger = logging.getLogger()


def measure_execution_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        # print(f"{func.__name__} execution time: {execution_time:.6f} seconds")
        return result, round(execution_time,3)
    return wrapper