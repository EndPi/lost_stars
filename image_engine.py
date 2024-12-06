import numpy as np
import scipy as sp
import os
import cv2
from PIL import Image, ImageDraw
from pathlib import Path
Image.MAX_IMAGE_PIXELS = None


def crop_to_tiles(image_path: Path, tile_size: int) -> None:
    '''
    Function to crop an image into smaller 
    tiles of a given size.
    @Args:
        image_path: Path to image folder.
        tile_size: Desired size of the tiles.
    @Return:
        None.
    '''
    # For each image in the provided path,
    # create a subdirectory to store the tiles
    for image in image_path.iterdir(): 
        if image.is_file():
            final_path = Path.joinpath(image_path,image.stem)
            final_path.mkdir(parents=True, exist_ok=True)

        # Open the original image
            with Image.open(image) as img:
                width, height = img.size    

                # Calculate the number of tiles along each dimension
                x_tiles = width // tile_size
                y_tiles = height // tile_size

                # Crop the image into tiles
                for i in range(x_tiles):
                    for j in range(y_tiles):

                        # Define the box for each tile
                        left = i * tile_size
                        upper = j * tile_size
                        right = left + tile_size
                        lower = upper + tile_size

                        # Crop the tile and save it
                        tile = img.crop((left, upper, right, lower))
                        tile_filename = f"tile_{i}_{j}.tif"
                        tile.save(final_path/tile_filename)

def normalize_image(image_path: Path) -> np.array:
    '''
    Firstly converts the image into a numpy array
    and then normalizes it to 8 bit.
    @Args:
        image: Image to normalize.
    @Return:
        Normalized image.
    '''
    image = Image.open(image_path)
    image = np.array(image)
    # 1. Normalize the array to the 0–255 range
    image = (image / image.max()) * 255
    return image.astype(np.uint8)  # Convert to 8-bit (0-255)
    
def invert_image(image: np.array) -> np.array:
    '''
    Inverts an image using bitwise operation.
    @Args:
        image: Image to invert.
    @Return:
        Returns an inverted image.
    '''
    return cv2.bitwise_not(image)

def find_brightest_spots(image: np.array, treshold: int) -> Image:
    '''
    Finds pixels within an image above the given treshold,
    and draws a circle around them.
    @Args:
        image: Image to find the spots on.
        treshold: Minimal brightness.
    @Return:
        PIL Image with drawn circles.
    '''
    # Find coordinates of pixels that are above the threshold
    spots = np.argwhere(image >= treshold)

    # Convert back to a PIL image for drawing
    highlighted_image = Image.fromarray(image).convert("RGB")
    draw = ImageDraw.Draw(highlighted_image)

    # Set circle radius
    circle_radius = 5

    for (y, x) in spots:  

        # Define the bounding box of the circle around each bright pixel
        bbox = [
            (x - circle_radius, y - circle_radius),
            (x + circle_radius, y + circle_radius)
        ]

        # Draw a red circle around each bright pixel
        draw.ellipse(bbox, outline="red", width=1)
    
    return highlighted_image
        
def denoise_image():
    pass
