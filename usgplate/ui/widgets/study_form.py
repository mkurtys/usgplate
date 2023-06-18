from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QLineEdit, QDateEdit
from PySide6.QtCore import QDate

from usgplate.study.study import StudyProperties
import datetime

class StudyForm(QWidget):

    def __init__(self, study_properties: StudyProperties, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.name_label = QLabel("Patient Name")
        self.name_edit = QLineEdit()

        self.id_label = QLabel("Patient ID")
        self.id_edit = QLineEdit()

        self.date_label = QLabel("Study Date")
        self.date_edit = QDateEdit()

        self.study_id: str = ""
        self.set_study(study_properties)    
        
        self.setup_ui()

    def setup_ui(self):
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.name_edit)
        self.layout.addWidget(self.id_label)
        self.layout.addWidget(self.id_edit)
        self.layout.addWidget(self.date_label)
        self.layout.addWidget(self.date_edit)
        self.layout.addStretch()

        for widget in [self.name_label, self.name_edit,
                       self.id_label, self.id_edit, self.date_label,
                       self.date_edit]:
            widget.setSizePolicy(
                QtWidgets.QSizePolicy.Policy.Maximum,
                QtWidgets.QSizePolicy.Policy.Maximum,
            )

        self.setLayout(self.layout)

    def sizeHint(self) -> QtCore.QSize:
        return super().sizeHint()
    
    def set_study(self, study: StudyProperties):
        self.name_edit.setText(study.patient_name)
        self.id_edit.setText(study.patient_id)
        self.date_edit.setDate(QDate(*study.study_date.timetuple()[:3]))
        self.study_id = study.study_id

    def get_study(self) -> StudyProperties:
        return StudyProperties(
            study_id=self.study_id,
            patient_name=self.name_edit.text(),
            patient_id=self.id_edit.text(),
            study_date=self.date_edit.date().toPython(),
        )

