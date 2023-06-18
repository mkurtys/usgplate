from pathlib import Path

import pydicom

from .dcm_repository import DCMRepository
from ..entities.dicom_instance_info import DicomInstanceInfo


class DCMFileRepository(DCMRepository):

    def __init__(self, repository_path: Path|str) -> None:
        self.repository_path = Path(repository_path)

    def save(self, ds: pydicom.Dataset) -> None:
        info = DicomInstanceInfo.from_dataset(ds)
        destination_path = self.resolve_instance_path(info)
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        ds.save_as(str(destination_path), write_like_original=False)

    def read(self, dcm_instance_info: DicomInstanceInfo) -> pydicom.Dataset:
        destination_path =  self.resolve_instance_path(dcm_instance_info)
        return pydicom.dcmread(str(destination_path))
        
    def resolve_instance_path(self, dcm_file_info) -> Path:
        return self.repository_path / "dicom" / dcm_file_info.patient_name / dcm_file_info.study_uid / dcm_file_info.series_uid / f"{dcm_file_info.instance_number}.dcm"
    
    def resolve_series_path(self, dcm_file_info) -> Path:
        return self.repository_path / "dicom" / dcm_file_info.patient_name / dcm_file_info.study_uid / dcm_file_info.series_uid