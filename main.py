from services.task_service import TaskService
from utils.storage import save_tasks, load_tasks


def show_menu() -> None:
    print("\n" + "=" * 40)
    print("           TASK MANAGER")
    print("=" * 40)
    print("1. Показать задачи")
    print("2. Добавить задачу")
    print("3. Найти задачу")
    print("4. Выполнить задачу")
    print("5. Изменить задачу")
    print("6. Удалить задачу")
    print("0. Выйти")
    print("=" * 40)


def show_tasks(service: TaskService) -> None:
    tasks = service.get_tasks()

    if not tasks:
        print("\nСписок задач пуст.")
        return

    print("\n=== СПИСОК ЗАДАЧ ===")

    for task in tasks:
        status = "✓ Выполнена" if task.completed else "○ Не выполнена"

        print(f"\n[{task.id}] {task.title}")
        print(f"    {task.description}")
        print(f"    Статус: {status}")


def main() -> None:
    tasks = load_tasks()
    service = TaskService(tasks)

    while True:
        show_menu()

        choice = input("Выберите действие: ").strip()

        if choice == "1":
            show_tasks(service)

        elif choice == "2":
            title = input("Введите название задачи: ").strip()
            description = input("Введите описание задачи: ").strip()

            if not title:
                print("Название задачи не может быть пустым.")
                continue

            task = service.create_task(title, description)

            save_tasks(service.get_tasks())

            print("\nЗадача успешно добавлена!")
            print(f"ID: {task.id}")
            print(f"Название: {task.title}")

        elif choice == "3":
            try:
                task_id = int(input("Введите ID задачи: "))
            except ValueError:
                print("ID должен быть числом.")
                continue

            task = service.find_task(task_id)

            if task is None:
                print("\nЗадача не найдена.")
            else:
                status = "Выполнена" if task.completed else "Не выполнена"

                print("\n=== ЗАДАЧА ===")
                print(f"ID: {task.id}")
                print(f"Название: {task.title}")
                print(f"Описание: {task.description}")
                print(f"Статус: {status}")

        elif choice == "4":
            try:
                task_id = int(input("Введите ID задачи: "))
            except ValueError:
                print("ID должен быть числом.")
                continue

            task = service.complete_task(task_id)

            if task is None:
                print("\nЗадача не найдена.")
            else:
                save_tasks(service.get_tasks())
                print(f"\nЗадача '{task.title}' отмечена как выполненная.")

        elif choice == "5":
            try:
                task_id = int(input("Введите ID задачи: "))
            except ValueError:
                print("ID должен быть числом.")
                continue

            task = service.find_task(task_id)

            if task is None:
                print("\nЗадача не найдена.")
                continue

            title = input("Введите новое название: ").strip()
            description = input("Введите новое описание: ").strip()

            if not title:
                print("Название задачи не может быть пустым.")
                continue

            task = service.update_task(
                task_id,
                title,
                description
            )

            save_tasks(service.get_tasks())

            print("\nЗадача успешно обновлена!")

        elif choice == "6":
            try:
                task_id = int(input("Введите ID задачи: "))
            except ValueError:
                print("ID должен быть числом.")
                continue

            task = service.find_task(task_id)

            if task is None:
                print("\nЗадача не найдена.")
                continue

            deleted = service.delete_task(task_id)

            if deleted:
                save_tasks(service.get_tasks())
                print(f"\nЗадача '{task.title}' удалена.")

        elif choice == "0":
            print("\nДо свидания!")
            break

        else:
            print("\nНеизвестная команда. Выберите пункт от 0 до 6.")


if __name__ == "__main__":
    main()