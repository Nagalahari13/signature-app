from flask import Flask, render_template, request, session, redirect, url_for
import os
import hashlib


from modules.signer import sign_document
from modules.verifier import verify_signature
from modules.certificate_manager import (
    generate_keys, save_private_key, save_public_key,
    load_private_key, load_public_key
)
from modules.logger import log_event
from flask import send_from_directory
from functools import wraps


app = Flask(__name__)

app.secret_key = "supersecretkey"

from functools import wraps

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect("/login")
        return func(*args, **kwargs)
    return wrapper

if not os.path.exists("uploads"):
    os.makedirs("uploads")


UPLOAD_FOLDER = "uploads/"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists("private_key.pem"):
    private_key, public_key = generate_keys()
    save_private_key(private_key, "private_key.pem")
    save_public_key(public_key, "public_key.pem")
else:
    private_key = load_private_key("private_key.pem")
    public_key = load_public_key("public_key.pem")



@app.route("/")
@login_required
def home():
    return render_template("home.html")


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload_file():
    if request.method == "POST":
        file = request.files.get("pdf_file")

        if not file:
            return "No file selected"

       
        if not os.path.exists("uploads"):
            os.makedirs("uploads")

        file_path = os.path.join("uploads", file.filename)

       
        file.save(file_path)
        log_event(f"Uploaded file: {file.filename}")
        print("PDF SAVED TO:", file_path)

        
        with open(file_path, "rb") as f:
            pdf_data = f.read()

        print("SIGN PDF BYTES:", len(pdf_data))   

        
        signature = sign_document(pdf_data, private_key)
        pdf_hash = hashlib.sha256(pdf_data).hexdigest()
        signature_size = len(signature)
        key_size = private_key.key_size

       
        sig_path = file_path + ".sig"
        with open(sig_path, "wb") as f:
            f.write(signature)

        log_event(f"Signed file: {file.filename}")
        print("SIGNATURE SAVED TO:", sig_path)

        return f"""
        <h2>File Signed Successfully!</h2>

        <h3>Signature Metadata</h3>
        <p><b>SHA-256 Hash of PDF:</b> {pdf_hash}</p>
        <p><b>Signature Size:</b> {signature_size} bytes</p>
        <p><b>Key Size:</b> {key_size} bits</p>

        <br>

        <a href='/download/{file.filename}'><button>Download Signed PDF</button></a>
        <br><br>
        <a href='/download/{file.filename}.sig'><button>Download Signature File (.sig)</button></a>
        <br><br>
        <a href='/'><button>Back to Home</button></a>
        """

    return render_template("upload.html")


@app.route("/verify", methods=["GET", "POST"])
@login_required
def verify_page():
    if request.method == "POST":
        pdf_file = request.files["pdf_file"]
        sig_file = request.files["sig_file"]

        pdf_data = pdf_file.read()
        signature = sig_file.read()

        result = verify_signature(pdf_data, signature, public_key)

        if result:
            log_event("Signature verification: VALID")
            return "Signature is VALID ✔"
        else:
            log_event("Signature verification: INVALID")
            return "Signature is INVALID ❌"

    return render_template("verify.html")

@app.route("/download/<filename>")
@login_required
def download_file(filename):
    return send_from_directory("uploads", filename, as_attachment=True)

@app.route("/delete/<filename>")
@login_required
def delete_file(filename):
    file_path = os.path.join("uploads", filename)
    
    if os.path.exists(file_path):
        os.remove(file_path)
        log_event(f"Deleted file: {filename}")
        return f"{filename} deleted successfully! <br><br> <a href='/files'><button>Back</button></a>"
    
    return "File not found!"
@app.route("/logs")
@login_required
def view_logs():
    try:
        with open("logs/activity.log", "r") as f:
            log_data = f.read()
    except:
        log_data = "No logs found."

    return render_template("logs.html", logs=log_data)

@app.route("/files")
@login_required
def view_files():
    files = os.listdir("uploads")
    return render_template("signed_files.html", files=files)

@app.route("/login", methods=["GET", "POST"])

def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        
       
        session["user"] = username
        return redirect("/")
        
        return "Invalid username or password!"

    return render_template("login.html")
@app.route("/logout")

def logout():
    session.pop("user", None)
    return redirect("/login")

@app.route("/clear")
def clear_session():
    session.clear()
    return "Session cleared!"

@app.route("/documentation")
@login_required
def documentation():
    return render_template("documentation.html")

if __name__ == "__main__":
    app.run(debug=True)