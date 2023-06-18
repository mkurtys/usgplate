from PySide6.QtWidgets import QFormLayout, QLabel, QLineEdit, QCheckBox, QWidget

from PySide6.QtWidgets import QFormLayout, QLabel, QLineEdit, QCheckBox, QWidget
from PySide6 import QtCore
from usgplate.settings.settings import ImageDirScannerSettings


class DirDirScannerSettingsWidget(QWidget):
    def __init__(self, settings: ImageDirScannerSettings, parent=None):
        super().__init__(parent)
        
        self.layout = QFormLayout(self)
        self.enabled_checkbox = QCheckBox()
        self.directory_edit = QLineEdit()

        self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.layout.setLabelAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.layout.addRow(QLabel("Directory Scan Enabled"), self.enabled_checkbox)
        self.layout.addRow(QLabel("Directory Path"), self.directory_edit)

        self.setup_ui(settings)

    def set_settings(self, settings: ImageDirScannerSettings):
        self.enabled_checkbox.setChecked(settings.enabled)
        self.directory_edit.setText(str(settings.directory))

    def setup_ui(self, settings: ImageDirScannerSettings):
        self.set_settings(settings)
        # self.layout.addStretch()
        self.setLayout(self.layout)

    def get_settings(self) -> ImageDirScannerSettings:
        return ImageDirScannerSettings(
            enabled=self.enabled_checkbox.isChecked(),
            directory=self.directory_edit.text()
        )

    def sizeHint(self) -> QtCore.QSize:
        return self.layout.sizeHint()