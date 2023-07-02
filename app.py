import os
import requests
import json

from flask import Flask, render_template, request, flash, redirect, session, g, abort
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError


from models import User, db, connect_db
from forms import UserAddForm, LoginForm, CommentForm
from secret import MQ_SECRET_KEY

CURR_USER_KEY = "curr_user"
MQ_API_BASE_URL = "https://www.mapquestapi.com/geocoding/v1"
key_mq = MQ_SECRET_KEY


app = Flask(__name__)
app.app_context().push()

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///movein_db'))


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.environ.get(
    'SECRET_KEY', "this is wildly unpredictable")
toolbar = DebugToolbarExtension(app)

connect_db(app)
db.create_all()


#########################################################################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = db.session.get(User, CURR_USER_KEY)

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

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


#########################################################################################################################
# Display location on Map via:
#  Mapquest API geocoding
# Google Maps API marker

def get_coords(address):
    res = requests.get(f"{MQ_API_BASE_URL}/address",
                       params={'key': key_mq, 'location': address})
    data = res.json()
    lat = data['results'][0]['locations'][0]['latLng']['lat']
    lng = data['results'][0]['locations'][0]['latLng']['lng']
    coords = {'lat': lat, 'lng': lng}
    return coords


@ app.route('/search')
def show_mapping():
    return render_template("address_form.html")


@ app.route('/api/geocode', methods=["POST"])
def locate_on_map():
    print(request)
    data = request.json
    location = data['address']
    coords = get_coords(location)
    print(coords)
    return coords


@ app.route('/api/map')
def show_map():

    return render_template("map.html")
