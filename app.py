from flask import Flask, request, jsonify
from models import db, User
from flask_cors import CORS
from datetime import datetime
import logging

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///DataBase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

### MiddleWare ###
logging.basicConfig(level=logging.INFO)

@app.before_request
def log_request_info():
    logging.info(f"{datetime.utcnow().isoformat()} - {request.method} {request.path}")

### Get endpoints ###
@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([u.to_dict() for u in users]), 200

### POST endpoints ###
@app.route('/users',methods=['POST'])
def create_user():
    """Create a new user"""
    if not request.json or 'pseudo' not in request.json or 'mail' not in request.json or 'password' not in request.json:
        response_data = {
            'message': 'Format invalid or missing values',
            'status': 'error'
            }
        return response_data, 400
    
    user = User(
        pseudo=request.json.get('pseudo'),
        mail=request.json.get('mail'),
        password=request.json.get('password'),
        role="user"
    )

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        print(e)
        return jsonify({'status':'error',
                        'message':'User already exists'}), 409
    
    return jsonify({'status':'success',
                    'message':'User successfully created',
                    'data':[user.to_dict()]
                   }), 201

if __name__ == "__main__":
    app.run(debug=True)
