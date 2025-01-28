from flask import Flask, render_template, flash, redirect, url_for, session, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
# from index import d_dtcn
import cv2

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    uname = db.Column(db.String(20), unique=True, nullable=False)
    lname = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    date = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.String(20), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
   
    pass1 = db.Column(db.String(60), nullable=False)

# admin database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        pass1 = request.form['pass1']
        user = Users.query.filter_by(phone=phone).first()
        if user and check_password_hash(user.pass1, pass1):
            flash('Login successful!', 'success')
            session['user_id'] = user.id
            return redirect(url_for('home'))
        else:
            flash('Login failed. Check your email and password.', 'danger')
    return render_template('login.html')

@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        uname = request.form['uname']
        lname = request.form['lname']
        email = request.form['email']
        date = request.form['date']
        address = request.form['address']
        phone = request.form['phone']
        pass1 = request.form['pass1']
        pass2 = request.form['pass2']

        if pass1 == pass2:
            hashed_password = generate_password_hash(pass1)
            new_user = Users(username=username,uname=uname,lname=lname, email=email,date=date,address=address,phone=phone, pass1=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Passwords do not match.', 'danger')

    return render_template('user_registration.html')

@app.route('/logout/')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('base'))




@app.route('/users/edit/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    user = Users.query.get_or_404(id)
    if request.method == 'POST':
        # Update user
        user.username = request.form['username']
        user.uname = request.form['uname']
        user.lname = request.form['lname']
        user.email = request.form['email']
        user.date = request.form['date']
        user.address = request.form['address']
        user.phone = request.form['phone']
        user.pass1 = request.form['pass1']

        db.session.commit()
        flash('User updated successfully', 'success')
        return redirect(url_for('users'))
    else:
        return render_template('edit_user.html', user=user)
    

@app.route('/users/delete/<int:id>', methods=['POST'])
def delete_user(id):
    user = Users.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully', 'success')
    return redirect(url_for('users'))









@app.route("/home",methods=['GET', 'POST'])
def home():
    print(request.method)
    if request.method == 'POST':
        if request.form.get('Continue') == 'Continue':
           return render_template("test1.html")
    else:
        # pass # unknown
        return render_template("index.html")



@app.route("/")
def base():
    return render_template("base.html")


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            flash('Login successful!', 'success')
            session['user_id'] = user.id
            return redirect(url_for('admin_home'))
        else:
            flash('Login failed. Check your email and password.', 'danger')
    return render_template('admin_login.html')

@app.route('/admin_register/', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password == confirm_password:
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('admin_login'))
        else:
            flash('Passwords do not match.', 'danger')

    return render_template('admin_register.html')

@app.route('/admin_logout/')
def admin_logout():
    session.pop('user_id', None)
    return redirect(url_for('base'))


@app.route("/admin_home")
def admin_home():
    return render_template("admin_home.html")


@app.route("/view_user")
def view_user():
    users = Users.query.all()
    return render_template('view_user.html', users=users)
    


import cv2
import numpy as np
import pyttsx3

@app.route("/start", methods=['GET', 'POST'])
def index():
    print(request.method)
    if request.method == 'POST':
        if request.form.get('Start') == 'Start':
            # Open webcam
            cap = cv2.VideoCapture(0)

            # Initialize the text-to-speech engine
            engine = pyttsx3.init()
            net = cv2.dnn.readNetFromDarknet('yolov3.cfg', 'yolov3.weights')
            classes = []
            with open('coco.names', 'r') as f:
                classes = [line.strip() for line in f.readlines()]
            layer_names = net.getLayerNames()
            output_layers = net.getUnconnectedOutLayersNames()
            colors = np.random.uniform(0, 255, size=(len(classes), 3))

            FOCAL_LENGTH = 1000  # in pixels
            OBJECT_HEIGHT = 0.5  # in meters
            MIN_DISTANCE = 2  # in meters

            while True:
                ret, img = cap.read()
                height, width, channels = img.shape

                # Perform object detection
                blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
                net.setInput(blob)
                outs = net.forward(output_layers)

                # Process the detections
                class_ids = []
                confidences = []
                boxes = []
                for out in outs:
                    for detection in out:
                        scores = detection[5:]
                        class_id = np.argmax(scores)
                        confidence = scores[class_id]
                        if confidence > 0.5:
                            # Object detected
                            center_x = int(detection[0] * width)
                            center_y = int(detection[1] * height)
                            w = int(detection[2] * width)
                            h = int(detection[3] * height)
                            x = center_x - w // 2
                            y = center_y - h // 2
                            boxes.append([x, y, w, h])
                            confidences.append(float(confidence))
                            class_ids.append(class_id)

                # Apply non-max suppression to eliminate duplicate detections
                indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

                # Generate voice output and distance warning for each object detected
                for i in range(len(boxes)):
                    if i in indexes:
                        x, y, w, h = boxes[i]
                        label = str(classes[class_ids[i]])
                        color = colors[class_ids[i]]
                        cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
                        
                        # Draw label text on the image
                        cv2.putText(img, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                        # Calculate distance to object
                        obj_height = h
                        distance = (OBJECT_HEIGHT * FOCAL_LENGTH) / obj_height
                        distance = round(distance, 2)

                        # Generate voice output and warning message
                        if distance < MIN_DISTANCE:
                            engine.say(f"Warning! {label} too close {distance} meters.")
                            engine.runAndWait()
                        else:
                            engine.say(f"{label} detected at {distance} meters.")
                            engine.runAndWait()

                # Display the resulting image
                cv2.imshow('Blind Assistance', img)

                if cv2.waitKey(1) == ord('q'):
                    break

            # Release the webcam and destroy all OpenCV windows
            cap.release()
            cv2.destroyAllWindows()

            return render_template("index.html")
    else:
        # pass # unknown
        return render_template("index.html")




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
