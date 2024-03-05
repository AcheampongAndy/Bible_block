from flask import render_template, url_for, flash, redirect
from flask_block import app
from flask_block.forms import RegistrationForm, LoginForm
from flask_block.modules import User, Post

posts = [
        {
            'author': 'Acheapong Andrews',
            'title': 'Bible Post 1',
            'content': 'First content',
            'date_posted': 'March 02, 2018'
            },
        {
            'author': 'Dabla Eugenia',
            'title': 'Bible Post 2',
            'content': 'Second content',
            'date_posted': 'March 03, 2018'
            }

        ]

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=posts)

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.username.data == "AcheampongAndy" and form.password.data == "password":
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful, please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)
