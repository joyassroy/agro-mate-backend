import urllib
import certifi
from functools import wraps
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, jsonify
)
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from model import predict_crop

app = Flask(__name__)
# IMPORTANT: Change this to a long, random, and secret string!
app.secret_key = "a-very-long-and-random-secret-key"

# --- Database Configuration ---
username = "joyassroy"
raw_password = "joyassroy171107"
password = urllib.parse.quote_plus(raw_password)
mongo_uri = (
    f"mongodb+srv://{username}:{password}"
    "@cluster0.txd1jyo.mongodb.net/cropdb"
    "?retryWrites=true&w=majority"
)
# Use certifi to provide SSL certificates for the database connection
mongo = PyMongo(app, uri=mongo_uri, tlsCAFile=certifi.where())
users = mongo.db.users


# --- Context Processor to make login status available to all templates ---
@app.context_processor
def inject_user():
    """Injects user login status into templates."""
    return dict(user_logged_in=('user_email' in session))


# --- Route Protection Decorator ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            flash("You must be logged in to view this page.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# --- Main Routes ---
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


# --- Service Route (Now Protected) ---
@app.route("/service", methods=["GET", "POST"])
@login_required  # Use the decorator to protect this route
def service():
    recommendation = None
    if request.method == "POST":
        data = {
            "nitrogen": float(request.form["nitrogen"]),
            "phosphorus": float(request.form["phosphorus"]),
            "potassium": float(request.form["potassium"]),
            "temperature": float(request.form["temperature"]),
            "humidity": float(request.form["humidity"]),
            "ph": float(request.form["ph"]),
            "rainfall": float(request.form["rainfall"]),
        }
        recommendation = predict_crop(data)
    return render_template("service.html", result=recommendation)


# --- Authentication Routes ---
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email'].lower()
        if users.find_one({'email': email}):
            flash('That email is already registered.', 'error')
            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(request.form['password'])
        users.insert_one({'email': email, 'password': hashed_password})
        flash('Signup successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # This handles the AJAX request from your login form
        data = request.get_json()
        email = data.get('email', '').lower()
        password = data.get('password', '')

        user = users.find_one({'email': email})

        if user and check_password_hash(user['password'], password):
            # Passwords match, store user in session
            session['user_email'] = user['email']
            return jsonify({'success': True})
        else:
            # Invalid credentials
            return jsonify({'success': False, 'message': 'Invalid email or password.'})

    # For GET request, just show the login page
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logs the user out by clearing the session."""
    session.pop('user_email', None)
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)