from usgplate.reports.odt_image_report import create_odt_image_report, substitute_text
from odf.opendocument import OpenDocumentText, load
import io

def test_create_odt_image_report_from_template_no_images():
    doc = create_odt_image_report(input_doc_filename="tests/data/sample_report.odt",
                                  picture_filenames=[]
                                 )
    
def test_create_odt_image_report_from_template_with_one_image():
    doc = create_odt_image_report(input_doc_filename="tests/data/sample_report.odt",
                                  picture_filenames=["tests/data/ultrasound.png"]
                                 )


def test_create_odt_image_report_from_template_with_one_image_and_substitionon():
    doc = create_odt_image_report(input_doc_filename="tests/data/sample_report.odt",
                                  picture_filenames=["tests/data/ultrasound.png"],
                                  substitutions={"Pancreas": "PANCREAS"}
                                 )
    with io.StringIO() as f:
        doc.text.toXml(0, f)
        xml_text = f.getvalue()
        assert "PANCREAS" in xml_text
    


# testing somewhat the internals of the module, but who cares
def test_substitute_text():
    doc = load("tests/data/sample_report.odt")
    substitute_text(doc.text, {"Pancreas": "PANCREAS"})
    with io.StringIO() as f:
        doc.text.toXml(0, f)
        xml_text = f.getvalue()
        assert "PANCREAS" in xml_text