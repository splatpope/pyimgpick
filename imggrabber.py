import os
from PIL import Image, ImageTk, UnidentifiedImageError

class ImgFolder():
    def __init__(self, path, recursive=True, extensions=["jpg", "jpeg", "png", "bmp"]):
        self.paths = []
        for (root, dirs, files) in os.walk(path):
            for imgfile in files:
                if imgfile.split(".")[1] in extensions:
                    self.paths.append(os.path.join(root, imgfile))
        self.head = -1

    def curpath(self):
        return self.paths[self.head]

    def curimg(self):
        imgpath = self.curpath()
        try:
            return squash_image(Image.open(imgpath))
        except UnidentifiedImageError:
            print("Tried to load invalid image", imgpath)
            return None

    def next(self):
        self.head += 1
        if self.head >= len(self.paths):
            raise StopIteration
        return self.curimg()

    def prev(self):
        self.head -= 1
        if self.head < 0:
            self.head = 0
            raise StopIteration
        return self.curimg()
    
    def completed(self):
        return self.head == len(self.paths)

    def reset(self):
        self.head = 0

def load_image(path):
    return Image.open(path)

def load_tk_image(source):
    if isinstance(source, str):
        img = load_image(source)
    elif isinstance(source, Image.Image):
        img = source
    return ImageTk.PhotoImage(img)

def squash_image(img):
    if not isinstance(img, Image.Image):
        raise TypeError("Can only squash PIL image objects.")
    PYIMG_MAX_SIZE = 600
    ratio = img.height/img.width
    goodw = lambda: img.width <= PYIMG_MAX_SIZE
    goodh = lambda: img.height <= PYIMG_MAX_SIZE
    good = lambda: goodh() and goodw()
    while not good():
        print(f"h or w wrong : {img.width}, {img.height}")
        if not goodw():
            print("it was w")
            img = img.resize((PYIMG_MAX_SIZE, int(PYIMG_MAX_SIZE*ratio)), Image.ANTIALIAS)
            print(f"new shape : {img.width}, {img.height}")
        if not goodh():
            print("it was h")
            img = img.resize((int(PYIMG_MAX_SIZE/ratio), PYIMG_MAX_SIZE), Image.ANTIALIAS)
            print(f"new shape : {img.width}, {img.height}")
    return img
