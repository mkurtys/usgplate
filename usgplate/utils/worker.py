import sys
import traceback
from typing import Generic, TypeVar, Callable
T = TypeVar('T')

from PySide6.QtCore import QRunnable, Slot, Signal, QObject, QSemaphore


# https://www.pythonguis.com/tutorials/multithreading-pyside6-applications-qthreadpool/

class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    progress
        int indicating % progress

    '''
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(int)


class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        # self.kwargs['progress_callback'] = self.signals.progress

    @Slot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done


class SimpleFutureWorker(Generic[T], QRunnable):

    _SEMAPHORE_GUADS = 1000

    def __init__(self, fn: Callable[..., T], *args, **kwargs):
        super(SimpleFutureWorker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.result = None
        self._is_running = False
        self._is_finished = False
        self._semaphore = QSemaphore(SimpleFutureWorker._SEMAPHORE_GUADS)
        self._semaphore.acquire(SimpleFutureWorker._SEMAPHORE_GUADS)

        # Add the callback to our kwargs
        # self.kwargs['progress_callback'] = self.signals.progress

    def run(self) -> None:
        '''
        Initialise the runner function with passed args, kwargs.
        '''
        # Retrieve args/kwargs here; and fire processing using them
        self._is_running = True
        try:
            # from PySide6.QtCore import QThread
            # QThread.msleep(1000)
            self.result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(self.result)  # Return the result of the processing
        finally:
            self._is_finished = True
            self._is_running = True
            self.signals.finished.emit()  # Done
            self._semaphore.release(SimpleFutureWorker._SEMAPHORE_GUADS)

    def is_finished(self) -> bool:
        return self._is_finished
    
    def is_running(self) -> bool:
        return self._is_running
    
    def get(self) -> T:
        self._semaphore.acquire(1)
        result = self.result
        self._semaphore.release(1)
        return result
        
    



