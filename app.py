from flask import Flask, render_template, request
from model import predict_crop

app = Flask(__name__)


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/service", methods=["GET", "POST"])
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


@app.route("/", methods=["GET", "POST"])
def index():
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

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
