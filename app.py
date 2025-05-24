import os
from flask import Flask, request, render_template, redirect, url_for, session
from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv

# 读取 .env 配置
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "change-me")
APP_PASS = os.getenv("SITE_PASS", "1314502")

# Supabase 设置
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/")
def home():
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

@app.route("/anniversary")
def anniversary():
    return render_template("anniversary.html")

@app.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        name = request.form.get("name", "").strip() or "某人"
        to = request.form.get("to", "").strip() or "TA"
        content = request.form.get("content", "").strip()
        time_now = datetime.now().isoformat()

        if content:
            try:
                supabase.table("messages").insert({
                    "from": name,
                    "to": to,
                    "content": content,
                    "timestamp": time_now
                }).execute()
            except Exception as e:
                print("写入留言失败：", e)

        return redirect(url_for("messages"))

    return render_template("submit.html")

@app.route("/messages")
def messages():
    try:
        response = supabase.table("messages").select("*").order("timestamp", desc=True).execute()
        all_msgs = response.data
    except Exception as e:
        print("读取留言失败：", e)
        all_msgs = []

    return render_template("messages.html", messages=all_msgs)
