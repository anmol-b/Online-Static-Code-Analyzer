import hashlib
import pymongo
from flask import Flask, render_template, request, session, url_for
import datetime
import tempfile
import os
from werkzeug import secure_filename


app = Flask(__name__)
app.secret_key = "5ceD0ff"
app.config['UPLOAD_FOLDER'] = '/uploads/'

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

userIndex = "users"

db_user = '' #username
db_pass = '' #password


app.config['ALLOWED_EXTENSIONS'] = set(['py']) #Only Pyhton files tobe excepted.

#Validate file extension.
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


# Connecting to MongoDB
def createDBConn():
    client = pymongo.MongoClient('mongodb://'+db_user+':'+db_pass+'@########.mlab.com:######/securedb')#MongoDB URI
    db = client.securedb
    return client, db

@app.route('/')
def init():
  return render_template("index.html")


@app.route('/login', methods=['POST'])
def login_user():
    if request.form['modeSelection'] != "":
        t1 = datetime.datetime.now()
        if request.form['modeSelection'] == 'New user Register here':
            return render_template('register.html')
        else:
            if (request.form['loginid'] != "") and (request.form['password'] != ""):
                loginid = request.form['loginid']
                getmd5 = hashlib.md5(request.form['password'].encode()) #Generate MD5 of the password and then store it.
                password = getmd5.hexdigest()
                client, db = createDBConn()
                userDirectory = db[userIndex]
                userDict = {}
                userDict['loginid'] = loginid
                userDict['password'] = password
                user = userDirectory.find_one(userDict)
                client.close()
                if user is not None:
                    session['loginid'] = loginid
                    session['userid'] = str(user['_id'])
                    t2 = datetime.datetime.now()
                    time_login = str(t2-t1)
                    return render_template('home.html', loginid=loginid, msg="Time to login : "+time_login)
                else:
                    return render_template('index.html')
            else:
                return "<div align='center'>One of the field had invalid text. Please click submit to go to login page.<form action='/'><input type='submit' value='Go Back'></form></div>"
    else:
        return render_template("index.html")

@app.route('/logout', methods=['POST'])
def logout_user():
    session.clear
    return render_template("index.html")

@app.route('/register_user', methods=['POST'])
def register_user():
    if ((request.form['name'] != "") and (request.form['loginid'] != "") and (request.form['password'] != "")):
        name = request.form['name']
        loginid = request.form['loginid']
        print (request.form['password'])
        getmd5 = hashlib.md5(request.form['password'].encode())
        #getmd5.update(request.form['password'].encode('utf-8'))
        password = getmd5.hexdigest()
        print (password)
        loginRegister = {}
        loginRegister['name'] = name
        loginRegister['loginid'] = loginid
        loginRegister['password'] = password

        client, db = createDBConn()

        userDirectory = db[userIndex]

        userDirectory.insert(loginRegister)
        client.close()
        return render_template('index.html')
    else:
        return "<div align='center'>One of the field had invalid text. Please click submit to go to login page.<form action='/'><input type='submit' value='Go Back'></form></div>"


@app.route('/upload', methods=['POST'])
def upload():
    print ("in Uploads")
    print ("file to be fetched.")
    file = request.files['fileToUpload']
    #if file and allowed_file(file.filename):

    print ("Valid File :)")

    target = os.path.join(APP_ROOT, 'uploads/')

    if not os.path.isdir(target):
        print (target)
        os.mkdir(target)

    filename = secure_filename(file.filename)
    destination =  "".join([target, filename])
    file.save(destination)
    running_command = "pylint " + destination + " > " + target + "analysed_" + filename.rsplit('.', 1)[0] + str(session['loginid'])  + ".txt"
    result = os.system(running_command)
    f = open(target + "analysed_" + filename.rsplit('.', 1)[0] + ".txt", 'r')
    content = f.read()
    return "<b>Results are :</b> \n \n" + content

if __name__ == '__main__':
  app.run()