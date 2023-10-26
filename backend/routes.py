from flask import Flask, request, jsonify
from app import app
from flask_pymongo import PyMongo
from pymongo import MongoClient
import os
from flask import session
from auth import SECRET_KEY
import jwt
from flask import send_from_directory

mongo = PyMongo(app)

@app.route('/SignIn', methods=['POST'])
def login():
    users = mongo.db.users
    user = users.find_one({"user": request.json['user']})
    if user and user["pwd"] == request.json['pwd']:
        token = jwt.encode({"username": request.json['user']}, SECRET_KEY, algorithm="HS256")
        return jsonify(token=token, message="Logged in successfully!"), 200
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/register', methods=['POST'])
def register():
    users = mongo.db.users
    existing_user = users.find_one({"user": request.json['user']})
    if existing_user:
        return jsonify({"error": "Username already taken"}), 409

    users.insert_one({"user": request.json['user'], "pwd": request.json['pwd']})
    token = jwt.encode({"username": request.json['user']}, SECRET_KEY, algorithm="HS256")
    return jsonify(token=token, message="User registered successfully!"), 201

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_image():
    # Obtain the token from the Authorization header.
    auth_header = request.headers.get('Authorization')
    if not auth_header or 'Bearer' not in auth_header:
        return jsonify(error="Not authenticated"), 401

    token = auth_header.split(' ')[1]

    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        current_user = data["username"]
    except:
        return jsonify({"message": "Token is invalid!"}), 403

    # Checking if image exists in the request.
    if 'image' not in request.files:
        return jsonify(error="No image part"), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify(error="No selected file"), 400

    print("Current working directory:", os.getcwd())
    
    # Checking if the image is of an allowed type.
    if file and allowed_file(file.filename):
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        print(f"File {filename} saved successfully!")

        # Save the image filename or path to MongoDB.

        label = request.form.get('label')

        image_info = {
            "url": file.filename,
            "label": label
        }

        image_files = mongo.db.image_files
        image_files.insert_one({"filename": file.filename, "user": current_user, "label": label})  # Add user association here.

        users = mongo.db.users
        users.update_one({"user": current_user}, {"$push": {"images": image_info}})

        return jsonify(success=True), 200

    return jsonify(error="Invalid file type"), 400

@app.route('/uploads/<filename>', methods=['GET'])
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/gallery', methods=['GET'])
def get_images():
    auth_header = request.headers.get('Authorization')
    if not auth_header or 'Bearer ' not in auth_header:
        return jsonify(error="Not authenticated"), 401

    token = auth_header.split('Bearer ')[1]  # Split the token from "Bearer "

    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        current_user = data["username"]

    except Exception as e:
        print(f"Error decoding token: {e}")
        return jsonify({"message": "Token is invalid!"}), 403

    user = mongo.db.users.find_one({"user": current_user})
    if not user:
        return jsonify(error="User not found"), 404

    images = user.get("images", [])

    # Modify the images list to include both URL and label
    updated_images = []
    for image_info in images:
        if isinstance(image_info, dict):  # Check if image_info is a dictionary
            filename = image_info.get("url", "")
            label = image_info.get("label", "")
            if filename:
                updated_images.append({
                    "url": f"http://127.0.0.1:5000/uploads/{filename}",  # Construct the image URL
                    "label": label
                })
    pendingDocRequests = user.get("pendingDocRequests", [])
    response_data = {
        "username": current_user,
        "images": updated_images,
        "pendingDocRequests": pendingDocRequests
    }

    return jsonify(response_data)

@app.route('/request', methods=['GET'])
def request_doc():
    try:
        # Obtain the token from the Authorization header.
        auth_header = request.headers.get('Authorization')
        if not auth_header or 'Bearer ' not in auth_header:
            return jsonify(error="Not authenticated"), 401

        token = auth_header.split('Bearer ')[1]

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            print('Decoded data:', data)
            current_user = data.get("username")

            if current_user is None:
                return jsonify({"message": "Username not found in token"}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired"}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({"message": "Token is invalid"}), 401

        # Fetch all users' usernames excluding the current user
        all_users = mongo.db.users.find({}, {"user": 1, "_id": 0})

        all_users_list = [user['user'] for user in all_users if 'user' in user and user['user'] != current_user]

        # Log the data you are returning
        print("Users:", all_users_list)
        print("Current User:", current_user)

        response_data = {
            "current_user": current_user,
            "all_users": all_users_list
        }

        # Return as JSON
        return jsonify(response_data)
    except Exception as e:
        # Log any exceptions for debugging
        print("Error:", str(e))
        return jsonify(error="An error occurred"), 500  # Return a JSON error response

@app.route('/request-document', methods=['POST'])
def request_document():
    data = request.get_json()
    print('data: ', data)
    if 'username' not in data or 'documentType' not in data:
        return jsonify({'error': 'Invalid request'}), 400
    
    username = data['username']
    document_type = data['documentType']
    fromUser = data['from']

    try:
        # Update the user's pendingDocRequests using the mongo object
        print('pre success')
        mongo.db.users.update_one(
            {"user": username},
            {"$push": {"pendingDocRequests": {"documentType": document_type, "from": fromUser}}}
        )
        print('Success')

        return jsonify({'message': 'Document request successful'})
    except Exception as e:
        return jsonify({'error': 'An error occurred while processing your request.'}), 500
