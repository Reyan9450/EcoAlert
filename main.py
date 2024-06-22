from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import os
import tensorflow as tf
from tensorflow.keras.models import load_model
import numpy as np
from twilio.rest import Client

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests for development purposes

# Load your pre-trained model
model = load_model("garbage_classifier.h5")

# Create a list to store image metadata (file path and severity)
images_metadata = []

# Twilio credentials

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')

twilio_phone_number = '+15627413564'
authority_phone_number = '+918081660482'  # Replace with actual authority phone number

# Initialize Twilio client
client = Client(account_sid, auth_token)

# Serve the landing page
@app.route('/')
def index():
    return render_template('landingPage.html')

@app.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template('dashboarad.html')

@app.route('/public', methods=['GET'])
def public():
    return render_template('index.html') 



@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file in request'}), 400

    file = request.files['image']

    # Save the file to a directory (e.g., uploads/)
    if not os.path.exists('uploads'):
        os.makedirs('uploads')

    file_path = os.path.join('uploads', file.filename)
    file.save(file_path)

    # Process the image and get the severity
    img = tf.keras.preprocessing.image.load_img(file_path, target_size=(180, 180))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)  # Create a batch

    predictions = model.predict(img_array)
    score = tf.nn.softmax(predictions[0])
    severity_label = np.argmax(score)
    severity = "High Severity" if severity_label == 1 else "Low Severity"

    # Store image metadata
    images_metadata.append({'file_path': file_path, 'severity': severity})

    # Send SMS alert if high severity image is detected
    if severity == "High Severity":
        send_alert_via_sms()

    return jsonify({'severity': severity})

def send_alert_via_sms():
    message = client.messages.create(
        body='High severity garbage image uploaded! Please take action.',
        from_=twilio_phone_number,
        to=authority_phone_number
    )
    print(f"SMS alert sent to {authority_phone_number}. SID: {message.sid}")

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

@app.route('/images/<severity>')
def get_images(severity):
    filtered_images = [img for img in images_metadata if img['severity'] == severity]
    return jsonify(filtered_images)

if __name__ == '__main__':
    app.run(debug=True)
