from PySide6.QtCore import Qt, QAbstractListModel, QItemSelectionModel, QModelIndex, QSize, QRect
from PySide6.QtGui import QPixmap, QColor, QColorConstants
from PySide6.QtWidgets import QWidget, QSizePolicy, QStyledItemDelegate, QListView, QHBoxLayout, QStyle

from usgplate.pixmap.pixmap import AnnotatedPixmap
from usgplate.pixmap.annotated_pixmap_model import AnnotatedPixmapModel

from usgplate.utils.worker import SimpleFutureWorker


class AnnotatedPixmapDelegate(QStyledItemDelegate):
    def __init__(self, parent=None,
                 selected_frame_width: int = 5,
                 frame_color: QColor= QColorConstants,
                 center: bool = True):
        self.sfw = selected_frame_width
        self.frame_color = frame_color
        self.view: QListView = parent
        # spacing used if view.gridSize() is valid
        self.spacing = self.view.spacing() or 5
        self.center = center
        self.placeholder = QPixmap(256, 256)
        self.placeholder.fill(QColorConstants.LightGray)
        super().__init__(parent)

    def paint(self, painter, option, index):
        
        pixmap_thumbnail = index.data(Qt.DecorationRole)
        if not pixmap_thumbnail:
            pixmap = self.placeholder
        else:
            pixmap, thumbnail = pixmap_thumbnail
            # fixme
            # if option.rect.size() < thumbnail.size():
            #     pixmap = thumbnail
        
        pixmap_scaled_size = pixmap.size().scaled(option.rect.size(),
                                                  Qt.AspectRatioMode.KeepAspectRatio)
        selected = option.state & QStyle.State_Selected
        drawing_rect = option.rect
        if self.center:
            grid_center_rect = QRect(option.rect.x(), 
                    option.rect.y(),
                    pixmap_scaled_size.width(),
                    pixmap_scaled_size.height())
            grid_center_rect.moveCenter(option.rect.center())
            grid_center_rect = grid_center_rect.adjusted(self.spacing, self.spacing, -self.spacing, -self.spacing)
            drawing_rect = grid_center_rect
  
        if selected:
            painter.fillRect(drawing_rect, self.frame_color)
            adjusted_rect = drawing_rect.adjusted(self.sfw, self.sfw, -self.sfw, -self.sfw)
            painter.drawPixmap(adjusted_rect, pixmap)
        else:
            painter.drawPixmap(drawing_rect, pixmap)
        

    def sizeHint(self, option, index):
        # o'rly? need to think about this
        
        gs = self.view.gridSize()
        if gs.isValid():
            return gs
        else:
            pg = self.view.geometry()
            pixmap = self.view.model().pixmaps[index.row()].thumbail
            spacing = self.view.spacing()
            # 2 colmns, hardcoded 400 height
            pixmap_scaled_size = pixmap.size().scaled( QSize(pg.width()//2 - 3*spacing, 400), Qt.KeepAspectRatio)
            return QSize(pixmap_scaled_size.width(), 400)
    

class UImageGrid(QWidget):

    def __init__(self,
                pixmap_model: AnnotatedPixmapModel,
                selected_frame_width: int = 5,
                frame_color: QColor= QColorConstants.Svg.darkblue,
                parent: QWidget = None):
        super().__init__()

        self._model = pixmap_model
        self._view = QListView()
        self._view.setModel(self._model)
        self._view.setItemDelegate(
            AnnotatedPixmapDelegate(
            parent=self._view,
            selected_frame_width=selected_frame_width,
                                     frame_color=frame_color))
        self._view.setFlow(QListView.Flow.LeftToRight)
        self._view.setWrapping(True)
        self._view.setResizeMode(QListView.ResizeMode.Adjust)
        # self._view.setSpacing(5)
        self._view.setGridSize(QSize(200, 200))
        self._view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._view.setWordWrap(True)

        self._view.setSelectionMode(QListView.SelectionMode.MultiSelection)
        self._selection_model = self._view.selectionModel()
        self._model.rowsInserted.connect(self._on_rows_inserted)
        
        self._layout = QHBoxLayout()
        self._layout.addWidget(self._view)
        self.setLayout(self._layout)
        

    def _on_rows_inserted(self, parent, first, last):
        for i in range(first, last + 1):
            index = self._model.index(i)
            self._selection_model.select(index, QItemSelectionModel.SelectionFlag.Select)
   
    def sizeHint(self):
        return self.layout().sizeHint()
    
    def getSelected(self) -> list[AnnotatedPixmap]:
        return [self._model.pixmaps[index.row()] for index in self._view.selectionModel().selectedIndexes() ]
    
    def setGridSize(self, size: QSize):
        self._view.setGridSize(size)
