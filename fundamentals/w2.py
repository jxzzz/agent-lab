import json
from pathlib import Path

def load_tasks():
    with open('./task.json', 'r') as f:
        return json.load(f)


def save_tasks(tasks):
    with open('./task.json', 'w') as f:
        json.dump(tasks, f, indent=4)

def add_task():
    tasks = load_tasks()
    title = input("Enter the task title: ")
    new_task = {"id": len(tasks) + 1, "title": title, "done": False}
    tasks.append(new_task)
    save_tasks(tasks)
    return new_task

def list_tasks():
    tasks = load_tasks()
    for task in tasks:
        status = "Done" if task["done"] else "Not Done"
        print(f"{task['id']}. {task['title']} - {status}")

def mark_task_done():
    tasks = load_tasks()
    task_id = int(input("Enter the task id: "))
    
    for task in tasks:
        if task["id"] == task_id:
            task["done"] = True
    
    save_tasks(tasks)
    return None

def main():
    while True:
        print("\nTask Manager")
        print("1. List tasks")
        print("2. Add task")
        print("3. Mark task as done")
        print("4. Exit")
        choice = input("Choose an option: ")

        if choice == '1':
            list_tasks()
        elif choice == '2':
            add_task()
        elif choice == '3':
            mark_task_done()
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()