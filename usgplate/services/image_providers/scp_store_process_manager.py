import logging
import multiprocessing as mp
import queue

from PySide6.QtCore import QObject, QThread, Signal

from usgplate.dicom.networking.storescp_server import StoreSCPConfig
from usgplate.dicom.runners.storescp_runner import run_store_scp
from usgplate.dicom.entities.dicom_instance_info import DicomInstanceInfo
from usgplate.dicom.repository.dcm_file_repository import DCMFileRepository
from .study_image_provider import StudyImageProvider
from usgplate.study.study import StudyProperties

logger = logging.getLogger(__name__)

class QueueReaderThread(QThread):
    element_read = Signal(object)

    def __init__(self, queue_: mp.Queue):
        super().__init__()
        self.queue = queue_

    def run(self):
        while not self.isInterruptionRequested():
            try:
                queue_elem = self.queue.get(timeout=1)
            except queue.Empty:
                continue
            self.element_read.emit(queue_elem)


class DicomScpStoreProcessMonitorThread(QThread):
    server_stopped = Signal()

    def __init__(self, poll_interval: int = 1):
        super().__init__()
        self.scp_process = None
        self.poll_interval = poll_interval

    def set_scp_process(self, scp_process: mp.Process):
        self.scp_process = scp_process

    def run(self):
        while not self.isInterruptionRequested():
            self.sleep(self.poll_interval)
            if not self.scp_process.is_alive():
                logger.info("Monitor thread detected that the scp process has stopped")
                self.server_stopped.emit()
                break

class DicomScpStoreProcessManager(StudyImageProvider):
    """
    This class is responsible for starting and stopping the scp process

    Todo: run manager in seperate thread, main problem is stop method, which is blocking
    """


    dicom_received = Signal(object)

    def __init__(self, scp_store_config: StoreSCPConfig) -> None:
        super().__init__()

        self.scp_process = None
        self.scp_queue = mp.Queue()
        self.queue_reader_thread = QueueReaderThread(self.scp_queue)
        self.queue_reader_thread.element_read.connect(self.on_dicom_received)
        self.server_monitor_thread = DicomScpStoreProcessMonitorThread()
        self.scp_store_config = scp_store_config
        self.dicom_repository = DCMFileRepository(repository_path=scp_store_config.dcm_repository_root)
        self.last_dicom_info = None

    def on_dicom_received(self, dicom_info: DicomInstanceInfo):
        self.dicom_received.emit(dicom_info)
        self.image_found.emit(str(self.dicom_repository.resolve_instance_path(dicom_info)))

        if self.last_dicom_info:
            if dicom_info.study_uid != self.last_dicom_info.study_uid:
                self.study_found.emit(StudyProperties( 
                    patient_id=dicom_info.patient_id,
                    patient_name=dicom_info.patient_name,
                    study_id=dicom_info.study_uid
                    ))
        self.last_dicom_info = dicom_info

    def start(self):
        logger.info("Starting the scp process")
        ctx = mp.get_context('spawn')
        self.scp_process = ctx.Process(target=run_store_scp,
                                       args=(self.scp_queue, self.scp_store_config))
        
        self.scp_process.start()
        self.server_monitor_thread.set_scp_process(self.scp_process)
        self.server_monitor_thread.start()
        self.queue_reader_thread.start()
        logger.info("The scp process has been started")

    def stop(self):
        if self.scp_process is None:
            return
        logger.info("Stopping the scp process")
        self.scp_process.terminate()
        self.scp_process.join(timeout=3)
        if self.scp_process.is_alive():
            self.scp_process.kill()
            self.scp_process.join()
        self.queue_reader_thread.requestInterruption()
        self.queue_reader_thread.wait()
        self.server_monitor_thread.requestInterruption()
        self.server_monitor_thread.wait()
        logger.info("The scp process has been stopped")

    def restart(self):
        logger.info("Restarting the scp process")
        self.stop()
        self.start()

    def set_config(self, scp_store_config: StoreSCPConfig):
        self.scp_store_config = scp_store_config
