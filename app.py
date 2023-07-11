import os
import requests


from flask import Flask, g, render_template, request, flash, redirect, session, abort
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError


from models import db, connect_db, User, City, State, Location, Favorite
from forms import UserAddForm, LoginForm, CommentForm
from secret import MQ_SECRET_KEY, RM_SECRET_KEY


MQ_API_BASE_URL = "https://www.mapquestapi.com/geocoding/v1"
RM_API_BASE_URL = "https://realty-mole-property-api.p.rapidapi.com/zipCodes"
key_mq = MQ_SECRET_KEY
key_rm = RM_SECRET_KEY

CURR_USER_KEY = "curr_user"

app = Flask(__name__)
app.app_context().push()

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///moveIn'))


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = os.environ.get(
    'SECRET_KEY', "this is wildly unpredictable")
toolbar = DebugToolbarExtension(app)

connect_db(app)
# db.drop_all()


#########################################################################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    maybe_user_id = session.get(CURR_USER_KEY)
    if maybe_user_id is not None:
        g.user = db.session.get(User, maybe_user_id)
    # if CURR_USER_KEY in session:
    #     g.user = db.session.get(User, CURR_USER_KEY)
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
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,

            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/search")

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
            return redirect("/search")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""
    do_logout()
    flash("You've logged out of MoveIn.")

    return redirect('/login')
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


def get_realty_data(zip_code):
    res = requests.get(f"{RM_API_BASE_URL}/{zip_code}",
                       headers={'X-RapidAPI-Key': key_rm, 'X-RapidAPI-Host': "realty-mole-property-api.p.rapidapi.com", 'Content-Type': 'application/json'})
    data = res.json()
    return data


@ app.route('/search')
def show_mapping():

    return render_template("address_form.html")


@ app.route('/api/geocode', methods=["POST"])
def locate_on_map():
    data = request.json
    address = data['address']
    coords = get_coords(address)
    return coords


@app.route('/api/rental-data', methods=["POST"])
def get_rental_data():
    data = request.json
    zip_code = data['zipcode']
    rental_data = get_realty_data(zip_code)
    print(rental_data)
    return rental_data


# @ app.route('/search/favorite')
