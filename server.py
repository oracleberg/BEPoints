# This file is the main server for Points API
from flask import render_template
import connexion

# Creating App instance
app = connexion.App(__name__, specification_dir="./")

# Read Yaml to configure endpoints
app.add_api("Swag.yml")

# Create home URL route
@app.route("/")
def home():
    """
    Responds to the URL localhost:5000/

    :return: rendered template "home.html"
    """
    return render_template("home.html")

if __name__ == "__main__":
    app.run()
