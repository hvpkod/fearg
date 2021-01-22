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
-v for verbose mode. Shows detailed info. Default for single images.
-nopalette for skipping color palette sample card. Default created a colorexport directory.
-nojson for no json data. Otherwise creates a <date>_imgdata.json file.

Fearg support following formats: jpg, jpeg and png.


## License
[MIT](https://choosealicense.com/licenses/mit/)
