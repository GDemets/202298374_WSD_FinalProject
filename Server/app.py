from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # autorise les requêtes du front

@app.route("/api/hello")
def hello():
    return jsonify({"message": "Hello depuis Flask !"})
