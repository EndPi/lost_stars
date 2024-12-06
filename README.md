# Lost Stars Project


## Setup
There are currently two python files, `main.py` and `image_engine.py`. The program runs by launching `main.py`, where the following arguments are neccessary/optional:
```
1. -p path | for specifying the path to past images. Mandatory.
2. -r path | for specifying the path to recent images. Mandatory.
3. -d      | for debug mode. Displays additional information. Optional.
```
Additionally, the program can be run by using a bash script, i.e. `./run.sh` for regular version and `./run_debug.sh` for the debug version. It is neccessary to adjust the path to the images within those files if you wish to use this way.

## Workflow
My personal suggestion of possible work-flow is the following. We take two folders of images, one with the past images (i.e. let's say 1930) and the other with the more recent images (e.g. 1970). We organise the images within the folders so that the corresponding images are at the same index, e.g. `folder_past/img_1` and `folder_recent/img_1` are the "same" picture, just the former is the older one and the latter is the younger one.

For each such pair, we find the transformation and subsequently apply the transformation, to let's say, the older picture, i.e. the past one. To do this, we will likely need to crop down the images into smaller tiles and figure out, how to determine the transformation of the whole picture. 

Once that's done, we can compare the pictures, since they should now be essentially of the same orientation etc., and create some sort of difference map. For instance, if the first picture contains a  huge star with brightness/pixel value of e.g. `255`, and the next picture contains just blank space (suggesting we found a lost star), i.e. the value is e.g. `20`, the difference map will contain the value `255-20`. In other words, it will contain white (or pretty much any other color) spots, where those spots will represent a location, where a significant difference occured. Something like [this](https://www.researchgate.net/publication/270216822/figure/fig1/AS:613883505045506@1523372641055/a-Difference-map-retrieved-from-image-differencing-b-Difference-map-retrieved-from.png).

Once we do this, we can possibly average the value of each pixel within the difference map throughout the whole set (i.e. not just from one pair), so that small fluctations or such dissappear. We can then look at the biggest spots in the difference map, that means most probable candidates, and let's say, project those areas to the original images and check manually/visually, whether it is indeed a lost star candidate or just a flaw in our program, image corruption etc. What I imagine is something like [this](https://i.sstatic.net/5NuyK.png).

## Possible Implementation

```python
1. get set of recent/past images
2. reduce the size of images/preprocess/denoise*
3. find transformation between each pair*
4. apply transformation*
5. create diff map*
6. compare diff map with original set
```
Commands with * would be done performed within `image_engine.py`. 

[Link](https://mwcraig.github.io/ccd-as-book/01-05-Calibration-overview.html) to possible method of image processing/denoising.