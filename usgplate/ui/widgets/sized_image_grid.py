from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QColorConstants
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSlider

from usgplate.pixmap.pixmap import AnnotatedPixmap
from usgplate.ui.widgets.image_grid import UImageGrid, AnnotatedPixmapModel


class USizedImageGrid(QWidget):

    def __init__(self, 
                pixmap_model: AnnotatedPixmapModel,
                selected_frame_width: int = 5,
                frame_color: QColor= QColorConstants.Svg.darkblue,
                parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.image_grid = UImageGrid(pixmap_model=pixmap_model,
                                     selected_frame_width=selected_frame_width,
                                     frame_color=frame_color,
                                     parent=self)
        self.grid_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.grid_size_slider.setRange(100, 500)
        self.grid_size_slider.setValue(200)
        self.grid_size_slider.setTickInterval(100)
        self.grid_size_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.grid_size_slider.setSingleStep(100)
        self.grid_size_slider.valueChanged.connect( lambda value: self.image_grid.setGridSize(QSize(value, value)) )
        self._setup_ui()

    def _setup_ui(self):
        self.layout.addWidget(self.image_grid)
        self.layout.addWidget(self.grid_size_slider)
        self.setLayout(self.layout)

    def sizeHint(self):
        return self.layout.sizeHint()
    
    def getSelected(self) -> list[AnnotatedPixmap]:
        return self.image_grid.getSelected()