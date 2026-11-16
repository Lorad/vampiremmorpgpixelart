from PIL import Image
import json
def hex2rgb(h): return tuple(int(h[i:i+2],16) for i in (1,3,5))
def grid_to_img(rows, pal, bg=None):
    H = len(rows); W = max(len(r) for r in rows)
    im = Image.new("RGBA", (W,H), (0,0,0,0) if bg is None else bg)
    px = im.load()
    for y,r in enumerate(rows):
        for x,ch in enumerate(r):
            if ch in pal: px[x,y] = hex2rgb(pal[ch]) + (255,)
    return im
def upscale(im, s): return im.resize((im.width*s, im.height*s), Image.NEAREST)
def on_bg(im, color=(255,255,255,255)):
    bg = Image.new("RGBA", im.size, color); bg.alpha_composite(im); return bg
