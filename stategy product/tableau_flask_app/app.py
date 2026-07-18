from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    """Landing page with links to Dashboard and Story."""
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    """Page that embeds the Tableau Public Dashboard."""
    return render_template("dashboard.html")


@app.route("/story")
def story():
    """Page that embeds the Tableau Public Story."""
    return render_template("story.html")


if __name__ == "__main__":
    app.run(debug=True)
