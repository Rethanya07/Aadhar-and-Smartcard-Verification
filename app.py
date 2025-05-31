import os
import cv2
import pytesseract
import re
import pymysql
from flask import Flask, request, jsonify, render_template
from flask import Flask, render_template, request, redirect, url_for, flash
import smtplib
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#app = Flask(__name__)
app = Flask(__name__, static_folder="static", template_folder="templates")

# Function to preprocess image
def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    return thresh

# Function to extract Aadhar and Smart Card numbers using OCR
def extract_text(image_path):
    image = cv2.imread(image_path)
    processed = preprocess_image(image)
    text = pytesseract.image_to_string(processed)
    
    aadhar_match = re.search(r'\b\d{4} \d{4} \d{4}\b', text)
    aadhar_number = aadhar_match.group() if aadhar_match else None

    smartcard_match = re.search(r'\b\d{12}\b', text)
    smartcard_number = smartcard_match.group() if smartcard_match else None
    print(aadhar_number, smartcard_number)
    return aadhar_number, smartcard_number

def extract_smart_card_number(image_path):
    
    image = cv2.imread(image_path)

    # Get image dimensions
    h, w, _ = image.shape

    # Define ROI for bottom left corner (adjust values as needed)
    roi = image[int(h * 0.75):h, 0:int(w * 0.5)] 

    # Preprocess the cropped ROI
    processed = preprocess_image(roi)

    # Perform OCR with digit filtering
    extracted_text = pytesseract.image_to_string(processed, config='--psm 6 -c tessedit_char_whitelist=0123456789')

    # Extract only 12-digit numbers
    matches = re.findall(r'\b\d{12}\b', extracted_text)

    if matches:
        return matches[0]  
    else:
        return "No valid Smart Card number found."

#Function to connect to database
def get_db_connection():
        print("🔄 Trying to connect to MySQL...")

        conn = pymysql.connect(
            host="localhost", 
            user="rethanya",
            password="password", 
            database="loan_db",
            port=3306,  
            
        )
        return conn
               
# Function to verify extracted numbers in the database
def verify_in_db(aadhar,smartcard):
    db = get_db_connection()
    if db:
        print("Connected!")
    else:
        print("Failed to connect.")
    cursor = db.cursor()
    cursor.execute("SELECT * FROM borrowers WHERE aadhar_number=%s AND smartcard_number=%s", (aadhar, smartcard))
    result = cursor.fetchone()
    db.close()
    return result

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        conn = get_db_connection()  # ✅ Get connection here
        cursor = conn.cursor()
        # Dummy check — replace with real authentication
        if role == 'official':
            cursor.execute("SELECT * FROM officials WHERE email=%s AND password=%s", (email, password))
            user = cursor.fetchone()
            if user:
                return redirect(url_for('verify'))
            else:
                flash('Invalid official credentials')
        elif role == 'admin':
            cursor.execute("SELECT * FROM admins WHERE email=%s AND password=%s", (email, password))
            user = cursor.fetchone()
            if user:
                return redirect(url_for('admin_panel'))
            else:
                flash('Invalid admin credentials')
        else:
            flash('Invalid role selected')

        return redirect(url_for('login'))

    return render_template('login.html')


#adminpanel backend
#-------------------------------------------------------------------

@app.route('/admin_panel', methods=['GET'])
def admin_panel():
    db = get_db_connection()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM officials")
    officials = cursor.fetchall()
    db.close()
    return render_template('admin_panel.html', officials=officials)

