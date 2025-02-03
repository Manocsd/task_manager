from flask import Flask, request, jsonify, render_template, redirect, url_for
from models import db, User, Task

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = r'sqlite:///D:\\rec\\7sem\\task_manager\\your_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Dummy login simulation
current_user = {'id': 1, 'role': 'admin'}  # Simulate an admin user

with app.app_context():
    db.create_all()

# Home Page - Display Tasks
@app.route('/')
def index():
    if current_user['role'] == 'admin':
        tasks = Task.query.all()
    else:
        tasks = Task.query.filter(
            (Task.creator_id == current_user['id']) | (Task.assignee_id == current_user['id'])
        ).all()
    return render_template('index.html', tasks=tasks, user=current_user)

# Create Task Page
@app.route('/create_task', methods=['GET', 'POST'])
def create_task():
    if request.method == 'POST':
        data = request.form
        task = Task(
            title=data['title'],
            description=data['description'],
            creator_id=current_user['id'],
            assignee_id=data.get('assignee_id')
        )
        db.session.add(task)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create_task.html')

# User Management (Admin Only)
@app.route('/users', methods=['GET', 'POST'])
def users():
    if current_user['role'] != 'admin':
        return "Unauthorized", 403
    if request.method == 'POST':
        data = request.form
        user = User(username=data['username'], role=data.get('role', 'user'))
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('users'))
    users = User.query.all()
    return render_template('users.html', users=users)

# Delete Task (Admin or Creator)
@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if current_user['role'] != 'admin' and task.creator_id != current_user['id']:
        return "Unauthorized", 403
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
