import PIL.Image
import numpy as np
import pydicom
import pydicom.pixel_data_handlers


def data_to_monochrome2(data, ds: pydicom.Dataset) -> np.array:
    if ds.PhotometricInterpretation == "MONOCHROME1":
        data_max = np.amax(data)
        return data_max - data  
    else:
        return data
    
def uint8_pixel_array(ds: pydicom.Dataset) -> np.array:
    data = ds.pixel_array
    voi_data = pydicom.pixel_data_handlers.apply_voi_lut(data, ds)
    # data = data_to_monochrome2_if_needed(data, ds)
    voi_data = data_to_monochrome2(voi_data, ds)
    if voi_data.dtype != np.uint8:
        voi_data = voi_data - np.min(voi_data)
        voi_data = voi_data / np.max(voi_data)
        voi_data = (voi_data * 255).astype(np.uint8)
    return voi_data


def numpy_array_from_dicom(ds: pydicom.Dataset) -> np.array:
    return uint8_pixel_array(ds)

def pil_image_from_dicom(ds: pydicom.Dataset) -> PIL.Image:
    try:
        pixel_array = ds.pixel_array
    except AttributeError as e:
        raise Exception("Image extraction from dicom failed: " + str(e))
    except RuntimeError as e:
        # The following handlers are available to decode the pixel data however
        # they are missing required dependencies: GDCM (req. GDCM), pylibjpeg (req. )
        raise Exception("Image extraction from dicom failed: " + str(e))
    return PIL.Image.fromarray(pixel_array)
    # try:
    #    return PIL.Image.fromarray(ds.pixel_array)
    # except Exception as e:
    #     raise Exception("Image extraction from dicom failed: " + str(e))