from flask import Flask, render_template, request, jsonify
import os, re, smtplib, ssl
from email.message import EmailMessage

app = Flask(__name__)

# ---- Pages ----
@app.route("/")
def home():
    # Make sure templates/index.html exists
    return render_template("index.html")

# ---- Health ----
@app.route("/api/health")
def health():
    return {"ok": True}

# ---- Contact API ----
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

@app.route("/api/contact", methods=["POST", "OPTIONS"])
def api_contact():
    if request.method == "OPTIONS":
        return ("", 204)

    data = request.get_json(silent=True) or request.form or {}

    # Simple honeypot
    if (data.get("_gotcha") or "").strip():
        return jsonify(ok=True), 200

    name    = (data.get("name")    or "").strip()
    email   = (data.get("email")   or "").strip()
    phone   = (data.get("phone")   or "").strip()
    subject = (data.get("subject") or "").strip()
    message = (data.get("message") or "").strip()

    if not name or not subject or not message:
        return jsonify(error={"code":"VALIDATION","message":"Name, subject, and message are required."}), 400
    if not EMAIL_RE.match(email):
        return jsonify(error={"code":"VALIDATION","message":"Valid email required."}), 400

    # Email config
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = int(os.environ.get("SMTP_PORT", "465"))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("SMTP_PASS")
    mail_from = os.environ.get("MAIL_FROM", smtp_user or "no-reply@example.com")
    mail_to   = os.environ.get("MAIL_TO")

    if not (smtp_host and smtp_user and smtp_pass and mail_to):
        return jsonify(error={"code":"CONFIG","message":"Email not configured on server."}), 503

    def sanitize(s: str) -> str:
        return (s or "").replace("\r","").replace("\n","").strip()

    msg = EmailMessage()
    msg["From"] = sanitize(mail_from)            # your verified address
    msg["To"] = sanitize(mail_to)                # where you receive
    msg["Subject"] = f"[Portfolio] {subject} — {name}"
    msg["Reply-To"] = sanitize(email)            # replies go to visitor
    msg.set_content(f"Name: {name}\nEmail: {email}\nPhone: {phone}\n\n{message}\n")

    try:
        context = ssl.create_default_context()
        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as server:
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
    except Exception as e:
        # Print to console so you see why it failed
        print("SMTP ERROR:", repr(e))
        return jsonify(error={"code":"SMTP_ERROR","message":"Unable to send email right now."}), 502

    return jsonify(ok=True), 200

if __name__ == "__main__":
    print("Starting Flask on http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
