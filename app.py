#our web app framework!

#you could also generate a skeleton from scratch via
#http://flask-appbuilder.readthedocs.io/en/latest/installation.html

#Generating HTML from within Python is not fun, and actually pretty cumbersome because you have to do the
#HTML escaping on your own to keep the application secure. Because of that Flask configures the Jinja2 template engine 
#for you automatically.
#requests are objects that flask handles (get set post, etc)
from flask import Flask, render_template,request,redirect,url_for, send_from_directory,make_response
#scientific computing library for saving, reading, and resizing images
from scipy.misc import imsave, imread, imresize  #depriciated old version
#from cv2 import imread, resize
#for matrix math
import numpy as np
#for importing our keras model
import keras.models
#for regular expressions, saves time dealing with string data
import re

#system level operations (like loading files)
import sys 
#for reading operating system data
import os
#tell our app where our saved model is

#CRUD with CKeditor here......
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor, CKEditorField, upload_fail, upload_success
import pdfkit
#CRUD with CKeditor End here......



sys.path.append(os.path.abspath("./model"))
from load import * 

#base64
import base64

#initalize our flask app
app = Flask(__name__)


#CRUD with CKeditor here......
app.secret_key = 'azad-ali-969-md'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///thesis.db'  #4 slash for direct database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['CKEDITOR_SERVE_LOCAL'] = True
app.config['CKEDITOR_HEIGHT'] = 400
app.config['CKEDITOR_FILE_UPLOADER'] = 'upload'
# app.config['CKEDITOR_ENABLE_CSRF'] = True  # if you want to enable CSRF protect, uncomment this line
app.config['UPLOADED_PATH'] = os.path.join(basedir, 'uploads')
ckeditor = CKEditor(app)
db = SQLAlchemy(app)
#CRUD with CKeditor End here......


binary=0
#global vars for easy reusability
global model, graph
#initialize these variables
model, graph = init()
#decoding an image from base64 into raw representation
def convertImage(imgData1):
    imgstr = re.search(b'data:image/png;base64,(.*)', imgData1).group(1)
    with open('output.png', 'wb') as output:
        output.write(base64.b64decode(imgstr))

@app.route('/')
def index():
	#initModel()
	#render out pre-built HTML file right on the index page
	return render_template("index.html")

@app.route('/predict/',methods=['GET','POST'])
def predict():
	#whenever the predict method is called, we're going
	#to input the user drawn character as an image into the model
	#perform inference, and return the classification
	#get the raw data format of the image
	imgData = request.get_data()
	#print(imgData)
	#encode it into a suitable format
	convertImage(imgData)
	print ("debug")
	#read the image into memory
	x = imread('output.png',mode='L')
	#compute a bit-wise inversion so black becomes white and vice versa
	x = np.invert(x)
	#make it the right size
	x=imresize(x,(112,112))
	#imshow(x)
	#convert to a 4D tensor to feed into our model
	x = x.reshape(1,112,112,1)
	with open('bin_file.txt', 'w') as f:
		np.array(x, dtype=np.int16).tofile(f)
	x=x/255
	binary=[x for x in x]
	#with open('bin_file.txt', 'r') as f:
	#	lineArr=f.read().split('\n')
	#	if 'Sample Text' in lineArr:
	#		timeTaken = [s for s in lineArr if "Time Taken" in s]
	#		print (timeTaken[0])
	print ("debug2")
	#in our computation graph
	with graph.as_default():
		#perform the prediction
		print("1")
		print(x)
		out = model.predict(x)
		print(out)
		print(np.argmax(out,axis=1))
		print ("debug3")
		#convert the response to a string
		response = np.array_str(np.argmax(out,axis=1))
		return response	




#Extra (  MySelf )
#Myself
def bin():
	#print('in bin: ', x)
	print('In bin',binary)
	with open('bin_file.txt', 'wb') as f:
		np.array(binary, dtype=np.uint32).tofile(f)

@app.route('/binary',methods=['GET','POST'])
def binary():
	b=np.ravel(binary)
	print(b)
	return render_template('binary.html', b=b)
#CRUD with CKeditor here......
class Post(db.Model):  # database model class
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.Text)
	body = db.Column(db.Text)
	reference = db.Column(db.Text)
	published = db.Column(db.Text)
	pdf = db.Column(db.Text)

