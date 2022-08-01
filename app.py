#This document contains all the configuration,app routes and sqlalchemy coding
#Created By Zilong Wu on the 5th of July 2022

#Where data are imported from wefewf
from flask import Flask,render_template,request,redirect,flash,url_for,session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from formsubmissions import registerpageform

app = Flask(__name__) 

#Configurations
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sensor.db'
app.secret_key="__privatekey__"

#SQLALCHEMY OBJECTS
db = SQLAlchemy(app)

#User class will match to a table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), nullable=False)
    passWord = db.Column(db.String(100))
    email = db.Column(db.String(20))
    

    def __init__(self,name,password,email):
        self.name = name
        self.password = password
        self.email = email


    



#Home Page route
@app.route('/')
def defaultHome():
    return render_template('home.html')

#Login Page route
@app.route('/home')
def home():
    return render_template('home.html')

#Logins Page route user able to login after register or already registered before
@app.route('/logins', methods=['POST','GET'])
def logins():
    #If the request method equals to POST then check whether user login details in database if yes return their dashboard 
    if request.method == "POST":
        userName = request.form['name']
        session['name'] = userName
        passWord = request.form['passWord']
        session['passWord'] = passWord
        tracked_User = User.query.filter(User.name == userName and User.passWord == passWord).all()
        if tracked_User:
            return render_template("dashboard.html")
            #If not found user in databsase then will pop up message saying sorry have not found your login details, would you like to login
        else:
            if not tracked_User:
                return render_template("login.html")
    else:
        request.method == "GET"
        return render_template('login.html')

#Register route, user will have to register before being able to access the dashboard and having their own unique login details
@app.route('/register', methods=['POST','GET'])
def register():

    something =registerpageform()#making something = registerpageform

    #If method is POST
    if request.method == 'POST':
            if(request.form['name'] == '' and request.form['passWord'] == ''):
                flash("please fill out this particular field")
            if(request.form['name'] != '' and request.form['passWord'] != '' and request.form['email'] != ''):
                name = request.form["name"]
                passWord = request.form["passWord"]
                email = request.form['email']
                #Checked whether user registered same name before
                tracked_User = User.query.filter(User.name == name and User.passWord == passWord and User.email == email).all()
                #If it does it'll return user already exist page
                if tracked_User:
                    return render_template("404.html")
                else:
                    #If didn't found user
                    if not tracked_User:
                        #Information will be added into database
                        information = User(request.form['name'],request.form['passWord'],request.form['email'])
                        db.session.add(information)
                        db.session.commit()
                        return render_template("login.html")
    #If POST method is GET 
    elif request.method == 'GET':
        return render_template('register.html',form=something )

#Successionsubmission page returned if user logs on correctly
@app.route('/successformsubmission')
def successformsubmission():
    name = session.get('name',None)
    return render_template('successformsubmission.html')

#Classrooms route
@app.route('/classrooms')
def classrooms():
    return render_template("classrooms.html")




#Runs the route
if __name__=="__main__":
    db.create_all()
    app.run(debug=True)

