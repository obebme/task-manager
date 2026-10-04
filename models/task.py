class Task:
    def __init__(
        self,
        task_id: int,
        title: str,
        description: str,
        completed: bool = False
    ):
        self.id: int = task_id
        self.title: str = title
        self.description: str = description
        self.completed: bool = completed

    def to_dict(self) -> dict[str, int | str | bool]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["id"],
            data["title"],
            data["description"],
            data["completed"]
        )

    def __repr__(self) -> str:
        return (
            f"Task("
            f"id={self.id}, "
            f"title='{self.title}', "
            f"description='{self.description}', "
            f"completed={self.completed}"
            f")"
        )