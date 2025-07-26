import urllib
import certifi
from functools import wraps
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, jsonify
)
import datetime
import pytz
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from model import predict_crop

# ==============================================================================
# >> REPLACE your old crop_details dictionary with this new one <<
# ==============================================================================
crop_details = {
    # This dictionary now contains all 22 of your crops.
    # I have used a placeholder description that you can edit later.

    'rice': {
        'image': 'images/crop/ml-rice.jpg',
        'description': "Rice is a water-intensive crop, typically grown in flooded paddies. It thrives in hot and humid conditions with prolonged sunshine. The soil should be heavy, with a high clay content to hold water."
    },
    'maize': {
        'image': 'images/crop/ml-maize.jpg',
        'description': "Maize (corn) prefers warm, sunny weather and grows well in fertile, well-drained soils. Consistent watering is crucial, especially during the pollination stage, to ensure full kernel development."
    },
    'chickpea': {
        'image': 'images/crop/ml-ChickPea.jpeg',
        'description': "Chickpea is a cool-season legume that grows best in well-drained, sandy loam soils. It is relatively drought-tolerant but requires moisture during the flowering and pod-filling stages."
    },
    'kidneybeans': {
        'image': 'images/crop/ml-KidneyBeans.jpg',
        'description': "Kidney beans are a warm-season crop that requires consistent moisture and well-drained soil. They are sensitive to frost and should be planted after the last frost date."
    },
    'pigeonpeas': {
        'image': 'images/crop/ml-PigeonPeas.jpg',
        'description': "Pigeon peas are a hardy, drought-resistant legume grown in semi-arid regions. They thrive in a wide range of soils and are known for their deep root system which helps with soil aeration."
    },
    'mothbeans': {
        'image': 'images/crop/ml-MothBeans.jpg',
        'description': "Moth beans are highly drought-resistant and thrive in hot, dry, sandy soils. They are a short-duration crop, often grown in arid and semi-arid regions of India."
    },
    'mungbean': {
        'image': 'images/crop/ml-MungBean.jpg',
        'description': "Mung beans are a warm-season legume that prefer well-drained loam to sandy loam soils. They have a short growing cycle, often maturing in just 60-90 days."
    },
    'blackgram': {
        'image': 'images/crop/ml-Blackgram.jpeg',
        'description': "Black gram grows best in clay loam or heavy soils that retain moisture. It is a warm-weather crop and is often planted during the rainy season in South Asia."
    },
    'lentil': {
        'image': 'images/crop/ml-lentil.jpeg',
        'description': "Lentils are a cool-season crop that can tolerate frost. They prefer well-drained, fertile loamy soils and are often grown as a winter crop."
    },
    'pomegranate': {
        'image': 'images/crop/ml-Pomegranate.jpeg',
        'description': "Pomegranates are drought-tolerant and prefer a semi-arid climate. They grow well in a variety of soils, from sandy to clay, but require good drainage."
    },
    'banana': {
        'image': 'images/crop/ml-Banana.jpeg',
        'description': "Bananas flourish in tropical regions with high humidity and rainfall. They need rich, well-drained soil and are heavy feeders, requiring plenty of potassium."
    },
    'mango': {
        'image': 'images/crop/ml-Mango.jpeg',
        'description': "Mango trees require a climate with a distinct dry season for good fruit production. They grow in a wide variety of well-drained soils and need plenty of sunlight."
    },
    'grapes': {
        'image': 'images/crop/ml-Grapes.jpeg',
        'description': "Grapes grow on vines and require a long season of warm to hot, dry weather. They thrive in well-drained, deep, and light-textured soils."
    },
    'watermelon': {
        'image': 'images/crop/ml-Watermelon.jpg',
        'description': "Watermelons are a warm-season fruit that requires lots of space to grow. They prefer sandy, well-drained soil and consistent watering."
    },
    'muskmelon': {
        'image': 'images/crop/ml-Muskmelon.jpg',
        'description': "Muskmelons need a long, warm growing season. They grow best in well-drained, sandy loam soils rich in organic matter."
    },
    'apple': {
        'image': 'images/crop/ml-Apple.jpeg',
        'description': "Apples grow best in cool, temperate climates with a cold winter for dormancy. They require well-drained loamy soil with a pH between 6.0 and 7.0."
    },
    'orange': {
        'image': 'images/crop/ml-Orange.jpg',
        'description': "Oranges are subtropical fruits that are sensitive to frost. They need well-drained soil, plenty of sunlight, and consistent moisture."
    },
    'papaya': {
        'image': 'images/crop/ml-Papaya.jpeg',
        'description': "Papayas are fast-growing tropical plants that require warmth and sunlight. They are susceptible to root rot and need very well-drained soil."
    },
    'coconut': {
        'image': 'images/crop/ml-Coconut.jpeg',
        'description': "Coconut palms grow in tropical coastal areas with high humidity and rainfall. They tolerate saline conditions and prefer sandy soils."
    },
    'cotton': {
        'image': 'images/crop/ml-Cotton.jpg',
        'description': "Cotton is a warm-climate crop that requires a long, frost-free period. It grows best in fertile, well-drained soils in areas with plenty of sunshine."
    },
    'jute': {
        'image': 'images/crop/ml-Jute.jpg',
        'description': "Jute is a cash crop in Bangladesh and India, thriving in monsoon climates with high humidity. It grows best in alluvial, loamy soils."
    },
    'coffee': {
        'image': 'images/crop/ml-Coffee.jpg',
        'description': "Coffee plants prefer a stable climate with moderate temperatures and rainfall. They grow best in rich, well-drained soil, often at high altitudes."
    },
    'default': {
        'image': 'images/crop/default.jpg',
        'description': "No specific growing information available. General best practices include ensuring proper sunlight, water, and soil nutrients."
    }
}


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


# Add this new route to app.py

@app.route('/output/<crop_name>')
def output(crop_name):
    # Find the details for the requested crop.
    # .get() is used to safely retrieve the item, and provides a default if not found.
    details = crop_details.get(crop_name.lower(), crop_details['default'])

    # Pass the crop name and its details to the new template.
    return render_template('output.html', crop_name=crop_name, details=details)
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
        # Get all the data from the form
        email = request.form.get('email').lower()
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        password = request.form.get('password')
        location = request.form.get('location')
        # Use .getlist() for <select multiple>
        crops = request.form.getlist('crops_of_interest')

        # Check if the email already exists in the database
        if users.find_one({'email': email}):
            flash('That email is already registered.', 'error')
            return redirect(url_for('signup'))

        # Hash the password for security
        hashed_password = generate_password_hash(password)

        # Create a dictionary with all the new user's data
        new_user = {
            'full_name': full_name,
            'email': email,
            'phone': phone,
            'password': hashed_password,
            'location': location,
            'crops_of_interest': crops,
            'signup_date': datetime.datetime.now(pytz.timezone('Asia/Dhaka'))
        }

        # Insert the new user data into the 'users' collection
        users.insert_one(new_user)

        flash('Signup successful! Please log in.', 'success')
        return redirect(url_for('login'))

    # If it's a GET request, just show the signup page
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