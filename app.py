import os
import json
from flask import Flask, request, render_template, redirect, url_for
from datetime import datetime
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "change-me")  # session 加密
APP_PASS = os.getenv("SITE_PASS", "1314502")          # 登录暗号

# 留言数据文件
DATA_FILE = "messages.json"
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

@app.route("/anniversary")
def anniversary():
    return render_template("anniversary.html")
@app.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        name = request.form.get("name", "").strip() or "某人"
        to = request.form.get("to", "").strip() or "TA"
        content = request.form.get("content", "").strip()

        if content:
            msg = {
                "from": name,
                "to": to,
                "content": content,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    all_msgs = json.load(f)
            else:
                all_msgs = []

            all_msgs.append(msg)

            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(all_msgs, f, ensure_ascii=False, indent=2)

        return redirect(url_for("messages"))

    return render_template("submit.html")

@app.route("/messages")
def messages():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            all_msgs = json.load(f)
    else:
        all_msgs = []
    return render_template("messages.html", messages=all_msgs[::-1])

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))
