#!/usr/bin/env python
# coding='utf-8'

import os
from flask import Flask, render_template
from werkzeug.contrib.fixers import  ProxyFix
import redis

app = Flask(__name__)
app.debug = True

photo_dir = 'static/photo/'

@app.route('/')
def start():
    return render_template('page.html', gals = read_photos_from_disk(), edit='', msg='' )

@app.route('/admin/<key>')
def start_admin(key):
    for f in os.listdir(photo_dir):
        if f == 'key.txt':
            with open(photo_dir  + 'key.txt') as f1:
                stored_key = f1.read().strip()
    editable ='tt'
    error = 'ok'
    if key == stored_key:
        editable = 'editText'
    else:
         error = key + ' != ' + stored_key

    return render_template('page.html', gals = read_photos_from_disk(), edit = editable , msg=error)



@app.route('/edit/<type>/<val1>')
def edit_comment(type,val1):
    r = redis.StrictRedis(host="localhost",port=6379,db=1)
    text = val1
    if text == " ":
        text = 'empty'
    r.set(type + ':' + (val1.split("&")[:-1])[0].strip(), (val1.split("&")[:-1])[1].strip())
    return  (val1.split("&")[:-1])[1].strip()



def read_photos_from_disk():
    r = redis.StrictRedis(host="localhost",port=6379,db=1)
    gals = []
    for dir in os.listdir(photo_dir):
        gallery = {}
        if not os.path.isfile(photo_dir + dir):
            gallery['id'] = dir
            gallery['name'] = dir
            gallery['description'] = 'empty'
            gallery['photos'] = []
            for f in os.listdir(photo_dir + dir):
                gallery_name = r.get('name:'+dir)
                if gallery_name:
                    gallery['name'] = gallery_name
                gallery_description = r.get('description:'+dir)
                if gallery_description:
                    gallery['description'] = gallery_description

                if os.path.isfile(photo_dir + dir + '/' + f) and f.endswith(".jpg"):
                    gallery['photos'].append('/' + photo_dir + dir + '/' + f)
        if gallery:
             gals.append(gallery)

    return gals




app.wsgi_app = ProxyFix(app.wsgi_app)
app.secret_key = 'A0Zr98j/sds43edsX R~XHH!jmN]LWX/,?RT'

if __name__ == "__main__":
    app.run(host='0.0.0.0')






