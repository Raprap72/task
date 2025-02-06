from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Initialize the database and create the tasks table
def initialize_database():
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            task_id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_name TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Delete a task by its ID
@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

# Update a task's details
@app.route('/update/<int:task_id>', methods=['GET', 'POST'])
def update_task(task_id):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        task_name = request.form.get('task_name')  # Safely retrieve form data
        description = request.form.get('description')  # Add this line
        status = request.form.get('status')

        # Validate the inputs
        if len(task_name) > 20 or len(description) > 100:
            flash("Task name must be 20 characters or less. Description must be 100 characters or less.")
            return redirect(url_for('update_task', task_id=task_id))

        # Update the task in the database
        cursor.execute("""
            UPDATE tasks 
            SET task_name = ?, description = ?, status = ? 
            WHERE task_id = ?
        """, (task_name, description, status, task_id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    # For GET, fetch the task details to pre-fill the form
    cursor.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,))
    task = cursor.fetchone()
    conn.close()
    return render_template("update_task.html", task=task)

# Route for adding a new task (this page will contain an empty form for adding a new task)
@app.route("/add", methods=["GET", "POST"])
def add_task():
    if request.method == "POST":
        task_name = request.form["task_name"]
        description = request.form["description"]
        status = request.form["status"]
        
        # Save the task to the database
        conn = sqlite3.connect("tasks.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (task_name, description, status) VALUES (?, ?, ?)", 
                       (task_name, description, status))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    
    # Render an empty form
    return render_template("update_task.html", task=[None, '', '', 'Not Started'])

@app.route('/view/<int:task_id>')
def view_task(task_id):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute("SELECT task_name, description, status FROM tasks WHERE task_id = ?", (task_id,))
    task = cursor.fetchone()
    conn.close()
    return render_template("view_task.html", task=task)
    
# Home page to display tasks
@app.route('/')
def index():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    conn.close()
    return render_template("index.html", tasks=tasks)

# Initialize the database
initialize_database()

if __name__ == "__main__":
    app.run(debug=True)
