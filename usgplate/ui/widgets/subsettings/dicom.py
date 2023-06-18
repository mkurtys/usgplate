from PySide6.QtWidgets import QFormLayout, QLabel, QLineEdit, QCheckBox, QWidget

from PySide6.QtWidgets import QFormLayout, QLabel, QLineEdit, QCheckBox, QWidget
from PySide6 import QtCore
from usgplate.settings.settings import StoreSCPSettings


class DicomSettingsWidget(QWidget):
    def __init__(self, settings: StoreSCPSettings, parent=None):
        super().__init__(parent)
        
        self.layout = QFormLayout(self)
        self.enabled_checkbox = QCheckBox()
        self.dicom_cstore_port_edit = QLineEdit()
        self.dicom_aetitle_edit = QLineEdit()
        # center adjusted settings label

        self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.layout.setLabelAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.layout.addRow(QLabel("DICOM Store SCP Enabled"), self.enabled_checkbox)
        self.layout.addRow(QLabel("DICOM C-Store Port"), self.dicom_cstore_port_edit)
        self.layout.addRow(QLabel("DICOM AE Title"), self.dicom_aetitle_edit)

        self.setup_ui(settings)

    def set_settings(self, settings: StoreSCPSettings):
        self.enabled_checkbox.setChecked(settings.enabled)
        self.dicom_cstore_port_edit.setText(str(settings.port))
        self.dicom_aetitle_edit.setText(settings.ae_title)

    def setup_ui(self, settings: StoreSCPSettings):
        self.set_settings(settings)
        # self.layout.addStretch()
        self.setLayout(self.layout)

    def get_settings(self) -> StoreSCPSettings:
        return StoreSCPSettings(
            enabled=self.enabled_checkbox.isChecked(),
            port=int(self.dicom_cstore_port_edit.text()),
            ae_title=self.dicom_aetitle_edit.text(),
            dcm_repository_root="output/dcm_repository" # TODO: make this configurable
        )

    def sizeHint(self) -> QtCore.QSize:
        return self.layout.sizeHint()