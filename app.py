import os
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "change-me")  # session 加密
APP_PASS = os.getenv("SITE_PASS", "1314502")          # 登录暗号

@app.route("/", methods=["GET"])
def home():
    # 没登录？去 /login
    if not session.get("auth_ok"):
        return redirect(url_for("login"))
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if request.form.get("password") == APP_PASS:
            session["auth_ok"] = True
            return redirect(url_for("home"))
        else:
            error = "暗号不对哦～"
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))
