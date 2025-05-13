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
        help="RAM mode. Can be type 'show' (default), 'add', 'check' or 'del'"
    )

    parser.add_argument(
        "name",
        nargs="?",
        default=None,
        help="The task name to be added, checked off, shown or deleted"
    )

    parser.add_argument(
        "-n", "--name",
        metavar="TASK",
        dest="name",
        help="Flag for adding the task name. Is identical to just adding the task name as the second arg"
    )
    parser.add_argument(
        "-i", "--id",
        type=int,
        metavar="TASK_ID",
        help="Instead of task name it is also possible to provide a task id for the show, done, and del modes"
    )

    parser.add_argument(
        "-y", "--yes",
        action="store_true",
        dest="yes",
        help="skip confirmation"
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

    def load_file():
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
        return (lines, tasks)

    lines, tasks = load_file()

    def check_tasks_empty():
        if len(tasks) == 0:
            print("warning: selection criteria id and or name filtered tasks so much that none were left")
            print("aborting...")
            return True
        return False

    if args.id is not None:
        tasks = [(i, task) for (i, task) in tasks if i == args.id]

    if args.name is not None:
        tasks = [(i, task) for (i, task) in tasks if args.name.upper() in task.upper()]

    def show(tasks=tasks):
        print(cur_date)
        for i, task in tasks:
            print(f"{i} {task}")

    def reload_and_show_all():
        lines, tasks = load_file()
        show(tasks)

    if args.mode == "show":
        valid_mode = True
        show()

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
        lines.append(f" - [ ] {args.name}\n")
        write_lines_to_file(lines)
        print(f"added new ram entry {args.name}")

    if args.mode == 'add':
        valid_mode = True
        add()

    def get_user_confirmation():
        while (True):
            response = input("continue (y/n): ").strip().lower()
            if response == "y" or response == "yes":
                return True
            if response == "n" or response == "no":
                return False
            print("could not identify the response as either yes or no")

    def delete():
        if check_tasks_empty():
            return

        if args.id is None and args.name is None:
            print("Error: when deleting todos you have to provide an id or part of the name of the task")
            print("aborting...")
            return

        print("Will delete task" + ("" if len(tasks) == 1 else "s"))
        for i, task in tasks:
            print(f"{i} {task}")
        if not args.yes:
            if not get_user_confirmation():
                print("aborting...")
                return

        for (i, task) in tasks:
            for idx, line in enumerate(lines):
                if line.strip() == task.strip():
                    del lines[idx]
                    break
        write_lines_to_file(lines)
        print("Deleted selected task" + ("" if len(tasks) == 1 else "s"))
        reload_and_show_all()

    if args.mode == 'del':
        valid_mode = True
        delete()

    def check():
        if args.id is None and args.name is None:
            print("Error: when checking off todos you have to provide an id or part of the name of the task")
            print("aborting...")
            return

        if check_tasks_empty():
            return

        if len(tasks) != 1:
            print("Multiple tasks selected")
            for i, task in tasks:
                print(f"{i} {task}")
            print("check all those tasks?")
            if not args.yes:
                if not get_user_confirmation():
                    print("aborting...")
                    return

        for i, task in tasks:
            for idx, line in enumerate(lines):
                if line.strip() == task.strip():
                    if "[ ]" in line:
                        lines[idx] = line.replace("[ ]", "[x]")
                    else:
                        lines[idx] = line.replace("[x]", "[ ]")
        write_lines_to_file(lines)
        reload_and_show_all()

    if args.mode == 'check':
        valid_mode = True
        check()

    if not valid_mode:
        print("No valid mode selected, options are: show, add, del, check (list might be outdated)")
