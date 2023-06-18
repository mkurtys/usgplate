import logging
from usgplate.services.image_providers.scp_store_process_manager import DicomScpStoreProcessManager
from usgplate.services.image_providers.image_dir_scanner import ImageDirScanner
from usgplate.settings.settings import ApplicationSettings
from .study_image_provider import StudyImageProvider

logger = logging.getLogger(__name__)

class ImageProviderManager(StudyImageProvider):

    def __init__(self):
        super().__init__()
        self.dicom_store_service: DicomScpStoreProcessManager| None = None
        self.image_dir_scanner: ImageDirScanner | None = None

    def refresh_services_settings(self, settings: ApplicationSettings|None , new_settings: ApplicationSettings):
        logger.info("Refreshing services settings")

        if (settings and settings.store_scp != new_settings.store_scp) or not self.dicom_store_service:
            if self.dicom_store_service:
                self.dicom_store_service.stop()
            if new_settings.store_scp.enabled:
                self.dicom_store_service = DicomScpStoreProcessManager(
                    new_settings.store_scp
                )
                self.dicom_store_service.image_found.connect(self.image_found)
                self.dicom_store_service.study_found.connect(self.study_found)
                self.dicom_store_service.start()

        if (settings and settings.image_dir_scanner != new_settings.image_dir_scanner) or not self.image_dir_scanner:
            if self.image_dir_scanner:
                self.image_dir_scanner.stop()
            if new_settings.image_dir_scanner.enabled:
                self.image_dir_scanner = ImageDirScanner(directory=new_settings.image_dir_scanner.directory)
                self.image_dir_scanner.image_found.connect(self.image_found)
                self.image_dir_scanner.study_found.connect(self.study_found)
                self.image_dir_scanner.start()

    def stop(self):
        if self.dicom_store_service:
            self.dicom_store_service.stop()
        if self.image_dir_scanner:
            self.image_dir_scanner.stop()