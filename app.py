from flask import Flask, render_template, request, redirect
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)
DB_NAME = 'todo.db'

# 🔸 データベースを初期化（テーブルがなければ作成）
def init_db():
    if not os.path.exists(DB_NAME):
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute('''
                CREATE TABLE tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    done INTEGER DEFAULT 0,
                    due_date TEXT,
                    memo TEXT
                )
            ''')



# 🔸 タスク一覧を取得する関数
def get_all_tasks():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute("SELECT id, content, done, due_date, memo FROM tasks")
        return cursor.fetchall()



# 🔸 ルート（"/"）でタスク一覧を表示
@app.route("/")
def index():
    tasks = get_all_tasks()
    today = datetime.now().strftime("%Y-%m-%d")
    return render_template("index.html", tasks=tasks, today=today)

# 🔸 タスクを追加するルート（POST専用）
@app.route("/add", methods=["POST"])
def add_task():
    content = request.form.get("content")
    due_date = request.form.get("due_date")
    memo = request.form.get("memo")
    if content:
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute(
                "INSERT INTO tasks (content, due_date, memo) VALUES (?, ?, ?)",
                (content, due_date, memo)
            )
    return redirect("/")


@app.route("/done/<int:task_id>", methods=["POST"])
def toggle_done(task_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute("SELECT done FROM tasks WHERE id = ?", (task_id,))
        done = cursor.fetchone()[0]
        new_status = 0 if done == 1 else 1
        conn.execute("UPDATE tasks SET done = ? WHERE id = ?", (new_status, task_id))
    return redirect("/")


@app.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    return redirect("/")

@app.route("/edit/<int:task_id>", methods=["GET"])
def edit_task(task_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        task = cursor.fetchone()
    return render_template("edit.html", task=task)

@app.route("/edit/<int:task_id>", methods=["POST"])
def update_task(task_id):
    memo = request.form.get("memo")
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("UPDATE tasks SET memo = ? WHERE id = ?", (memo, task_id))
    return redirect("/")


# アプリ起動時にDB初期化
if __name__ == "__main__":
    init_db()
    app.run(debug=True)

