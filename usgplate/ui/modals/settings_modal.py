from PySide6 import QtCore
from PySide6.QtWidgets import QDialog, QDialogButtonBox, \
    QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem, QWidget, QSizePolicy

from usgplate.settings.settings import ApplicationSettings
from usgplate.ui.widgets.subsettings.dicom import DicomSettingsWidget
from usgplate.ui.widgets.subsettings.dirdir import DirDirScannerSettingsWidget



class SettingsModal(QDialog):
    def __init__(self, settings: ApplicationSettings, parent=None):
        super().__init__(parent)
        self._layout = QVBoxLayout()
        self.main_layout = QHBoxLayout()
        self.suboptions_list_widget = QListWidget()
        self.suboptions_list_widget.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.suboptions_list_widget.currentItemChanged.connect(self.on_suboption_changed)

        self.empty_suboptions_widget = QWidget()
        self.active_suboptions_widget = self.empty_suboptions_widget
        self.active_suboptions_layout = QVBoxLayout()
        self.active_suboptions_layout.addWidget(self.active_suboptions_widget)
        
        self.dicom_suboptions_widget = DicomSettingsWidget(settings.store_scp)
        self.dir_dirs_scanner_suboptions_widget = DirDirScannerSettingsWidget(settings.image_dir_scanner)
        QListWidgetItem("DICOM", self.suboptions_list_widget)
        QListWidgetItem("DirScanner", self.suboptions_list_widget)
        self.setWindowTitle("Settings")
        self.set_settings(settings)

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.button_box = QDialogButtonBox(QBtn)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.setup_ui(settings)

    def set_settings(self, settings: ApplicationSettings):
        self.dicom_suboptions_widget.set_settings(settings.store_scp)

    def setup_ui(self, settings: ApplicationSettings):
        self.suboptions_list_widget.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.suboptions_list_widget.setSizeAdjustPolicy(QListWidget.SizeAdjustPolicy.AdjustToContents)
        self.main_layout.addWidget(self.suboptions_list_widget)
        self.main_layout.addLayout(self.active_suboptions_layout)
        self._layout.addLayout(self.main_layout)
        self._layout.addWidget(self.button_box)
        # self.layout.addStretch()
        self.setLayout(self._layout)

    def get_settings(self) -> ApplicationSettings:
        return ApplicationSettings(
            store_scp=self.dicom_suboptions_widget.get_settings(),
            image_dir_scanner=self.dir_dirs_scanner_suboptions_widget.get_settings()
        )
    
    def on_suboption_changed(self, current: QListWidgetItem, previous: QListWidgetItem):
        self.active_suboptions_widget.hide()
        if current.text() == "DICOM":
            self.active_suboptions_layout.replaceWidget(self.active_suboptions_widget, self.dicom_suboptions_widget)
            self.active_suboptions_widget = self.dicom_suboptions_widget
        elif current.text() == "DirScanner":
            self.active_suboptions_layout.replaceWidget(self.active_suboptions_widget, self.dir_dirs_scanner_suboptions_widget)
            self.active_suboptions_widget = self.dir_dirs_scanner_suboptions_widget
        self.active_suboptions_widget.show()
    
    def sizeHint(self) -> QtCore.QSize:
        return super().sizeHint()