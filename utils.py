#!/usr/bin/env python3

import os
import sys
import numpy as np
from glob import glob
from pathlib import Path

def print_folder_content(debug: bool, source_path: Path) -> None: 
    '''
    Helper function to print the content 
    of the given folder.
    @Args:
        debug: Debug flag.
        source_path: Path to the folder to print the content of.
    @Return:
        None.
    '''
    if debug:
        print(f'DEBUG: Trying to access the content of {source_path}!')
    for entry in source_path.iterdir():
        if entry.is_file():
            print(f'INFO: Found the following file: {entry}!')

def check_folder_content(debug: bool, path1: Path, path2: Path) -> None:
    '''
    Helper function to make sure that
    the provided directories exist and
    the number of files within them is 
    the same.
    @Args:
        debug: Debug flag. 
        path1: Path to the first folder.
        path2: Path to the second folder.
    @Return:
        None.
    '''
    if not(path1.exists()) or not(path2.exists()):
        print(f'WARN: Directory does not exist. Quitting!')
        sys.exit()
    if (sum(1 for x in path1.glob('*') if x.is_file())) != (sum(1 for x in path2.glob('*') if x.is_file())):
        print(f'WARN: Mismatch in number of files in {path1} and {path2}. Quitting!')
        sys.exit()
    if debug:
        print(f'DEBUG: Directories exist and the number of files in {path1} and {path2} is the same!')

def list_pairs(image_pairs: list) -> None:
    '''
    Helper function to list the image pairs.
    @Args:  
        image_pairs: Array of image pairs.
    @Return:
        None.
    '''
    # Start numbering at 1 for better clarity.
    for i, pair in enumerate(image_pairs, start=1):
        print(f"Pair {i}:")
        print(f"  Past Image: {pair['past_image']}")
        print(f"  Recent Image: {pair['recent_image']}")

def load_tiles_from_folder(debug: bool, folder_path: Path) -> list:
    '''
    Function to load all paths to all tiles within a specific folder.
    The paths are then used to create tile pairs for further processing.
    @Args:
        debug: Debug flag.
        folder_path: Path to the folder containing the image tiles.
    @Returns:
        tile_paths: List contaning paths to all tiles within a given folder.
    '''
    # Search within the given folder for files named tile_*.tif
    tile_paths = sorted(glob(os.path.join(folder_path, "tile_*.tif")))
    if debug:
        print(f"DEBUG: Found {len(tile_paths)} tiles in {folder_path}!")
    return tile_paths

def sort_corresponding_stars(debug: bool, array1: list, array2: list, num_matches: int = 3) -> np.array:
    '''
    Matches points (stars coordinates) from two arrays based on minimal distances, keeping the closest matches.
    Only the 'num_matches' closest points (in terms of minimal distance) are kept.
    @Args:
        debug: Debug flag.
        array1: List of tuples containing stars coordinates from the first image.
        array2: List of tuples containing stars coordinates from the second image.
        num_matches: The number of closest matches to retain. By default 3.
    @Returns:
        reordered_array1: The reorder version of original array1, containing only num_matches of points
        reordered_array2: The reorder version of original array2, containing only num_matches of points
    '''
    # Calculate distances between all pairs (i from array1, j from array2).
    if debug:
        print(f'DEBUG: Calculating distances!')
    distances = []
    for i, p1 in enumerate(array1):
        for j, p2 in enumerate(array2):
            dist = np.linalg.norm(np.array(p1) - np.array(p2))
            distances.append((dist, i, j))  #[(distance, index_in_array1, index_in_array2), ...].
    
    # Sort distances by the smallest distance first.
    distances.sort(key=lambda x: x[0])

    # Keep only the best closest matches.
    best_matches = distances[:num_matches]

    # Reconstruct the matched arrays based on the best matches
    reordered_array1 = [array1[i] for _, i, _ in best_matches]
    reordered_array2 = [array2[j] for _, _, j in best_matches]
    if debug:
        print(f'DEBUG: Arrays sorted!')

    return np.array(reordered_array1), np.array(reordered_array2)
