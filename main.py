import random
import pdb
import argparse
from datetime import datetime, timedelta
import json
from pathlib import Path

SETTINGS_FILE = Path("RAM_Settings.json")


def get_user_confirmation(args):
    if args.yes:
        print("Skipping confirmation because the --yes flag was set")
        return True
    while (True):
        response = input("continue (y/n): ").strip().lower()
        if response == "y" or response == "yes":
            return True
        if response == "n" or response == "no":
            return False
        print("could not identify the response as either yes or no")


# persistent settings
def load_settings():
    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    else:
        return {
            "include_prev": False
        }


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Expected a boolean value.")


def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)



def parse_args():
    parser = argparse.ArgumentParser(
        description="Script for showing, adding and checking off todos from a daily todo-list. Plus some more nice features"
    )

    parser.add_argument(
        "mode",
        nargs="?",
        default="show",
        help="RAM mode. Can be type 's(how)' (default), 'a(dd)', 'c(heck)', 'd(el)', 'r(and(om))' or 'p(rint)'"
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
        metavar="ID",
        help="Instead of task name it is also possible to provide a task id for the show, done, and del modes"
    )

    parser.add_argument(
        "-y", "--yes",
        action="store_true",
        dest="yes",
        help="skip confirmation for deleting tasks or for checking off multiple tasks at once."
    )

    parser.add_argument(
        "--keep-prev",
        type=str2bool,
        metavar="True/False",
        help="Set whether the --prev flag should always be applied. WARNING: this setting persists between calls of the RAM script"
    )

    parser.add_argument(
        "-p", "--prev",
        action="store_true",
        help="This is a combination of the --all flag and the --date <date> flag with the previous date as the argument because this is something that I need often. So basically it will show yesterdays and todays ram entries. This is especially useful just after 0 o'clock.\n\nThis flag will be ignored if either the --all or the --date flag are set"
    )

    parser.add_argument(
        "-a", "--all",
        action="store_true",
        help="show all ram entries (or at least from the specified date until now if --prev or --date are set"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging (so far unused)"
    )

    parser.add_argument(
        "-d", "--date",
        help = "Format 'dd.mm.yyyy'. select a specified date to view tasks from. Or with the --all option view all tasks from that date until today. Instead of this you can also set the --prev flag to get the previous day."
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
        if self.args.date is not None:
            self.cur_date = self.args.date
            try:
                datetime.strptime(self.args.date, "%d.%m.%Y")
            except ValueError:
                print("Error: specified date could not be parsed")
                return
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
        actual_cur_date = datetime.now().strftime("%d.%m.%Y")
        if self.args.all:
            print(f"Showing ram entries from {self.cur_date} until today ({actual_cur_date})")
        else:
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
        actual_cur_date = datetime.now().strftime("%d.%m.%Y")
        if self.cur_date != actual_cur_date:
            print("Warning: you have selected another date than today (or are using the --all flag). Be aware that this will get ignored when adding tasks")
            if not get_user_confirmation(self.args):
                print("aborting...")
                return
            else:
                self.cur_date = datetime.now().strftime("%d.%m.%Y")
                self.args.all = False
                self.args.date = None
                self.filter_tasks()

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
        if not get_user_confirmation(self.args):
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
            if not get_user_confirmation(self.args):
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

    def print(self):
        print(self.cur_date)
        for i, task in self.tasks:
            done = "[x]" in task
            task = task.replace("- [ ] ", "").replace("- [x] ", "")
            if done:
                print(f":white_check_mark: {task}")
            else:
                print(f":white_square_button: {task}")


if __name__ == "__main__":
    args = parse_args()
    settings = load_settings()

    if args.keep_prev is not None:
        if args.keep_prev is True:
            settings["include_prev"] = True
        else:
            settings["include_prev"] = False
        save_settings(settings)

    if settings["include_prev"]:
        args.prev = True

    # Handle the --prev flag
    if not args.date and not args.all:
        if args.prev:
            args.date = (datetime.now() - timedelta(days=1)).strftime("%d.%m.%Y")
            args.all = True

    ram = RAM(args)
    valid_mode = False

    if args.mode == "show" or args.mode == 's':
        valid_mode = True
        ram.show_tasks()

    if args.mode == 'add' or args.mode == 'a':
        valid_mode = True
        ram.add()

    if args.mode == 'del' or args.mode == 'd':
        valid_mode = True
        ram.delete()

    if args.mode == 'check' or args.mode == 'c':
        valid_mode = True
        ram.check()

    if args.mode == 'random' or args.mode == 'rand' or args.mode == 'r':
        valid_mode = True
        ram.random()

    if args.mode == 'print' or args.mode == 'p':
        valid_mode = True
        ram.print()

    if not valid_mode:
        print("No valid mode selected, options are: s(how), a(dd), d(el), c(heck), r(and(om)) or p(rint)")
