from .study_image_provider import StudyImageProvider
from .dir_dir_scanner import DirDirScanner
from usgplate.study.study import StudyProperties
import os

class ImageDirScanner(StudyImageProvider):
    def __init__(self, directory: str, file_extensions: list[str] = ["png", "jpg", "jpeg", "dcm", "dicom", "bmp"]):
        super().__init__()
        self.directory = directory
        self.dir_scanner = DirDirScanner(directory,
                                         file_filter_fn=lambda filename: any([filename.lower().endswith(ext) for ext in file_extensions]))
        self.dir_scanner.file_found.connect(self.on_file_found)
        self.dir_scanner.directory_found.connect(self.on_directory_found)

    def start(self):
        self.dir_scanner.start()
    
    def stop(self):
        self.dir_scanner.terminate()

    def on_file_found(self, filename: str):
        self.image_found.emit(filename)
 
    def on_directory_found(self, directory: str):
        self.study_found.emit(StudyProperties.with_random_id(
            patient_name=os.path.basename(directory),
        ))

    
        
