from models.task import Task


class TaskService:
    def __init__(self, tasks: list[Task] | None = None):
        self.tasks: list[Task] = tasks if tasks is not None else []

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def get_tasks(self) -> list[Task]:
        return self.tasks

    def find_task(self, task_id: int) -> Task | None:
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def complete_task(self, task_id: int) -> Task | None:
        task = self.find_task(task_id)

        if task is not None:
            task.completed = True
            return task

        return None

    def delete_task(self, task_id: int) -> bool:
        task = self.find_task(task_id)

        if task is not None:
            self.tasks.remove(task)
            return True

        return False

    def update_task(
        self,
        task_id: int,
        title: str,
        description: str
    ) -> Task | None:
        task = self.find_task(task_id)

        if task is not None:
            task.title = title
            task.description = description
            return task

        return None

    def create_task(self, title: str, description: str) -> Task:
        task_id = max((task.id for task in self.tasks), default=0) + 1
        new_task = Task(task_id, title, description)
        self.add_task(new_task)
        return new_task