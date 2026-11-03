"""Turns the Gemini sheets in images/coderotimages into upload-ready PNGs in assets/gemini/.

textures/  seamless textures, 512x512
heroes/    front view of each hero sheet, white background removed, 256x256
weapons/   side view of each weapon sheet, white background removed, 512x256
maps/      beauty shots and the training blueprint, 1024 wide, for the hub screen
Run: python tools/images/prepare.py
"""
import os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "images", "coderotimages")
OUT = os.path.join(ROOT, "assets", "gemini")

TEXTURES = ["lane-floor", "lane-edge", "jungle-floor", "jungle-wall", "camp-floor", "boss-pit", "base-compilers",
            "base-rot", "catwalk", "tower-metal", "bridge-deck", "void-sky"]
HEROES = ["segfault", "hotfix", "regex", "null-pointer", "recursion", "garbage-collector", "race-condition",
          "spaghetti", "mutex", "infinite-loop", "memory-leak", "vibe-coder"]
WEAPONS = {
    "segfault": "weapon-segfault-called-coredumper", "hotfix": "weapon-hotfix-called-patchgun",
    "regex": "weapon-regex-called-railgun", "null-pointer": "weapon-nullpointer-called-silencedSMG",
    "recursion": "weapon-recursion-called-mirrorwand", "garbage-collector": "weapon-garbagecollector-called-slowcannon",
    "race-condition": "weapon-racecondition-called-dualpistols", "spaghetti": "weapon-spaghetti-called-noodlespray",
    "mutex": "weapon-mutex-called-lockdownrifle", "infinite-loop": "weapon-infiniteloop-burstrifle",
    "memory-leak": "weapon-memoryleak-acidstaff", "vibe-coder": "weapon-vibecoder-autocompletewand",
}


def cutout(im):
    """Flood-fills the white background from the border and makes it transparent."""
    im = im.convert("RGB")
    key = (255, 0, 254)
    w, h = im.size
    for x in range(0, w, 8):
        for y in (0, h - 1):
            if im.getpixel((x, y)) != key and min(im.getpixel((x, y))) > 225:
                ImageDraw.floodfill(im, (x, y), key, thresh=40)
    for y in range(0, h, 8):
        for x in (0, w - 1):
            if im.getpixel((x, y)) != key and min(im.getpixel((x, y))) > 225:
                ImageDraw.floodfill(im, (x, y), key, thresh=40)
    rgba = im.convert("RGBA")
    rgba.putdata([(0, 0, 0, 0) if p[:3] == key else p for p in rgba.getdata()])
    return rgba


def clear_white(im):
    """Clears enclosed white gaps (trigger guards) the border flood fill can't reach."""
    im.putdata([(0, 0, 0, 0) if min(px[:3]) > 236 else px for px in im.getdata()])
    return im


def fit(im, size):
    bbox = im.getbbox()
    if bbox:
        im = im.crop(bbox)
    im.thumbnail((size[0] - 8, size[1] - 8), Image.LANCZOS)
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    canvas.paste(im, ((size[0] - im.width) // 2, (size[1] - im.height) // 2), im)
    return canvas


# map art shown on the hub's mode screen
MAPS = {"monorepo": "main-lain-beauty", "bridge": "bridge-beauty", "training": "training-layout", "lobby": "lobby-beauty"}


def main():
    for d in ("textures", "heroes", "weapons", "maps"):
        os.makedirs(os.path.join(OUT, d), exist_ok=True)
    for t in TEXTURES:
        Image.open(os.path.join(SRC, t + ".jpg")).convert("RGB").resize((512, 512), Image.LANCZOS).save(
            os.path.join(OUT, "textures", t + ".png"))
    for h in HEROES:
        im = Image.open(os.path.join(SRC, "heroes-" + h + ".jpg"))
        front = im.crop((0, 0, im.width * 36 // 100, im.height))  # sheets are front | side | back
        fit(cutout(front), (256, 256)).save(os.path.join(OUT, "heroes", h + ".png"))
    for h, f in WEAPONS.items():
        im = Image.open(os.path.join(SRC, f + ".jpg"))
        side = im.crop((0, 0, im.width, im.height * 52 // 100))  # side view fills the top half
        fit(clear_white(cutout(side)), (512, 256)).save(os.path.join(OUT, "weapons", h + ".png"))
    for name, f in MAPS.items():
        im = Image.open(os.path.join(SRC, f + ".jpg")).convert("RGB")
        im.thumbnail((1024, 1024), Image.LANCZOS)
        im.save(os.path.join(OUT, "maps", name + ".png"))
    print("done", OUT)


if __name__ == "__main__":
    main()
