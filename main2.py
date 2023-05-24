import os
import requests
import numpy as np
import cv2


def download_image(url, filename):
    response = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(response.content)


def get_average_color(image):
    average_color = np.average(image, axis=(0, 1))
    return average_color.astype(int)


def find_best_match(target_color, image_files, image_directory):
    best_match_index = None
    best_match_diff = np.inf

    for i, image_file in enumerate(image_files):
        image_path = os.path.join(image_directory, image_file)
        image = cv2.imread(image_path)

        image_color = get_average_color(image)
        color_diff = np.sum(np.abs(target_color - image_color))

        if color_diff < best_match_diff:
            best_match_index = i
            best_match_diff = color_diff

    return os.path.join(image_directory, image_files[best_match_index])


def create_mosaic(target_image_path, image_directory, mosaic_size):
    target_image = cv2.imread(target_image_path)
    target_height, target_width = target_image.shape[:2]
    mosaic_height, mosaic_width = mosaic_size

    # Resize target image to match mosaic dimensions
    target_image = cv2.resize(target_image, (mosaic_width * target_width, mosaic_height * target_height))

    mosaic = np.zeros_like(target_image, dtype=np.uint8)

    image_files = os.listdir(image_directory)

    for i in range(mosaic_height):
        for j in range(mosaic_width):
            target_patch = target_image[i * target_height: (i + 1) * target_height,
                                        j * target_width: (j + 1) * target_width]
            target_color = get_average_color(target_patch)

            best_match_path = find_best_match(target_color, image_files, image_directory)

            image = cv2.imread(best_match_path)
            image = cv2.resize(image, (target_width, target_height))

            mosaic[i * target_height: (i + 1) * target_height, j * target_width: (j + 1) * target_width] = image

    # Save the mosaic as a TIFF file
    mosaic_filename = 'mosaic.tiff'
    cv2.imwrite(mosaic_filename, mosaic)

    return mosaic_filename


# Example usage
target_image_url = 'https://example.com/path/to/target/image.jpg'
target_image_filename = 'target_image.jpg'
image_directory = 'path/to/image/directory'
mosaic_size = (5, 5)  # Number of tiles in the mosaic (e.g., 5x5)

# Download the target image
download_image(target_image_url, target_image_filename)

# Create the mosaic
mosaic_filename = create_mosaic(target_image_filename, image_directory, mosaic_size)

print("Mosaic created:", mosaic_filename)
