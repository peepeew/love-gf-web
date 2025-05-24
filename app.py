import os
from flask import Flask, request, render_template, redirect, url_for, session
from datetime import datetime, date
from supabase import create_client
from dotenv import load_dotenv

# 读取 .env 配置
load_dotenv()
app = Flask(__name__)
app.debug = True

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

@app.route("/anniversaries")
def anniversaries():
    try:
        response = supabase.table("anniversaries").select("*").order("date", desc=False).execute()
        all_days = response.data
    except Exception as e:
        print("拉取纪念日失败：", e)
        all_days = []

    # 加计算天数字段（兼容 str/date/datetime）
    for a in all_days:
        raw_date = a["date"]
        if isinstance(raw_date, str):
            try:
                d = datetime.strptime(raw_date, "%Y-%m-%d").date()
            except ValueError:
                d = date.today()
        elif isinstance(raw_date, date):
            d = raw_date
        elif isinstance(raw_date, datetime):
            d = raw_date.date()
        else:
            d = date.today()

        a["days_left"] = days_diff(d)

    return render_template("anniversaries.html", anniversaries=all_days)


# 添加纪念日页面 + 表单提交
@app.route("/anniversary/add", methods=["GET", "POST"])
def add_anniversary():
    if request.method == "POST":
        title = request.form.get("title", "无标题").strip()
        date_str = request.form.get("date", "")
        note = request.form.get("note", "").strip()
        creator = request.form.get("creator", "TA")

        if title and date_str:
            try:
                # 👇 转换为标准日期格式
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                iso_date = date_obj.isoformat()

                supabase.table("anniversaries").insert({
                    "title": title,
                    "date": iso_date,
                    "note": note,
                    "creator": creator,
                    "bg_image": None
                }).execute()
            except Exception as e:
                print("插入纪念日失败：", e)

        return redirect(url_for("anniversaries"))

    return render_template("add_anniversary.html")


# 删除纪念日（不限制是谁删的，可根据 creator 加限制）
@app.route("/anniversary/delete/<int:id>")
def delete_anniversary(id):
    try:
        supabase.table("anniversaries").delete().eq("id", id).execute()
    except Exception as e:
        print("删除失败：", e)
    return redirect(url_for("anniversaries"))


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
