import pydicom
import PIL.Image
import numpy as np
import argparse

def image_to_dicom(source_file, target_file,
                   convert_to_grayscale=False,
                   implicit_vr=True):
    img = PIL.Image.open(source_file)

    if convert_to_grayscale:
        img = img.convert("L")
    pixel_array = np.array(img)

    ds = pydicom.Dataset()
    # Get the colorspace from the image
    if img.mode == "RGB":
        ds.PhotometricInterpretation = "RGB"
        ds.SamplesPerPixel = 3
        ds.PlanarConfiguration = 0
    if img.mode == "RGBA":
        ds.PhotometricInterpretation = "RGB"
        ds.SamplesPerPixel = 3
        pixel_array = pixel_array[..., :3]
        ds.PlanarConfiguration = 0
    elif img.mode == "L":
        ds.PhotometricInterpretation = "MONOCHROME2"
        ds.SamplesPerPixel = 1
    else:
        raise ValueError(f"Unsupported image mode: {img.mode}")
    
    # Add random metadata to the dataset
    ds.PatientName = "Test^Firstname"
    ds.PatientID = "123456"
    ds.PatientBirthDate = "19000101"
    ds.PatientSex = "F"
    ds.StudyInstanceUID = "1.2.3"
    ds.SeriesInstanceUID = "1.2.3"
    ds.InstanceNumber = "1"
    ds.SOPInstanceUID = "1.2.3"
    ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.6.1"
    ds.Modality = "US"
    ds.StudyDescription = "Test Study"
    ds.SeriesDescription = "Test Series"

    ds.PerformingPhysicianName = "Test^Doctor"
    ds.InstitutionName = "Test Hospital"

    ds.StudyDate = "19000101"
    ds.SeriesDate = "19000101"
    ds.AcquisitionDate = "19000101"

    ds.BitsStored = 8
    ds.BitsAllocated = 8
    ds.HighBit = 7
    ds.PixelRepresentation = 0

    ds.LossyImageCompression = "00"

    ds.is_little_endian = True
    ds.is_implicit_VR = True if implicit_vr else False
    ds.PixelData = pixel_array.tobytes()
    # PIL -> The size is given as a 2-tuple (width, height)
    ds.Columns, ds.Rows = img.size



    file_ds = pydicom.FileDataset(target_file, ds)
    if not implicit_vr:
        file_ds.file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian
    else:
        file_ds.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian

    file_ds.save_as(target_file, write_like_original=False)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Convert an image to a DICOM file.')
    parser.add_argument('source_file', type=str, help='The source image file.')
    parser.add_argument('target_file', type=str, help='The target DICOM file.')
    parser.add_argument('--grayscale', action='store_true', help='Convert the image to grayscale.')
    parser.add_argument('--explicit-vr', action='store_true', help='Use explicit VR.')
    args = parser.parse_args()
    image_to_dicom(args.source_file, args.target_file, args.grayscale, not args.explicit_vr)

