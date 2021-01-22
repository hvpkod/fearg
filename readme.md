# Fearg

Fearg (Färg) is a python command line tool to extract color information from images.
The tool extract the 10 most common colors and outputs a json summary as well as
color sample card along with resolution and color data. Fearg supports both batch (directories) of images and single images.

## Installation

Clone the repository and make sure you have the correct dependencies installed.


```bash
pip install click
pip install colr
pip install pillow
```

## Usage

```bach
python fearg.py (-v) (-nojson) (-nopalette) [directory]/[file]
```


Supports following modes:
* v, verbose: Shows detailed info and metadata. Default for single images.
* nopalette: Skipping creating color palette sample card. Default created a colorexport directory.
* nojson: No json data. Default creates a <date>_imgdata.json file in root folder.
* color,c: Ignore white and black img. Exclued for grayscales and images with less ten colors.  

Fearg support following formats: jpg, jpeg and png.

## Examples 

_Show the 3 dominate colors for each image in the input directory_

![Directory](https://github.com/hvpkod/fearg/blob/main/example/batch.png)
 
_Show the 10 dominate colors and metadata for single image input or directory with verbose mode_

![Singe file](https://github.com/hvpkod/fearg/blob/main/example/file.png)

_Create a color palette samle image with the 10 most dominate colors, percentage of dominace_

![Palette](https://github.com/hvpkod/fearg/blob/main/example/palette.png)


## License
[MIT](https://choosealicense.com/licenses/mit/)
