
import logging
from PySide6.QtCore import Qt, QAbstractListModel, QItemSelectionModel, QModelIndex, QSize, QRect
from PySide6.QtGui import QPixmap, QColor, QColorConstants
from PySide6.QtWidgets import QWidget, QSizePolicy, QStyledItemDelegate, QListView, QHBoxLayout, QStyle

from usgplate.pixmap.pixmap import AnnotatedPixmap
from usgplate.utils.worker import SimpleFutureWorker

logger = logging.getLogger(__name__)

class AnnotatedPixmapModel(QAbstractListModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pixmaps: list[SimpleFutureWorker[AnnotatedPixmap]] = []

    def rowCount(self, parent):
        return len(self.pixmaps)

    def data(self, index, role):
        annotated_pixmap_future = self.pixmaps[index.row()]
        if not annotated_pixmap_future.is_finished():
            # logger.debug("i never return none")
            return None

        annotated_pixmap = annotated_pixmap_future.get()
        if role == Qt.DisplayRole:
            return annotated_pixmap.filename
        elif role == Qt.DecorationRole:
            return annotated_pixmap.pixmap, annotated_pixmap.thumbail  
        elif role == Qt.UserRole:
            return annotated_pixmap

    def add_pixmap(self, pixmap: SimpleFutureWorker):
        self.beginInsertRows(QModelIndex(), len(self.pixmaps), len(self.pixmaps))
        self.pixmaps.append(pixmap)
        self.endInsertRows()

        # notify view that pixmap has finished loading
        # works also without this, but then the view will not update unitil the pixmap is visible
        pixmap.signals.finished.connect(lambda pixmap=pixmap: self._on_pixmap_finished(pixmap))

    def add_pixmaps(self, pixmaps: list[SimpleFutureWorker]):
        self.beginInsertRows(QModelIndex(), len(self.pixmaps), len(self.pixmaps) + len(pixmaps) - 1)
        self.pixmaps.extend(pixmaps)
        self.endInsertRows()

    def remove_pixmap(self, index: int):
        self.beginRemoveRows(QModelIndex(), index, index)
        self.pixmaps.pop(index)
        self.endRemoveRows()

    def clear(self):
        self.beginResetModel()
        self.pixmaps.clear()
        self.endResetModel()

    def _on_pixmap_finished(self, pixmap_future: SimpleFutureWorker[AnnotatedPixmap]):
        pixmap_index = self._find_pixmap_future(pixmap_future)
        if pixmap_index is None:
            return
        self.dataChanged.emit(self.index(pixmap_index), self.index(pixmap_index))

    def _find_pixmap_future(self, pixmap_future: SimpleFutureWorker[AnnotatedPixmap]):
        for i, p in enumerate(self.pixmaps):
            if p is pixmap_future:
                return i
        return None
    