class PostForm(FlaskForm):  # form class
	title = StringField('title',validators=[DataRequired()])
	body = CKEditorField('body', validators=[DataRequired()])
	reference = CKEditorField('reference')
	published = SelectField(u'published', choices=[('IEEE', 'IEEE'), ('SPRINGER', 'SPRINGER'), ('ELSEVIER', 'ELSEVIER'), ('ACM', 'ACM'), ('Others', 'Others'),('Source', 'Source')])
	pdf = CKEditorField('pdf')
	submit = SubmitField('submit')
@app.route('/home',methods=['GET','POST'])
def home():
	q=Post.query.all()
	text = request.form.get('filter')
	if text == 'all':
		q=Post.query.all()
	else:
		q=Post.query.filter_by(published=text)
	allc=Post.query.count()
	iec=Post.query.filter_by(published='IEEE').count()
	sc=Post.query.filter_by(published='SPRINGER').count()
	elc=Post.query.filter_by(published='ELSEVIER').count()
	acmc=Post.query.filter_by(published='ACM').count()
	return render_template('thesis.html', q=q, allc=allc, iec=iec, sc=sc, elc=elc, acmc=acmc)


@app.route('/add',methods=['GET','POST'])
def add():
	form = PostForm()
	return render_template('add.html', form=form)


@app.route('/added',methods=['GET','POST'])
def added():
	form = PostForm()
	if form.validate_on_submit:  # create new post
		title = form.title.data
		body = form.body.data
		reference = form.reference.data
		published = form.published.data
		pdf = form.pdf.data
		post = Post(title=title, body=body, reference=reference, published=published, pdf=pdf)  # create record instance
		db.session.add(post)  # add to database session
		db.session.commit()  # commit change into database
		print("Post Added Successfully")      
		return redirect("/add")
	else:
		print("Not Valid")


@app.route('/files/<filename>')
def uploaded_files(filename):
    path = app.config['UPLOADED_PATH']
    return send_from_directory(path, filename)

import uuid

@app.route('/upload', methods=['POST'])
def upload():
    f = request.files.get('upload')
    extension = f.filename.split('.')[1].lower()
    if extension not in ['jpg', 'gif', 'png', 'jpeg']:
        return upload_fail(message='Image only!')
    unique_filename = str(uuid.uuid4())
    f.filename = unique_filename + '.' + extension
    f.save(os.path.join(app.config['UPLOADED_PATH'], f.filename))
    url = url_for('uploaded_files', filename=f.filename)
    return upload_success(url=url)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
	post = Post.query.get_or_404(id)  # query post in database
	form = PostForm()
	form.title.data=post.title
	form.body.data = post.body  # preset the form input data
	form.reference.data = post.reference
	form.published.data = post.published
	form.pdf.data = post.pdf
	return render_template('edit.html', form=form, id=id)

@app.route('/edited/<int:id>', methods=['GET', 'POST'])
def edited(id):
	post = Post.query.get_or_404(id)  # query post in database
	form = PostForm()
	if form.validate_on_submit:  # edit/update created post
		post.title = form.title.data  # set new value
		post.body = form.body.data  # set new value
		post.reference = form.reference.data
		post.published = form.published.data
		post.pdf = form.pdf.data
		db.session.commit()  # commit change into database
		print("Successfully Updated")      
		return redirect("/home")
	else:
		print("Not Valid")

@app.route('/delete/<id>', methods=['POST'])
def delete(id):
	print(id)
	q=Post.query.filter_by(id=id).first()
	print(q)
	db.session.delete(q)
	db.session.commit()
	print("Successfully deleted")
	return redirect("/home")

@app.route('/pdf')
def makepdf():
	options = {
    'page-size': 'Letter',
    'margin-top': '0.75in',
    'margin-right': '0.75in',
    'margin-bottom': '0.75in',
    'margin-left': '0.75in',
    'encoding': "UTF-8",
    'custom-header' : [
        ('Accept-Encoding', 'gzip')
    ],
    'no-outline': None
	}
	#css = 'https://maxcdn.bootstrapcdn.com/bootstrap/3.4.0/js/bootstrap.min.js'
	pdfkit.from_file('templates/thesis.html', 'out.pdf', options=options)
#CRUD with CKeditor End here......

if __name__ == "__main__":
	#decide what port to run the app in
	#run the app locally on the givn port
	#optional if we want to run in debugging mode
	app.run(debug=True)