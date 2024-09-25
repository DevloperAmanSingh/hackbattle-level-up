import json
from flask import Flask, request, render_template, redirect, url_for
import os
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
POINTS_DB_PATH = 'points_database.json'


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(POINTS_DB_PATH):
    with open(POINTS_DB_PATH, 'w') as db_file:
        json.dump({}, db_file)

ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv', 'mov'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def home():
    # Changed to return HTML for better testing
    return "<h1>Hello, World!</h1><p>Welcome to the video upload app</p>"


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part in the request"
    
    file = request.files['file']
    print(file)
    if file.filename == '':
        return "No selected file"

    if file and allowed_file(file.filename):
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return f"File {filename} uploaded successfully!"

    return "File format not allowed."

@app.route('/uploadPoints', methods=['POST'])
def uploadPoints():
    data = request.json
    print(data)
    username = data.get('username')
    points = data.get('points')

    if not username or points is None:
        return "Username and points are required", 400

    with open(POINTS_DB_PATH, 'r') as db_file:
        points_data = json.load(db_file)

    if username not in points_data:
        points_data[username] = 0

    points_data[username] += points

    with open(POINTS_DB_PATH, 'w') as db_file:
        json.dump(points_data, db_file)

    return {"message": "Points uploaded successfully", "username": username, "total_points": points_data[username]}


@app.route('/getPoints', methods=['GET'])
def getPoints():
    username = request.args.get('username')
    if not username:
        return "Username is required", 400
    
    with open(POINTS_DB_PATH,'r') as db_file:
        points_data = json.load(db_file)

    if username not in points_data:
        return {"message" : "User not found", "total_points":0}
    
    return {"message": "User found", "total_points": points_data[username]}
    

@app.route('/leaderboard',methods=['GET'])
def leaderboard():
    with open(POINTS_DB_PATH,'r') as db_file:
        points_data = json.load(db_file)
    sorted_points = dict(sorted(points_data.items(), key=lambda x:x[1], reverse=True))
    return {"leaderboard": sorted_points}

if __name__ == "__main__":
    app.run(debug=True)
