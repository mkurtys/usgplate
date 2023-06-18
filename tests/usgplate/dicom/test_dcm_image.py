import pydicom
from usgplate.dicom.image import pil_image_from_dicom

def test_pil_image_from_dcm():
    ds = pydicom.dcmread("tests/data/ultrasound.dcm")
    img = pil_image_from_dicom(ds)
    assert img is not None
    assert img.size == (256, 256)
    assert img.mode == "RGB"

def test_pil_image_from_dcm_grayscale():
    ds = pydicom.dcmread("tests/data/ultrasound_grayscale.dcm")
    img = pil_image_from_dicom(ds)
    assert img is not None
    assert img.size == (256, 256)
    assert img.mode == "L"