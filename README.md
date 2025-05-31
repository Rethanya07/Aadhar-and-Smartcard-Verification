# Aadhar-and-Smartcard-Verification
# 🔍 Aadhar & Smart Card Verification System for Loan Waiver

A Flask-based web application designed to verify Aadhar and Smart Card numbers from uploaded images using Optical Character Recognition (OCR). This system streamlines the verification process for loan waiver schemes by automating data extraction and validation against a MySQL database.

---

## ✨ Features

- 🔐 **Login System** with role-based access (Admin, Official)
- 🧠 **OCR Integration** using Tesseract to extract text from uploaded card images
- 🧾 **Image Region Targeting** for accurate number extraction
- 🗃️ **MySQL Integration** for borrower and official records
- ✅ **Auto-Verification** against stored database entries
- 📧 **Email Notifications** for verification results
- 📊 **Admin Dashboard** to manage users and verification logs
- 📤 **Upload and Status Tracking** per user
- 🌙 **Dark Mode Toggle** *(Optional)*
- 🧪 **Error Handling & Validation** throughout the system

---

## 🛠️ Tech Stack

- **Backend**: Python (Flask)
- **Frontend**: HTML, CSS, JavaScript (with Bootstrap)
- **OCR**: Tesseract + OpenCV
- **Database**: MySQL
- **Others**: Gmail SMTP for email alerts
  
---

## 📂 Project Structure
loan-verification-system/  
├── app.py # Main Flask application  
├── templates/ # HTML templates (login, dashboard, verify, etc.)  
├── static/ # CSS, JS, and image files  
├── uploads/ # Folder for uploaded card images  
├── requirements.txt # Python dependencies  
└── README.md # Project documentation  

## 🚀 Getting Started

### 1️⃣ Clone the Repository
  
git clone https://github.com/Rethanya07/Aadhar-and-Smartcard-Verification.git  
cd Aadhar-and-Smartcard-Verification  

### 2️⃣ Create Virtual Environment and Install Dependencies
  
python -m venv venv  
source venv/bin/activate   # On Windows: venv\Scripts\activate  
pip install -r requirements.txt  

### 3️⃣ Configure Database
Set up a MySQL database named loan_verification  
Import the borrowers and officials tables  
Update your MySQL credentials in app.py:  
db = mysql.connector.connect(  
    host="localhost",  
    user="your_user",  
    password="your_password",  
    database="loan_verification"  
)  

### 4️⃣ Run the App
python app.py  
Visit http://127.0.0.1:5000/ in your browser.

---

## 📧 Email Notification Format
Subject: Loan Verification Report  
Body: Your loan verification report was verified successfully. Your petition was approved for the loan waiving process.  
Contact your bank officials for further steps.  
Regards,  
Loan Waiver Team

---

## 🤝 Contributing
Contributions are welcome! Feel free to submit issues or pull requests.

---

## 👨‍💻 Developed By
Rethanya S  
B.Tech IT – Government College of Engineering, Erode  
GitHub: @rethanya07  
