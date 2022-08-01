#Using Flask-wtf using it to support data validation

from ipaddress import summarize_address_range
from tkinter import Label
from flask_wtf import FlaskForm
from wtforms import TextAreaField,PasswordField,IntegerField,TextAreaField,RadioField,SubmitField,StringField
from wtforms.validators import ValidationError, DataRequired, InputRequired,Length

#This is the class for registerpageform, users have the option to enter data below in the text box
class registerpageform(FlaskForm):
    email = StringField("Please enter your email", validators = [InputRequired(message="Please enter this field")])
    name = StringField("Please Create a Username",validators = [InputRequired(message="Please fill out this username field"), Length(min = 5,max =20)])
    passWord = PasswordField(label = " Choose a Passweord",validators = [InputRequired()])
    phoneNumber = IntegerField('Contact',validators=[InputRequired()])
    gender = RadioField(label = 'Gender',choices = ['Male','Female'])
    address = TextAreaField(label = "Address")
    age = IntegerField(label = "Age")
    submit = SubmitField("Send")

