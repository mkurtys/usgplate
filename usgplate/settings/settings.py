import os
from dataclasses import dataclass, field

from dataclasses_json import dataclass_json

from usgplate.dicom.networking.storescp_server import StoreSCPConfig


@dataclass
class StoreSCPSettings(StoreSCPConfig):
    enabled: bool = True

@dataclass
class ImageDirScannerSettings:
    enabled: bool = True
    directory: str = field(default_factory=lambda: os.path.expanduser("~/DICOM"))

@dataclass_json
@dataclass(eq=True)
class ApplicationSettings:
    store_scp: StoreSCPSettings
    image_dir_scanner: ImageDirScannerSettings
    reports_dir: str = field(default_factory=lambda: os.path.expanduser("~/Reports"))

