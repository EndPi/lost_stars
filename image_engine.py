#!/usr/bin/env python3

import cv2
import sys
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from PIL import Image, ImageOps, ImageDraw, ImageFont
from scipy.ndimage import label, binary_closing, find_objects, center_of_mass

# Since we are dealing with big pictures :)
Image.MAX_IMAGE_PIXELS = None


def crop_to_tiles(debug: bool, image_path: Path, tile_size: int) -> None:
    '''
    Function to crop an image into smaller 
    tiles of a given size.
    @Args: 
        debug: Debug flag.
        image: Path to the image to open.
        tile_size: Desired size of the tiles.
    @Return:
        None.
    '''
    try:
        with Image.open(image_path.with_suffix(".tif")) as img:
            width, height = img.size    
            # Calculate the number of tiles (rounded up)
            x_tiles = int(np.ceil(width / tile_size))
            y_tiles = int(np.ceil(height / tile_size))

            # Resize image to ensure full coverage
            new_width = x_tiles * tile_size
            new_height = y_tiles * tile_size
            img_resized = img.resize((new_width, new_height), Image.LANCZOS)

            # Create the folder for tiles.
            tile_folder = image_path.parent / image_path
            tile_folder.mkdir(parents=True, exist_ok=True)

            # Crop the image into tiles.
            for i in range(x_tiles):
                for j in range(y_tiles):

                    # Define the box for each tile.
                    left = i * tile_size
                    upper = j * tile_size
                    right = left + tile_size
                    lower = upper + tile_size

                    # Crop the tile and save it.
                    tile = img_resized.crop((left, upper, right, lower))
                    tile_filename = f"tile_{i}_{j}.tif"
                    tile.save(tile_folder / tile_filename)
    except FileNotFoundError:
        print(f'ERROR: File {image_path} not found. Quitting!')
        sys.exit()
    finally:
        if debug:
            print(f'DEBUG: Cropped {image_path} into tiles!')

def normalize_image(image_path: Path) -> np.array:
    '''
    Firstly converts the image into a numpy array
    and then normalizes it.
    @Args:
        image: Path to image to normalize.
    @Return:
        Normalized image.
    '''
    try:
        image = Image.open(image_path)
    except FileNotFoundError:
        print(f'ERROR: Image {image_path} not found. Quitting!')
        sys.exit()
    finally:
        image = np.array(image)
        image = (image - image.min()) / (image.max() - image.min()) * 255
        return image.astype(np.uint8)  
    
def invert_image(image: np.array) -> np.array:
    '''
    Inverts an image using numpy.
    @Args:
        image: Image to invert.
    @Return:
        Returns an inverted image.
    '''
    return np.invert(image)

