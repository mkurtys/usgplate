import logging
import tempfile
import os
import copy

from usgplate.pixmap.pixmap import AnnotatedPixmap, ImageFilesScaler
from usgplate.reports.odt_image_report import create_odt_image_report
from odf.opendocument import OpenDocument, load
from pathlib import Path
from PySide6.QtCore import QRunnable, Signal


logger = logging.getLogger(__name__)

class OdtReportGenerator(QRunnable):

    def __init__(self, 
                 annotated_pixmaps: list[AnnotatedPixmap],
                 output_file: str,
                 substitutions: dict[str, str] = {},
                 image_size_real_cm = 6.0,
                 ppi = 300,
                 template_filename: str|Path|None = None,
                ):
        super().__init__()
        self.annotated_pixmaps = annotated_pixmaps
        self.template_filename = template_filename
        self.output_file = output_file
        self.substitutions = substitutions
        self.image_size_real_cm = image_size_real_cm
        self.ppi = ppi

    def run(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            filenames = [annotated_pixmap.filename for annotated_pixmap in self.annotated_pixmaps]
            scaled_filenames = ImageFilesScaler(tmpdirname, self.image_size_real_cm, self.ppi).scale(filenames)
            # template = copy.deepcopy(self.template_doc) if self.template_doc else None
            doc = create_odt_image_report(self.template_filename, scaled_filenames, substitutions=self.substitutions)
            doc.save(self.output_file)
            logger.info("Report generated %s", self.output_file)