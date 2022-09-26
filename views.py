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
)
from flask_login import (
    login_required,
    current_user,
)
from flask_login import UserMixin
from sqlalchemy.sql import func
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager


# Blueprints for different routes
auth = Blueprint("auth", __name__)
views = Blueprint("views", __name__)


# Database name
db = SQLAlchemy()
DB_NAME = "sensor.db"


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sensor.db'
    app.secret_key = "__privatekey__"
    db.init_app(app)
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    create_database(app)
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

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

        user = User.query.filter_by(email=email).first()
        if user:
            # Check sha256 password hashing
            if check_password_hash(user.password, password):
                flash("Logged in!", category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                # If password wrong it'll flash message
                flash('Password is incorrect.', category='error')
        else:
            flash('Email does not exist.', category='error')

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

        email_exists = User.query.filter_by(email=email).first()
        username_exists = User.query.filter_by(username=username).first()
        # If any information already exists then it'll flash error message
        if email_exists:
            flash('Email is already in use.', category='error')
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
            new_user = User(
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


# Models
# User Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    classrooms = db.relationship(
        'Classroom', backref='user', passive_deletes=True)
    comments = db.relationship('Comment', backref='user', passive_deletes=True)
    likes = db.relationship('Like', backref='user', passive_deletes=True)


# Classroom Model
class Classroom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    end_user = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete="CASCADE"), nullable=False)
    comments = db.relationship(
        'Comment', backref='classroom', passive_deletes=True)
    likes = db.relationship('Like', backref='classroom', passive_deletes=True)


# Comment Model
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(35), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    end_user = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete="CASCADE"), nullable=False)
    classroom_id = db.Column(db.Integer, db.ForeignKey(
        'classroom.id', ondelete="CASCADE"), nullable=False)


# Like Model
class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    end_user = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete="CASCADE"), nullable=False)
    classroom_id = db.Column(db.Integer, db.ForeignKey(
        'classroom.id', ondelete="CASCADE"), nullable=False)


# User View routes
@views.route("/")
@views.route("/home")
@login_required
def home():
    classrooms = Classroom.query.all()
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
            classroom = Classroom(text=text, end_user=current_user.id)
            db.session.add(classroom)
            db.session.commit()
            flash('Classroom created!', category='success')
            return redirect(url_for('views.home'))

    return render_template(
        'create_classroom.html', user=current_user)


# User delete classroom by id routes
@views.route("/delete-classroom/<id>")
@login_required
def delete_classroom(id):
    classroom = Classroom.query.filter_by(id=id).first()

    if not classroom:
        flash("Classroom does not exist.", category='error')
    elif current_user.id != classroom.id:
        flash(
            'You do not have permission to delete this classroom.',
            category='error')
    else:
        db.session.delete(classroom)
        db.session.commit()
        flash('Classroom deleted.', category='success')

    return redirect(url_for('views.home'))


@views.route("/classrooms/<username>")
@login_required
def classrooms(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash('No user with that username exists.', category='error')
        return redirect(url_for('views.home'))

    classrooms = user.classrooms
    return render_template(
        "classrooms.html",
        user=current_user,
        classrooms=classrooms,
        username=username)


@views.route("/create-comment/<classroom_id>", methods=['POST'])
@login_required
def create_comment(classroom_id):
    text = request.form.get('text')

    if not text:
        flash('Comment cannot be empty.', category='error')

    elif len(text) > 100:
            flash('Please make comment less than 100 characters', category='error')
    
    else:
        classroom = Classroom.query.filter_by(id=classroom_id)
        if classroom:
            comment = Comment(
                text=text, end_user=current_user.id, classroom_id=classroom_id)
            db.session.add(comment)
            db.session.commit()
        else:
            flash('classroom does not exist.', category='error')

    return redirect(url_for('views.home'))


@views.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()

    if not comment:
        flash(
            'Comment does not exist.', category='error')
    elif current_user.id != comment.end_user and current_user.id != comment.classroom.end_user:
        flash(
            'You do not have permission to delete this comment.',
            category='error')
    else:
        db.session.delete(comment)
        db.session.commit()

    return redirect(url_for('views.home'))


# Allows users to like classroom by their user_id
@views.route("/like-classroom/<classroom_id>", methods=['POST'])
@login_required
def like(classroom_id):
    classroom = Classroom.query.filter_by(id=classroom_id).first()
    like = Like.query.filter_by(
        end_user=current_user.id, classroom_id=classroom_id).first()

    if not classroom:
        return jsonify(
            {'error': 'classroom does not exist.'}, 400)
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(end_user=current_user.id, classroom_id=classroom_id)
        db.session.add(like)
        db.session.commit()

    return jsonify(
        {"likes": len(classroom.likes), "liked": current_user.id in map(lambda x: x.end_user, classroom.likes)})


@views.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html')


# Runs the website
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
