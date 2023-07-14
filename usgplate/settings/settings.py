import os
from dataclasses import dataclass, field

from dataclasses_json import dataclass_json

from usgplate.dicom.networking.storescp_server import StoreSCPConfig


DEFAULT_SETTINGS_PATH = "settings/default_settings.json"
SETTINGS_PATH = "settings/settings.json"

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


def read_settings() -> ApplicationSettings:
    try:
        with open(SETTINGS_PATH, "r") as f:
            return ApplicationSettings.from_json(f.read())
    except FileNotFoundError:
        try:
            with open(DEFAULT_SETTINGS_PATH, "r") as f:
                return ApplicationSettings.from_json(f.read())
        except FileNotFoundError:
            return ApplicationSettings()
        
def save_settings(settings: ApplicationSettings) -> None:
    with open(SETTINGS_PATH, "w") as f:
        f.write(settings.to_json())

