import numpy as np

def image_to_scaled_array(image):
    img_array = np.array(image.convert("L"))

    # interpolate pixel values to be between 0 and 9
    scaled_array = np.interp(img_array, (img_array.min(), img_array.max()), (0, 9))
    # round and convert to integers
    rounded_array = np.round(scaled_array).astype(int)

    return rounded_array


# def random_pattern_generator(width, height):
#     grid =
#     while
