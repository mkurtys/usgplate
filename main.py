import os
import datetime
import logging
import os
import signal

from PySide6.QtCore import QThread, QThreadPool
from PySide6.QtGui import QImage, QAction, QCloseEvent
from PySide6.QtWidgets import QApplication, QMainWindow, QStyle, QVBoxLayout, QHBoxLayout, QPushButton, QWidget

import usgplate.logging.logging  # noqa
from usgplate.pixmap.pixmap import PixmapCachedLoader
from usgplate.reports.odt_image_report import create_odt_image_report
from usgplate.services.image_providers.image_provider_manager import ImageProviderManager
from usgplate.settings.settings import ApplicationSettings
from usgplate.ui.modals.choose_directory_modal import choose_directory_modal
from usgplate.ui.modals.settings_modal import SettingsModal
from usgplate.ui.widgets.study_form import StudyForm
from usgplate.ui.widgets.sized_image_grid import USizedImageGrid
from usgplate.utils.default_app_open import open_file_with_default_app
from usgplate.services.odt_report_generator import OdtReportGenerator
from usgplate.study.study import Study, StudyProperties
from usgplate.utils.worker import Worker

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self,
                settings: ApplicationSettings):
        super().__init__()
        self.settings: ApplicationSettings| None = settings
        self.image_provider_manager = ImageProviderManager()
        self.image_provider_manager.image_found.connect(self.on_image_found)
        self.image_provider_manager.study_found.connect(self.on_study_found)
        # TODO stop services on exit
        self.image_provider_manager.refresh_services_settings(None, settings)
        self.settings_modal = SettingsModal(settings=settings)
        self.study = Study()
        self.pixmap_loader = PixmapCachedLoader(thumbnail_size=200)


        self.reports_path = os.path.expanduser("~/Reports")
        self.load_directory_start_path = os.path.expanduser("~/")
        self.last_loaded_directory = None
        if not os.path.exists(self.reports_path):
            os.makedirs(self.reports_path)

        self.setWindowTitle("USGPlate")
        self.resize(800, 600)

        self.main_layout = QHBoxLayout()
        self.left_layout = QVBoxLayout()
        self.right_layout = QVBoxLayout()
        
        self.v_layout = QVBoxLayout()
        self.h_layout = QHBoxLayout()
        self.side_v_layout = QVBoxLayout()
        self.load_directory_button = QPushButton("Load Directory")
        self.generate_report_button = QPushButton("Generate Report")
        self.report_form = StudyForm(self.study)
        self.image_grid = USizedImageGrid(pixmap_model=self.study.pixmap_model)


        self.load_directory_button.clicked.connect(lambda: self.on_load_directory())
        self.generate_report_button.clicked.connect(lambda: self.on_generate_report())

        self.main_layout.addLayout(self.left_layout)
        self.left_layout.addWidget(self.report_form)

        self.main_layout.addLayout(self.right_layout)
        self.right_layout.addLayout(self.v_layout)
        self.v_layout.addLayout(self.h_layout)
        self.h_layout.addLayout(self.side_v_layout)
        self.v_layout.addWidget(self.load_directory_button)
        self.v_layout.addWidget(self.generate_report_button)
        self.v_layout.addWidget(self.image_grid)

        # Set the central widget of the Window.
        self.widget = QWidget()
        self.widget.setLayout(self.main_layout)
        self.setCentralWidget(self.widget)
        self.widget.setFocus()

        settings_action = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon),
                                 "&Settings", self)
        settings_action.setStatusTip("Settings")
        settings_action.triggered.connect(self.on_settings_action_triggered)

        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        file_menu.addAction(settings_action)

    def on_settings_action_triggered(self):
        # should I push settings to modal before exec?
        self.settings_modal.set_settings(self.settings)
        if self.settings_modal.exec():
            new_settings = self.settings_modal.get_settings()
            self.image_provider_manager.refresh_services_settings(self.settings, new_settings)
            self.settings=new_settings

    def on_image_found(self, image_filename: str):
        logger.debug(f"Image found: {image_filename}")
        self.read_images([image_filename])

    def on_study_found(self, study_properties: StudyProperties):
        self.report_form.set_study(study_properties)
    
    def on_load_directory(self):
        image_directory = choose_directory_modal(self.load_directory_start_path)
        if image_directory is not None:
            self.load_directory_start_path = image_directory
            self.last_loaded_directory = image_directory
        else:
            return
        image_names = self.get_images_filenames_from_dir(image_directory)
        self.read_images(image_names)


    def read_images(self, image_filenames: list[str]) -> None:
        # fixme
        logger.debug("Reading Images. Preparing futures")
        images_futures = [self.pixmap_loader.load(image_name) for image_name in image_filenames]
        logger.debug("Futures ready, adding to model")
        self.study.pixmap_model.add_pixmaps(images_futures)

    @staticmethod
    def get_images_filenames_from_dir(directory: str) -> list[str]:
        # get all files in selected directory
        files = os.listdir(directory)
        # filter all files to only get images
        images = [os.path.join(directory,file) for file in files if file.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".dicom", ".dcm")) ]
        # return list of images
        return images

    def on_generate_report(self):
        logger.info("Generating report")
        selected_pixmaps_futures = self.image_grid.getSelected()
        selected_pixmaps = [future.get() for future in selected_pixmaps_futures]
        study_properties = self.report_form.get_study()

        report_filename = os.path.join(self.reports_path, self.resolve_report_name(study_properties) + ".odt")
        report_generator = OdtReportGenerator(template_filename=os.path.join(os.path.dirname(__file__), 'assets', "base_ultrasound_template.odt"),
            image_size_real_cm=6.0,
            ppi=300,
            output_file=report_filename,
            annotated_pixmaps=selected_pixmaps,
            substitutions={
                "$patient_name": study_properties.patient_name,
                "$patient_id": study_properties.patient_id,
                "$study_date": study_properties.study_date.strftime("%Y-%m-%d")
        })
        # print(report_generator.generated)
        report_generator_worker = Worker(report_generator.run)
        report_generator_worker.signals.finished.connect(lambda report_filename=report_filename: open_file_with_default_app(report_filename))
        QThreadPool.globalInstance().start(report_generator_worker)
        
        

    def resolve_report_name(self, study_properties: StudyProperties) -> str:
        date_string = study_properties.study_date.strftime("%Y-%m-%d")
        if study_properties.patient_name:
            return f"{study_properties.patient_name} {date_string}"
        else:
            return f"report {date_string}"

    def closeEvent(self, event: QCloseEvent) -> None:
        self.image_provider_manager.stop()
        return super().closeEvent(event)
    

def sigint_handler(*args):
    """Handler for the SIGINT signal."""
    logger.debug("SIGINT received")
    # QApplication.closeAllWindows()

def main():
    signal.signal(signal.SIGINT, sigint_handler)

    try:
        with open("settings.json", "r") as f:
            application_settings = ApplicationSettings.from_json(f.read())
    except FileNotFoundError:
        application_settings = ApplicationSettings()

    app = QApplication()
    app.setQuitOnLastWindowClosed(True)
    # add main window
    window = MainWindow(application_settings)
    window.show()
    app.exec()

    
if __name__ == "__main__":
    main()