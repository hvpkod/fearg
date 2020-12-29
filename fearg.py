import datetime
import json
import os
from collections import Counter
from pathlib import Path

import click
from colr import Colr as C
from PIL import Image

outputdata = {}
verboseflag = False
jsonflag = True
slipflag = True
timestamp = str(datetime.datetime.now())
date = str(datetime.date.today())


@click.command()
@click.option("--verbose", "--v", is_flag=True, help="Will print extended metadata")
@click.option("--nojson", is_flag=True, help="Extract no json data file")
@click.option("--noslip", is_flag=True, help="Extract no color slip")
@click.argument("img")
def inputvalidate(verbose, nojson, noslip, img):
    """Fearg is a batch tool to get meta data and create color slips."""
    if noslip:
        global slipflag
        slipflag = False

    if nojson:
        global jsonflag
        jsonflag = False

    if verbose:
        global verboseflag
        verboseflag = True

    getpath(img)


def json_export(jsonindata):
    """Dump output to file as json."""
    with open(date + "_imgdata.json", "w") as fp:
        json.dump(jsonindata, fp)


def imgcheck(check):
    """Validate the suffix as img."""
    imgformats = [".png", ".jpg", ".jpeg"]
    return Path(check).suffix.lower() in imgformats


def getpath(inputdata):
    """Validate input data."""
    imgs = []
    try:
        if Path(inputdata).exists:
            if Path(inputdata).is_file() and imgcheck(inputdata):
                print("File input")
                global verboseflag
                verboseflag = True
                imgs.append(inputdata)
            elif Path(inputdata).is_dir():
                print("Directory input")
                for (dirpath, dirnames, filenames) in os.walk(inputdata):
                    imgs += [
                        os.path.join(dirpath, file)
                        for file in filenames
                        if imgcheck(file)
                    ]
            else:
                print("Not a image file")
                exit()
        main(imgs)

    except FileNotFoundError:
        print("File or Directory dont exists")


def setstructure(albumindata):
    """Create skeleton for json-structure."""
    albumdata = {}
    albumdata["rootsource"] = albumindata[0].split("/")[0]
    albumdata["files"] = len(albumindata)
    albumdata["Timestamp"] = timestamp
    albumdata["date"] = date
    outputdata["albumdata"] = albumdata
    outputdata["filedata"] = []


def createColor(colormix, name, px):
    """Create two sets of img as color representation and diversion."""
    if slipflag:
        tmpim = Image.new("RGB", (len(colormix) * 50, 50))
        makedirectory()
        offset = 0
        offset2 = 0
        totalpx = sum(px)

        try:
            for index, c in enumerate(colormix):
                tmpc = Image.new("RGB", (50, 40), c)
                tmpim.paste(tmpc, (offset, 0))
                offset += 50
            for index, c in enumerate(colormix):
                tmpwidth = int(len(colormix) * 51 * (px[index] / totalpx))
                tmpcs = Image.new("RGB", (tmpwidth, 10), c)
                tmpim.paste(tmpcs, (offset2, 40))
                offset2 += tmpwidth
            tmpim.save("colorexport/_" + name + ".png")
        except Exception as e:
            print(e)
    else:
        print("No colorslips created")


def getmetadata(meta):
    """Extract metadata from from img file with focus on colors."""
    imgInfo = {}
    imgInfotmp = {}
    im = Image.open(meta)
    color = Counter(im.getdata())
    colorcommon = color.most_common(10)
    imgInfo["numbercolors"] = len(color)
    imgsize = im.size
    imgwidth, imgheight = im.size
    imgpixels = imgheight * imgwidth
    imgInfo["imgsrc"] = str(Path(meta))
    imgname = str(Path(meta).name.lower())
    imgstem = str(Path(meta).stem.lower())
    imgInfo["imgname"] = imgname
    imgInfo["imgtype"] = str(Path(meta).suffix.lower())
    imgInfo["imgstem"] = imgstem
    imgInfo["imgsize"] = imgsize
    imgInfo["imgwidth"] = imgwidth
    imgInfo["imgheight"] = imgheight
    imgInfo["imgpixels"] = imgpixels
    imgInfotmp["rgbs"] = []
    tmpxc = []
    colormeta = []
    for c in colorcommon:
        colorinfo = {}
        rgbvalue, pixelcount = c
        R, G, B = rgbvalue
        colorinfo["px#"] = pixelcount
        colorinfo["rgb"] = rgbvalue
        colorinfo["r"] = R
        colorinfo["g"] = G
        colorinfo["b"] = B
        colorinfo["textcontrast"] = (
            "#5d5d5d" if (R * 0.299 + G * 0.587 + B * 0.114) > 186 else "#ededed"
        )
        hex = "#%02x%02x%02x" % (rgbvalue)
        colorinfo["hex"] = hex
        imgInfotmp["rgbs"].append(rgbvalue)
        colorinfo["%"] = "%0.2f" % (pixelcount / imgpixels * 100.0)
        colormeta.append(colorinfo)
        tmpxc.append(pixelcount)
    createColor(imgInfotmp["rgbs"], imgInfo["imgstem"], tmpxc)
    imgInfo["colormeta"] = colormeta
    outputdata["filedata"].append(imgInfo)


def printoutlist():
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

        c1rgb = str(color[0]["rgb"])
        c1hex = color[0]["hex"]
        r1, g1, b1 = color[0]["rgb"]
        c1hextext = color[0]["textcontrast"]
        c1hexc = C().b_hex(c1hex, rgb_mode=True).hex(c1hextext, c1hex)
        c1rgbc = C().b_rgb(r1, g1, b1).hex(c1hextext, c1rgb)

        c2hexc = ""
        c2rgbc = ""

        if data["numbercolors"] > 1:
            c2rgb = str(color[1]["rgb"])
            c2hex = color[1]["hex"]
            r2, g2, b2 = color[1]["rgb"]
            c2hextext = color[1]["textcontrast"]
            c2hexc = C().b_hex(c2hex, rgb_mode=True).hex(c2hextext, c2hex)
            c2rgbc = C().b_rgb(r2, g2, b2).hex(c2hextext, c2rgb)

        c3hexc = ""
        c3rgbc = ""

        if data["numbercolors"] > 2:
            c3rgb = str(color[2]["rgb"])
            c3hex = color[2]["hex"]
            r3, g3, b3 = color[2]["rgb"]
            c3hextext = color[2]["textcontrast"]
            c3hexc = C().b_hex(c3hex, rgb_mode=True).hex(c3hextext, c3hex)
            c3rgbc = C().b_rgb(r3, g3, b3).hex(c3hextext, c3rgb)

        print(
            "# {:<3d}{:7}{:16}{:7}{:16}{:7}{:16}{:<}".format(
                i + 1,
                c1hexc,
                c1rgbc,
                c2hexc,
                c2rgbc,
                c3hexc,
                c3rgbc,
                data["imgname"],
            )
        )


def printoutextended():
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


def makedirectory():
    """Directory validation."""
    Path("colorexport").mkdir(parents=True, exist_ok=True)


def main(indata):
    """Program main."""
    setstructure(indata)

    try:
        for index, i in enumerate(indata):
            print("Img {} out of {} - {}".format(index + 1, len(indata), i))
            getmetadata(i)
        print("> All processed")
        print("=" * 50, "\n")
    except Exception as e:
        print(e)

    if jsonflag:
        json_export(outputdata)
    else:
        print("No json file created")
    if verboseflag:
        printoutextended()
    else:
        printoutlist()


if __name__ == "__main__":
    inputvalidate()
