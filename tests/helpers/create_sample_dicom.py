from pydicom.data import get_testdata_file
import pydicom

filename = get_testdata_file("rtplan.dcm")
ds = pydicom.dcmread(filename)
ds.save_as("tests/data/rtplan.dcm")