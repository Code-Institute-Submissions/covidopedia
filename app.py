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
    # terms = list(mongo.db.terms.find())
    terms = list(mongo.db.terms.find().sort("term_name", 1))
    return render_template("terms.html", terms=terms)


@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    terms = list(mongo.db.terms.find({"$text": {"$search": query}}))
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
    terms = list(mongo.db.terms.find().sort("term_name", 1))
    # print(user)
    if session["user"]:
        return render_template(
            "profile.html", first_name=user["first_name"], email=user["email"],
            terms=terms)
        # return render_template("profile.html", terms=terms)

# @app.route("/profile/<first_name>", methods=["GET", "POST"])
# def profile_name(first_name):
# first_name = mongo.db.users.find_one(
    # {"first_name": session["user"]})["first_name"]
    # return render_template("profile.html", first_name=first_name)


@app.route("/logout")
def logout():
    # user = mongo.db.users.find_one({"email": session["user"]})
    flash("You've been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/new_term", methods=["GET", "POST"])
def new_term():
    if request.method == "POST":
        print(request.form.get("term_name"))
        term = {
            "term_name": request.form.get("term_name"),
            "definition_01": request.form.get("definition_01"),
            "see_also_01": request.form.get("see_also_01"),
            "source_name_01": request.form.get("source_name_01"),
            "source_01": request.form.get("source_01"),
            "category_name": request.form.get("category_name"),
            "created_by": session["user"]
        }
        mongo.db.terms.insert_one(term)
        flash("Thank you, the new term has been added to covidopedia")
        return redirect(url_for("get_terms"))

    see_also = mongo.db.terms.find().sort("term_name", 1)
    see_also = list([x["term_name"] for x in list(see_also)])

    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("new_term.html", categories=categories,
                           see_also=see_also)


@app.route("/edit_term/<term_id>", methods=["GET", "POST"])
def edit_term(term_id):
    if request.method == "POST":
        submit = {
            "term_name": request.form.get("term_name"),
            "definition_01": request.form.get("definition_01"),
            "see_also_01": request.form.get("see_also_01"),
            "source_name_01": request.form.get("source_name_01"),
            "source_01": request.form.get("source_01"),
            "category_name": request.form.get("category_name"),
            "created_by": session["user"]
        }
        mongo.db.terms.update({"_id": ObjectId(term_id)}, submit)
        flash("Thank you, your edit has been included in covidopedia")

    see_also = mongo.db.terms.find().sort("term_name", 1)
    see_also = list([x["term_name"] for x in list(see_also)])

    categories = mongo.db.categories.find().sort("category_name", 1)
    term = mongo.db.terms.find_one({"_id": ObjectId(term_id)})
    return render_template("edit_term.html", term=term,
                           see_also=see_also, categories=categories)


@app.route("/delete_term/<term_id>")
def delete_term(term_id):
    mongo.db.terms.remove({"_id": ObjectId(term_id)})
    flash("Thank you, the term has been deleted from covidopedia")
    return redirect(url_for("get_terms"))


@app.route("/get_categories")
def get_categories():
    categories = list(mongo.db.categories.find().sort("category_name", 1))
    return render_template("categories.html", categories=categories)


@app.route("/new_category", methods=["GET", "POST"])
def new_category():
    if request.method == "POST":
        category = {
            "category_name": request.form.get("category_name")
        }
        mongo.db.categories.insert_one(category)
        flash("Thank you for adding a new category to covidopedia")
        return redirect(url_for("get_categories"))

    return render_template("new_category.html")


@app.route("/edit_category/<category_id>", methods=["GET", "POST"])
def edit_category(category_id):
    if request.method == "POST":
        submit = {
            "category_name": request.form.get("category_name")
        }
        mongo.db.categories.update({"_id": ObjectId(category_id)}, submit)
        flash("Thank you for updating the category in covidopedia")
        return redirect(url_for("get_categories"))

    category = mongo.db.categories.find_one({"_id": ObjectId(category_id)})
    return render_template("edit_category.html", category=category)


@app.route("/delete_category/<category_id>")
def delete_category(category_id):
    mongo.db.categories.remove({"_id": ObjectId(category_id)})
    flash("Thank you, the category has been deleted from covidopedia")
    return redirect(url_for("get_categories"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=False)
