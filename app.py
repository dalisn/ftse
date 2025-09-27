from flask import Flask, request, jsonify, render_template_string
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Initialize SQLite database
def init_db():
    with sqlite3.connect('tasks.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

# Root route with HTML form
@app.route('/')
def home():
    return render_template_string('''
        <h1>Task Manager</h1>
        <form method="POST" action="/add_task">
            <input type="text" name="content" placeholder="Enter task" required>
            <button type="submit">Add Task</button>
        </form>
        <h2>Tasks</h2>
        <ul>
            {% for task in tasks %}
                <li>{{ task.content }} (Added: {{ task.created_at }})</li>
            {% endfor %}
        </ul>
        <a href="/tasks">View JSON</a>
    ''', tasks=get_tasks_data())

# Helper function to get tasks
def get_tasks_data():
    with sqlite3.connect('tasks.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, content, created_at FROM tasks')
        tasks = cursor.fetchall()
    return [{'id': task[0], 'content': task[1], 'created_at': task[2]} for task in tasks]

# Route to add a task
@app.route('/add_task', methods=['POST'])
def add_task():
    content = request.form.get('content') or (request.get_json() and request.get_json().get('content'))
    if not content:
        return jsonify({'error': 'Content is required'}), 400
    
    with sqlite3.connect('tasks.db') as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO tasks (content) VALUES (?)', (content,))
        conn.commit()
    
    if request.form:
        return home()  # Redirect to HTML page if form submission
    return jsonify({'message': 'Task added successfully'}), 201

# Route to get all tasks
@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = get_tasks_data()
    return jsonify(tasks)

# Run the app
if __name__ == '__main__':
    init_db()
    app.run(debug=True)