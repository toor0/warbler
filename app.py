import os
from flask import Flask, render_template, request, flash, redirect, session, g, jsonify
# from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from forms import UserAddForm, LoginForm, MessageForm, EditUserForm, PasswordForm
from models import db, connect_db, User, Message, Like
from functools import wraps

CURR_USER_KEY = "curr_user"
app = Flask(__name__)
# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgres:///warbler'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
# toolbar = DebugToolbarExtension(app)

connect_db(app)


##############################################################################
# Check if logged in decorator


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            flash("Access unauthorized.", "danger")
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None


def do_login(user):
    """Log in user."""
    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.
    Create new user and add to DB. Redirect to home page.
    If form not valid, present form.
    If the there already is a user with that username: flash message
    and re-present form.
    """
    form = UserAddForm()
    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()
        except IntegrityError as e:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)
        do_login(user)
        return redirect("/")
    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)
        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")
        flash("Invalid credentials.", 'danger')
    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""
    do_logout()
    flash("Logged out successfully")
    return redirect("/login")


##############################################################################
# General user routes:


@app.route('/users')
def list_users():
    """Page with listing of users.
    Can take a 'q' param in querystring to search by that username.
    """
    search = request.args.get('q')
    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f"%{search}%")).all()
    return render_template('users/index.html', users=users)


@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show user profile."""
    user = User.query.get_or_404(user_id)
    # snagging messages in order from the database
    # user.messages won't be in order by default
    messages = (Message
                .query
                .filter(Message.user_id == user_id)
                .order_by(Message.timestamp.desc())
                .limit(100)
                .all())
    return render_template('users/show.html', user=user, messages=messages)


@app.route('/users/<int:user_id>/following')
@login_required
def show_following(user_id):
    """Show list of people this user is following."""
    user = User.query.get_or_404(user_id)
    return render_template('users/following.html', user=user)


@app.route('/users/<int:user_id>/followers')
@login_required
def users_followers(user_id):
    """Show list of followers of this user."""
    user = User.query.get_or_404(user_id)
    return render_template('users/followers.html', user=user)


@app.route('/users/follow/<int:follow_id>', methods=['POST'])
@login_required
def add_follow(follow_id):
    """Add a follow for the currently-logged-in user."""
    followee = User.query.get_or_404(follow_id)
    g.user.following.append(followee)
    db.session.commit()
    return redirect(f"/users/{g.user.id}/following")


@app.route('/users/stop-following/<int:follow_id>', methods=['POST'])
@login_required
def stop_following(follow_id):
    """Have currently-logged-in-user stop following this user."""
    followee = User.query.get(follow_id)
    g.user.following.remove(followee)
    db.session.commit()
    return redirect(f"/users/{g.user.id}/following")


@app.route('/users/<int:user_id>/likes', methods=["GET"])
@login_required
def messages_liked_list(user_id):
    """Show page displaying messages a user has liked"""
    return render_template('users/liked-messages.html', user=g.user)


@app.route('/users/profile', methods=["GET", "POST"])
@login_required
def profile():
    """Update profile for current user."""
    form = EditUserForm(obj=g.user)
    if form.validate_on_submit():
        user = User.authenticate(g.user.username,
                                 form.password.data)
        if user:
            user.username = form.username.data
            user.email = form.email.data
            user.image_url = form.image_url.data
            user.header_image_url = form.header_image_url.data
            user.bio = form.bio.data
            db.session.add(user)
            db.session.commit()
            flash(f"{user.username} your changes were successful!")
            return redirect(f"/users/{user.id}")
        flash("Invalid credentials.", 'danger')
    return render_template('users/edit.html', form=form)


@app.route('/users/password', methods=["GET", "POST"])
@login_required
def new_pass():
    """ """
    form = PasswordForm()
    if form.validate_on_submit():
        user = User.authenticate(g.user.username,
                                 form.old_pwd.data)
        if user:
            user.password = user.new_pwd(form.new_pwd.data)
        db.session.commit()
        flash("Password updated!", 'success')
        return redirect(f"users/{user.id}")
    return render_template('users/password.html', form=form)


@app.route('/users/delete', methods=["POST"])
@login_required
def delete_user():
    """Delete user."""
    do_logout()
    db.session.delete(g.user)
    db.session.commit()
    return redirect("/signup")


##############################################################################
# Messages routes:


@app.route('/messages/new', methods=["POST"])
@login_required
def messages_add():
    """ """
    msg = Message(text=request.form["text"])
    g.user.messages.append(msg)
    db.session.commit()
    referrer = request.headers.get("Referer")
    if referrer != f"/users/{g.user.id}":
        return f"/users/{g.user.id}"


@app.route('/messages/<int:message_id>', methods=["GET"])
def messages_show(message_id):
    """Show a message."""
    msg = Message.query.get(message_id)
    return render_template('messages/show.html', message=msg)


@app.route('/messages/<int:message_id>/delete', methods=["POST"])
@login_required
def messages_destroy(message_id):
    """Delete a message."""
    msg = Message.query.get(message_id)
    db.session.delete(msg)
    db.session.commit()
    return redirect(f"/users/{g.user.id}")


@app.route('/messages/<int:message_id>/like', methods=["POST"])
@login_required
def messages_like(message_id):
    """Logic for liking a message"""
    like = Like(message_id=message_id, user_id=g.user.id)
    db.session.add(like)
    db.session.commit()
    message = Message.query.get(message_id)
    amount = len(message.likes)
    return jsonify(amount)


@app.route('/messages/<int:message_id>/unlike', methods=["POST"])
@login_required
def messages_un_like(message_id):
    """Logic for unliking a message"""
    likes = (Like
             .query
             .filter(Like.user_id == g.user.id)
             .filter(Like.message_id == message_id)
             .first())
    db.session.delete(likes)
    db.session.commit()
    message = Message.query.get(message_id)
    amount = len(message.likes)
    return jsonify(amount)


##############################################################################
# Homepage and error pages


@app.route('/')
def homepage():
    """Show homepage:
    - anon users: no messages
    - logged in: 100 most recent messages of followees
    """
    if g.user:
        ids = [user.id for user in g.user.following]
        messages = (Message
                    .query
                    .filter(Message.user_id.in_(ids))
                    .order_by(Message.timestamp.desc())
                    .limit(100)
                    .all())
        return render_template('home.html', messages=messages, user=g.user)
    else:
        return render_template('home-anon.html')


@app.errorhandler(404)
def show_404_page(err):
    return render_template("404.html")


##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask


@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""
    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req
