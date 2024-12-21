#!/usr/bin/env python3
import sys
import yaml
import argparse
import astroalign as aa
from pathlib import Path

# To prevent certain issues I encountered.
import matplotlib
matplotlib.use('tkagg')

from image_engine import *
from utils import *

DEBUG = False
PAST_IMAGES_PATH = None
RECENT_IMAGES_PATH = None
TRSF_PATH = None
DIFF_MAP_PATH = None

def resolve_args(args) -> None:
    '''
    Try to resolve the args given by the user.
    The following is currently required:
    i) source_folder with past images
    ii) source folder with recent images
    Debug mode is disabled by default.
    If no args are given, quit.
    @Args:
        args: Console args given by the user.
    @Return:
        None.
    '''
    global DEBUG, PAST_IMAGES_PATH, RECENT_IMAGES_PATH, TRSF_PATH, DIFF_MAP_PATH
    if len(sys.argv) <= 1:
        print(f'WARN: No arguments were provided. Quitting!')
        sys.exit()
    else:
        if args.debug:
            DEBUG = True
            print(f'DEBUG: Debug mode enabled!')
        if not(args.source_folder_past):
            print(f'WARN: No source folder for past images provided. Quitting')
            sys.exit()
        if not(args.source_folder_recent):
            print(f'WARN: No source folder for recent images provided. Quitting!')
            sys.exit()
        check_folder_content(debug=DEBUG, path1=Path(args.source_folder_past), path2=Path(args.source_folder_recent))

        # Once the folders are checked, assign the corresponding paths.
        PAST_IMAGES_PATH = Path(args.source_folder_past).resolve()
        RECENT_IMAGES_PATH = Path(args.source_folder_recent).resolve()
        if DEBUG:
            print(f'DEBUG: PAST_IMAGES_PATH and RECENT_IMAGES_PATH both correctly set!')

        # Create directories for transformatios and diff. maps.
        trsf_path = PAST_IMAGES_PATH.parent / "transformations"
        trsf_path.mkdir(parents=True, exist_ok=True)
        diff_map_path = PAST_IMAGES_PATH.parent / "diff_maps"
        diff_map_path.mkdir(parents=True, exist_ok=True)
        if DEBUG:
            print(f'DEBUG: Created root paths for transformations and difference maps!')

        # Assign those paths.
        TRSF_PATH = trsf_path
        DIFF_MAP_PATH = diff_map_path
        if DEBUG:
            print(f'DEBUG: TRSF_PATH and DIFF_MAP_PATH both set correctly!')
        if DEBUG:
            print(f'DEBUG: Args parsed!')
        print(f'INFO: Initialization complete!')

def main() -> None:
    print(f'INFO: Starting main!')
    try:
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
        image_pairs = config['image_pairs']
    except FileNotFoundError:
        print(f'ERROR: Config file not found!')
    finally:
        if DEBUG:
            print(f'DEBUG: Config file read successfully!')
    print(f'INFO: Starting pair processing!')
    for i, pair in enumerate(image_pairs, start=1):
        print(f"INFO: Processing pair {i}...")
        past, recent = pair['past_image'], pair['recent_image']
        
        crop_to_tiles(debug=DEBUG, image_path=Path.joinpath(PAST_IMAGES_PATH, past), tile_size=2048)
        crop_to_tiles(debug=DEBUG, image_path=Path.joinpath(RECENT_IMAGES_PATH, recent), tile_size=2048)
        print(f'INFO: Cropped!')
        
        # Load paths to tiles.
        past_tiles = load_tiles_from_folder(debug=DEBUG, folder_path=Path.joinpath(PAST_IMAGES_PATH, past))
        recent_tiles = load_tiles_from_folder(debug=DEBUG, folder_path=Path.joinpath(RECENT_IMAGES_PATH, recent))

        # Create subfolders.
        image_pair_folder_name = f"{Path(past).stem}_vs_{Path(recent).stem}"  # e.g. 602940_vs_603172.
        pair_folder_path = TRSF_PATH / image_pair_folder_name
        pair_folder_path.mkdir(parents=True, exist_ok=True)  
        diff_map_path = DIFF_MAP_PATH / image_pair_folder_name
        diff_map_path.mkdir(parents=True, exist_ok=True)
        if DEBUG:
            print(f'DEBUG: Folders for each pair transformation and difference map created successfully!')

        print(f'INFO: Determining transformations!')
        for past_tile_path, recent_tile_path in zip(past_tiles, recent_tiles):
            norm_past = invert_image(image=normalize_image(image_path=past_tile_path))
            norm_recent = invert_image(image=normalize_image(image_path=recent_tile_path))
            if DEBUG:
                print(f'DEBUG: Images {norm_past} and {norm_recent} inverted!')
            
            past_spots, past_cords = find_brightest_spots((norm_past), 200)
            recent_spots, recent_cords = find_brightest_spots((norm_recent), 200)

            src_cords, trgt_cords = sort_corresponding_stars(debug=DEBUG, array1=past_cords, array2=recent_cords)
            if DEBUG:
                print(f'DEBUG: Stars coordinates sorted!')
            try:    
                tform = aa.estimate_transform('affine', src_cords, trgt_cords)
                if DEBUG:
                    print(f'DEBUG: Transformation found!')
            except aa.MaxIterError:
                print(f'ERROR: Transformation not found!')
            try:
                transformed_past, footprint = aa.apply_transform(tform, norm_past, norm_recent)
                if DEBUG:
                    print(f'DEBUG: Transformation applied!')
            except np.linalg.LinAlgError:
                print(f'ERROR: Unable to apply transformation!')
                
            # Make plots.
            print(f'INFO: Preparing plots!')
            tile_name = Path(past_tile_path).stem  
            prepare_fig(image1=past_spots, image2=recent_spots, image3=transformed_past, image4=footprint, tile_name=tile_name,save_path=pair_folder_path)      
            create_diff_map(image1=norm_past, image2=norm_recent, image3=transformed_past, tile_name=tile_name, save_path=diff_map_path) 
        
    print(f'INFO: Done!')



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Lost Stars')
    parser.add_argument('-d', '--debug', action='store_true', dest='debug')
    parser.add_argument('-p', '--source_folder_past',dest='source_folder_past')
    parser.add_argument('-r', '--source_folder_recent', dest ='source_folder_recent')
    args = parser.parse_args()
    resolve_args(args)
    main()