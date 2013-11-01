#!/usr/bin/python3
# -*- coding: utf-8 -*- ex:set ts=4 sw=4:

import os
from flask import Flask, Blueprint, g, render_template, safe_join, send_from_directory, \
                  redirect, request, url_for, current_app
from PIL import Image

from dumbgal.database import TagStore

gallery = Blueprint('dumbgal', __name__, template_folder='templates')

@gallery.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(os.path.join(current_app.config.ROOT_DIR, 'static'), filename)

@gallery.route('/image/<path:filename>_<any(h,w,s):mode><int:size>.jpg')
def images(filename, size, mode):
    root_dir = current_app.config.ROOT_DIR
    orig_path = safe_join(os.path.join(root_dir, 'gallery'), filename + '.jpg')
    cache_path = safe_join(os.path.join(root_dir, 'cache'), filename + '_%s%d.jpg' % (mode, size))

    if not os.path.exists(cache_path) or os.stat(cache_path).st_mtime < os.stat(orig_path).st_mtime:
        img = Image.open(orig_path)

        if mode == 'h':
            t = (img.size[0], size)
        elif mode == 'w':
            t = (size, img.size[1])
        else:
            t = (size, size)

        img.thumbnail(t, Image.ANTIALIAS)
        img.save(cache_path, 'JPEG')

    return send_from_directory (os.path.join(root_dir, 'cache'), filename + '_%s%d.jpg' % (mode, size))

@gallery.route('/image/<path:filename>')
def image_pages(filename):
    tags = g.tagstore.list_tags_for_image(filename)
    all_tags = [tag['name'] for tag in g.tagstore.list_all_tags() if tag['name'] not in tags]
    return render_template('image_wrapper.html', filename=filename,
                           tags=tags, all_tags=all_tags)

@gallery.route('/image/<path:filename>/add-tag', methods=['POST'])
def add_tag(filename):
    g.tagstore.add_tag(filename, request.form['tag'])
    return redirect(url_for('dumbgal.image_pages', filename=filename))

@gallery.route('/tag/<tag>')
def tag_pages(tag):
    files = g.tagstore.list_images_for_tag(tag)
    return render_template('index.html', files=files, tags=[])

@gallery.route('/')
def serve_index():
    tags = g.tagstore.list_all_tags()
    files = g.tagstore.list_all_images()

    return render_template('index.html', files=files, tags=tags)


def setup_webapp(root_dir, debug=False):
    app = Flask(__name__)
    app.config.ROOT_DIR = root_dir
    app.debug = True

    @app.before_request
    def open_tagstore():
        if not hasattr(g, 'tagstore'):
            g.tagstore = TagStore(os.path.join(root_dir, 'meta.db'))

    @app.teardown_appcontext
    def close_tagstore(exception):
        if hasattr(g, 'tagstore'):
            g.tagstore.close()

    app.register_blueprint(gallery)
    return app
