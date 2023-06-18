from dataclasses import dataclass, field
from usgplate.ui.widgets.image_grid import AnnotatedPixmapModel
import datetime
import random

def _random_id():
    return str(random.randint(100000000, 999999999))

@dataclass
class StudyProperties:
    study_id: str = field(default_factory=_random_id)
    patient_name: str = ""
    patient_id: str = field(default_factory=_random_id)
    study_date: datetime.date = field(default_factory=datetime.date.today)

    @classmethod
    def with_random_id(cls, *args, **kwargs):
        return StudyProperties(*args, 
                            study_id=_random_id(),
                            patient_id=_random_id(),
                            **kwargs)

@dataclass
class Study(StudyProperties):
    pixmap_model: AnnotatedPixmapModel = field(default_factory=AnnotatedPixmapModel)