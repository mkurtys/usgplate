from PySide6.QtCore import QThread, Signal, QObject
from abc import ABC, abstractmethod

class StudyImageProvider(QObject):
    image_found = Signal(str)
    study_found = Signal(object)

    

