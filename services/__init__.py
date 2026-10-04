from models.task import Task


class TaskService:
    def __init__(self, tasks: list[Task] | None = None):
        self.tasks: list[Task] = tasks if tasks is not None else []