import logging
import multiprocessing
import queue
import signal
import threading
import time

from usgplate.dicom.networking.storescp_server import StoreSCPServer, StoreSCPConfig

logger = logging.getLogger(__name__)

def raise_keyboard_interrupt(signum, frame):
    raise KeyboardInterrupt("Interrupted by signal: {}".format(signum))

def move_to_mp_queue(dicom_info_queue: queue.Queue,
                        mp_queue: multiprocessing.Queue,
                        event_stop: threading.Event ):
    logger.debug("The queue reader thread has been started")
    while not event_stop.is_set():      
        try:
            dicom_info_elem = dicom_info_queue.get(timeout=1)
        except queue.Empty:
            continue
        logger.debug("Received dicom info element: %s", dicom_info_elem)
        if mp_queue is not None:
            mp_queue.put(dicom_info_elem)
    logger.debug("The queue reader thread has been stopped")


def run_store_scp(mp_queue: multiprocessing.Queue = None,
                  store_scp_config: StoreSCPConfig = None):
    """
    Run the store scp server and move the received dicom info elements to the mp_queue
    Args and Kwargs are passed to the StoreSCPServer
    """
    if not store_scp_config:
        store_scp_config = StoreSCPConfig()
    store_scp = StoreSCPServer(store_scp_config)
    event_stop = threading.Event()
    queue_reader_thread = threading.Thread(target=move_to_mp_queue,
                                           args=(store_scp.received_queue,
                                                 mp_queue,
                                                 event_stop))
    queue_reader_thread.start()
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:   # is it okay to catch the KeyboardInterrupt only?
        pass
    finally:
        store_scp.stop()
        event_stop.set()
        queue_reader_thread.join()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, raise_keyboard_interrupt)
    signal.signal(signal.SIGTERM, raise_keyboard_interrupt)
    run_store_scp()
