######################################
# author ben lawson <balawson@bu.edu>
# Edited by: Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

from plistlib import UID
import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask_login

#for current date
from datetime import date

#for image uploading
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'GL2005-11!gj'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users")
users = cursor.fetchall()

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from Users")
	return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT user_pass FROM Users WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd
	return user

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT user_pass FROM Users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('hello.html', message='Logged out')

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html')


#USER REGISTER"

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier

def isEmailUnique(email):
    	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True

@app.route("/register", methods=['GET'])
def register():
	return render_template('register.html', supress='True')

@app.route("/register", methods=['POST'])
def register_user():
	try:
		email=request.form.get('email')
		password=request.form.get('password')
	except:
		print("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	firstName = request.form.get('firstname')
	lastName = request.form.get('lastname')
	hometown = request.form.get('hometown') #Do i need these even if they are optional?
	gender = request.form.get('gender')
	dateOfBirth = '2000-05-31'
	cursor = conn.cursor()
	test =  isEmailUnique(email)
	if test:
		print(cursor.execute("INSERT INTO Users (email, user_pass, firstname, lastname, dob ,hometown, gender) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')".format(email, password, firstName, lastName, dateOfBirth, hometown, gender)))
		conn.commit()
		#log user in
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('hello.html', name=email, message='Account Created!') #do we keep name = email or change it to name=firstname?
	else:
		print("Email is not Unique")
		return flask.redirect(flask.url_for('register'))

#PROFILE PAGE

@app.route('/profile',methods =['GET'])
@flask_login.login_required
def protected():
    email = flask_login.current_user.id
    user_id = getUserIdFromEmail(email)
    print(flask_login.current_user.id)
    return render_template('profile.html', name=flask_login.current_user.id,
                           friends = getFriendsList(user_id),
						   photos = getUsersPhotos(user_id),
						   albums = getUsersAlbums(user_id),
                           message= "Here's your profile",
						   base64=base64)

#FRIENDS

def getFriendsList(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT friend_id FROM Friends WHERE user_id ='{0}'".format(uid))
    data = cursor.fetchall()
    fid = [item[0] for item in data]
    friends = []
    for names in fid:
        cursor.execute("SELECT firstname, lastname FROM Users WHERE user_id ='{0}'".format(names))
        friends.append(cursor.fetchone())
    friendsList = [((item[0], item[1])) for item in friends]
    return friendsList

@app.route('/friend', methods=['GET','POST'])
@flask_login.login_required
def friendsList():
    if request.method == "POST":
        fEmail = request.form.get('fEmail')
        fname = getUsernameFromEmail(fEmail)
        friend_id = getUserIdFromEmail(fEmail)
        return render_template('profile.html', fname = fname, friend_id = friend_id)
    else:
        return flask.redirect(url_for('protected'))
    
@app.route('/addFriend', methods=['POST'])
@flask_login.login_required
def add_friend():
    cursor = conn.cursor()
    friend_id = request.form.get('friend_id')
    user_id = getUserIdFromEmail(flask_login.current_user.id)
    cursor.execute("INSERT INTO Friends(user_id, friend_id) VALUES ('{0}','{1}')".format(user_id, friend_id))
    conn.commit()
    return flask.redirect(url_for('protected'))

#USER ACTIVITY

def userActivity():
    cursor = conn.cursor()
    cursor.execute("SELECT Users.user_id, (COUNT(picture_id) + COUNT(comments_id)) FROM Users, Pictures, Comments WHERE Users.user_id=Pictures.user_id AND (Comments.comment_owner=Users.user_id AND Comments.comment_photo_id <> Pictures.picture_id) GROUP BY Users.user_id ORDER BY COUNT(picture_id) DESC LIMIT 10")
    data = cursor.fetchall()
    print("data", data)
    data = [getUsernameFromEmail(item[0]) for item in data]
    return data

# TAG MANAGEMENT

#ALBUM MANAGEMENT

@app.route('/createAlbum', methods=['GET', 'POST'])
@flask_login.login_required
def createAlbum():
    if request.method == 'POST':
        user_id = getUserIdFromEmail(flask_login.current_user.id)
        print(user_id)
        album_name = request.form.get('album_name')
        albumDate = date.today()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Albums (album_name, albumDate, owner_id) VALUES ('{0}','{1}','{2}')".format(album_name, albumDate, user_id))
        conn.commit()
        return render_template('profile.html',name = flask_login.current_user.id, photos = getUsersPhotos(user_id), albums= getUsersAlbums(user_id), base64=base64)
    else:
        return flask.redirect(url_for('protected'))

def getAlbum(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT album_name FROM Albums WHERE user_id = '{0}'".format(uid))
    data = cursor.fetchall()
    albums = [item[0] for item in data]
    return albums

@app.route('/profile', methods=['GET', 'POST'])
@flask_login.login_required
def delete_album():
    if request.method == 'POST':
        user_id = getUserIdFromEmail(flask_login.current_user.id)
        album_id = request.form.get('album_id')
        print(album_id)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Pictures WHERE album_id= '{0}'".format(album_id))
        cursor.execute("DELETE FROM Albums WHERE albums_id = '{0}'".format(album_id))
        conn.commit()
        return flask.redirect(url_for('delete_album',name = flask_login.current_user.id, friends = getFriendsList(user_id),
						   photos = getUsersPhotos(user_id),
						   albums = getUsersAlbums(user_id),
						   comments = getAllComments(),
                           userActivity = userActivity(),
                           message= "Album Deleted!",
						   base64=base64))
    else:
        return flask.redirect(url_for('protected'))
    

#PICTURE MANAGEMENT

# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

    
@app.route('/photosInAlbum/<album_id>')   
def getAlbumPhotos(album_id):
    cursor = conn.cursor()
    cursor.execute("SELECT imgdata, caption FROM Pictures WHERE album_id = '{0}'".format(album_id))
    pictures = cursor.fetchall()
    return render_template("photosInAlbum.html", album_id = album_id, photos = pictures)

@app.route('/photosInAlbum',  methods =['GET','POST'])
@flask_login.login_required
def addPhotoToAlbum():
    if request.method =='POST':
        user_id = getUserIdFromEmail(flask_login.current_user.id)
        imgfile = request.files['photo']
        imgdata = imgfile.read()
        caption = request.form.get('caption')
        album_id = request.args.get('album_id')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Pictures (user_id, imgdata, caption, album_id) VALUES ('{0}', '{1}', '{2}', '{3}')".
                       format(user_id, imgdata, caption, album_id))  # not sure why the encoding for image isn't working
        conn.commit()
        return render_template('photosInAlbum.html',name = flask_login.current_user.id, 
						   photos = getAlbumPhotos(album_id), album_id = album_id,
                           message= "Photo uploaded!")
    else:
        return flask.redirect(url_for('protected'))

    
@app.route('/allPhotosFromTag/<tag>')
def getTagPhotos(tag):
	cursor = conn.cursor()
	cursor.execute("SELECT Tags.picture_id, imgdata, caption FROM Pictures, Tags WHERE Pictures.picture_id=Tags.picture_id AND Tags.tag = '{0}'".format(tag))
	pictures = cursor.fetchall()
	return render_template("allPhotosFromTag.html", tag=tag, photos=pictures)

@app.route('/allPhotosFromTag', methods =['GET', 'POST'])
def displayTagPhotos():
	if request.method =='POST':
		tag = request.args.get('tag')
		return render_template('allPhotosFromTag.html', tag=tag)
	else:
		return flask.redirect(url_for('protected'))

@app.route('/userPhotosFromTag/<tag>')
def getUserTagPhotos(tag):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT Tags.picture_id, imgdata, caption FROM Pictures, Tags WHERE Pictures.picture_id=Tags.picture_id AND Pictures.user_id='{0}' AND Tags.tag = '{1}'".format(uid, tag))
	pictures = cursor.fetchall()
	return render_template("userPhotosFromTag.html", tag=tag, photos=pictures)

@app.route('/userPhotosFromTag', methods =['GET', 'POST'])
@flask_login.login_required
def displayUserTagPhotos():
	if request.method =='POST':
		tag = request.args.get('tag')
		return render_template('userPhotosFromTag.html', tag=tag)
	else:
		return flask.redirect(url_for('protected'))

@app.route('/allPhotosFromPopTag/<tag>')
def getAllPopTagPhotos(tag):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT Tags.picture_id, imgdata, caption FROM Pictures, Tags WHERE Pictures.picture_id=Tags.picture_id AND Pictures.user_id='{0}' AND Tags.tag = '{1}'".format(uid, tag))
	pictures = cursor.fetchall()
	return render_template("allPhotosFromPopTag.html", tag=tag, photos=pictures)

@app.route('/allPhotosFromPopTag', methods =['GET', 'POST'])
@flask_login.login_required
def displayAllPopTagPhotos():
	if request.method =='POST':
		tag = request.args.get('tag')
		return render_template('allPhotosFromPopTag.html', tag=tag)
	else:
		return flask.redirect(url_for('protected'))

@app.route('/usersWhoLiked/<photo_id>')
def getUsersWhoLiked(photo_id):
	photo_id = request.args.get('photo_id')
	cursor = conn.cursor()
	cursor.execute("SELECT firstname FROM Users, Likes WHERE Likes.photo_id='{0}' and Users.user_id = Likes.user_id".format(photo_id))
	likers = cursor.fetchall()
	return render_template("usersWhoLiked.html", photo_id=photo_id, users=likers)

@app.route('/usersWhoLiked', methods =['GET', 'POST'])
@flask_login.login_required
def displayUsersWhoLiked():
	if request.method =='POST':
		photo_id = request.args.get('photo_id')
		return render_template('usersWhoLiked.html', photo_id=photo_id)
	else:
		return flask.redirect(url_for('protected'))

@app.route('/photoFromProfile/<photo_id>')
def getPhotoFromProfile(photo_id):
	photo_id = request.args.get('photo_id')
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id FROM Pictures WHERE Pictures.photo_id = '{0}'".format(photo_id))
	pictures = cursor.fetchall()
	return render_template("photoFromProfile.html", photo_id=photo_id, photos=pictures)

@app.route('/photoFromProfile', methods =['GET', 'POST'])
@flask_login.login_required
def displayPhotoFromProfile():
	if request.method =='POST':
		photo_id = request.args.get('photo_id')
		return render_template('photoFromProfile.html', photo_id=photo_id)
	else:
		return flask.redirect(url_for('protected'))

@app.route('/pictures', methods = ['GET'])
def pictures(album_name,email):
    user_id = getUserIdFromEmail(email)
    album_id = getAlbumId(album_name,user_id)
    cursor = conn.cursor()
    cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures WHERE user_id = user_id AND album_id = album_id ")
    data = cursor.fetchall()
    pictures =  [((item[0], str(item[2]))) for item in data]
    return pictures

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		tag = request.form.get('tag')
		# album_id = getAlbumId(album_name,uid)
		imgdata =imgfile.read()
		cursor = conn.cursor()
		cursor.execute('''INSERT INTO Pictures (user_id, imgdata, caption) VALUES (%s, %s, %s )''' ,(uid,imgdata,caption))
		conn.commit()
		photo_id = getPhotoId(uid, caption)
		print(photo_id)
		cursor = conn.cursor()
		cursor.execute('''INSERT INTO Tags (tag, picture_id) VALUES (%s, %s)''' ,(tag, photo_id))
		conn.commit()
		return render_template('photos.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getAllPhotos(), albums=getAllAlbums(), tags=getAllTags(), poptags=getPopularTags(), comments=getAllComments(), likes=getAllLikes(), base64=base64)
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		return render_template('upload.html')

@app.route('/profile', methods=['GET', 'POST'])
def delete_picture():
	if request.method == 'POST':
		picture_id = request.form.get('picture_id')
		user_id = getUserIdFromEmail(flask_login.current_user.id)
		cursor = conn.cursor()
		cursor.execute("DELETE FROM Pictures WHERE picture_id = '{0}'".format(picture_id))
		conn.commit()
		return flask.redirect(url_for('delete_picture', name=flask_login.current_user.id,
							friends = getFriendsList(user_id),
							photos = getUsersPhotos(user_id),
							albums = getUsersAlbums(user_id),
							comments=getAllComments(),
							userActivity = userActivity(),
							message= "Picture Deleted!",
							base64=base64))
	else:
		return flask.redirect(url_for('protected'))

def getUserIdFromEmail(email):
    cursor = conn.cursor()
    cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
    return cursor.fetchone()[0]

def getUsernameFromEmail(email):
    cursor = conn.cursor()
    print(cursor.execute("SELECT firstname FROM Users WHERE email = '{0}'".format(email)))
    return cursor.fetchone()[0]

def getUsersPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

def getUsersAlbums(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT albums_id, album_name FROM Albums WHERE owner_id='{0}'".format(uid))
	return cursor.fetchall()

def getUsersFromComment():
	comment = request.form.get('comment')
	cursor.execute("SELECT firstname,COUNT(*)  AS ccount FROM Comments, USERS WHERE comment_text='{0}' AND Comments.comment_owner=Users.user_id GROUP BY comment_owner ORDER BY ccount DESC".format(comment))
	return cursor.fetchall()

def getAllPhotos():
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption, user_id FROM Pictures")
	return cursor.fetchall()

def getAllAlbums():
	cursor = conn.cursor()
	cursor.execute("SELECT albums_id, album_name FROM Albums")
	return cursor.fetchall()

def getAllTags():
	cursor = conn.cursor()
	print(cursor.execute("SELECT DISTINCT tag FROM Tags"))
	return cursor.fetchall()

def getAllComments():
	cursor = conn.cursor()
	print(cursor.execute("SELECT comment_photo_id, comment_text, comment_date FROM Comments ORDER BY comment_date DESC"))
	return cursor.fetchall()

def getAllLikes():
	cursor = conn.cursor()
	print(cursor.execute("SELECT photo_id, COUNT(*) FROM Likes GROUP BY photo_id"))
	return cursor.fetchall()

def getLikesForPhoto():
	photo_id = request.args.get('photo_id')
	cursor = conn.cursor("SELECT firstname FROM Users, Likes WHERE Likes.photo_id='{0}' and Users.user_id = Likes.user_id".format(photo_id))

def getUsersPhotosComments(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT comments_id, comment_owner, comment_photo_id, comment_text, comment_date FROM Comments INNER JOIN Pictures ON Comments.comment_photo_id=Pictures.picture_id AND Pictures.user_id='{0}' GROUP BY Comments.comment_photo_id ORDER BY Comments.comment_date".format(uid))
	return cursor.fetchall()

def getPhotoId(uid, caption):
	cursor = conn.cursor()
	print(caption)
	cursor.execute("SELECT picture_id FROM Pictures WHERE Pictures.user_id='{0}' AND Pictures.caption='{1}'".format(uid, caption))
	return cursor.fetchone()[0]

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def getAllPhotosfromTag():
	tag = request.args.get('tag')
	cursor = conn.cursor()
	cursor.execute("SELECT Tags.picture_id, imgdata FROM Pictures, Tags WHERE Pictures.picture_id=Tags.picture_id AND Tags.tag = '{0}'".format(tag))
	return cursor.fetchall()

def getPopularTags():
	cursor = conn.cursor()
	cursor.execute("SELECT tag,COUNT(*)  AS ccount FROM Tags GROUP BY tag ORDER BY ccount DESC")
	return cursor.fetchall()

@flask_login.login_required
def getUserPhotosfromTag():
	tag = request.args.get('tag')
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT Tags.picture_id, imgdata FROM Pictures, Tags WHERE Pictures.picture_id=Tags.picture_id AND Pictures.user_id='{0}' AND Tags.tag = '{1}'".format(uid, tag))
	return cursor.fetchall()

def getAlbumId(album_name, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT albums_id FROM Albums WHERE album_name = '{0}' AND owner_id = '{1}'".format(album_name,user_id))
    return cursor.fetchone()[0]
    
@flask_login.login_required
@app.route("/photos")
def likePhoto():
	photoid = request.args.get('photoid')
	print(photoid)
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("INSERT INTO Likes (user_id, photo_id) VALUES (%s, %s)", (uid, photoid))
	conn.commit()
	return render_template('photos.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getAllPhotos(), albums=getAllAlbums(), tags=getAllTags(), poptags=getPopularTags(), comments=getAllComments(), likes=getAllLikes(), base64=base64)
	
@app.route("/photos", methods=['GET'])
def display_photos():
	print(getAllComments())
	print("uid", getUserIdFromEmail(flask_login.current_user.id))
	return render_template('photos.html', name=getUserIdFromEmail(flask_login.current_user.id), photos=getAllPhotos(), albums=getAllAlbums(), tags=getAllTags(), poptags=getPopularTags(), comments=getAllComments(), likes=getAllLikes(), base64=base64)

@app.route("/hello", methods=['POST'])
def add_comment():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	day = date.today()
	print("uid", uid)
	try:
		comment=request.form.get('comment')
		photoid=request.form.get('photoid')
	except:
		print("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('hello'))
	cursor = conn.cursor()
	test = True
	if test:
		print(cursor.execute("INSERT INTO Comments (comment_owner, comment_text, comment_date, comment_photo_id) VALUES (%s, %s, %s, %s)", (uid, comment, day, photoid)))
		conn.commit()
		print(getAllComments())
		return render_template('photos.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getAllPhotos(), albums=getAllAlbums(), tags=getAllTags(), comments=getAllComments(), likes=getAllLikes(), base64=base64)


#default page
@app.route("/", methods=['GET'])
def hello():
	return render_template('hello.html', message='Welcome to Photoshare')


if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)
