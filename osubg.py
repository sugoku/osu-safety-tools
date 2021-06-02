# sugoku's osu! safety tools

# generates osu backgrounds

from PIL import Image, ImageDraw, ImageFont
import os, re, sys
from pathlib import Path

fontname = 'cmunssdc.ttf'

def generate_bg(bfn):
    bfn = Path(bfn)
    
    title = ""
    artist = ""
    creator = ""

    splt = lambda x: line.strip().split(x)[1]

    with open(bfn) as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if line.startswith('Title:'):
                title = splt('Title:')
            elif line.startswith('Artist:'):
                artist = splt('Artist:')
            elif line.startswith('Creator:'):
                creator = splt('Creator:')
            if line.startswith('[Events]'):
                break
        for line in lines[i+1:]:
            m = re.match('0,0,"(.*)",0,0', line)
            if m:
                imfn = bfn.parent/m.group(1)
                break

    W, H = (1280, 720)
    msg = f"{title}\n{artist}\n{creator}"
    
    # https://stackoverflow.com/a/49581617
    # Based on aaronpenne's solution, licensed under CC BY-SA 3.0

    # Create blank rectangle to write on
    im = Image.new('RGB', (W, H), "black")
    draw = ImageDraw.Draw(im)

    x1, y1, x2, y2 = [int(W*0.25), int(H*0.25), int(W*0.75), int(H*0.75)]

    font = ImageFont.truetype(fontname, size=W//30)

    # Calculate the width and height of the text to be drawn, given font size
    w, h = draw.textsize(msg, font=font)

    # Calculate the mid points and offset by the upper left corner of the bounding box
    x = (x2 - x1 - w)/2 + x1
    y = (y2 - y1 - h)/2 + y1

    # Write the text to the image, where (x,y) is the top left corner of the text
    draw.text((x, y), msg, "white", align='center', font=font)

    im.save(imfn, "PNG")
    
    # CC BY-SA 3.0 code ends here
    
if __name__ == '__main__':
    main()