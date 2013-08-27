#!/usr/bin/env python
# coding: utf-8
#
#

import os
from flask import Flask, render_template, url_for, redirect, request, session
from werkzeug.contrib.fixers import  ProxyFix
import redis

app = Flask(__name__)
app.debug = True

photo_dir = 'static/photo/'


@app.route('/')
def start():
    editable = ''
    if 'isAdmin' in session and session['isAdmin']:
         editable = 'editText'
    return render_template('index.html', gals = read_photos_from_disk(), edit=editable, msg='' )

@app.route('/index')
def index():
    return redirect(url_for('start'))

@app.route('/about')
def about():
    about_txt = ''
    f = photo_dir  + 'about.txt'
    if os.path.exists(f) and os.path.isfile(f):
        with open(f) as f1:
            about_txt = f1.read()
    return render_template('text.html', content =  about_txt )


@app.route('/contacts')
def contacts():
    contacts_txt = ''
    f = photo_dir  + 'contacts.txt'
    if os.path.exists(f) and os.path.isfile(f):
        with open(f) as f1:
            contacts_txt = f1.read()
    return render_template('text.html', content =  contacts_txt )

@app.route('/works')
def works():
    return redirect(url_for('start'))

@app.route('/works/<gal_id>')
def show_gallery(gal_id):
    editable = ''
    if 'isAdmin' in session and session['isAdmin']:
         editable = 'editText'
    return render_template('works.html', gal_id = gal_id, gallery_name =get_gallery_name(gal_id) , gallery_description = get_gallery_description(gal_id), photos = read_gallery_from_disk(gal_id), edit=editable, msg='' )

def get_gallery_name(gal_id):
    r = redis.StrictRedis(host="localhost", port=6379, db=1)
    gal_name = r.get('name:'+gal_id)
    if gal_name:
        return gal_name
    else:
        return gal_id

def get_gallery_description(gal_id):
    r = redis.StrictRedis(host="localhost", port=6379, db=1)
    gallery_description = r.get('description:'+gal_id)
    if gallery_description:
        return gallery_description
    else:
        return gal_id + ' : no description'


@app.route('/login', methods=['POST', 'GET'])
def login():
    error = ''
    for f in os.listdir(photo_dir):
        if f == 'key.txt':
            with open(photo_dir  + 'key.txt') as f1:
                stored_key = f1.read().strip()

    if request.method == 'POST':
        if stored_key == request.form['key']:
            session['isAdmin'] = True
            return redirect(url_for('start'))
        else:
            error = 'Invalid key'
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    if 'isAdmin' in session and session['isAdmin']:
        error = 'Already logged in!'
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    if 'isAdmin' in session and session['isAdmin']:
        session.pop('isAdmin', None)
    return redirect(url_for('start'))


@app.route('/edit/<type>/<val1>')
def edit_comment(type,val1):
    r = redis.StrictRedis(host="localhost",port=6379,db=1)
    text = val1
    if text == " ":
        text = 'empty'
    r.set(type + ':' + (val1.split("&")[:-1])[0].strip(), (val1.split("&")[:-1])[1].strip())
    return  (val1.split("&")[:-1])[1].strip()


def read_gallery_from_disk(gal_id):
    r = redis.StrictRedis(host="localhost",port=6379,db=1)
    photos = []
    for f in os.listdir(photo_dir + gal_id):
        if os.path.isfile(photo_dir + gal_id + '/' + f) and f.endswith(".jpg"):
            photo = {}
            photo['id'] = '/' + photo_dir + gal_id + '/' + f
            photo['caption'] = r.get('caption:'+ gal_id+ ':'+ f)
            if not photo['caption']:
                photo['caption'] = u'без названия'

            if photo:
                photos.append(photo)

    return photos


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
            gallery['captions'] = []
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






