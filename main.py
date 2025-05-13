import random
import pdb
import argparse
import datetime

ram_path = "/home/ceadeus/Main/Organization/ObsidianVaults/Introspection_und_Organisation/0_most_important_pages/RAM - List.md"
ram_path = "./test_ram_file.txt"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Script for showing, adding and checking off todos from a daily todo-list. Plus some more nice features"
    )

    parser.add_argument(
        "mode",
        nargs="?",
        default="show",
        help="can be type 'show' (default), 'add', 'done' or 'del'"
    )

    parser.add_argument(
        "-n", "--name",
        metavar="TASK",
        help="The task name to be added, checked off, shown or deleted"
    )
    parser.add_argument(
        "-i", "--id",
        type=int,
        metavar="TASK_ID",
        help="Instead of task name it is also possible to provide a task id for the show, done, and del modes"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging (so far unused)"
    )

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = parse_args()
    cur_date = datetime.datetime.now().strftime("%d.%m.%Y")
    valid_mode = False

    lines = None
    tasks = []
    with open(ram_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            if (line == ""):
                continue
            if (line.startswith("#") and "cur_date" not in line):
                break
            if (not line.startswith("#")):
                tasks.append(line)
    tasks = list(enumerate(tasks))

    def check_tasks_empty():
        if len(tasks) == 0:
            print("warning: selection criteria id and or name filtered tasks so much that none were left... aborting")
            return True
        return False

    if args.id is not None:
        tasks = [(i, task) for (i, task) in tasks if i == args.id]

    if args.name is not None:
        tasks = [(i, task) for (i, task) in tasks if args.name.upper() in task.upper()]

    if args.mode == "show":
        valid_mode = True
        print(cur_date)
        for i, task in tasks:
            print(f"{i} {task}")

        #     def select_random_task(tasks):
    #         return random.choice(tasks)
    #     random_task = select_random_task(tasks)

    def write_lines_to_file(new_lines):
        with open(ram_path, "w") as file:
            file.writelines(new_lines)

    def add():
        if args.name is None:
            print("Error: cannot add a new ram entry without a given name")
            return
        lines.append(f" - [ ] {args.name}")
        write_lines_to_file(lines)
        print(f"added new ram entry {args.name}")

    if args.mode == 'add':
        valid_mode = True
        add()

    def delete():
        if check_tasks_empty():
            return

        if args.id is None and args.name is None:
            print("Error: when deleting todos you have to provide an id or part of the name of the task")
            return

        if len(tasks) != 1:
            print("Warning: There are multiple tasks selected, do you really want to delete all of them?")
            for i, task in tasks:
                print(f"{i} {task}")
            valid_response = False
            while (not valid_response):
                response = input("continue (y/n): ").strip().lower()
                if response == "y" or response == "yes":
                    valid_response = True
                if response == "n" or response == "no":
                    print("aborting...")
                    return
                if not valid_response:
                    print("could not identify the response as either yes or no")

        for (i, task) in tasks:
            for idx, line in enumerate(lines):
                if line.strip() == task.strip():
                    del lines[idx]
                    break
        write_lines_to_file(lines)
        print("Deleted selected task" + ("" if len(tasks) == 1 else "s"))

    if args.mode == 'del':
        valid_mode = True
        delete()

    if not valid_mode:
        print("No valid mode selected, options are: show, add, del, done (list might be outdated)")
