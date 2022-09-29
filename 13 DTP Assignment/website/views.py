# This code was created by Zilong Wu on the 01/08/2022


# All imports
from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    jsonify,
    render_template_string
)
from flask_login import (
    login_required,
    current_user,
)
from flask_login import UserMixin
from sqlalchemy.sql import func
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
import models 


# Blueprints for different routes
auth = Blueprint("auth", __name__)
views = Blueprint("views", __name__)


# Database name
db = SQLAlchemy()
DB_NAME = "sensor.db"

import models 


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "helloworld"
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    db.init_app(app)

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    
    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return models.User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists("website/" + DB_NAME):
        db.create_all(app=app)
        print("Created database!")


# Authentication routes, for login and register
@auth.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Getting user email n password
        email = request.form.get("email")
        password = request.form.get("password")

        user = models.User.query.filter_by(email=email).first()
        if user:
            # Check sha256 password hashing
            if check_password_hash(user.password, password):
                flash("Welcome you are logged in!", category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                # If password wrong it'll flash message
                flash('Password is incorrect.', category='error')
        else:
            flash('Email does not exist. Please register if you havent signed up before', category='error')

    return render_template("login.html", user=current_user)


# User Signup route authentication - route
@auth.route("/sign-up", methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        # Requests for users email, username, password and password again
        email = request.form.get("email")
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        email_exists = models.User.query.filter_by(email=email).first()
        username_exists = models.User.query.filter_by(username=username).first()
        # If any information already exists then it'll flash error message
        if email_exists:
            flash('Email is already in use, please sign up using a different email or login using login page.', category='error')
        elif username_exists:
            flash('Username is already in use.', category='error')
        elif password1 != password2:
            flash('Password don\'t match!', category='error')
        elif len(username) < 2:
            flash('Username is too short.', category='error')
        elif len(username) > 12:
            flash('Please make username less than 12 characters', category='error')
        elif len(password1) < 6:
            flash('Password is too short.', category='error')
        elif len(password1) > 12: 
            flash('Password is too long, please shorten to less than 12 characters', category='error')
        elif len(email) < 4:
            flash("Email is invalid.", category='error')
        else:
            # If no user found password is hashed
            new_user = models.User(
                email=email,
                username=username,
                password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('User created!')
            return redirect(url_for('views.home'))

    return render_template("signup.html", user=current_user)


# User logout route
@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.home"))


# User View routes
@views.route("/")
@views.route("/home")
@login_required
def home():
    classrooms = models.Classroom.query.all()
    return render_template(
        "home.html", user=current_user, classrooms=classrooms)


# User are able to create a classroom
@views.route("/create-classroom", methods=['GET', 'POST'])
@login_required
def create_classroom():
    if request.method == "POST":
        text = request.form.get('text')

        if not text:
            flash('Classroom cannot be empty', category='error')


        elif len(text) > 100:
            flash('Please make comment less than 100 characters', category='error')

        else:
            classroom = models.Classroom(text=text, end_user=current_user.id)
            db.session.add(classroom)
            db.session.commit()
            flash('Classroom created!', category='success')
            return redirect(url_for('views.home'))

    return render_template(
        'create_classroom.html', user=current_user)


# User delete classroom by id routes
@views.route("/delete-classroom/<id>")
@login_required
def delete_classroom(id,classroom_id):
    classroom = models.Classroom.query.filter_by(id=id).first()

    if not classroom:
        flash("Classroom comment does not exist.", category='error')

    else:
        classroom = models.Classroom.query.filter_by(id=id).first()
        comment = models.Comment.query.filter_by(id=classroom_id).all()

        current_delete = db.session.merge(classroom,comment)
        
        db.session.delete(current_delete)
        db.session.commit()
        flash('Classroom comment deleted.', category='success')
    return redirect(url_for('views.home'))


@views.route("/classrooms/<username>")
@login_required
def classrooms(username):
    user = models.User.query.filter_by(username=username).first()

    if not user:
        flash('No user with that username exists.', category='error')
        return redirect(url_for('views.home'))

    classrooms = user.classrooms
    return render_template(
        "classrooms.html",
        user=current_user,
        classrooms=classrooms,
        username=username)


# Allows the user to create the comment 
@views.route("/create-comment/<classroom_id>", methods=['POST'])
@login_required
def create_comment(classroom_id):
    text = request.form.get('text')

    if not text:
        flash('Comment cannot be empty.', category='error')
    elif len(text) > 100:
            flash('Please make comment less than 100 characters', category='error')
    else:
        classroom = models.Classroom.query.filter_by(id=classroom_id)
        if classroom:
            comment = models.Comment(
                text=text, end_user=current_user.id, classroom_id=classroom_id)
            db.session.add(comment)
            db.session.commit()
            flash('Comment Successfully Added')
        else:
            flash('classroom does not exist.', category='error')
    return redirect(url_for('views.home'))


# Allows user to delete only their comment and no one elses
@views.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    comment = models.Comment.query.filter_by(id=comment_id).first()
    existing_object = db.session.merge(comment)

    if not comment:
        flash(
            'Comment does not exist.', category='error')
            
    elif current_user.id != comment.end_user and current_user.id != comment.classroom.end_user:
        flash(
            'You do not have permission to delete this comment.',
            category='error')
    else:
        db.session.delete(existing_object)
        db.session.commit()
        flash('Comment Successfully Deleted')

    return redirect(url_for('views.home'))


# Allows users to like classroom by their user_id
@views.route("/like-classroom/<classroom_id>", methods=['POST'])
@login_required
def like(classroom_id):
    classroom = models.Classroom.query.filter_by(id=classroom_id).first()
    like = models.Like.query.filter_by(
        end_user=current_user.id, classroom_id=classroom_id).first()
    
    if not classroom:
        return jsonify(
            {'error': 'classroom does not exist.'}, 400)

    elif like:
        current_like = db.session.merge(like)
        db.session.delete(current_like)
        db.session.commit()

    else:
        like = models.Like.query.filter_by(
        end_user=current_user.id, classroom_id=classroom_id).first()
        like = models.Like(end_user=current_user.id, classroom_id=classroom_id)
        db.session.add(like)
        db.session.commit()

    return jsonify(
        {"likes": len(classroom.likes), "liked": current_user.id in map(lambda x: x.end_user, classroom.likes)})


# Error handler for 404 error (This returns 404.html instead of standard 404.html)
@views.app_errorhandler(404)
def error404(error):
    return render_template('404.html', title='Error'), 404


# Runs the website
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)