from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "app.sqlite")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    text = db.Column(db.String(255), nullable=False)
    completed = db.Column(db.Boolean, default=False)

with app.app_context():
    db.create_all()

class TaskSchema(ma.Schema):
    class Meta:
        fields = ("id", "text", "completed")

task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)

def update_task_counts():
    total_tasks = Task.query.count()
    pending_tasks = Task.query.filter_by(completed=False).count()
    return total_tasks, pending_tasks

# **** Get Tasks EndPoint ****
@app.route("/tasks", methods=["GET"])
def get_tasks():
    total_tasks, pending_tasks = update_task_counts()
    tasks = Task.query.all()
    result = tasks_schema.dump(tasks)
    return jsonify({"tasks": result, "total_tasks": total_tasks, "pending_tasks": pending_tasks})

# **** Add Tasks EndPoint ****
@app.route("/tasks", methods=["POST"])
def add_task():
    new_task_data = request.json
    new_task = Task(text=new_task_data["text"], completed=new_task_data.get("completed", False))
    db.session.add(new_task)
    db.session.commit()
    total_tasks, pending_tasks = update_task_counts()
    result = task_schema.dump(new_task)
    return jsonify({"tasks": [result], "total_tasks": total_tasks, "pending_tasks": pending_tasks})

# **** Update Tasks EndPoint ****
@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    updated_task_data = request.json
    task = Task.query.get(task_id)
    if task:
        if "text" in updated_task_data:
            task.text = updated_task_data["text"]
        task.completed = updated_task_data.get("completed", task.completed)
        db.session.commit()
    total_tasks, pending_tasks = update_task_counts()
    result = task_schema.dump(task)
    return jsonify({"tasks": [result], "total_tasks": total_tasks, "pending_tasks": pending_tasks})

# **** Delete Tasks Endpoint ****
@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
    total_tasks, pending_tasks = update_task_counts()
    return jsonify({"tasks": [], "total_tasks": total_tasks, "pending_tasks": pending_tasks})

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("port", 5000)))