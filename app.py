#our web app framework!

#you could also generate a skeleton from scratch via
#http://flask-appbuilder.readthedocs.io/en/latest/installation.html

#Generating HTML from within Python is not fun, and actually pretty cumbersome because you have to do the
#HTML escaping on your own to keep the application secure. Because of that Flask configures the Jinja2 template engine 
#for you automatically.
#requests are objects that flask handles (get set post, etc)
from flask import Flask, render_template,request,redirect,url_for
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
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor, CKEditorField
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
ckeditor = CKEditor(app)
db = SQLAlchemy(app)
#CRUD with CKeditor End here......



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
	x=x/255
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
	reference = StringField('reference')
	published = StringField('published')
	pdf = StringField('pdf')
	submit = SubmitField('submit')
@app.route('/home',methods=['GET','POST'])
def home():
	q=Post.query.all()
	return render_template('thesis.html', q=q)


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
		return redirect("/home")
		print("Successfully Updated")
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

#CRUD with CKeditor End here......

if __name__ == "__main__":
	#decide what port to run the app in
	#run the app locally on the givn port
	#optional if we want to run in debugging mode
	app.run(debug=True)