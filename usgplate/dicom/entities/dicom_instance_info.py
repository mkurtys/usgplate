from dataclasses import dataclass

import pydicom


@dataclass
class DicomInstanceInfo:
    patient_id: str
    patient_name: str
    study_uid: str
    series_uid: str
    instance_number: str

    @classmethod
    def from_dataset(cls, dataset: pydicom.Dataset):
        return cls(
            patient_id=str(dataset.get("PatientID", "Unknown")),
            patient_name=str(dataset.get("PatientName", "Unknown")).replace("^", " "),
            study_uid=dataset.get("StudyInstanceUID", "Unknown"),
            series_uid=dataset.get("SeriesInstanceUID", "Unknown"),
            instance_number=dataset.get("InstanceNumber", 0)
        )
