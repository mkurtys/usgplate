from PySide6 import QtCore
from PySide6.QtWidgets import QDialog, QDialogButtonBox, \
    QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem, QWidget, QSizePolicy, QLabel




class AutoNewStudyModal(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._layout = QVBoxLayout()
        self._accept_label = QLabel("Accept new study?")
        self._accept_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._layout.addWidget(self._accept_label)
        
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(QBtn)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self._layout.addWidget(self.button_box)
        self.setLayout(self._layout)
        self.setWindowTitle("New study found")
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(300, 100)


    def sizeHint(self) -> QtCore.QSize:
        return super().sizeHint()