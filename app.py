from flask import Flask, render_template, request
from utils import fact_check

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():

    result = None
    articles = []

    if request.method == "POST":

        claim = request.form["news"]

        result, articles = fact_check(claim)

    return render_template("index.html", result=result, articles=articles)


if __name__ == "__main__":
    app.run(debug=True)