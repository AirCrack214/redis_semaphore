from threading import Thread
import requests
from time import time
import sys
import logging

from distributed_semaphore import DistributedSemaphore


logger = logging.getLogger()
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s', "%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('socks').setLevel(logging.WARNING)


def send_request(request_index : int):
    with semaphore:
        r = requests.get(url)
        logger.info(f'Handled api request №{request_index} with status code {r.status_code}')


if __name__ == '__main__':
    logger.info('DistributedSemaphore API requests process started')
    start_timestamp = time()
    api_requests = 5
    semaphore_limit = 5
    url = 'https://www.yandex.ru/'
    
    semaphore = DistributedSemaphore(
        bounded_limit=semaphore_limit
    )
    
    threads = []
    for task_index in range(1, api_requests + 1):
        th = Thread(target=send_request, args=[task_index])
        th.start()
        threads.append(th)
        
    for th in threads:
        th.join()

    logger.info(f'DistributedSemaphore takes ~{round(time() - start_timestamp, 4)} seconds to handle {api_requests} with {semaphore_limit} bounded limit')