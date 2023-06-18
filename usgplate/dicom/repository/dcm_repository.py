import abc

import pydicom

from ..entities.dicom_instance_info import DicomInstanceInfo


class DCMRepository(abc.ABC):

    def __init__(self) -> None:
        pass

    @abc.abstractmethod
    def save(self, ds: pydicom.Dataset) -> None:
        pass

    @abc.abstractmethod
    def read(self, dcm_instance_info: DicomInstanceInfo) -> pydicom.Dataset:
        pass

