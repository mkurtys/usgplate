from dataclasses import dataclass
from pathlib import Path
import logging
import os

import PIL.Image
import PIL.ImageQt
import PySide6  # noqa
import pydicom
from PySide6.QtCore import QThreadPool, QMutex, QCoreApplication, QThread
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, QSize, Signal, QObject

from usgplate.dicom.image import pil_image_from_dicom
from usgplate.utils.worker import SimpleFutureWorker, Worker, WorkerSignals

logger = logging.getLogger(__name__)

@dataclass
class AnnotatedPixmap:
    pixmap: QPixmap
    thumbail: QPixmap
    filename: str


def is_file_dicom(filename: str|Path) -> bool:
    filename = Path(filename)
    print(filename, filename.suffix)
    return filename.suffix == ".dcm" or filename.suffix == ".dicom"


def qimage_from_dcm_or_img_file(filename: str|Path) -> QImage:
    filename = Path(filename)
    if is_file_dicom(filename):
        ds = pydicom.read_file(filename)
        image = pil_image_from_dicom(ds)
        qt_image = PIL.ImageQt.ImageQt(image)
        return QImage(qt_image)
    else:
        return QImage(str(filename))
    
def qpixmap_from_dcm_or_img_file(filename: str|Path) -> QPixmap:
    image = qimage_from_dcm_or_img_file(filename)
    return QPixmap.fromImage(image)


def centemeters_to_inches(centemeters: float) -> float:
    return centemeters/3.21

def pixels_for_cm_with_ppi(size_cm, ppi: int) -> int:
    size_inches = centemeters_to_inches(size_cm)
    points_needed = int(size_inches*ppi)
    return points_needed


def scale_qimage_with_ppi(qimage: QImage,
                     real_size_cm: float,
                     ppi: int) -> QImage:
    qimage_size = qimage.size()
    longer_axis_pixels, shorter_axis_pixels = max(qimage_size.toTuple()), min(qimage_size.toTuple())
    qimage_size_ratio = shorter_axis_pixels/longer_axis_pixels

    longer_axis_cm = real_size_cm
    shorter_axis_cm = real_size_cm*qimage_size_ratio

    longer_axis_pixels_for_ppi = min(pixels_for_cm_with_ppi(longer_axis_cm, ppi), longer_axis_pixels)
    shorter_axis_pixels_for_ppi = min(pixels_for_cm_with_ppi(shorter_axis_cm, ppi), shorter_axis_pixels)

    qimage_scaled = qimage.scaled( QSize(longer_axis_pixels_for_ppi, 
                                         shorter_axis_pixels_for_ppi), Qt.KeepAspectRatio)
    
    return qimage_scaled



class ImageFilesScaler(QObject):
    """
    Not thread safe.
    """

    finished = Signal()
    progress = Signal(float)

    def __init__(self, output_dir=".",  ppi: int=300, real_size_cm: float = 6.0) -> None:
        super().__init__()
        self.ppi: int = ppi
        self.real_size_cm=real_size_cm
        self.output_dir=output_dir
        self.thread_pool = QThreadPool()
        self.images_finished = 0
        self.images_total = 0

    def _scale_image_file_with_ppi(self, input_filename, output_filename):
        qimage = qimage_from_dcm_or_img_file(input_filename)
        qimage_scaled = scale_qimage_with_ppi(qimage, self.real_size_cm, self.ppi)
        logger.debug(f"Scaling {input_filename} size {qimage.size().toTuple()} {output_filename} size {qimage_scaled.size().toTuple()}")
        qimage_scaled.save(output_filename)


    def scale(self, filenames: list[str|Path]) -> list[str]:
        self.images_finished = 0
        self.images_total = len(filenames)
        output_filenames = []
        for filename in filenames:
            output_filename = os.path.join(self.output_dir, os.path.basename(filename).split(".")[0] + ".png")
            output_filenames.append(output_filename)
            worker = Worker(fn=self._scale_image_file_with_ppi,
                             input_filename=filename,
                             output_filename=output_filename)
            worker.signals.finished.connect(self._on_worker_finished)
            self.thread_pool.start(worker)
        self.thread_pool.waitForDone()
        return output_filenames


    def _on_worker_finished(self):
        self.images_finished += 1
        self.progress.emit(self.images_finished/self.images_total)
        if self.images_finished == self.images_total:
            self.finished.emit()


class PixmapCachedLoader:
    def __init__(self, thumbnail_size: int) -> None:
        self.thumbnail_size = thumbnail_size
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(10)
        self.queue_mutex = QMutex()
        self.cache = {}
        self.load_cache = {}

    def _read(self, filename: str|Path) -> AnnotatedPixmap:
        image = qimage_from_dcm_or_img_file(filename)
        pixmap = QPixmap.fromImage(image)
        # pixmap = QPixmap.fromImage(QImage(str(filename)))
        # do not scale pixmaps - we will use full size images
        thumbnail = pixmap.scaled(self.thumbnail_size, self.thumbnail_size, aspectMode=Qt.KeepAspectRatio)
        return AnnotatedPixmap(pixmap, thumbnail, str(filename))

    def load(self, filename: str|Path) -> SimpleFutureWorker[AnnotatedPixmap]:
        logger.debug(f"Creating worker for loading {filename}")
        worker = SimpleFutureWorker(self._read, filename=filename)
        worker.signals.result.connect(self._on_load_finished)
        self.load_cache[(str(filename))] = True
        self.thread_pool.start(worker)
        return worker

    def _on_load_finished(self, annotated_pixmap: AnnotatedPixmap):
        # self.queue_mutex.lock()
        del self.load_cache[annotated_pixmap.filename]
        self.cache[annotated_pixmap.filename] = annotated_pixmap
        # self.queue_mutex.unlock()
        logger.debug("Loaded pixmap: %s", annotated_pixmap.filename)    
    
    def get(self, filename: str|Path) -> AnnotatedPixmap:
        filename = str(filename)
        if filename in self.cache:
            return self.cache[filename]
        else:
            return None
    
    def request(self, filename: str|Path) -> AnnotatedPixmap:
        filename = str(filename)
        if filename in self.cache:
            return self.cache[filename]
        elif filename in self.load_cache:
            return None
        else:
            self.load(filename)
            return None
        
    def clear(self):
        self.cache.clear()
    
    def waitTillDone(self, msecs=-1):
        return self.thread_pool.waitForDone(msecs)