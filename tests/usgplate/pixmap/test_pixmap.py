from usgplate.pixmap.pixmap import qpixmap_from_dcm_or_img_file, AnnotatedPixmap, PixmapCachedLoader
from PySide6.QtWidgets import QApplication


def test_qpixmap_from_dcm_file(qtbot):
    pixmap = qpixmap_from_dcm_or_img_file("tests/data/ultrasound.dcm")
    assert pixmap is not None
    assert pixmap.width() == 256
    assert pixmap.height() == 256

def test_qpixmap_from_img_file(qtbot):
    pixmap = qpixmap_from_dcm_or_img_file("tests/data/ultrasound.png")
    assert pixmap is not None
    assert pixmap.width() == 256
    assert pixmap.height() == 256

def test_pixmap_loader(qtbot):
    loader = PixmapCachedLoader(thumbnail_size=64)
    filename = "tests/data/ultrasound.png"
    loader.load(filename)
    loader.waitTillDone()
    QApplication.processEvents()
    pixmap = loader.get(filename)
    assert pixmap is not None
    assert pixmap.pixmap.width() == 256
    assert pixmap.pixmap.height() == 256
    assert pixmap.thumbail.width() == 64
    assert pixmap.thumbail.height() == 64
    assert pixmap.filename == "tests/data/ultrasound.png"