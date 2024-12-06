import numpy as np
import scipy as sp
import argparse
import sys
from pathlib import Path
import os
import cv2
from image_engine import *

#https://mwcraig.github.io/ccd-as-book/01-05-Calibration-overview.html

DEBUG = 0
PAST_IMAGES_PATH = None
RECENT_IMAGES_PATH = None

def resolve_args(args) -> None:
    '''
    Try to resolve the args given by the user.
    The following is currently required:
    i) source_folder with past images
    ii) source folder with recent images
    If no args are given, quit.
    @Args:
        args: Console args given by the user.
    @Return:
        None.
    '''
    global DEBUG, PAST_IMAGES_PATH, RECENT_IMAGES_PATH
    if len(sys.argv) <= 1:
        print(f'WARN: No arguments were provided. Quitting!')
        sys.exit()
    else:
        if args.debug:
            DEBUG = 1
            print(f'DEBUG: Debug mode enabled!')
        if not(args.source_folder_past):
            print(f'WARN: No source folder for past images provided. Quitting')
            sys.exit()
        if not(args.source_folder_recent):
            print(f'WARN: No source folder for recent images provided. Quitting!')
            sys.exit()
        check_content(Path(args.source_folder_past), Path(args.source_folder_recent))
        PAST_IMAGES_PATH = Path(args.source_folder_past).resolve()
        RECENT_IMAGES_PATH = Path(args.source_folder_recent).resolve()
        if DEBUG:
            print(f'DEBUG: Args parsed!')

def print_content(source_path: Path) -> None: 
    '''
    Helper function to print the content 
    of the given folder.
    @Args:
        source_path: Path to print the content of.
    @Return:
        None.
    '''
    if DEBUG:
        print(f'DEBUG: Trying to access the content of {source_path}!')
    for entry in source_path.iterdir():
        if entry.is_file():
            print(f'INFO: Found the following file: {entry}!')

def check_content(path1: Path, path2: Path) -> None:
    '''
    Helper function to make sure that
    the provided directories exist and
    the number of files within them is 
    the same.
    @Args:
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
    if DEBUG:
        print(f'DEBUG: Directories exist and the number of files in {path1} and {path2} is the same!')

def main():
    crop_to_tiles(PAST_IMAGES_PATH, 2048)
    # Example 1
    #test_image = normalize_image('/home/matej/Desktop/astro/past_images/602940/tile_3_3.tif')
    #Image.fromarray(invert_image(test_image)).show()
    # Example 2
    #image_with_spots = normalize_image('/home/matej/Desktop/astro/past_images/602940/tile_3_3.tif')
    #find_brightest_spots(invert_image(image_with_spots), 150).show()
    print(f'INFO: Done!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Lost Stars')
    parser.add_argument('-d', '--debug', action='store_true', dest='debug')
    parser.add_argument('-p', '--source_folder_past',dest='source_folder_past')
    parser.add_argument('-r', '--source_folder_recent', dest ='source_folder_recent')
    args = parser.parse_args()
    resolve_args(args)
    main()