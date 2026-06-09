from flask import Flask, request, render_template_string
from datetime import datetime
import os
import json

import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)

# =========================
# GOOGLE SHEETS AUTH (ENV VAR)
# =========================
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Read credentials from Render Environment Variable
service_account_info = json.loads(os.environ["GOOGLE_CREDENTIALS"])

creds = Credentials.from_service_account_info(
    service_account_info,
    scopes=scope
)

client = gspread.authorize(creds)

# MUST match your Google Sheet name exactly
sheet = client.open("Bookings").sheet1

print("✅ CONNECTED TO GOOGLE SHEETS")


# =========================
# SAVE FUNCTION
# =========================
def save_to_sheet(name, email, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([name, email, message, timestamp])
    print("✅ WRITE SUCCESS")


# =========================
# FRONTEND UI
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
            color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .card {
            background: #111827;
            padding: 30px;
            border-radius: 12px;
            width: 400px;
        }
        input, textarea {
            width: 100%;
            padding: 10px;
            margin-top: 5px;
            margin-bottom: 15px;
            border-radius: 8px;
            border: none;
        }
        button {
            width: 100%;
            padding: 10px;
            background: #3b82f6;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
        }
        button:hover {
            background: #2563eb;
        }
    </style>
</head>
<body>

<div class="card">
    <h2>Book Appointment</h2>

    <form method="POST">
        <label>Name</label>
        <input name="name" required>

        <label>Email</label>
        <input name="email" type="email" required>

        <label>Message</label>
        <textarea name="message"></textarea>

        <button type="submit">Submit</button>
    </form>
</div>

</body>
</html>
"""


success_html = """
<div style="height:100vh;display:flex;justify-content:center;align-items:center;
background:#0b1220;color:white;font-family:Arial;text-align:center;">
    <div>
        <h2>✅ Booking Received</h2>
        <p>We saved your request successfully.</p>

        <a href="/" style="
            display:inline-block;
            margin-top:15px;
            padding:10px 20px;
            background:#3b82f6;
            color:white;
            text-decoration:none;
            border-radius:8px;
        ">
            Back
        </a>
    </div>
</div>
"""


# =========================
# ROUTE
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

        try:
            save_to_sheet(name, email, message)
        except Exception as e:
            print("❌ GOOGLE SHEETS ERROR:", repr(e))

        return success_html

    return render_template_string(form_html)


# =========================
# START APP (Render safe)
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
