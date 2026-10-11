"""CreatorLink: rights-safe, vernacular AI creators for small brands.

Run:  python app.py      then open http://127.0.0.1:5000
"""
from flask import Flask, abort, redirect, render_template, request, url_for

import core

app = Flask(__name__)

SAMPLE_BRIEFS = [
    dict(label="Pickle brand (Telugu)", brand="Amma's Kitchen", product="Mango Pickle",
         audience="families in Andhra and Telangana", language="Telugu", niche="food",
         budget=5000, tone="warm festive homely"),
    dict(label="Saree boutique (Tamil)", brand="Kaveri Weaves", product="Silk Saree collection",
         audience="women planning festival shopping", language="Tamil", niche="handmade",
         budget=4000, tone="traditional colourful festive"),
    dict(label="Study app (Hindi)", brand="PadhoPlus", product="Class 10 revision app",
         audience="students and parents", language="Hindi", niche="education",
         budget=6000, tone="friendly relatable story"),
]


@app.route("/")
def index():
    return render_template("index.html", languages=core.LANGUAGES, niches=core.NICHES,
                           samples=SAMPLE_BRIEFS)


@app.route("/match", methods=["POST"])
def match():
    brief = core.clean_brief(request.form)
    results, ms = core.match(brief)
    return render_template("results.html", brief=brief, results=results, ms=ms,
                           total=len(core.load_creators()))


@app.route("/shortlist/<creator_id>", methods=["POST"])
def shortlist(creator_id):
    creator = core.get_creator(creator_id)
    if creator is None:
        abort(404)
    brief = core.clean_brief(request.form)
    return render_template("agreement.html", brief=brief, creator=creator,
                           concept=core.sample_concept(brief, creator),
                           agreement=core.agreement_text(brief, creator))


@app.route("/creators")
def creators():
    return render_template("creators.html", creators=core.load_creators(),
                           languages=core.LANGUAGES, niches=core.NICHES,
                           added=request.args.get("added"), error=request.args.get("error"))


@app.route("/creators/new", methods=["POST"])
def creators_new():
    try:
        creator = core.new_creator_from_form(request.form)
    except ValueError as e:
        return redirect(url_for("creators", error=str(e)))
    core.save_creator(creator)
    return redirect(url_for("creators", added=creator["name"]))


if __name__ == "__main__":
    app.run(debug=False, port=5000)
