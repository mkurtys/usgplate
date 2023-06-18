from usgplate.reports.odt_image_report import create_odt_image_report

def test_create_odt_image_report_from_template_with_one_image():
    doc = create_odt_image_report(input_doc_filename="tests/data/sample_report.odt",
                                  picture_filenames=["tests/data/ultrasound.png"]
                                 )
    doc.save("output/sample_report_with_one_image.odt")
