import datetime
import json
import os
from collections import Counter
from pathlib import Path

import click
from colr import Colr as C
from PIL import Image

outputdata = {}
verbose_flag = False
json_flag = True
slip_flag = True
timestamp = str(datetime.datetime.now())
date = str(datetime.date.today())


@click.command()
@click.option("-verbose", "-v", is_flag=True, help="Will print extended metadata")
@click.option("-nojson", is_flag=True, help="Extract no json data file")
@click.option("-noslip", is_flag=True, help="Extract no color slip")
@click.argument("img")
def inputvalidate(verbose, nojson, noslip, img):
    """Fearg is a batch tool to get meta data and create color slips."""
    if noslip:
        global slip_flag
        slip_flag = False

    if nojson:
        global json_flag
        json_flag = False

    if verbose:
        global verbose_flag
        verbose_flag = True

    get_path(img)


def json_export(jsonindata):
    """Dump output to file as json."""
    with open(date + "_imgdata.json", "w") as fp:
        json.dump(jsonindata, fp)


def img_check(check):
    """Validate the suffix as img."""
    imgformats = [".png", ".jpg", ".jpeg"]
    return Path(check).suffix.lower() in imgformats


def get_path(inputdata):
    """Validate input data."""
    imgs = []
    try:
        if Path(inputdata).exists:
            if Path(inputdata).is_file() and img_check(inputdata):
                print("File input")
                global verbose_flag
                verbose_flag = True
                imgs.append(inputdata)
            elif Path(inputdata).is_dir():
                print("Directory input")
                for (dirpath, dirnames, filenames) in os.walk(inputdata):
                    imgs += [
                        os.path.join(dirpath, file)
                        for file in filenames
                        if img_check(file)
                    ]
            else:
                print("Not a image file")
                exit()
        main(imgs)

    except FileNotFoundError:
        print("File or Directory dont exists")


def set_structure(albumindata):
    """Create skeleton for json-structure."""
    albumdata = {}
    albumdata["rootsource"] = albumindata[0].split("/")[0]
    albumdata["files"] = len(albumindata)
    albumdata["Timestamp"] = timestamp
    albumdata["date"] = date
    outputdata["albumdata"] = albumdata
    outputdata["filedata"] = []


def create_color(colormix, name, px):
    """Create two sets of img as color representation and diversion."""
    if slip_flag:
        tmpim = Image.new("RGB", (len(colormix) * 50, 50))
        make_directory()
        offset = 0
        offset2 = 0
        totalpx = sum(px)

        for i, c in enumerate(colormix):
            tmpc = Image.new("RGB", (50, 40), c)
            tmpim.paste(tmpc, (offset, 0))
            offset += 50
        for i, c in enumerate(colormix):
            tmpwidth = int(len(colormix) * 51 * (px[i] / totalpx))
            tmpcs = Image.new("RGB", (tmpwidth, 10), c)
            tmpim.paste(tmpcs, (offset2, 40))
            offset2 += tmpwidth
        tmpim.save("colorexport/_" + name + ".png")
    else:
        print("No colorslips created")


def get_metadata(meta):
    """Extract metadata from from img file with focus on colors."""
    img_info = {}
    img_info_tmp = {}
    im = Image.open(meta).convert("RGB")
    color = Counter(im.getdata())
    color_common = color.most_common(10)
    img_info["numbercolors"] = len(color)
    img_size = im.size
    img_width, imgheight = im.size
    img_pixels = imgheight * img_width
    img_info["imgsrc"] = str(Path(meta))
    img_name = str(Path(meta).name.lower())
    img_stem = str(Path(meta).stem.lower())
    img_info["imgname"] = img_name
    img_info["imgtype"] = str(Path(meta).suffix.lower())
    img_info["imgstem"] = img_stem
    img_info["imgsize"] = img_size
    img_info["imgwidth"] = img_width
    img_info["imgheight"] = imgheight
    img_info["imgpixels"] = img_pixels
    img_info_tmp["rgbs"] = []
    xc_tmp = []
    color_meta = []
    for c in color_common:
        color_info = {}
        rgb_value, pixel_count = c
        R, G, B = rgb_value
        color_info["px#"] = pixel_count
        color_info["rgb"] = rgb_value
        color_info["r"] = R
        color_info["g"] = G
        color_info["b"] = B
        color_info["textcontrast"] = (
            "#5d5d5d" if (R * 0.299 + G * 0.587 + B * 0.114) > 186 else "#ededed"
        )
        hex = "#%02x%02x%02x" % (rgb_value[:3])
        color_info["hex"] = hex
        img_info_tmp["rgbs"].append(rgb_value)
        color_info["%"] = "%0.2f" % (pixel_count / img_pixels * 100.0)
        color_meta.append(color_info)
        xc_tmp.append(pixel_count)
    create_color(img_info_tmp["rgbs"], img_info["imgstem"], xc_tmp)
    img_info["colormeta"] = color_meta
    outputdata["filedata"].append(img_info)