@app.route('/add_official', methods=['POST'])
def add_official():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("INSERT INTO officials (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
    db.commit()
    db.close()
    return redirect(url_for('admin_panel'))

@app.route('/delete_official/<int:id>', methods=['POST'])
def delete_official(id):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM officials WHERE id = %s", (id,))
    db.commit()
    db.close()
    return redirect(url_for('admin_panel'))


# Route for homepage
@app.route('/')
def index():
    return render_template('intro.html')

@app.route('/index')
def index1():
    return render_template('index.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

# Route to render verification page
@app.route('/verify')
def verify():
    return render_template('verify.html')

@app.route('/eligibility')
def eligibility():
    return render_template('eligibility.html')

@app.route('/documents')
def documents():
    return render_template('documents.html')

@app.route('/rules')
def rules():
    return render_template('rules.html')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/failure')
def failure():
    return render_template('failure.html')

@app.route('/error')
def error():
    return render_template('error.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/get_borrowers')
def get_borrowers():
    db = get_db_connection()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT id,name, aadhar_number, smartcard_number, IF(verified=1, 'Verified✅', 'Pending❌') AS status FROM borrowers")
    data = cursor.fetchall()
    db.close()
    return jsonify(data)

@app.route('/send_report', methods=['POST', 'GET'])
def send_report():
    db = None
    cursor = None
    msg = None
    try:
        print("send sms report route triggered")
        data = request.get_json(force=True)
        print("received data", data)
        
        aadhar, smartcard = data.values()
        print("aadhar : ", aadhar)
        print("smartcard : ", smartcard)

        # Fetch user email from DB
        db = get_db_connection()
        cursor = db.cursor(pymysql.cursors.DictCursor)

        cursor.execute("SELECT name, email FROM borrowers WHERE aadhar_number = %s AND smartcard_number=%s", (aadhar, smartcard))
        result = cursor.fetchone()
        print(result)

        if not result:
            return jsonify({"message": "User not found"}), 404

        name = result['name']
        recipient_email = result['email']
        print(f"Found user {name} with email {recipient_email}")

        # Email details
        sender_email = 'sifanaalwmanager@gmail.com'
        sender_password = 'uyscbysunqexdite'
        subject = "Loan Verification Report"
        body = f"""Dear {name},

Your loan verification report was verified successfully. Your petition was approved for the loan waiving process.

Contact your bank officials for further steps.

Regards,
Loan Waiver Team"""

        # Prepare the email
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg.attach(MIMEText(body, 'plain'))

        # Send email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()

        print("Email sent successfully")
        return jsonify({'status': 'success', 'message': 'Verification report sent successfully'}), 200

    except Exception as e:
        print("Error in sending report:", str(e))
        return jsonify({'message': 'Internal server error', 'error': str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

#API route to send notification to the failed sender
@app.route('/send_report_failure', methods=['POST', 'GET'])
def send_report_failure():
    db = None
    cursor = None
    msg = None
    try:
        print("send sms report route triggered")
        data = request.get_json(force=True)
        print("received data", data)
        
        aadhar, smartcard = data.values()
        print("aadhar : ", aadhar)
        print("smartcard : ", smartcard)

        # Fetch user email from DB
        db = get_db_connection()
        cursor = db.cursor(pymysql.cursors.DictCursor)

        cursor.execute("SELECT name, email FROM borrowers WHERE aadhar_number = %s OR smartcard_number=%s", (aadhar, smartcard))
        result = cursor.fetchone()
        print(result)

        if not result:
            return jsonify({"message": "User not found"}), 404

        name = result['name']
        recipient_email = result['email']
        print(f"Found user {name} with email {recipient_email}")

        # Email details
        sender_email = 'sifanaalwmanager@gmail.com'
        sender_password = 'uyscbysunqexdite'
        subject = "Loan Verification Report"
        body = f"""Dear {name},

Your loan verification report was not verified. Your petition was not approved for the loan waiving process.

Contact your bank officials to provide valid aadhar and smart card details.

Regards,
Loan Waiver Team"""

        # Prepare the email
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg.attach(MIMEText(body, 'plain'))

        # Send email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()

        print("Email sent successfully")
        return jsonify({'status': 'success', 'message': 'Verification report sent successfully'}), 200

    except Exception as e:
        print("Error in sending report:", str(e))
        return jsonify({'message': 'Internal server error', 'error': str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

# API Route to upload & verify images
@app.route('/upload', methods=['POST'])
def upload_image():
    print("🔹 Received upload request")
    if "aadhaar_image" not in request.files or "smartcard_image" not in request.files:
        print("❌ Missing files in request:", request.files)
        return jsonify({"error": "Both Aadhaar and Smart Card images are required"}), 400

    aadhaar_file = request.files["aadhaar_image"]
    smartcard_file = request.files["smartcard_image"]

    if not aadhaar_file.filename or not smartcard_file.filename:
        print("❌ One or both files are empty")
        return jsonify({"error": "Empty file uploaded"}), 400

    aadhaar_path = os.path.join("static/uploads", aadhaar_file.filename)
    smartcard_path = os.path.join("static/uploads", smartcard_file.filename)
    print(smartcard_path)
    aadhaar_file.save(aadhaar_path)
    smartcard_file.save(smartcard_path)

    print("✅ Files saved:", aadhaar_path, smartcard_path)
    aadhar, _ = extract_text(aadhaar_path)
    smartcard = extract_smart_card_number(smartcard_path)
    if aadhar:
        aadhar = aadhar.replace(" ", "")

    if smartcard:
        smartcard = smartcard.replace(" ", "")

    print(f"📌 Processed Aadhaar: {aadhar}, Processed Smart Card: {smartcard}")

    if (aadhar is None or not aadhar.strip()) and (smartcard is None or not smartcard.strip()):
        return jsonify({"error": "No valid details found"}), 400
    
    else:
        print("Need Aadhar and Smart Card")

    print(f"📌 Extracted Aadhar: {aadhar}, Smart Card: {smartcard}")

    Vverification_status = verify_in_db(aadhar,smartcard)
    print(Vverification_status)
    if Vverification_status:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("UPDATE borrowers SET verified = 1 WHERE aadhar_number=%s AND smartcard_number=%s", 
                       (aadhar, smartcard))
        db.commit()
        cursor.close()
        db.close()
        name = Vverification_status[3]  
        verification_status = "Verified"
        return render_template('success.html', name=name, aadhar=aadhar, smartcard=smartcard, verified=verification_status)
    else:
        return render_template('failure.html')
    
if __name__ == '__main__':
    app.run(debug=True)


