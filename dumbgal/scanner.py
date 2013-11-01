#!/usr/bin/python3
# -*- coding: utf-8 -*- ex:set ts=4 sw=4:

import os
from PIL import Image

from dumbgal.database import TagStore

def scan_directory(root_dir):
    store = TagStore(os.path.join(root_dir, 'meta.db'))
    gallery_dir = os.path.join(root_dir, 'gallery')

    existing_images = store.list_all_images()

    for filename in os.listdir(gallery_dir):
        imgname = os.path.splitext(filename)[0]

        img = Image.open(os.path.join(gallery_dir, filename))
        store.add_image(imgname, img.size[0], img.size[1])
        print("%s added." % imgname)
