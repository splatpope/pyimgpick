import os, sys
from PIL import Image, UnidentifiedImageError

contents = os.walk(sys.argv[1])
for (root, folders, files) in contents:
    v = 0
    i = 0
    for image in files:
        try:
            img = Image.open(os.path.join(root, image))
            v += 1
        except UnidentifiedImageError:
            i += 1
            os.remove(os.path.join(root, image))


    print(v, i)