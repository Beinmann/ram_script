import random
import pdb
import argparse
from datetime import datetime, timedelta


def get_user_confirmation():
    while (True):
        response = input("continue (y/n): ").strip().lower()
        if response == "y" or response == "yes":
            return True
        if response == "n" or response == "no":
            return False
        print("could not identify the response as either yes or no")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Script for showing, adding and checking off todos from a daily todo-list. Plus some more nice features"
    )

    parser.add_argument(
        "mode",
        nargs="?",
        default="show",
        help="RAM mode. Can be type 'show' (default), 'add', 'check', 'del' or 'random'/'rand'/'ran'"
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
        "-p", "--prev",
        action="store_true",
        help="handle previous days tasks instead"
    )

    parser.add_argument(
        "-a", "--all",
        action="store_true",
        help="show all ram entries (or at least from the specified date until now if --prev or --date (WIP) are set"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging (so far unused)"
    )

    args = parser.parse_args()

    return args


class RAM:
    def __init__(self, args):
        self.ram_path = "/home/ceadeus/Main/Organization/ObsidianVaults/Introspection_und_Organisation/0_most_important_pages/RAM - List.md"
        # self.ram_path = "/home/ceadeus/Main/Scripts/RAM_Script_Python/test_ram_file.txt"

        self.args = args
        self.lines = None
        self.tasks = None
        if self.args.prev:
            self.cur_date = (datetime.now() - timedelta(days=1)).strftime("%d.%m.%Y")
        elif self.args.all:
            self.cur_date = (datetime.now() - timedelta(days=100000)).strftime("%d.%m.%Y") # this is a slight hack. It just sets the destination date hundredthousand days in the past and since args.all is set, it will collect all entries from that date until now
        else:
            self.cur_date = datetime.now().strftime("%d.%m.%Y")
        open(self.ram_path, "a").close()  # create the file if it does not exist yet
        self.load_file()
        self.add_daily_heading_if_not_exists()
        self.filter_tasks()

    def load_file(self):
        with open(self.ram_path, 'r') as file:
            self.lines = file.readlines()
        self.get_tasks_from_lines()

    def get_tasks_from_lines(self):
        self.tasks = []
        found_todays_heading = False
        for line in self.lines:
            line = line.strip()
            if (line == ""):
                continue
            if (line.startswith("#")):
                if self.cur_date not in line:
                    if found_todays_heading:
                        break
                else:
                    found_todays_heading = True
            if (not line.startswith("#")):
                if found_todays_heading or self.args.all:
                    self.tasks.append(line)
        self.tasks = list(enumerate(self.tasks))

    def add_daily_heading_if_not_exists(self):
        cur_date = datetime.now().strftime("%d.%m.%Y")
        todays_heading_exists = False
        for line in self.lines:
            if line.startswith('#') and cur_date in line:
                todays_heading_exists = True

        if not todays_heading_exists:
            self.lines.insert(0, f"### {cur_date}\n")
            self.write_lines_to_file()
            self.load_file()  # reload file

    def filter_tasks(self):
        if self.args.id is not None:
            self.tasks = [(i, task) for (i, task) in self.tasks if i == self.args.id]

        if self.args.name is not None:
            self.tasks = [(i, task) for (i, task) in self.tasks if self.args.name.upper() in task.upper()]

    def show_tasks(self):
        print(self.cur_date)
        for i, task in self.tasks:
            print(f"{i} {task}")

    def reload_and_show_all(self):
        self.load_file()
        self.show_tasks()

    def check_tasks_empty(self):
        if len(self.tasks) == 0:
            print("warning: selection criteria id and or name filtered tasks so much that none were left")
            print("aborting...")
            return True
        return False

    def write_lines_to_file(self):
        with open(self.ram_path, "w") as file:
            file.writelines(self.lines)

    def add(self):
        if self.args.name is None:
            print("Error: cannot add a new ram entry without a given name")
            return
        last_line_with_daily_todo = 0
        for idx, line in enumerate(self.lines):
            if line.startswith("#") and self.cur_date not in line:
                break
            elif line.strip() == "":
                continue
            else:
                last_line_with_daily_todo = idx
        self.lines[last_line_with_daily_todo] += f"- [ ] {self.args.name}\n"
        self.write_lines_to_file()
        print(f"added new ram entry {self.args.name}")
        print()
        self.reload_and_show_all()

    def random(self):
        self.tasks = [(i, task) for (i, task) in self.tasks if "[x]" not in task]
        self.tasks = [random.choice(self.tasks)]
        self.show_tasks()

    def delete(self):
        if self.check_tasks_empty():
            return

        if self.args.id is None and self.args.name is None:
            print("Error: when deleting todos you have to provide an id or part of the name of the task")
            print("aborting...")
            return

        print("Will delete task" + ("" if len(self.tasks) == 1 else "s"))
        for i, task in self.tasks:
            print(f"{i} {task}")
        if not self.args.yes:
            if not get_user_confirmation():
                print("aborting...")
                return

        for (i, task) in self.tasks:
            for idx, line in enumerate(self.lines):
                if line.strip() == task.strip():
                    del self.lines[idx]
                    break
        self.write_lines_to_file()
        print("Deleted selected task" + ("" if len(self.tasks) == 1 else "s"))
        print()
        self.reload_and_show_all()

    def check(self):
        if self.args.id is None and self.args.name is None:
            print("Error: when checking off todos you have to provide an id or part of the name of the task")
            print("aborting...")
            return

        if self.check_tasks_empty():
            return

        if len(self.tasks) != 1:
            print("Multiple tasks selected")
            for i, task in self.tasks:
                print(f"{i} {task}")
            print("check all those tasks?")
            if not self.args.yes:
                if not get_user_confirmation():
                    print("aborting...")
                    return

        for i, task in self.tasks:
            for idx, line in enumerate(self.lines):
                if line.strip() == task.strip():
                    if "[ ]" in line:
                        self.lines[idx] = line.replace("[ ]", "[x]")
                    else:
                        self.lines[idx] = line.replace("[x]", "[ ]")
        self.write_lines_to_file()
        print("Checking off task" + ("" if len(self.tasks) == 1 else "s"))
        print()
        self.reload_and_show_all()


if __name__ == "__main__":
    args2 = parse_args()
    ram = RAM(args2)
    valid_mode = False

    if args2.mode == "show":
        valid_mode = True
        ram.show_tasks()

        #     def select_random_task(tasks):
    #         return random.choice(tasks)
    #     random_task = select_random_task(tasks)

    if args2.mode == 'add':
        valid_mode = True
        ram.add()

    if args2.mode == 'del':
        valid_mode = True
        ram.delete()

    if args2.mode == 'check':
        valid_mode = True
        ram.check()

    if args2.mode == 'random' or args2.mode == 'rand' or args2.mode == 'ran':
        valid_mode = True
        ram.random()


    if not valid_mode:
        print("No valid mode selected, options are: show, add, del, check, random/rand/ran")
