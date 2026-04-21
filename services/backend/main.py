from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import psycopg2
import os

app = FastAPI(title="Task Manager API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "taskdb")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres")

def get_conn():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT,
        dbname=DB_NAME, user=DB_USER, password=DB_PASS
    )

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            done BOOLEAN DEFAULT FALSE
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.on_event("startup")
def startup():
    init_db()

class Task(BaseModel):
    title: str
    description: Optional[str] = ""
    done: Optional[bool] = False

class TaskOut(Task):
    id: int

@app.get("/tasks", response_model=List[TaskOut])
def get_tasks():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, title, description, done FROM tasks ORDER BY id DESC")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [{"id": r[0], "title": r[1], "description": r[2], "done": r[3]} for r in rows]

@app.post("/tasks", response_model=TaskOut)
def create_task(task: Task):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (title, description, done) VALUES (%s, %s, %s) RETURNING id",
        (task.title, task.description, task.done)
    )
    task_id = cur.fetchone()[0]
    conn.commit(); cur.close(); conn.close()
    return {**task.dict(), "id": task_id}

@app.patch("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, task: Task):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE tasks SET title=%s, description=%s, done=%s WHERE id=%s RETURNING id",
        (task.title, task.description, task.done, task_id)
    )
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    conn.commit(); cur.close(); conn.close()
    return {**task.dict(), "id": task_id}

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id=%s", (task_id,))
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    conn.commit(); cur.close(); conn.close()
    return {"message": "Deleted"}

@app.get("/health")
def health():
    return {"status": "ok"}
