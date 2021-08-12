import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
# Werkzeug security helpers to hash and salt passwords
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/get_terms")
def get_terms():
    terms = list(mongo.db.terms.find())
    return render_template("terms.html", terms=terms)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"email": request.form.get("email").lower()})

        if existing_user:
            flash("...that email exists already...")
            return redirect(url_for("register"))

        register = {
            "first_name": request.form.get("first_name").lower(),
            "last_name": request.form.get("last_name").lower(),
            "email": request.form.get("email").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        session["user"] = request.form.get("email")
        flash("You've successfully registered")
        return redirect(url_for("profile", email=session["user"]))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"email": request.form.get("email").lower()})

        if existing_user:
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("email").lower()
                flash("Hallo {}".format(
                    existing_user["first_name"].capitalize()))
                return redirect(url_for("profile", email=session["user"]))
            else:
                flash("Incorrect email and/or password")
                return redirect(url_for("login"))

        else:
            flash("Incorrect email and/or password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<email>", methods=["GET", "POST"])
def profile(email):
    user = mongo.db.users.find_one({"email": session["user"]})
    # print(user)
    if session["user"]:
        return render_template(
            "profile.html", first_name=user["first_name"], email=user["email"])


# @app.route("/profile/<first_name>", methods=["GET", "POST"])
# def profile_name(first_name):
# first_name = mongo.db.users.find_one(
    # {"first_name": session["user"]})["first_name"]
    # return render_template("profile.html", first_name=first_name)

@app.route("/logout")
def logout():
    flash("You've been logged out")
    session.clear
    return redirect(url_for("login"))


@app.route("/new")
def new():
    return render_template("new.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
