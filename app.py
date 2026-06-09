from flask import Flask, request, render_template_string
from datetime import datetime
import os

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

sheet = None

try:
    creds = Credentials.from_service_account_file(
        "credentials.json",
        scopes=scope
    )

    client = gspread.authorize(creds)

    # MUST match your Google Sheet name exactly
    sheet = client.open("Bookings").sheet1

    print("✅ Google Sheets connected")

except Exception as e:
    print("❌ Google Sheets error:", e)


# =========================
# SAVE FUNCTION
# =========================
def save_to_sheet(name, email, message):
    if sheet:
        try:
            sheet.append_row([name, email, message, str(datetime.now())])
        except Exception as e:
            print("❌ Failed to write to sheet:", e)
    else:
        print("⚠️ Sheet not available. Data not saved.")


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
            margin-top: 10px;
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
    </style>
</head>
<body>

<div class="card">
    <h2>Book Appointment</h2>

    <form method="POST">
        <input name="name" placeholder="Name" required>
        <input name="email" placeholder="Email" type="email" required>
        <textarea name="message" placeholder="Message"></textarea>
        <button type="submit">Submit</button>
    </form>

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

        save_to_sheet(name, email, message)

        return """
        <h2 style='text-align:center;margin-top:100px;'>
            Thanks! We received your request.
        </h2>
        """

    return render_template_string(form_html)


# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
