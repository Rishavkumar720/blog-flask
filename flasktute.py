from flask import Flask, render_template,request,session,redirect
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import os
import math
import json
import pymysql.cursors
from werkzeug.utils import secure_filename


with open("config.json",'r') as c:
    params=json.load(c)["params"]
local_server=True
app=Flask(__name__,template_folder='template')
app.secret_key = 'super-secret-key'
app.config['UPLOAD_FOLDER']=params['upload_location']
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']



#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/blog.db'



db = SQLAlchemy(app)


class Contact(db.Model):

    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    phonenum = db.Column(db.String(12), nullable=False)
    mess = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)


class Post(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(25), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    name = db.Column(db.String(25), nullable=False)
    img_file=db.Column(db.String(25),nullable=False)








@app.route("/about")
def about():
    return render_template("about.html")
@app.route("/", methods=['GET'])

def home():
    post = Post.query.filter_by().all()
    last = math.ceil(len(post) / int(params['no_of_posts']))
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    post = post[(page - 1) * int(params['no_of_posts']):(page - 1) * int(params['no_of_posts']) + int( params['no_of_posts'])]
    if page == 1:
         prev = "#"
         next = "/?page=" + str(page + 1)
    elif page == last:
         prev = "/?page=" + str(page - 1)
         next = "#"
    else:
         prev = "/?page=" + str(page - 1)
         next = "/?page=" + str(page + 1)

    return render_template('home.html', params=params, post=post, prev=prev, next=next)

@app.route("/contact", methods = ['GET', 'POST'])
def contacts():
    if (request.method == 'POST'):

        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        mess = request.form.get('mess')

        entry = Contact(name=name, phonenum=phone, mess=mess, date= datetime.now(), email=email)

        db.session.add(entry)
        db.session.commit()


    return render_template('contact.html')

@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Post.query.filter_by(slug=post_slug).first()

    return render_template('post.html', params=params, post=post)

@app.route("/uploader",methods=["GETS","POST"])
def uploader():

    if (request.method=='POST'):
        f=request.files['file1']
        f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
        return "uploaded succesfully"

@app.route("/delete/<string:sno>", methods=['GET', 'POST'])
def delete(sno):
    post = Post.query.filter_by(sno=sno).first()
    db.session.delete(post)
    db.session.commit()
    return redirect('/dashboard')




@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit(sno):



    if request.method=='POST':
        box_title=request.form.get('title')
        slug=request.form.get('slug')
        img_file=request.form.get('img_file')
        content=request.form.get('content')
        name=request.form.get('name')
        date=request.form.get('date')


        if sno=="0":
            post=Post(title=box_title,slug=slug,img_file=img_file,content=content,name=name,date=date)
            db.session.add(post)
            db.session.commit()

        else:
             post=Post.query.filter_by(sno=sno).first()
             post.title=box_title
             post.slug=slug
             post.content=content
             post.img_file=img_file
             post.name=name
             post.date=date

             db.session.commit()
             return redirect('/edit/'+sno)



    post = Post.query.filter_by(sno=sno).first()

    return render_template("edit.html",params=params,sno=sno,post=post)









@app.route("/dashboard", methods=['GET','POST'])
def dashboard():
    if request.method == 'POST':
        if request.form['uname'] != params['admin_user'] or request.form['pass'] != params['admin_password']:
             return render_template('login.html',params=params)
        else:
            post = Post.query.all()
            return render_template('dashboard.html', params=params, post=post)
    return render_template('login.html', params=params)



    return render_template('login.html', params=params)


@app.route("/faculties")
def faculties():
    return render_template("faculties.html")





app.run(debug=True)