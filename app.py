#!/usr/bin/env python
# coding='utf-8'

import os
from flask import Flask, redirect, render_template, session, escape, url_for, flash
from werkzeug.contrib.fixers import  ProxyFix


app = Flask(__name__)
app.debug = True

photo_dir = 'static/photo/'

@app.route("/")
def start():
    return render_template('page.html', gals = read_photos_from_disk() )

def read_photos_from_disk():
    gals = []
    for dir in os.listdir(photo_dir):
        gallery = {}
        if not os.path.isfile(photo_dir + dir):
            gallery['name'] = dir
            gallery['description'] = ''
            gallery['captions'] = ''
            gallery['photos'] = []
            for f in os.listdir(photo_dir + dir):
                if os.path.isfile(photo_dir + dir + '/' + f) and f == 'descr.txt':
                    with open(photo_dir + dir + '/' + f) as f1:
                        gallery['description'] = f1.read()
                if os.path.isfile(photo_dir + dir + '/' + f) and f == 'name.txt':
                    with open(photo_dir + dir + '/' + f) as f1:
                        gallery['name'] = f1.read()
                if os.path.isfile(photo_dir + dir + '/' + f) and f == 'captions.txt':
                    with open(photo_dir + dir + '/' + f) as f1:
                        gallery['captions'] = f1.read()

                if os.path.isfile(photo_dir + dir + '/' + f) and f.endswith(".jpg"):
                    gallery['photos'].append('/' + photo_dir + dir + '/' + f)
        if gallery:
             gals.append(gallery)

    return gals




app.wsgi_app = ProxyFix(app.wsgi_app)
app.secret_key = 'A0Zr98j/sds43edsX R~XHH!jmN]LWX/,?RT'

if __name__ == "__main__":
    app.run(host='0.0.0.0')






