"""Reads a color palette file
   Format of the color palette file should be the name of the palette on the first line
   followed by a color name or comma separated RGB values on each of the following lines
"""
from numpy import array
from enthought.enable2.colors import color_table
import os

all = ["get_palette","read_palette"]

palettes={}

def _valid_component(val):
    try:
        v = float(val)
    except:
        print "Each color in palette must be 3 RGB values"
        return 0
    if not v >=0 and v<=255:
        print "Each RGB color in palette must be >=0 and <=255"
        v=0
    return v

def _format_path():
    fullpath=__file__
    path=os.path.split(fullpath)[0]
    formatpath=os.path.join(path,"formats")
    return formatpath


def read_palette(file):
    if os.path.exists(file):
        fname=file
    else:
        full=os.path.join(_format_path(),file)
        if os.path.exists(full):
            fname=full
        else:
            raise ValueError("Palette file %s not found" % file)
    #
    f=open(fname,'r')
    lines=[line.strip() for line in f.readlines() \
           if (line and not line.startswith("#") and not line.strip() == "")]
    name=lines[0]
    if (" " in name):
        raise ValueError("Palette name must not contain spaces")
    if (not file == name+"_palette.txt"):
        raise ValueError(
            "Palette file name (%s) must be palette name (%s) plus '_palette.txt'"
             % (file,name))
    palette=[]
    
    for line in lines[1:]:
        vals=line.split(",")
        if not vals:
            continue
        if len(vals) == 1:
            cname=vals[0].strip()
            try:
                col=color_table[cname]
            except:
                raise ValueError("Color name %s not understood" % vals[0])
        elif len(vals) == 3:
            col=tuple([_valid_component(val)/255. for val in vals])
        else:
            print line
            raise ValueError("Each color in palette must be 3 RGB values or predefined chaco color name")
        palette.append(col)
    palettes[name]=palette
    f.close()
    return palette

def get_palette(name):
    return palettes[name]

read_palette("default_palette.txt")

# EOF