def find_brightest_spots(image: np.array, threshold: int, min_blob_size: int = 50, 
                         use_adaptive_threshold: bool = True, max_stars: int = 5) -> Image.Image | list:
    '''
    Finds bright stars in the provided image and draws a circle around them. 
    Also returns their coordinates.
    @Args:
        image: Image to find stars in.
        threshold: Minimal brightness to identify a star. If None, an adaptive method is used. By default None
        min_blob_size: Minimum size of a blob to be considered a star. By default 50.
        use_adaptive_threshold: If True, use adaptive Otsu's method if no threshold is provided. By default True.
        max_stars: Maximum number of stars to detect. By default 5.      
    @Return:
        PIL Image with circles drawn at star locations, and a list of star center coordinates.
        List of the brightest stars coordinates.
    '''
    # Create binary mask for bright pixels.
    binary_mask = image >= threshold
    binary_mask = binary_closing(binary_mask, structure=np.ones((3, 3)))
    
    # Label connected components
    labeled_array, num_features = label(binary_mask)
    
    # Filter out small blobs 
    object_slices = find_objects(labeled_array)
    for i, obj_slice in enumerate(object_slices, start=1):
        region_size = np.sum(labeled_array[obj_slice] == i)
        if region_size < min_blob_size:  # Remove small blobs
            labeled_array[labeled_array == i] = 0
    labeled_array, num_features = label(labeled_array > 0)
    
    # Calculate centroids of connected components
    centroids = center_of_mass(binary_mask, labeled_array, range(1, num_features + 1))
    
    # Filter out only the brightest stars
    if len(centroids) > max_stars:
        # Sort centroids by image brightness at centroid positions and keep the top `max_stars`
        centroids = sorted(centroids, key=lambda c: image[int(c[0]), int(c[1])], reverse=True)[:max_stars]
    
    # Draw circles on the image at the positions of star centers
    output_image = Image.fromarray(np.uint8(image))
    output_image = output_image.convert("RGB")
    draw = ImageDraw.Draw(output_image)

    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 60)        
    except IOError:
        font = ImageFont.load_default()
    
    star_coordinates = []
    for index, (y, x) in enumerate(centroids):  
        x, y = int(x), int(y)  
        radius = 10  
        draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill="red", outline=None)
        label_text = str(index + 1)  # Label is 1-based index
        text_bbox = draw.textbbox((0, 0), label_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        
        text_position = (x - text_width // 2, y + radius + 3)
        draw.text(text_position, label_text, fill="green", font=font)
        star_coordinates.append((x, y))
    
    return output_image, star_coordinates

def prepare_fig(image1: np.array, image2: np.array, image3: np.array, image4:np.array, tile_name: str, save_path: Path) -> None:
    '''
    Funcion which saves the plot of four images. 
    Used for visualisation of transformations.
    @Args:
        image1: Expecting inverted and normalized past image.
        image2: Expecting inverted and normalized recent image.
        image3: Expecting the transformed past image (aligned with respect to recent pair image)
        image4: Expecting footprint of the transformation. If any.
        tile_name: Name of the tile. Used to file naming.
        save_path: Path where to save the file to.
    @Return:
        None
    '''
    fig, axes = plt.subplots(2, 2, figsize=(10, 10))
    axes[0, 0].imshow(np.flipud((image1)), cmap='gray', interpolation='none', origin='lower')
    axes[0, 0].axis('off')
    axes[0, 0].set_title("Past Image")

    axes[0, 1].imshow(np.flipud((image2)), cmap='gray', interpolation='none', origin='lower')
    axes[0, 1].axis('off')
    axes[0, 1].set_title("Recent Image")

    axes[1, 0].imshow(np.flipud((image3)), cmap='gray', interpolation='none', origin='lower')
    axes[1, 0].axis('off')
    axes[1, 0].set_title("Past Image aligned with Recent Image")

    axes[1, 1].imshow(np.flipud((image4)), cmap='gray', interpolation='none', origin='lower')
    axes[1, 1].axis('off')
    axes[1, 1].set_title("Footprint of the Transformation")

    axes[1, 0].axis('off')

    plt.tight_layout()
    fig_filename = f"{tile_name}_transformation.png"  # e.g. 'tile_0_0_transformation.png'.
    fig_path = save_path / fig_filename
    plt.savefig(fig_path, bbox_inches='tight')
    plt.close(fig)

def apply_non_local_means_denoising(image: np.array, h: int = 7) -> np.array:
    '''
    Currently redundant.
    Function which to certain extent is capable of denoising 
    the provided image using non-local means.
    @Args:
        image: Image to denoise.
    @Return:
        Denoised image.
    '''
    return cv2.fastNlMeansDenoising(image, None, h, 7, 21)

def create_diff_map(image1: np.array, image2: np.array, image3: np.array, tile_name: str, save_path: Path) -> None:
    '''
    Function to create and save a difference map between two provided images.
    @Args:
        image1: Expecting inverted and normalized past image.
        image2: Expecting inverted and normalized recent image.
        image3: Expecting transformed past image.
        tile_name: Name of the tile. Used to file naming.
        save_path: Path where to save the file to.
    @Return:
        None
    '''
    difference_map = np.abs(image3 - image2)

    fig = plt.figure(figsize=(10, 10))
    gs = GridSpec(2, 3, figure=fig, width_ratios=[1, 1, 0.05], height_ratios=[1, 1], wspace=0.1, hspace=0.2)

    # Plot norm_past.
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.imshow(np.flipud(image1), cmap='gray', interpolation='none', origin='lower')
    ax1.axis('off')
    ax1.set_title("Inverted and Normalized Past Image")

    # Plot norm_recent.
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.imshow(np.flipud(image2), cmap='gray', interpolation='none', origin='lower')
    ax2.axis('off')
    ax2.set_title("Inverted and Normalized Recent Image")

    # Plot transformed_past.
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.imshow(np.flipud(image3), cmap='gray', interpolation='none', origin='lower')
    ax3.axis('off')
    ax3.set_title("Transformed Past Image")

    # Plot difference map.
    ax4 = fig.add_subplot(gs[1, 1])
    img = ax4.imshow(np.flipud(difference_map), cmap='inferno', vmin=0, vmax=difference_map.max(), origin='lower')
    ax4.axis('off')
    ax4.set_title("Difference Map (Transformed Past - Recent)")

    # Colorbar placed in the 3rd column of the bottom row.
    cbar_ax = fig.add_subplot(gs[1, 2])
    cbar = fig.colorbar(img, cax=cbar_ax, orientation='vertical')
    cbar.set_label('Difference Intensity', rotation=270, labelpad=15)

    # Save the plot.
    fig_filename = f"{tile_name}_transformation.png"  # e.g. 'tile_0_0_transformation.png'.
    fig_path = save_path / fig_filename
    plt.savefig(fig_path, bbox_inches='tight')
    plt.close(fig)
    