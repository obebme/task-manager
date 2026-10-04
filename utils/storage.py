import json

from models.task import Task


def save_tasks(tasks: list[Task]) -> None:
    data = [task.to_dict() for task in tasks]

    with open("data/tasks.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_tasks() -> list[Task]:
    try:
        with open("data/tasks.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return []

    return [Task.from_dict(task_data) for task_data in data]