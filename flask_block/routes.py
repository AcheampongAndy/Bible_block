import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flask_block import app, db, bcrypt, mail
from sqlalchemy.orm import joinedload
from flask_block.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, RequestResetForm, ResetPasswordForm
from flask_block.modules import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

# Define the route for the home page
@app.route("/")
@app.route("/home")
def home():
    # Get the 'page' parameter from the request (default to 1 if not present)
    page = request.args.get('page', 1, type=int)
    
    # Query posts from the database with pagination and order by date
    posts = Post.query.options(joinedload(Post.author)).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)

    # Render the home page template with the retrieved posts
    return render_template('home.html', posts=posts)

# Define the route for the about page
@app.route("/about")
def about():
    # Render the about page template
    return render_template('about.html', title='About')

# Define the route for user registration
@app.route("/register", methods=['GET', 'POST'])
def register():
    # Check if the user is already authenticated and redirect to home if true
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    # Create a RegistrationForm instance
    form = RegistrationForm()

    # Validate the form on submission
    if form.validate_on_submit():
        # Generate hashed password and create a new user
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        
        # Add the new user to the database
        db.session.add(user)
        db.session.commit()
        
        # Flash a success message and redirect to login page
        flash('Your account has been created! You can now log in', 'success')
        return redirect(url_for('login'))
    
    # Render the registration page with the form
    return render_template('register.html', title='Register', form=form)

# Define the route for user login
@app.route("/login", methods=['GET', 'POST'])
def login():
    # Check if the user is already authenticated and redirect to home if true
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    # Create a LoginForm instance
    form = LoginForm()

    # Validate the form on submission
    if form.validate_on_submit():
        # Query the user from the database and check the password
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # Log in the user and redirect to the next page or home
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            # Flash an error message if login is unsuccessful
            flash('Login Unsuccessful. Please check username and password', 'danger')
    
    # Render the login page with the form
    return render_template('login.html', title='Login', form=form)

# Define the route for user logout
@app.route("/logout")
def logout():
    # Log out the user and redirect to home
    logout_user()
    return redirect(url_for('home'))

# Define a function to save the uploaded profile picture
def save_picture(form_picture):
    # Generate a random hex filename and get the file extension
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    
    # Set the file path to save the picture
    picture_path = os.path.join(app.root_path, 'static/profiles', picture_fn)

    # Open the image, resize it, and save it to the specified path
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    # Return the filename
    return picture_fn

# Define the route for the user account settings
@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    # Create an UpdateAccountForm instance
    form = UpdateAccountForm()

    # Validate the form on submission
    if form.validate_on_submit():
        if form.picture.data:
            # Save the new profile picture if provided
            picture_file = save_picture(form.picture.data)
            user = User.query.filter_by(username=current_user.username).first()
            user.image_file = picture_file
            db.session.commit()
        
        # Update the user's username and email
        user = User.query.filter_by(username=current_user.username).first()
        user.username = form.username.data
        user.email = form.email.data
        db.session.commit()
        
        # Flash a success message and redirect to the account page
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    
    # Populate the form with current user data for a GET request
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    
    # Get the URL for the user's profile picture
    image_file = url_for('static', filename='profiles/' + current_user.image_file)
    
    # Render the account page with the form and profile picture URL
    return render_template('account.html', title='Account', image_file=image_file, form=form)

# Define the route for creating a new post
@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    # Create a PostForm instance
    form = PostForm()

    # Validate the form on submission
    if form.validate_on_submit():
        # Create a new post and add it to the database
        user = User.query.filter_by(username=current_user.username).first()
        post = Post(title=form.title.data, content=form.content.data, user_id=user.id)
        db.session.add(post)
        db.session.commit()
        
        # Flash a success message and redirect to the home page
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    
    # Render the create post page with the form
    return render_template('create_post.html', title='New Post', form=form, legend='New Post')

# Define the route for viewing a single post
@app.route("/post/<int:post_id>")
def post(post_id):
    # Get the post with the specified ID from the database
    post = Post.query.options(joinedload(Post.author)).get_or_404(post_id)

    # Render the post page with the retrieved post
    return render_template('post.html', title=post.title, post=post)

# Define the route for updating an existing post
@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    # Get the post with the specified ID from the database
    post = Post.query.options(joinedload(Post.author)).get_or_404(post_id)
    
    # Check if the current user is the author of the post
    if post.author != current_user:
        abort(403)

    # Create a PostForm instance
    form = PostForm()

    # Validate the form on submission
    if form.validate_on_submit():
        # Update the post title and content in the database
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        
        # Flash a success message and redirect to the updated post
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    
    # Populate the form with current post data for a GET request
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    
    # Render the create post page with the form
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')

# Define the route for deleting a post
@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    # Get the post with the specified ID from the database
    post = Post.query.options(joinedload(Post.author)).get_or_404(post_id)
    
    # Check if the current user is the author of the post
    if post.author != current_user:
        abort(403)
    
    # Delete the post from the database
    db.session.delete(post)
    db.session.commit()
    
    # Flash a success message and redirect to the home page
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))

# Define the route for viewing posts by a specific user
@app.route("/user/<string:username>")
def user_posts(username):
    # Get the 'page' parameter from the request (default to 1 if not present)
    page = request.args.get('page', 1, type=int)
    
    # Query the user from the database
    user = User.query.filter_by(username=username).first_or_404()
    
    # Query posts by the user with pagination and order by date
    posts = Post.query.options(joinedload(Post.author)).filter_by(author=user)\
            .order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)

    # Render the user posts page with the retrieved posts and user
    return render_template('user_posts.html', posts=posts, user=user)

# Define a function to send a password reset email
def send_reset_email(user):
    # Generate a reset token and create a password reset email message
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    # Send the email
    mail.send(msg)

# Define the route for requesting a password reset
@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    # Check if the user is already authenticated and redirect to home if true
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    # Create a RequestResetForm instance
    form = RequestResetForm()

    # Validate the form on submission
    if form.validate_on_submit():
        # Query the user from the database and send a reset email
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    
    # Render the reset request page with the form
    return render_template('reset_request.html', title='Reset Password', form=form)

# Define the route for resetting the password using a token
@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    # Check if the user is already authenticated and redirect to home if true
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    # Verify the reset token and get the associated user
    user = User.verify_reset_token(token)
    
    # If the token is invalid or expired, flash a warning and redirect to reset_request
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    
    # Create a ResetPasswordForm instance
    form = ResetPasswordForm()

    # Validate the form on submission
    if form.validate_on_submit():
        # Update the user's password in the database
        user = User.query.filter_by(id=user.id).first()
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        
        # Flash a success message and redirect to the login page
        flash('Your password has been updated! You can now log in', 'success')
        return redirect(url_for('login'))
    
    # Render the reset token page with the form
    return render_template('reset_token.html', title='Reset Password', form=form)
