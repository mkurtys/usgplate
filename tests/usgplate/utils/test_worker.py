from usgplate.utils.worker import Worker, SimpleFutureWorker
from PySide6.QtCore import Qt, QRunnable, QThreadPool, QMutex




def test_simple_future(qtbot):

    def long_running_function():
        import time
        time.sleep(1)
        return 42

    thread_pool = QThreadPool()
    simple_future = SimpleFutureWorker(long_running_function)
    thread_pool.start(simple_future)
    result = simple_future.get()
    assert result == 42
    