def print_list():
    """Print to console. For multiple files."""
    headers = ["", "Color 1", "Color 2", "Color 3", "Filename"]

    print("Rootsource", outputdata["albumdata"]["rootsource"])
    print("Date: {}".format(outputdata["albumdata"]["date"]))

    print("")
    print("> Img data")
    print("{:5}{:23}{:23}{:23}{:<}".format(*headers))

    for i in range(len(outputdata["filedata"])):

        data = outputdata["filedata"][i]
        color = outputdata["filedata"][i]["colormeta"]

        col1_rgb = str(color[0]["rgb"])
        c1hex = color[0]["hex"]
        r1, g1, b1 = color[0]["rgb"]
        col1_hex_text = color[0]["textcontrast"]
        col1_hex_c = C().b_hex(c1hex, rgb_mode=True).hex(col1_hex_text, c1hex)
        col1_rgb_c = C().b_rgb(r1, g1, b1).hex(col1_hex_text, col1_rgb.ljust(15, " "))

        col2_hex_c = ""
        col2_rgb_c = ""

        if data["numbercolors"] > 1:
            col2_rgb = str(color[1]["rgb"])
            col2_hex = color[1]["hex"]
            r2, g2, b2 = color[1]["rgb"]
            col2_hex_text = color[1]["textcontrast"]
            col2_hex_c = C().b_hex(col2_hex, rgb_mode=True).hex(col2_hex_text, col2_hex)
            col2_rgb_c = (
                C().b_rgb(r2, g2, b2).hex(col2_hex_text, col2_rgb.ljust(15, " "))
            )

        col3_hex_c = ""
        col3_rgb_c = ""

        if data["numbercolors"] > 2:
            col3_rgb = str(color[2]["rgb"])
            col3_hex = color[2]["hex"]
            r3, g3, b3 = color[2]["rgb"]
            col3_hex_text = color[2]["textcontrast"]
            col3_hex_c = C().b_hex(col3_hex, rgb_mode=True).hex(col3_hex_text, col3_hex)
            col3_rgb_c = (
                C().b_rgb(r3, g3, b3).hex(col3_hex_text, col3_rgb.ljust(15, " "))
            )

        print(
            "# {:<4d}{:7}{:16}{:7}{:16}{:7}{:16}{:<}".format(
                i + 1,
                col1_hex_c,
                col1_rgb_c,
                col2_hex_c,
                col2_rgb_c,
                col3_hex_c,
                col3_rgb_c,
                data["imgname"],
            )
        )


def print_extended():
    """Print color into to terminal. For single files or extend info."""
    print("Rootsource", outputdata["albumdata"]["rootsource"])
    print("Date: {}".format(outputdata["albumdata"]["date"]))

    for i in range(len(outputdata["filedata"])):

        data = outputdata["filedata"][i]
        print("")
        print("Filename:            {}".format(data["imgname"]))
        print("Fileformat:          {}".format(data["imgtype"]))
        print("Resolution:          {}".format(data["imgsize"]))
        print("Number of colors:    {}".format(data["numbercolors"]))
        print("Width:               {}".format(data["imgwidth"]))
        print("Height:              {}".format(data["imgheight"]))
        print("Pixels:              {}".format(data["imgpixels"]))
        print("_" * 50)
        print("")

        color = outputdata["filedata"][i]["colormeta"]
        for index, c in enumerate(color):
            print("Color    {}:".format(index + 1))
            print(C().b_hex(c["hex"], rgb_mode=True).hex(c["hex"], " " * 30))
            print("Hex:     {}".format(c["hex"]))
            print("RGB:     {}".format(c["rgb"]))
            print("%:       {}".format(c["%"]))
            print("px:      {}".format(c["px#"]))
            print("")

        print("=" * 50)


def make_directory():
    """Directory validation."""
    Path("colorexport").mkdir(parents=True, exist_ok=True)


def main(indata):
    """Program main."""
    set_structure(indata)

    try:
        for i, d in enumerate(indata):
            print("Img {} out of {} - {}".format(i + 1, len(indata), d))
            get_metadata(d)
        print("> All processed")
        print("=" * 50, "\n")
    except Exception as e:
        print(e)

    if json_flag:
        json_export(outputdata)
    else:
        print("No json file created")
    if verbose_flag:
        print_extended()
    else:
        print_list()


if __name__ == "__main__":
    inputvalidate()
