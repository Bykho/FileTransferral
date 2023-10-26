from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo
import pymongo
import certifi
from flask import session
from flask_session import Session
from auth import SECRET_KEY  # Import the SECRET_KEY from auth.py

# Configure the Flask app instance with the static_folder and static_url_path arguments
app = Flask(__name__, static_folder='uploads', static_url_path='/uploads')
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*", "expose_headers": ["Authorization"]}})

app.config["MONGO_URI"] = "mongodb+srv://nico:xX2SUpVJA9Rcrgxg@cluster0.uu6cuq7.mongodb.net/Cluster0?retryWrites=true&w=majority&ssl=true&tlsAllowInvalidCertificates=true"
mongo = PyMongo(app)

#@app.after_request
#def after_request(response):
#    # response.headers['Access-Control-Allow-Credentials'] = 'true'
#    return response

#what does app.config do in flask.
#what does session(app) do

# Set the secret key for encrypting sessions. This should be a random string of bytes
app.config['SECRET_KEY'] = SECRET_KEY

# Use filesystem session (you can also use Redis, etc.)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

from routes import *

if __name__ == "__main__":
    app.run(debug=True)