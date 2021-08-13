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


@app.route("/new_term", methods=["GET", "POST"])
def new_term():
    if request.method == "POST":
        term = {
            "term_name": request.form.get("term_name"),
            "un_abbreviated": request.form.get("un_abbreviated"),
            "definition_01": request.form.get("definition_01"),
            "see_also_01": request.form.get("see_also_01"),
            "source_01": request.form.get("source_01"),
            "category_name": request.form.get("category_name"),
            "created_by": session["user"]
        }
        mongo.db.terms.insert_one(term)
        flash("Thank you, the new term has been added to covidopedia")
        return redirect(url_for("get_terms"))

    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("new_term.html", categories=categories)


@app.route("/edit_term/<term_id>", methods=["GET", "POST"])
def edit_term(term_id):
    if request.method == "POST":
        submit = {
            "term_name": request.form.get("term_name"),
            "un_abbreviated": request.form.get("un_abbreviated"),
            "definition_01": request.form.get("definition_01"),
            "see_also_01": request.form.get("see_also_01"),
            "source_01": request.form.get("source_01"),
            "category_name": request.form.get("category_name"),
            "created_by": session["user"]
        }
        mongo.db.terms.update({"_id": ObjectId(term_id)}, submit)
        flash("Thank you, your edit has been included in covidopedia")

    term = mongo.db.terms.find_one({"_id": ObjectId(term_id)})
    return render_template("edit_term.html", term=term)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
