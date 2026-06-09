from flask import Flask, request, render_template_string
import os
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)

# =========================
# GOOGLE SHEETS SETUP
# =========================
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file(
    "credentials.json",
    scopes=scope
)

client = gspread.authorize(creds)

sheet = client.open("Bookings").sheet1

print("✅ CONNECTED TO GOOGLE SHEETS")


def save_to_sheet(name, email, message):
    sheet.append_row([name, email, message, str(datetime.now())])


# =========================
# EMAIL NOTIFICATION (OPTIONAL)
# =========================
def send_email_notification(name, email, message):
    your_email = "YOUR_EMAIL@gmail.com"
    your_app_password = "YOUR_APP_PASSWORD"

    try:
        import smtplib

        subject = "New Booking Received"
        body = f"""
New Booking:

Name: {name}
Email: {email}
Message: {message}
Time: {datetime.now()}
"""

        msg = f"Subject: {subject}\n\n{body}"

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(your_email, your_app_password)
        server.sendmail(your_email, your_email, msg)
        server.quit()

        print("📧 Email sent")

    except Exception as e:
        print("Email error:", e)


# =========================
# FRONTEND
# =========================
form_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Booking System</title>
    <style>
        body {
            margin: 0;
            font-family: Arial;
            background: #0b1220;
            color: #e5e7eb;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }

        .card {
            background: #111827;
            padding: 36px;
            border-radius: 16px;
            width: 400px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.6);
            border: 1px solid #1f2937;
            text-align: center;
        }

        h2 {
            margin-bottom: 6px;
        }

        .subtitle {
            font-size: 13px;
            color: #9ca3af;
            margin-bottom: 20px;
        }

        .input-group {
            text-align: left;
            margin-bottom: 14px;
        }

        label {
            font-size: 12px;
            color: #9ca3af;
        }

        input, textarea {
            width: 100%;
            padding: 12px;
            margin-top: 6px;
            border-radius: 10px;
            border: 1px solid #1f2937;
            background: #0b1220;
            color: white;
        }

        button {
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 10px;
            background: #3b82f6;
            color: white;
            font-weight: bold;
            cursor: pointer;
        }

        button:hover {
            background: #2563eb;
        }

        .footer {
            margin-top: 12px;
            font-size: 11px;
            color: #6b7280;
        }
    </style>
</head>

<body>

<div class="card">
    <h2>Book an Appointment</h2>
    <div class="subtitle">We’ll respond within 24 hours</div>

    <form method="POST">

        <div class="input-group">
            <label>Name</label>
            <input name="name" required>
        </div>

        <div class="input-group">
            <label>Email</label>
            <input name="email" type="email" required>
        </div>

        <div class="input-group">
            <label>Message</label>
            <textarea name="message"></textarea>
        </div>

        <button type="submit">Submit Request</button>
    </form>

    <div class="footer">
        Secure system • Automated booking
    </div>
</div>

</body>
</html>
"""


# =========================
# ROUTES
# =========================
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        message = request.form["message"]

        print("\n=== NEW BOOKING ===")
        print("Name:", name)
        print("Email:", email)
        print("Message:", message)
        print("===================")

        # Save to Google Sheets
        try:
            save_to_sheet(name, email, message)
            print("✅ Saved to Google Sheets")
        except Exception as e:
            print("❌ Google Sheets error:", e)

        # Send email (optional)
        try:
            send_email_notification(name, email, message)
        except Exception as e:
            print("❌ Email error:", e)

        return """
        <div style="height:100vh;display:flex;justify-content:center;align-items:center;
        background:#0b1220;color:white;font-family:Arial;text-align:center;">
            <div>
                <h2>Thanks!</h2>
                <p>We received your request.</p>
                <a href="/" style="color:#3b82f6;">Go back</a>
            </div>
        </div>
        """

    return render_template_string(form_html)


# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)